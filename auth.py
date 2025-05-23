"""Auth routes"""
from flask import Blueprint
from flask import request
from werkzeug.security import generate_password_hash, check_password_hash
from globals import sessions
from box_api import list_files, file_content, upload
from uuid import uuid4
from json import dumps, loads
from urllib.parse import unquote_plus

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/authorized')
def authorized():
    """Check is user authorized. Returns '1' if authorized and '0' otherwise"""
    uuid = request.args.get('uuid')
    return str(int(uuid in sessions))

@bp.route('/signup', methods=['POST'])
def signup():
    """Sign up with login and password. Those credentials must be passed through the url parameters. Returns auth token if the registation is successful"""
    name = unquote_plus(request.args.get('name'))
    password = unquote_plus(request.args.get('password'))
    if name in [i.name for i in list_files('/storage')]:
        return 'already signed up', 409
    upload(dumps({'name': name, 'password_hash': generate_password_hash(password)}).encode(),
           '/storage/'+name+'/credentials.json')
    token = str(uuid4())
    sessions[token] = {'name': name}
    return {"status": "OK", "token": token}

@bp.route('/login')
def login():
    """Log in with login and password. Those credentials must be passed through the url parameters. Returns auth token if the registation is successful"""
    name = unquote_plus(request.args.get('name'))
    password = unquote_plus(request.args.get('password'))
    real_password = loads(file_content('/storage/'+name+'/credentials.json'))['password_hash']
    if not check_password_hash(real_password, password):
        return 'wrong password', 403
    token = str(uuid4())
    sessions[token] = {'name': name}
    return {"status": "OK", "token": token}

@bp.route('/logout', methods=['POST'])
def logout():
    """Shut down session by auth token"""
    uuid = request.args.get('uuid')
    if uuid not in sessions:
        return 'uuid does not present', 403
    del sessions[request.args.get('uuid')]
    return "OK"
