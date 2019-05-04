import datetime
import io
import os
import shutil
from threading import Lock

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from httplib2 import Http
from oauth2client import file, client, tools

from publisher.auth.authenticate import CONFIG_DIR
from backend.storage.db.helper import GdriveStorageDb
from backend.storage.utils import MIMETYPES
from backend.utility.Utility import FileInfo
from config.configure import BackendConfigure
from datetime import datetime
import calendar

config: BackendConfigure = BackendConfigure.get_config()
TmpCurDir = config.get_config().TmpDir

CurDir = os.path.dirname(os.path.realpath(__file__))
ClientSecretfile = os.path.join(CurDir, 'client_secrets.json')

SCOPES = 'https://www.googleapis.com/auth/drive'

config: BackendConfigure = BackendConfigure.get_config()
if config is None:
    CurDir = os.path.dirname(os.path.realpath(__file__))
    contentDir = os.path.join(CurDir, '../content')
    contentDir = os.path.abspath(contentDir)
    cachedcontentdir = contentDir
else:
    contentDir = config.StorageMountPoint
    cachedcontentdir = config.CacheStorageMountPoint


class GDriveMnger:
    GdriveCacheStorage = None
    GDriveStorage = None
    authLock = Lock()

    def __init__(self, cachestorage=False):
        self.iscachedstorage = cachestorage
        self.reset_authenticate()

    def reset_authenticate(self):
        cachestorage = self.iscachedstorage
        try:
            GDriveMnger.authLock.acquire()
            if cachestorage:
                token = os.path.join(TmpCurDir, 'cachestorage.json')
                if not os.path.exists(token):
                    shutil.copy2(os.path.join(CONFIG_DIR, 'cachestorage.json'),
                                 TmpCurDir)
                self.localdb = GdriveStorageDb('.cachedstoragedb.db')

            else:
                token = os.path.join(TmpCurDir, 'storage.json')
                if not os.path.exists(token):
                    shutil.copy2(os.path.join(CONFIG_DIR, 'storage.json'),
                                 TmpCurDir)
                self.localdb = GdriveStorageDb('.storagedb.db')
            store = file.Storage(token)
            self.creds = store.get()
            if not self.creds or self.creds.invalid:
                client_id = ClientSecretfile
                flow = client.flow_from_clientsecrets(client_id, SCOPES)
                flags = tools.argparser.parse_args(args=[])
                flags.noauth_local_webserver = True
                self.creds = tools.run_flow(flow, store, flags)
            self.service = build('drive', 'v3', http=self.creds.authorize(Http()))
        finally:
            GDriveMnger.authLock.release()

    @classmethod
    def get_instance(cls, iscached):
        if iscached:
            if GDriveMnger.GdriveCacheStorage is None:
                GDriveMnger.GdriveCacheStorage = GDriveMnger(cachestorage=True)
            return GDriveMnger.GdriveCacheStorage
        else:
            if GDriveMnger.GDriveStorage is None:
                GDriveMnger.GDriveStorage = GDriveMnger(cachestorage=False)
            return GDriveMnger.GDriveStorage

    def get_share_link(self, filepath: str):
        filename = FileInfo(filepath).filename
        fileinfo = self.viewFile(filename)
        if 'webContentLink' in fileinfo:
            return fileinfo['webContentLink']
        return None

    def viewFile(self, name=None, fid=None):
        self.reset_authenticate()

        """
        view-files: Filter based list of the names and ids of the first 10 files the user has access to
        """
        query = ""
        page_token = None
        if name:
            query = "name contains '" + name + "'"
        if fid:
            if name:
                query += " and "
            query += "'" + fid + "' in parents"

        response = self.service.files().list(q=query,
                                             spaces='drive',
                                             fields='nextPageToken, files(id,name,webContentLink,modifiedTime,mimeType)',
                                             pageToken=page_token).execute()
        templist = [response.get('files', [])[i:i + 25] for i in
                    range(0, len(response.get('files', [])), 25)]  # breakdown list to 25 entries at a time
        if len(templist):
            if len(templist[0]):
                return templist[0][0]
        else:
            return None

    def get_fid(self, inp):
        """
        get fileid from share ulr
        :param inp:
        :return:
        """
        if 'drive' in inp:
            if 'open' in inp:
                fid = inp.split('=')[-1]
            else:
                fid = inp.split('/')[-1].split('?')[0]
        else:
            fid = inp
        return fid

    def get_item_info(self, fid):
        self.reset_authenticate()
        files = self.service.files().get(fileId=fid,
                                         fields='id,name,webContentLink,modifiedTime,mimeType').execute()
        return files

    def get_request(self, service, fid):
        request = service.files().get_media(fileId=fid)
        return request, ""

    def download_file(self, fid, output='/tmp/raven/cache'):
        self.reset_authenticate()
        clone = self.get_item_info(fid)
        fname = clone['name']
        fh = io.BytesIO()
        request = self.service.files().get_media(fileId=fid)
        file_path = (os.path.join(output, fname))
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        with open(file_path, 'wb') as f:  # add dynamic name
            f.write(fh.getvalue())
        self.localdb.insert_file(clone)
        print('download file filepath {}'.format(file_path))
        return file_path

    @classmethod
    def identify_mimetype(cls, name):
        extension = "." + str(name.split('.')[-1])
        if (extension in MIMETYPES.keys()):
            return MIMETYPES[extension]
        else:
            return 'application/octet-stream'

    #
    def update_file(self, path, fid):
        self.reset_authenticate()
        fileinfo = FileInfo(filepath=path)
        file_mimeType = self.identify_mimetype(fileinfo.filename)
        media = MediaFileUpload(path, mimetype=file_mimeType)
        new_file = self.service.files().update(fileId=fid,
                                               media_body=media,
                                               fields='id,name,webContentLink,modifiedTime,mimeType').execute()
        return new_file

    def upload_file(self, path, pid):
        try:
            self.reset_authenticate()
            fileinfo = FileInfo(filepath=path)
            file = self.viewFile(fileinfo.filename, pid)
            if file:
                if self.push_needed(file, item_path=path):
                    new_file = self.update_file(path, file['id'])
                else:
                    print('file not change => reuse the exist remote file')
                    new_file = file
            else:
                print('upload new file')
                file_mimeType = self.identify_mimetype(fileinfo.filename)
                file_metadata = {
                    'name': fileinfo.filename,
                    'parents': [pid],
                    'mimeType': file_mimeType
                }
                media = MediaFileUpload(path, mimetype=file_mimeType)
                new_file = self.service.files().create(body=file_metadata,
                                                       media_body=media,
                                                       fields='id,name,webContentLink,modifiedTime,mimeType').execute()

            # self.localdb.insert_file(new_file)
            return new_file
        except Exception as exp:
            print('error on upload file to drive {}'.format(exp))

    def list_out(self, dirname=None, fid=None, mintype=None):
        self.reset_authenticate()
        if fid is None:
            dirinfo = self.viewFile(dirname)
            query = "'" + dirinfo['id'] + "' in parents"
        else:
            query = "'" + fid + "' in parents"
        query += " "
        if mintype:
            query += "and ("
            query += "mimeType='" + mintype + "'"
            query += ")"
            pass
        page_token = None
        resule = []
        while True:
            children = self.service.files().list(q=query,
                                                 spaces='drive',
                                                 fields='nextPageToken, files(id,mimeType,name)',
                                                 pageToken=page_token
                                                 ).execute()
            for child in children.get('files', []):
                resule.append(child)
            page_token = children.get('nextPageToken', None)
            if page_token is None:
                break
        return resule

    def create_dir(self, cwd, pid, name):
        self.reset_authenticate()
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [pid]
        }
        fid = self.service.files().create(body=file_metadata, fields='id').execute()
        full_path = os.path.join(cwd, name)
        return full_path, fid['id']

    def push_needed(self, drive, item_path):

        # drive_time = time.mktime(time.strptime(drive['modifiedTime'], '%Y-%m-%dT%H:%M:%S.%fZ'))
        drive_time = calendar.timegm(datetime.strptime(drive['modifiedTime'], '%Y-%m-%dT%H:%M:%S.%fZ').timetuple())
        # drive_time = time.mktime(time.strptime(drive['modifiedTime'], '%Y-%m-%dT%H:%M:%S.%fZ')) + float(19800.00)
        local_time = os.path.getmtime(item_path)
        if drive_time < local_time:
            return True
        return False

    def push_content(self, cwd, fid):
        self.reset_authenticate()
        local_lis = os.listdir(cwd)
        for item in local_lis:
            item_path = os.path.join(cwd, item)
            iteminfo = self.viewFile(item, fid=fid)
            if os.path.isdir(item_path):
                if iteminfo is None:
                    child_cwd, child_id = self.create_dir(cwd, fid, item)
                else:
                    child_cwd = os.path.join(cwd, item)
                    child_id = iteminfo['id']
                self.push_content(child_cwd, child_id)
            else:
                item_path = os.path.join(cwd, item)
                if iteminfo is None:
                    self.upload_file(item_path, fid)
                else:
                    if self.push_needed(iteminfo, item_path):
                        cid = iteminfo['id']
                        self.update_file(item_path, cid)

    def is_file_exists_at_local(self, filename):
        items = self.localdb.search_info_by_key_value('name', filename)
        if len(items):
            return True
        return False


