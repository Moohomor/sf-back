from flask import Flask
from flask_cors import CORS
from waitress import serve
import os
from dotenv import load_dotenv;load_dotenv()

import box_api

try:
    box_api.login('')
    print('Dropbox authorized')
except Exception as e:
    print('Please open "/dbx" page')

app = Flask(__name__)
CORS(app)
import api, auth
app.register_blueprint(api.bp, url_prefix='/api')
app.register_blueprint(auth.bp, url_prefix='/auth')

@app.route("/ping")
def ping():
    return "pong"

@app.route('/dbx')
def auth_page():
    if box_api.authorized():
        return "Dropbox is already authorized"
    return (f'1. Go to this <a target="DBX Auth" href="{box_api.get_link()}">page</a><br>'
            f"2. Click \"Allow\" (you might have to log in first).<br>"
            f"3. Copy the authorization code.<br>"
            f"4. Insert it in URL after /dbx/")
@app.route('/dbx/<token>')
def get_token_page(token):
    try:
        box_api.login(token.strip())
        return "Dropbox initialized successfully"
    except Exception as e:
        print(e)
        return str(e), 500

# serve(app, host='0.0.0.0',)
app.run(host='0.0.0.0')