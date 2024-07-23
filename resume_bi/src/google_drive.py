import io
import os

import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload


class GoogleDrive():

    def __init__(self, service_account_file: str, folder_name: str) -> None:

        """ connect """
        SCOPES = ['https://www.googleapis.com/auth/drive']
        CREDS = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=SCOPES
        )
        self.service = build('drive', 'v3', credentials=CREDS)

        """ takes main folder id """
        items = self.service.files().list(
            pageSize=1000,
            fields=(
                "nextPageToken, "
                "files(id, name, mimeType, size, modifiedTime)"
            ),
            q=(
                "mimeType = "
                "'application/vnd.google-apps.folder' and "
                f"name = '{folder_name}'"
            )
        ).execute()

        self._main_folder_id = items['files'][0]['id']

    @property
    def main_folder_id(self):
        return self._main_folder_id

    def list_folders_and_files(
        self, as_df=False, folder_id: str = None
    ) -> dict | pd.DataFrame:
        """ list files and foldes in a folder """

        if folder_id is None:
            folder_id = self._main_folder_id

        items = self.service.files().list(
            pageSize=1000,
            fields=(
                "nextPageToken, files(id, name, mimeType, size, modifiedTime)"
            ),
            q=f"'{folder_id}' in parents"
        ).execute()

        files_and_folders = items.get('files', [])

        if as_df:
            data = []

            for row in files_and_folders:
                # if row["mimeType"] != "application/vnd.google-apps.folder":
                row_data = []
                try:
                    row_data.append(round(int(row["size"]) / 1000000, 2))
                except KeyError:
                    row_data.append(0.00)
                row_data.append(row["id"])
                row_data.append(row["name"])
                row_data.append(row["modifiedTime"])
                row_data.append(row["mimeType"])
                data.append(row_data)

            cleared_df = pd.DataFrame(
                data,
                columns=[
                    'size_in_MB',
                    'id',
                    'name',
                    'last_modification',
                    'type_of_file'
                ]
            )

            return cleared_df

        return files_and_folders

    def upload_file(
        self, file_path: str, file_name: str, folder_id: str = None
    ) -> dict:
        """ upload file to drive """

        if folder_id is None:
            folder_id = self._main_folder_id

        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }

        media = MediaFileUpload(
            file_path,
            mimetype='application/octet-stream',
            resumable=True
        )

        file = (
            self.service.files()
            .create(body=file_metadata, media_body=media, fields='id')
            .execute()
        )

        return file

    def download_file(
        self, file_id: str, file_name: str, folder_path: str = None
    ) -> None:
        """ download file from drive """

        if folder_path is None:
            folder_path = './'

        request = self.service.files().get_media(fileId=file_id)

        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f'Download {int(status.progress() * 100)}%.')

        with open(os.path.join(folder_path, file_name), 'wb') as f:
            f.write(fh.getvalue())

    def download_folder(self, folder_id: str, local_folder_path: str) -> None:
        """ download a folder with pdf files to a local folder """

        os.makedirs(local_folder_path, exist_ok=True)

        files = self.list_folders_and_files(folder_id=folder_id)

        for file in files:
            if file['mimeType'] == 'application/pdf':
                self.download_file(
                    file_id=file['id'],
                    file_name=file['name'],
                    folder_path=local_folder_path
                )

"""  Replace with your actual values
service_account_file = 'path/to/your/service_account.json'
folder_name = 'My PDF Folder'
local_folder_path = './downloaded_pdfs'

drive = GoogleDrive(service_account_file, folder_name)

Get the folder ID (you can use list_folders_and_files to find it)
folder_id = 'your_folder_id'

drive.download_folder(folder_id, local_folder_path) """
