#!/usr/bin/env python3

from flask import Flask, render_template, url_for

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

@app.route('/about/')
def about():
    return render_template("about.html", **statics())



