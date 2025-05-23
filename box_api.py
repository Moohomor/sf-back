"""Interface module for Dropbox api. Provides functions required only for project purposes"""
import os
import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect
from dotenv import load_dotenv;load_dotenv()

DBX_APP_KEY = os.getenv('DBX_APP_KEY')
dbx: dropbox.Dropbox = None
auth_url: str = None
auth_flow = None

authorized = lambda: bool(dbx)

def get_link():
    """Get link to get auth code"""
    global auth_url, auth_flow
    auth_flow = DropboxOAuth2FlowNoRedirect(DBX_APP_KEY, use_pkce=True, token_access_type='offline')
    auth_url = auth_flow.start()
    return auth_url

def login(auth_code):
    """Login with auth code to get Dropbox 'refresh token'"""
    global dbx
    token = ''
    try:
        with open('dbx_token') as f:
            token = next(f)
            if not token.strip():
                raise Exception('dbx_token is empty')
    except Exception as e:
        print(e)
        token = os.getenv('DBX_TOKEN')
        if not token:
            oauth_result = auth_flow.finish(auth_code)
            token = oauth_result.refresh_token
        with open('dbx_token', 'w') as f:
            f.write(token)
    try:
        dbx = dropbox.Dropbox(oauth2_refresh_token=token, app_key=DBX_APP_KEY)
        dbx.users_get_current_account()
        print('Successfully logged into Dropbox')
    except dropbox.exceptions.AuthError as e:
        print(e)
        with open('dbx_token', 'w') as f:
            f.write(' ')
            print('dbx_token is literally dead')

def list_files(path: str):
    """List all files in specified Dropbox folder. Returns just a list of entries"""
    return dbx.files_list_folder(path).entries

def file_content(file, decode=True):
    """Read file. By default decode parameter is true, which means the function will return plain text. Otherwise will return raw bytes"""
    resp = dbx.files_download(file)[1].content
    return resp.decode() if decode else resp

def upload(data, path):
    """Upload raw bytes to Dropbox folder"""
    return dbx.files_upload(data, path, dropbox.files.WriteMode.overwrite)

def delete(path):  # also applicable to folders
    """Remove specified file/folder. Folder may be not empty, be careful!"""
    return dbx.files_delete(path)

def mkdir(path):
    """Create folder"""
    return dbx.files_create_folder(path)

def copy_files(frm, to):
    """Copy file from one folder to other folder"""
    dbx.files_copy_v2(from_path=frm, to_path=to)

if __name__ == '__main__':
    login(input().strip())
    for i in dbx.files_list_folder('/storage/moohomor/first').entries:
        print(i.name)
        print(dbx.files_download(i.path_display)[1].content.decode())