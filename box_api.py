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
    global auth_url, auth_flow
    auth_flow = DropboxOAuth2FlowNoRedirect(DBX_APP_KEY, use_pkce=True, token_access_type='offline')
    auth_url = auth_flow.start()
    return auth_url

def login(auth_code):
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
    return dbx.files_list_folder(path).entries

def file_content(file):
    return dbx.files_download(file)[1].content.decode()

def upload(data, path):
    return dbx.files_upload(data, path, dropbox.files.WriteMode.overwrite)

def delete(path): # also applicable to folders
    return dbx.files_delete(path)

def mkdir(path):
    return dbx.files_create_folder(path)

if __name__ == '__main__':
    # print(get_link())
    login(input().strip())
    for i in dbx.files_list_folder('/storage/moohomor/first').entries:
        print(i.name)
        print(dbx.files_download(i.path_display)[1].content.decode())