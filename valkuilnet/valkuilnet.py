#!/usr/bin/env python3

from flask import Flask, render_template, url_for, request, redirect

import os
import datetime
import random
import time
import json

import clam.common.data
import clam.common.client

if 'VALKUIL_SETTINGS' in os.environ:
    with open(os.environ['VALKUIL_SETTINGS'],'r',encoding='utf-8') as f:
        settings = json.load(f)
    if 'url' not in settings:
        raise Exception("Expected at least a url field in the settings!")
    if 'tmpdir' in settings:
        tmpdir = settings['tmpdir']
    elif 'TMPDIR' in os.environ:
        tmpdir = os.environ['TMPDIR']
    else:
        tmpdir = '/tmp'
else:
    raise Exception("Set VALKUIL_SETTINGS environment variable pointing to settings.json!")

app = Flask(__name__)

def statics():
   return {
       "style": url_for('static',filename='style.css'),
       "script": url_for('static',filename='script.js'),
       "jquery": url_for('static',filename='jquery.min.js'),
       "rotatescript": url_for('static',filename='jquery.rotate/jquery.rotate.js'),
       "icon": url_for('static',filename='favicon.ico')
   }

@app.route('/')
def inputform():
    return render_template("input.html", **statics())

@app.route('/info/')
def about():
    return render_template("about.html", **statics())


@app.route('/process/', methods=['POST'])
def process():
    """Process a given text and redirect to viewer"""
    if 'text' in request.form and request.form['text']:
        text = request.form['text']
    elif 'uploadfile' in request.files:
        text = request.files['uploadfile'].read()
    else:
        return render_template('error.html',**statics().update({'errormessage': "Er is geen geldige tekst ingevoerd!"}) )

    #Verify checkum and other measures to counter spammers
    d = datetime.datetime.utcnow()
    try:
        if int(request.form['checksum']) != d.year + d.month + d.day:
            return render_template('error.html',**statics().update({'errormessage': "Invalid checksum, are you sure you are human? If not, begone!"} ))
    except:
        return render_template('error.html',**statics().update({'errormessage': "Invalid checksum, are you sure you are human? If not, begone!"}) )
    if text.find("href=") != -1 or text.find("<iframe") != -1 or text.find("<img") != -1:
        return render_template('error.html',**statics().update({'errormessage': "Je invoer moet bestaan uit platte tekst, er zijn HTML elementen gedetecteerd en deze kunnen niet verwerkt worden"}) )
    elif text.find("[url=") != -1 or text.find("[img]") != -1:
        return render_template('error.html',**statics().update({'errormessage': "Je invoer moet bestaan uit platte tekst, er zijn BBCode elementen gedetecteerd en deze kunnen niet verwerkt worden"} ))
    elif text.count("http") > 10:
        return render_template('error.html',**statics().update({'errormessage': "Je invoer bevat teveel webaddressen in de tekst, dit is om spam tegen te gaan niet toegestaan"} ))


    #generate a random ID for this project
    doc_id = 'D' + hex(random.getrandbits(128))[2:-1]

    #create CLAM client
    if 'username' in settings:
        client = clam.common.client.CLAMClient(settings['url'],settings['username'], settings['password'], basicauth=True)
    else:
        client = clam.common.client.CLAMClient(settings['url'])

    #creat project
    client.create(doc_id)

    #get specification
    clamdata = client.get(doc_id)

    #add input file
    try:
        client.addinput(id, clamdata.inputtemplate('textinput'), text, filename=doc_id +'.txt',encoding='utf-8')
    except Exception as e:
        try:
            client.delete(doc_id)
        except:
            pass
        return render_template('error.html',**statics().update({'errormessage': "Kon het gekozen bestand niet toevoegen. Dit kan meerdere oorzaken hebben. Valkuil accepteert momenteel alleen platte UTF-8 gecodeerde tekst-bestanden. Met name Microsoft Word bestanden zijn nog niet ondersteund in dit stadium!",'debugmessage':str(e)} ))

    donate = 'donate' in request.form and request.form['donate'] == 'yes'

    #start CLAM
    client.start(doc_id, sensitivity=request.form['sensitivity'], donate=donate)

    while clamdata.status != clam.common.status.DONE:
        clamdata = client.get(doc_id)
        if clamdata == clam.common.status.DONE:
            break
        else:
            time.sleep(1) #wait 1 second before polling status again

    #retrieve output file
    found = False
    for outputfile in clamdata.output:
        if str(outputfile)[-4:] == '.xml':
            try:
                outputfile.loadmetadata()
            except:
                continue
            if outputfile.metadata.provenance.outputtemplate_id == 'foliaoutput' and not found:
                outputfile.copy(os.path.join(tmpdir, doc_id + '.xml'))
                found = True
        elif outputfile == 'error.log':
            outputfile.copy(os.path.join(tmpdir, doc_id + '.log'))



    if not found:
        return render_template('error.html', **statics().update({'errormessage': "Unable to retrieve file from CLAM service", 'debugmessage': " ".join([ str(x) for x in clamdata.output ])  }))

    #remove project
    client.delete(doc_id)

    #TODO: get forward URL from CLAM
    return redirect('/' + doc_id + '/')