class GdriveDbSchemma:

    def __init__(self):
        pass


import unittest


class Test_GoogleFiles(unittest.TestCase):
    def setUp(self):
        self.gdriver = GDriveMnger(cachestorage=False)
        # self.gdriver = GDriveMnger()

    def test_get_share_link(self):
        files = self.gdriver.viewFile('timshel_logo.png')
        print(files)
        fid = self.gdriver.get_fid(files['id'])
        fileinfo = self.gdriver.get_item_info(fid)
        print(fileinfo)
        filepath = self.gdriver.download_file(fid, '/tmp/')
        print(filepath)
        file_id_upload = self.gdriver.upload_file(filepath, '12-G8k4almxk1ZTiBp3SxnIRlXiVBDb_O')
        print(file_id_upload)
        # sharelink = self.gdriver.get_share_link('nham_mat_thay_mua_he.mp4')
        # print(sharelink)

    def test_list_out_dir(self):
        all_files = self.gdriver.list_out('content')
        print(all_files)

    def test_push_all_dir(self):
        root_content_dir = self.gdriver.viewFile('content')
        content_dir_id = root_content_dir['id']
        storage_dir_info = self.gdriver.viewFile('storage', content_dir_id)
        if storage_dir_info is None:
            fullpath, id = self.gdriver.create_dir(r'/tmp', content_dir_id, 'storage')
        else:
            id = storage_dir_info['id']
        self.gdriver.push_content('/mnt/Data/Project/ytcreatorservice/backend/storage', id)
        all_files = self.gdriver.list_out('storage', id)
        print(all_files)

