from flask import Flask
from sqlalchemy import text

from api import redis
from api.models import Session, Base, engine 

app = Flask(__name__)

@app.route("/test_db")
def test_db():
    with Session() as session:
        Base.metadata.create_all(engine)
        result = session.connection().execute(text("select version() as v"))
        return list(result)[0][0]

@app.route("/test_redis")
def test_redis():
    client = redis.get_default_client()
    client.set('test', 'hello')
    return client.get('test')

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
