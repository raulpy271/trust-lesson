from flask import Flask

from api import redis

app = Flask(__name__)

@app.route("/test_db")
def test_db():
    return ""

@app.route("/test_redis")
def test_redis():
    client = redis.get_default_client()
    client.set('test', 'hello')
    return client.get('test')

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
