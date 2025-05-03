from flask import Blueprint
from flask import request
from werkzeug.security import generate_password_hash, check_password_hash
from globals import sessions
from box_api import list_files, file_content, mkdir, upload
from uuid import uuid4
from json import dumps, loads

bp = Blueprint('auth', __name__, url_prefix='/auth')
@bp.route('/signup', methods=['POST'])
def signup():
    name = request.args.get('name')
    password = request.args.get('password')
    if name in [i.name for i in list_files('/storage')]:
        return 'already signed up', 409
    upload(dumps({'name':name,'password_hash':generate_password_hash(password)}).encode(),
           '/storage/'+name+'/credentials.json')
    return 'OK'

@bp.route('/login')
def login():
    name = request.args.get('name')
    password = request.args.get('password')
    real_password = loads(file_content('/storage/'+name+'/credentials.json'))['password_hash']
    if not check_password_hash(real_password, password):
        return 'wrong password', 403
    token = str(uuid4())
    sessions[token] = {'name': name}
    return '{"status": OK, "token": "'+token+'"}'