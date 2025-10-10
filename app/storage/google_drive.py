import json
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from app.core.config import settings
from app.core.logging import log

# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive.file']


class GoogleDriveManager:
    """Manage Google Drive uploads and folder organization"""
    
    def __init__(self):
        self.service = None
        self.credentials = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.authenticate()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        pass
    
    def authenticate(self):
        """Authenticate with Google Drive API"""
        try:
            creds_file = Path(settings.GOOGLE_DRIVE_CREDENTIALS_FILE)
            token_file = Path(settings.GOOGLE_DRIVE_TOKEN_FILE)
            
            if not creds_file.exists():
                raise FileNotFoundError(
                    f"Google Drive credentials file not found: {creds_file}\n"
                    "Please download OAuth credentials from Google Cloud Console"
                )
            
            creds = None
            
            # Load existing token
            if token_file.exists():
                creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
            
            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    log.info("Refreshed Google Drive credentials")
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(creds_file), SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                    log.info("Obtained new Google Drive credentials")
                
                # Save credentials
                token_file.parent.mkdir(parents=True, exist_ok=True)
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
            
            self.credentials = creds
            self.service = build('drive', 'v3', credentials=creds)
            
            log.info("Google Drive authenticated successfully")
            
        except Exception as e:
            log.error(f"Error authenticating with Google Drive: {str(e)}")
            raise
    
    def create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> str:
        """
        Create a folder in Google Drive
        
        Args:
            folder_name: Name of the folder
            parent_id: Parent folder ID (None for root)
            
        Returns:
            Folder ID
        """
        try:
            # Check if folder already exists
            existing_folder = self.find_folder(folder_name, parent_id)
            if existing_folder:
                log.info(f"Folder '{folder_name}' already exists: {existing_folder}")
                return existing_folder
            
            # Create new folder
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_id:
                file_metadata['parents'] = [parent_id]
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            
            folder_id = folder.get('id')
            log.info(f"Created folder '{folder_name}': {folder_id}")
            
            return folder_id
            
        except HttpError as e:
            log.error(f"Error creating folder '{folder_name}': {str(e)}")
            raise
    
    def find_folder(self, folder_name: str, parent_id: Optional[str] = None) -> Optional[str]:
        """Find folder by name and parent"""
        try:
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            
            if parent_id:
                query += f" and '{parent_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)',
                pageSize=1
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                return files[0]['id']
            
            return None
            
        except HttpError as e:
            log.error(f"Error finding folder '{folder_name}': {str(e)}")
            return None
    
    def create_folder_path(self, path_parts: List[str], root_folder_id: Optional[str] = None) -> str:
        """
        Create nested folder structure
        
        Args:
            path_parts: List of folder names in order
            root_folder_id: Root folder ID to start from
            
        Returns:
            ID of the deepest folder
        """
        current_parent = root_folder_id or settings.GOOGLE_DRIVE_ROOT_FOLDER_ID
        
        for folder_name in path_parts:
            current_parent = self.create_folder(folder_name, current_parent)
        
        return current_parent
    
    def upload_file(
        self,
        file_path: Path,
        folder_id: str,
        file_name: Optional[str] = None,
        mime_type: str = 'video/mp4',
        skip_duplicate_check: bool = False
    ) -> Dict:
        """
        Upload file to Google Drive
        
        Args:
            file_path: Local file path
            folder_id: Destination folder ID
            file_name: Custom file name (uses original if None)
            mime_type: MIME type of the file
            skip_duplicate_check: If True, skip checking for existing files
            
        Returns:
            Dictionary with file info (id, name, webViewLink)
        """
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            file_name = file_name or file_path.name
            
            # Check if file already exists (unless skipped)
            if not skip_duplicate_check:
                existing_file = self.find_file(file_name, folder_id)
                if existing_file:
                    log.info(f"File '{file_name}' already exists: {existing_file['id']}")
                    return existing_file
            
            file_metadata = {
                'name': file_name,
                'parents': [folder_id]
            }
            
            media = MediaFileUpload(
                str(file_path),
                mimetype=mime_type,
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink, size'
            ).execute()
            
            log.info(f"Uploaded file '{file_name}' to Drive: {file.get('id')}")
            
            return {
                'id': file.get('id'),
                'name': file.get('name'),
                'webViewLink': file.get('webViewLink'),
                'size': file.get('size')
            }
            
        except HttpError as e:
            log.error(f"Error uploading file '{file_path}': {str(e)}")
            raise
    
    def find_file(self, file_name: str, folder_id: str) -> Optional[Dict]:
        """Find file by name in specific folder"""
        try:
            query = f"name='{file_name}' and '{folder_id}' in parents and trashed=false"
            
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, webViewLink, size)',
                pageSize=1
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                return files[0]
            
            return None
            
        except HttpError as e:
            log.error(f"Error finding file '{file_name}': {str(e)}")
            return None
    
    def upload_video_with_metadata(
        self,
        video_path: Path,
        metadata: Dict,
        mode: str,
        value: str,
        video_id: str,
        created_at: Optional[datetime] = None
    ) -> Dict:
        """
        Upload video and metadata to organized folder structure
        
        Structure: /TikTok/{mode}/{value}/{YYYY}/{MM}/{video_id}.mp4
        
        Args:
            video_path: Local video file path
            metadata: Video metadata dictionary
            mode: 'profile' or 'hashtag'
            value: Username or hashtag
            video_id: TikTok video ID
            created_at: Video creation date
            
        Returns:
            Dictionary with upload info
        """
        try:
            # Determine date for folder structure
            if created_at:
                date = created_at
            else:
                date = datetime.utcnow()
            
            year = date.strftime('%Y')
            month = date.strftime('%m')
            
            # Create folder structure: TikTok/{mode}/{value}/{YYYY}/{MM}/
            folder_path = ['TikTok', mode, value, year, month]
            folder_id = self.create_folder_path(
                folder_path,
                settings.GOOGLE_DRIVE_ROOT_FOLDER_ID
            )
            
            # Upload video (skip duplicate check for monitoring to always upload new videos)
            video_file_name = f"{video_id}.mp4"
            video_info = self.upload_file(
                video_path,
                folder_id,
                video_file_name,
                'video/mp4',
                skip_duplicate_check=False  # Keep checking to avoid duplicates
            )
            
            # Upload metadata JSON
            metadata_file_name = f"{video_id}_metadata.json"
            metadata_path = video_path.parent / metadata_file_name
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            metadata_info = self.upload_file(
                metadata_path,
                folder_id,
                metadata_file_name,
                'application/json'
            )
            
            # Clean up local metadata file
            metadata_path.unlink()
            
            folder_path_str = '/'.join(folder_path)
            
            log.info(f"Uploaded video and metadata to Drive: {folder_path_str}")
            
            return {
                'video_file_id': video_info['id'],
                'video_web_link': video_info['webViewLink'],
                'metadata_file_id': metadata_info['id'],
                'metadata_web_link': metadata_info['webViewLink'],
                'folder_path': folder_path_str,
                'folder_id': folder_id
            }
            
        except Exception as e:
            log.error(f"Error uploading video with metadata: {str(e)}")
            raise
    
    def delete_file(self, file_id: str):
        """Delete file from Google Drive"""
        try:
            self.service.files().delete(fileId=file_id).execute()
            log.info(f"Deleted file from Drive: {file_id}")
        except HttpError as e:
            log.error(f"Error deleting file {file_id}: {str(e)}")
            raise
    
    def get_file_info(self, file_id: str) -> Optional[Dict]:
        """Get file information"""
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, size, webViewLink, createdTime, modifiedTime'
            ).execute()
            return file
        except HttpError as e:
            log.error(f"Error getting file info {file_id}: {str(e)}")
            return None
    
    def list_files_in_folder(self, folder_id: str, page_size: int = 100) -> List[Dict]:
        """List all files in a folder"""
        try:
            query = f"'{folder_id}' in parents and trashed=false"
            
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, mimeType, size, webViewLink)',
                pageSize=page_size
            ).execute()
            
            return results.get('files', [])
            
        except HttpError as e:
            log.error(f"Error listing files in folder {folder_id}: {str(e)}")
            return []
