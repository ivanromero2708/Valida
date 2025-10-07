from typing import Dict, List, Optional, Tuple, Union
import pandas as pd
import requests
import os
import urllib.parse
import io
import platform
from io import BytesIO
from langchain_core.document_loaders import Blob
from langchain_core.documents.base import Document
from langchain_community.document_loaders.parsers.pdf import PyPDFParser
from langchain_core.document_loaders.base import BaseLoader
from docx import Document as DocxDocument



def ensure_directory_exists(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def get_long_path(path):
    # Check if the operating system is Windows
    if platform.system() == 'Windows':
        # Apply the \\?\ prefix correctly to handle long paths on Windows
        return '\\\\?\\' + os.path.abspath(path).strip()
    else:
        # Return the normal path for Unix-based systems
        return os.path.abspath(path)

class SharePointClient:
    def __init__(self, tenant_id, client_id, client_secret, resource_url):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.resource_url = resource_url
        self.base_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.access_token = self.get_access_token()  # Initialize and store the access token upon instantiation

    def get_access_token(self):
        """
        This function retrieves an access token from Microsoft's OAuth2 endpoint.
        """
        body = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': self.resource_url + '/.default'
        }
        response = requests.post(self.base_url, headers=self.headers, data=body)

        # ✅ **CAMBIO IMPORTANTE AQUÍ**
        # Verifica si la solicitud fue exitosa antes de obtener el token
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            # Lanza un error para detener la ejecución y mostrar el problema
            raise Exception(f"Error al obtener el token: {response.status_code} - {response.text}")

    def _build_site_request_candidates(self, site_url: str) -> List[str]:
        if site_url is None:
            raise ValueError("site_url must not be None")

        cleaned = site_url.strip().strip('"').strip("'")
        if not cleaned:
            raise ValueError("site_url must not be empty")

        if cleaned.count(',') == 2 and ',' in cleaned:
            return [cleaned]

        host = ''
        segments: List[str] = []

        if cleaned.startswith(('http://', 'https://')):
            parsed = urllib.parse.urlparse(cleaned)
            host = parsed.netloc
            segments = [seg for seg in parsed.path.split('/') if seg]
        elif ":/" in cleaned:
            host, remainder = cleaned.split(':/', 1)
            segments = [seg for seg in remainder.split('/') if seg]
        elif '/' in cleaned:
            host, remainder = cleaned.split('/', 1)
            segments = [seg for seg in remainder.split('/') if seg]
        else:
            return [cleaned]

        host = host.strip()
        segments = [urllib.parse.unquote(seg.strip()) for seg in segments if seg.strip()]
        if not host:
            raise ValueError(f"Unable to determine SharePoint hostname from '{site_url}'")

        candidates: List[str] = []
        if not segments:
            candidates.append(host)
            return candidates

        min_length = 1
        if segments[0].lower() in {'sites', 'teams', 'personal'}:
            min_length = 2

        for end_idx in range(len(segments), min_length - 1, -1):
            candidate_path = '/' + '/'.join(segments[:end_idx])
            candidate = f"{host}:{candidate_path}"
            if candidate not in candidates:
                candidates.append(candidate)

        if not candidates:
            candidates.append(host)

        return candidates

    def _resolve_site_info(self, site_url: str) -> Dict[str, str]:
        candidates = self._build_site_request_candidates(site_url)
        last_error = None

        for candidate in candidates:
            full_url = f'https://graph.microsoft.com/v1.0/sites/{candidate}?$select=id,webUrl'
            response = requests.get(full_url, headers={'Authorization': f'Bearer {self.access_token}'})
            if response.status_code == 200:
                payload = response.json()
                payload['candidate'] = candidate
                return payload
            last_error = response

        error_details = {'site_url': site_url}
        if last_error is not None:
            try:
                error_details['response'] = last_error.json()
            except ValueError:
                error_details['response'] = {'status_code': last_error.status_code, 'text': last_error.text}

        raise Exception(f"Unable to resolve site metadata: {error_details}")

    def _split_sharepoint_path(self, resource_path: str) -> Dict[str, List[str]]:
        if resource_path is None:
            raise ValueError("resource_path must not be None")

        cleaned = resource_path.strip().strip('\"').strip("'")
        if not cleaned:
            raise ValueError("resource_path must not be empty")

        host = ''
        segments_raw: List[str] = []

        if cleaned.startswith(('http://', 'https://')):
            parsed = urllib.parse.urlparse(cleaned)
            host = parsed.netloc
            segments_raw = [seg for seg in parsed.path.split('/') if seg]
        elif ':/' in cleaned:
            host, remainder = cleaned.split(':/', 1)
            segments_raw = [seg for seg in remainder.split('/') if seg]
        elif '/' in cleaned:
            host, remainder = cleaned.split('/', 1)
            segments_raw = [seg for seg in remainder.split('/') if seg]
        else:
            host = cleaned

        host = host.strip()
        if not host:
            raise ValueError(f"Unable to determine SharePoint hostname from '{resource_path}'")

        segments = [urllib.parse.unquote(seg.strip()) for seg in segments_raw]

        return {'host': host, 'segments_raw': segments_raw, 'segments': segments}

    def _sanitize_drive_label(self, label: Optional[str]) -> str:
        if not label:
            return ''
        return ''.join(ch.lower() for ch in label if ch.isalnum())

    def _match_drive_by_label(self, drives: List[Dict[str, str]], library_label: str, library_label_raw: str) -> Optional[Dict[str, str]]:
        targets = {value for value in {self._sanitize_drive_label(library_label), self._sanitize_drive_label(library_label_raw)} if value}
        for drive in drives:
            candidates = [drive.get('name', '')]
            web_url = drive.get('webUrl') if isinstance(drive, dict) else None
            if web_url:
                parsed = urllib.parse.urlparse(web_url)
                if parsed.path:
                    candidates.append(urllib.parse.unquote(parsed.path.split('/')[-1]))
            for candidate in candidates:
                if self._sanitize_drive_label(candidate) in targets and self._sanitize_drive_label(candidate):
                    return drive
        return None

    def _resolve_sharepoint_download(self, sharepoint_path: str) -> Tuple[str, str]:
        split_info = self._split_sharepoint_path(sharepoint_path)
        candidate_path = split_info['host']
        if split_info['segments_raw']:
            candidate_path = f"{split_info['host']}/{'/'.join(split_info['segments_raw'])}"

        site_info = self._resolve_site_info(candidate_path)
        site_id = site_info.get('id')
        if not site_id:
            raise Exception(f"Unable to determine site id for '{sharepoint_path}'")

        candidate = site_info.get('candidate', '')
        candidate_segments_raw: List[str] = []
        if candidate:
            if ':/' in candidate:
                _, remainder = candidate.split(':/', 1)
                candidate_segments_raw = [seg for seg in remainder.split('/') if seg]
            elif '/' in candidate:
                parts = candidate.split('/', 1)
                remainder = parts[1] if len(parts) > 1 else ''
                candidate_segments_raw = [seg for seg in remainder.split('/') if seg]

        site_segment_count = len(candidate_segments_raw)
        segments_raw = split_info['segments_raw']
        segments = split_info['segments']

        if len(segments_raw) <= site_segment_count:
            raise Exception(f"The provided path does not point to a document library: '{sharepoint_path}'")

        library_segment_raw = segments_raw[site_segment_count]
        library_segment = segments[site_segment_count]
        item_segments = segments[site_segment_count + 1:]

        drives = self.get_drive_id(site_id)
        drive = self._match_drive_by_label(drives, library_segment, library_segment_raw)
        if drive is None:
            available = [drive.get('name', '') for drive in drives]
            raise Exception(f"Document library '{library_segment}' not found. Available drives: {available}")

        if not item_segments:
            raise Exception(f"The provided path does not include a file name: '{sharepoint_path}'")

        encoded_parts = [urllib.parse.quote(part.strip('/')) for part in item_segments if part.strip('/')]
        relative_path = '/'.join(encoded_parts)
        content_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive['id']}/root:/{relative_path}:/content"
        return content_url, item_segments[-1]

    def get_site_id(self, site_url):
        site_info = self._resolve_site_info(site_url)
        return site_info.get('id')

    def get_drive_id(self, site_id):
        """
        This function retrieves the IDs and names of all drives associated with a specified SharePoint site.
        
        Parameters:
        site_id (str): The ID of the SharePoint site.

        Returns:
        list: A list of dictionaries. Each dictionary represents a drive on the SharePoint site.
            Each dictionary contains the following keys:
            - 'id': The ID of the drive.
            - 'name': The name of the drive.
        """
        # Retrieve drive IDs and names associated with a site
        drives_url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drives'
        response = requests.get(drives_url, headers={'Authorization': f'Bearer {self.access_token}'})
        drives = response.json().get('value', [])
        return [{'id': drive['id'], 'name': drive.get('name', ''), 'webUrl': drive.get('webUrl', '')} for drive in drives]


    def get_folder_id(self, site_id, drive_id, folder_path):
        """
        This function retrieves the ID of a specified subfolder.
        
        Parameters:
        site_id (str): The ID of the site where the subfolder is located.
        drive_id (str): The ID of the drive where the subfolder is located.
        folder_path (str): The path of the subfolder whose ID is to be retrieved.

        Returns:
        str: The ID of the specified subfolder.
        """

        # Split the folder path into individual folders
        folders = folder_path.split('/')

        # Start with the root folder
        current_folder_id = 'root'

        # Loop through each folder in the path
        for folder_name in folders:
            # Build the URL to access the contents of the current folder
            folder_url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/items/{current_folder_id}/children'
            response = requests.get(folder_url, headers={'Authorization': f'Bearer {self.access_token}'})
            items_data = response.json()

            # Loop through the items and find the folder
            for item in items_data['value']:
                if 'folder' in item and item['name'] == folder_name:
                    # Update the current folder ID and break the loop
                    current_folder_id = item['id']
                    break
            else:
                # If the folder was not found, return None
                return None

        # Return the ID of the final folder in the path
        return current_folder_id

    def list_folder_contents(self, site_id, drive_id, folder_id='root'):
        """
        This function lists the contents of a specific folder in a drive on a site.

        Parameters:
        site_id (str): The ID of the site.
        drive_id (str): The ID of the drive.
        folder_id (str, optional): The ID of the folder. Defaults to 'root'.

        Returns:
        list: A list of dictionaries. Each dictionary contains details about an item in the folder.
            The details include 'id', 'name', 'type', 'mimeType', 'uri', 'path', 'fullpath', 'filename', and 'url'.
        """
        items_list = []
        folder_contents_url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/items/{folder_id}/children'
        while folder_contents_url:
                contents_response = requests.get(folder_contents_url, headers={'Authorization': f'Bearer {self.access_token}'})
                folder_contents = contents_response.json()
                for item in folder_contents.get('value', []):
                    path_parts = item['parentReference']['path'].split('root:')
                    path = path_parts[1] if len(path_parts) > 1 else ''
                    full_path = f"{path}/{item['name']}" if path else item['name']
                    
                    # Modifiez le site_web_url pour pointer vers l'élément spécifique
                    item_url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/items/{item["id"]}'
                    response = requests.get(item_url, headers={'Authorization': f'Bearer {self.access_token}'})
                    item_data = response.json()
                    item_web_url = item_data.get('webUrl', '')

                    items_list.append({
                        'id': item['id'],
                        'name': item['name'],
                        'type': 'folder' if 'folder' in item else 'file',
                        'mimeType': item['file']['mimeType'] if 'file' in item else '',
                        'uri': item.get('@microsoft.graph.downloadUrl', ''),
                        'path': path,
                        'fullpath': full_path,
                        'filename': item['name'],
                        'url': item_web_url
                    })
                folder_contents_url = folder_contents.get('@odata.nextLink')
        return items_list

    
    def download_file(self, download_url, local_path, file_name: Optional[str] = None):
        """
        Download a file either from a presigned/Graph URL or by resolving a SharePoint path.
        
        Parameters:
        download_url (str): Absolute download URL or SharePoint server-relative path.
        local_path (str): Local directory where the file will be stored.
        file_name (Optional[str]): Override for the saved file name.
        """
        if not download_url:
            raise ValueError("download_url must not be empty")

        resolved_url = download_url.strip()
        resolved_name = file_name
        if not resolved_url.lower().startswith(('http://', 'https://')):
            resolved_url, inferred_name = self._resolve_sharepoint_download(resolved_url)
            if resolved_name is None:
                resolved_name = inferred_name

        if resolved_name is None:
            parsed_path = urllib.parse.urlparse(resolved_url).path
            basename = os.path.basename(parsed_path)
            if basename:
                resolved_name = urllib.parse.unquote(basename)
            else:
                raise ValueError("file_name could not be determined for download")

        headers = {'Authorization': f'Bearer {self.access_token}'}
        parsed_url = urllib.parse.urlparse(resolved_url)
        request_headers = headers if parsed_url.netloc.endswith('graph.microsoft.com') else {}
        response = requests.get(resolved_url, headers=request_headers, stream=True)
        if response.status_code == 200:
            full_path = os.path.join(local_path, resolved_name)
            full_path = get_long_path(full_path)
            ensure_directory_exists(full_path)
            with open(full_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            return

        print(f"Failed to download {resolved_name}: {response.status_code} - {response.reason}")


    def download_folder_contents(self, site_id, drive_id, folder_id, local_folder_path, level=0):
        """
        This function recursively downloads all contents from a specified folder on a SharePoint site.
        
        Parameters:
        site_id (str): The ID of the SharePoint site.
        drive_id (str): The ID of the drive on the SharePoint site.
        folder_id (str): The ID of the folder whose contents are to be downloaded.
        local_folder_path (str): The local path where the downloaded files will be saved.
        level (int, optional): The current level of recursion (folder depth). Defaults to 0 for the root folder.

        Returns:
        None. The function saves the downloaded files to the specified local path and prints a success message for each downloaded file.
        """
        # Recursively download all contents from a folder
        folder_contents_url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/items/{folder_id}/children'
        contents_headers = {'Authorization': f'Bearer {self.access_token}'}
        contents_response = requests.get(folder_contents_url, headers=contents_headers)
        folder_contents = contents_response.json()

        if 'value' in folder_contents:
            for item in folder_contents['value']:
                if 'folder' in item:
                    new_path = os.path.join(local_folder_path, item['name'])
                    if not os.path.exists(new_path):
                        os.makedirs(new_path)
                    self.download_folder_contents(site_id, drive_id, item['id'], new_path,
                                                  level + 1)  # Recursive call for subfolders
                elif 'file' in item:
                    file_name = item['name']
                    file_download_url = f"{self.resource_url}/v1.0/sites/{site_id}/drives/{drive_id}/items/{item['id']}/content"
                    self.download_file(file_download_url, local_folder_path, file_name)
    
    def download_file_contents(self, site_id, drive_id, file_id, local_save_path):
        """
        This function downloads the contents of a specified file from a SharePoint site and saves it to a local path.
        
        Parameters:
        site_id (str): The ID of the SharePoint site.
        drive_id (str): The ID of the drive on the SharePoint site.
        file_id (str): The ID of the file to be downloaded.
        local_save_path (str): The local path where the downloaded file will be saved.

        Returns:
        bool: True if the file was successfully downloaded and saved, False otherwise.
        """
        try:
            # Get the file details
            file_url = f'https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/items/{file_id}'
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get(file_url, headers=headers)
            file_data = response.json()

            # Get the download URL and file name
            download_url = file_data['@microsoft.graph.downloadUrl']
            file_name = file_data['name']
            sharepoint_file_path = file_data['parentReference']['path']  # This is the SharePoint file path
            index = sharepoint_file_path.find(":/")

            # Extract everything after ":/"
            if index != -1:
                extracted_path = sharepoint_file_path[index+2:]  # Adding 2 to skip the characters ":/"
                local_save_path = local_save_path + "/" + extracted_path
                os.makedirs(local_save_path, exist_ok=True) # create loclal sub-folder
            else:
                extracted_path = ""
            # print(f"Downloading {file_name} from {extracted_path}")   
            
            # Download the file
            self.download_file(download_url, local_save_path, file_name)

            # If no exception was raised, the file download was successful
            return True

        except requests.exceptions.RequestException as e:
            print(f"Error downloading file: {file_name} err: {e}")
            return False

    def download_all_files(self, site_id, drive_id, local_folder_path, sharepoint_path="root"):
        """
        This method initiates the download of all files from a specific drive on a site.

        Args:
            site_id (str): The ID of the site from which files are to be downloaded.
            drive_id (str): The ID of the drive on the site from which files are to be downloaded.
            local_folder_path (str): The local path where the downloaded files should be stored.
        """
        try:
            if sharepoint_path != "root":
                folder_id = self.get_folder_id(site_id, drive_id, sharepoint_path)
            else:
                folder_id = sharepoint_path

            self.recursive_download(site_id, drive_id, folder_id, local_folder_path)
        except Exception as e:
            print(f"An error occurred while downloading files: {e}")

    def recursive_download(self, site_id, drive_id, folder_id, local_path):
        """
        This method downloads files from a folder and its subfolders recursively.

        Args:
            site_id (str): The ID of the site from which files are to be downloaded.
            drive_id (str): The ID of the drive on the site from which files are to be downloaded.
            folder_id (str): The ID of the folder from which files are to be downloaded.
            local_path (str): The local path where the downloaded files should be stored.
        """
        try:
            folder_contents = self.list_folder_contents(site_id, drive_id, folder_id)
            for item in folder_contents:
                sharepoint_path = item['path']
                sharepoint_path = sharepoint_path.lstrip('/')
                new_local_path = os.path.normpath(os.path.join(local_path, sharepoint_path))
                # Ensure the local directory exists before downloading
                #"data2\\BASIC STUDIES\\1. Cross Category
                #os.makedirs("data2\\BASIC STUDIES\\1. Cross Category", exist_ok=True)
                
                os.makedirs(new_local_path, exist_ok=True)
                if item['type'] == 'folder':
                    self.recursive_download(site_id, drive_id, item['id'], local_path)
                elif item['type'] == 'file':
                    # os.makedirs(os.path.dirname(new_local_path), exist_ok=True)
                    self.download_file(item['uri'], new_local_path, item['name'])
        except Exception as e:
            print(f"An error occurred while recursively downloading files:{new_local_path} {e}")




