from flask import Blueprint
from flask import request
from globals import sessions
from box_api import list_files, file_content, mkdir, upload

bp = Blueprint('api', __name__, url_prefix='/api')
def get_session():
    session = sessions.get(request.args.get('uuid'), None)
    return session

# /api/list/?uuid=0&project=  # if 'project' is empty lists user projects
@bp.route('/list')
def list_dir():
    session = get_session()
    if session is None:
        return 'not authorized', 403
    directory = request.args.get('project')
    return str([i.name for i in list_files('/storage/'+session['name']+'/'+directory)])

@bp.route('/list_public')
def list_public():
    directory = request.args.get('project')
    return str([i.name for i in list_files('/public/'+directory)])

@bp.route('/read')
def read_file():
    session = get_session()
    if session is None:
        return 'not authorized', 403
    file = request.args.get('file')
    return file_content('/storage/'+session['name']+'/'+file)

@bp.route('/read_public')
def read_public():
    file = request.args.get('file')
    return file_content('/public/'+file)

@bp.route('/md', methods=['POST'])
def make_dir():
    session = get_session()
    if session is None:
        return 'not authorized', 403
    name = request.args.get('name')
    if not name:
        return 'invalid name', 400
    print('Mkdir', mkdir('/storage/'+session['name']+name))

@bp.route('/md_public', methods=['POST'])
def make_dir_public ():
    name = request.args.get('name')
    if not name:
        return 'invalid name', 400
    print('Mkdir', mkdir('/public/'+name))

@bp.route('/upload', methods=['POST'])
def upload_file():
    session = get_session()
    if session is None:
        return 'not authorized', 403
    name = request.args.get('name')
    data = request.data
    return str(upload(data,'/storage/'+session['name']+'/'+name) is not None)

@bp.route('/upload_public', methods=['POST'])
def upload_public():
    name = request.args.get('name')
    data = request.data
    return str(upload(data,'/public/'+name) is not None)