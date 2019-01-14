from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

CurDir = os.path.dirname(os.path.realpath(__file__))
Settingfile = os.path.join(CurDir, 'settings.yaml')
Credentialfile = os.path.join(CurDir, 'credentials.json')


class YtCreatorGDrive:

    @staticmethod
    def authority():
        gauth = GoogleAuth(Settingfile)
        # Try to load saved client credentials
        gauth.LoadCredentialsFile(Credentialfile)
        if gauth.credentials is None:
            # Authenticate if they're not there
            gauth.CommandLineAuth()
        elif gauth.access_token_expired:
            # Refresh them if expired
            gauth.Refresh()
        else:
            # Initialize the saved creds
            gauth.Authorize()

        gauth.SaveCredentialsFile(Credentialfile)

        # Save the current credentials to a file
        return gauth

    def __init__(self):
        self.gauth = YtCreatorGDrive.authority()
        self.drive = GoogleDrive(self.gauth)

    def list_file(self):
        return

    def get_share_link(self, filename: str):
        query = "title = '{}'".format(filename)
        file_list = self.drive.ListFile({'q': query}).GetList()
        for file in file_list:
            return (file['webContentLink'])

    def generate_html_preview_file(self, filepath: str):
        from backend.utility.Utility import FileInfo
        fileinfo = FileInfo(filepath)
        previewlink = self.get_share_link(fileinfo.filename)
        print(previewlink)
        preview_html = """<html>
                <head>
                    <title>Video Test</title>
                </head>
                <body>
                    <video controls="controls">
                        <source src="{}" type='video/mp4'/>
                    </video>
                </body>
                </html>
                """.format(previewlink)
        from backend.utility.TempFileMnger import HtmlTempFile
        htmlfile = HtmlTempFile(pre='preview').getfullpath()
        with open(htmlfile, 'w') as previewfile:
            previewfile.write(preview_html)
        return htmlfile


def generate_html_file(output: str):
    gdriver = YtCreatorGDrive()
    previewfile = gdriver.generate_html_preview_file(output)
    return previewfile
