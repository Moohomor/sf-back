from flask import Flask
from waitress import serve

app = Flask(__name__)

@app.route("/ping")
def ping():
    return "pong"

# serve(app, port='8080')
app.run(port='8080')