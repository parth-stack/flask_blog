from flask import Flask,render_template
import json

with open('config.json','r') as c:
    config_json = json.load(c)

with open('posts.json','r') as p:
    posts_json = json.load(p)

app=Flask(__name__)

@app.route("/")
def initial():
    return render_template("index.html",urls=config_json["urls"],posts=posts_json)