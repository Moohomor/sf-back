"""The heart of backend. Allows to interact with Dropbox storage. Public routes can work without auth token and will work only in '/public/' folders but others require it and work only in '/storage/' folders. Auth token is passed in url parameters"""
from flask import Blueprint
from flask import request
from flask import Response
from globals import sessions
from mimetypes import guess_type
from box_api import list_files, file_content, mkdir, upload, delete, copy_files
from urllib.parse import unquote_plus
import os
import gpt

bp = Blueprint('api', __name__, url_prefix='/api')
def get_session():
    """Get current session. Now used just to get username by auth token"""
    session = sessions.get(request.args.get('uuid'), None)
    return session

# /api/list/?uuid=0&project=  # if 'project' is empty lists user projects
@bp.route('/list')
def list_dir():
    """List all files in specified folder ('project' parameter). Path must be passed through url parameters. Requires auth token ('uuid' parameter)"""
    session = get_session()
    if session is None:
        return 'not authorized', 403
    directory = unquote_plus(request.args.get('project'))
    return [i.name for i in list_files('/storage/'+session['name']+'/'+directory)]

@bp.route('/list_public')
def list_public():
    """List all files in specified folder ('project' parameter). Path must be passed through url parameters"""
    directory = unquote_plus(request.args.get('project'))
    return [i.name for i in list_files('/public/'+directory)]

@bp.route('/list_all_public_projects')
def list_all_public_projects():
    """Lists folders in user's folders and sorts in order of last modified file in them"""
    r = []
    for user in list_files('/public/'):
        for prj in list_files('/public/'+user.name):
            r+=[(max(file.server_modified for file in list_files('/public/'+user.name+'/'+prj.name)),
                 user.name+'/'+prj.name)]
    return [i[1] for i in sorted(r, reverse=True)]

@bp.route('/read')
def read_file():
    """Read some file ('file' parameter). Path must be passed through url parameters. Requires auth token ('uuid' parameter)"""
    session = get_session()
    if session is None:
        return 'not authorized', 403
    file = unquote_plus(request.args.get('file'))
    binary = '.' not in file or file[-3:] not in ['mod','txt','csv']
    return Response(file_content('/storage/'+session['name']+'/'+file, False),
                    mimetype=guess_type(file)[0] if binary else 'text/plain')

@bp.route('/read_public')
def read_public():
    """Read some file ('file' parameter). Path must be passed through url parameters"""
    file = unquote_plus(request.args.get('file'))
    print('the',file)
    binary = '.' not in file or file[-3:] not in ['mod','txt','csv']
    return Response(file_content('/public/'+file, False), mimetype=guess_type(file)[0] if binary else 'text/plain')

@bp.route('/md', methods=['POST'])
def make_dir():
    """Create folder ('name' parameter). Path must be passed through url parameters. Requires auth token ('uuid' parameter)"""
    session = get_session()
    if session is None:
        return 'not authorized', 403
    name = unquote_plus(request.args.get('name'))
    if not name:
        return 'invalid name', 400
    print('Mkdir', mkdir('/storage/'+session['name']+name))
    return 'OK'

@bp.route('/md_public', methods=['POST'])
def make_dir_public ():
    """Create folder ('name' parameter). Path must be passed through url parameters."""
    name = unquote_plus(request.args.get('name'))
    if not name:
        return 'invalid name', 400
    print('Mkdir', mkdir('/public/'+name))
    return 'OK'

@bp.route('/upload', methods=['POST'])
def upload_file():
    """Upload file from data section of request to some folder ('name' parameter). Path must be passed through url parameters. Requires auth token ('uuid' parameter)"""
    session = get_session()
    if session is None:
        return 'not authorized', 403
    name = unquote_plus(request.args.get('name'))
    data = request.data
    return str(upload(data,'/storage/'+session['name']+'/'+name) is not None)

@bp.route('/upload_public', methods=['POST'])
def upload_public():
    """Upload file from data section of request to some folder ('name' parameter). Path must be passed through url parameters."""
    name = unquote_plus(request.args.get('name'))
    data = request.data
    return str(upload(data,'/public/'+name) is not None)

@bp.route('/uploadb', methods=['POST'])
def uploadb_file():
    """Upload file from form to some folder ('name' parameter). Path must be passed through url parameters. Requires auth token ('uuid' parameter)"""
    session = get_session()
    if session is None:
        return 'not authorized', 403
    if 'file' not in request.files:
        return 'where is file', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    file.save(file.filename)
    name = unquote_plus(request.args.get('name'))
    with open(file.filename, 'rb') as f:
        data = f.read()
    os.remove(file.filename)
    return str(upload(data,'/storage/'+session['name']+'/'+name) is not None)

@bp.route('/uploadb_public', methods=['POST'])
def uploadb_public():
    """Upload file from form to some folder ('name' parameter). Path must be passed through url parameters."""
    if 'file' not in request.files:
        return 'where is file', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    file.save(file.filename)
    name = unquote_plus(request.args.get('name'))
    with open(file.filename, 'rb') as f:
        data = f.read()
    os.remove(file.filename)
    return str(upload(data,'/public/'+name) is not None)

@bp.route('/file_rd', methods=['PUT','DELETE'])
def file_rd():
    """Delete file('name' parameter). Path must be passed through url parameters."""
    session = get_session()
    if session is None:
        return 'not authorized', 403
    if request.method == 'PUT':  # TODO: rename file api on PUT
        return 'wip', 405
    name = unquote_plus(request.args.get('name'))
    delete('/storage/'+session['name']+'/'+name)
    return 'OK'

@bp.route('/file_public', methods=['PUT','DELETE'])
def file_public():
    """Delete file ('name' parameter). Path must be passed through url parameters. Requires auth token ('uuid' parameter)"""
    if request.method == 'PUT':  # TODO: rename file api on PUT
        return 'wip', 405
    name = unquote_plus(request.args.get('name'))
    delete('/public/'+name)
    return 'OK'

@bp.route('/copy', methods=['POST'])
def copy_handler():
    """Copy file from one folder to other one. Since just one of two pathes starts with '/storage/' auth token is required."""
    session = get_session()
    frm = unquote_plus(request.args.get('from'))
    to = unquote_plus(request.args.get('to'))
    if (frm.startswith('/storage') or to.startswith('/storage')) and session is None:
        return 'not authorized', 403
    copy_files(frm, to)
    return 'OK'

@bp.route('/gpt')
def gpt_handler():
    msgs = request.get_json(force=True)
    #msgs+=[{"role":"user","content":msg}]
    try:
        return gpt.gpt(msgs)
    except Exception as e:
        print(e)
        return 'Простите, я не могу вам сейчас ничем помочь :('
