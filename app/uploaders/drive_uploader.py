"""
Google Drive Uploader
"""
import os
import pickle
from pathlib import Path
from typing import Optional, Dict
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from app.core.logging import log

SCOPES = ['https://www.googleapis.com/auth/drive.file']


class DriveUploader:
    """Upload files to Google Drive"""
    
    def __init__(self):
        self.service = None
        from app.core.config import settings
        self.folder_id = settings.GOOGLE_DRIVE_ROOT_FOLDER_ID or "1eJ0IpGpy7KrHkh_157n-qBM04WQCCDc_"
        self.credentials_file = Path(settings.GOOGLE_DRIVE_CREDENTIALS_FILE)
        self.token_file = Path(settings.GOOGLE_DRIVE_TOKEN_FILE)
    
    def init_service(self):
        """Initialize Google Drive service"""
        try:
            log.info("🔐 Initializing Google Drive service...")
            
            creds = None
            
            # Check if token exists
            if self.token_file.exists():
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
            
            # If no valid credentials, authenticate
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    log.info("   Refreshing token...")
                    creds.refresh(Request())
                else:
                    if not self.credentials_file.exists():
                        log.error("❌ credentials.json not found!")
                        log.info("   Please download credentials.json from Google Cloud Console")
                        log.info("   See SETUP_GOOGLE_DRIVE.md for instructions")
                        return None
                    
                    log.info("   Starting OAuth flow...")
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            str(self.credentials_file), SCOPES)
                        creds = flow.run_local_server(port=0)
                    except KeyError:
                        # Handle web credentials format
                        import json
                        with open(self.credentials_file, 'r') as f:
                            creds_data = json.load(f)
                        
                        # Convert web to installed format
                        if 'web' in creds_data:
                            web_creds = creds_data['web']
                            installed_creds = {
                                'installed': {
                                    'client_id': web_creds['client_id'],
                                    'client_secret': web_creds['client_secret'],
                                    'auth_uri': web_creds['auth_uri'],
                                    'token_uri': web_creds['token_uri'],
                                    'redirect_uris': ['http://localhost']
                                }
                            }
                            
                            # Save converted credentials
                            temp_file = Path("credentials_converted.json")
                            with open(temp_file, 'w') as f:
                                json.dump(installed_creds, f)
                            
                            flow = InstalledAppFlow.from_client_secrets_file(
                                str(temp_file), SCOPES)
                            creds = flow.run_local_server(port=0)
                            
                            # Clean up temp file
                            temp_file.unlink(missing_ok=True)
                
                # Save token
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
            
            self.service = build('drive', 'v3', credentials=creds)
            log.info("✅ Google Drive service initialized")
            return self.service
            
        except Exception as e:
            log.error(f"❌ Failed to initialize Drive service: {e}")
            return None
    
    def upload_video(
        self,
        video_path: Path,
        folder_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Upload video to Google Drive
        
        Args:
            video_path: Path to video file
            folder_id: Google Drive folder ID
            metadata: Additional metadata
            
        Returns:
            Dict with upload info
        """
        try:
            if not video_path.exists():
                return {
                    'success': False,
                    'error': 'File not found'
                }
            
            # Initialize service if not already done
            if not self.service:
                self.init_service()
            
            if not self.service:
                return {
                    'success': False,
                    'error': 'Google Drive service not initialized',
                    'message': 'Please set up credentials.json first'
                }
            
            folder_id = folder_id or self.folder_id
            
            log.info(f"📤 Uploading {video_path.name} to Google Drive...")
            log.info(f"   Folder ID: {folder_id}")
            
            # File metadata
            file_metadata = {
                'name': video_path.name,
                'parents': [folder_id]
            }
            
            # Add custom metadata if provided
            if metadata:
                file_metadata.update(metadata)
            
            # Upload file
            media = MediaFileUpload(
                str(video_path),
                mimetype='video/mp4',
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()
            
            log.info(f"   ✅ Uploaded successfully!")
            log.info(f"   File ID: {file.get('id')}")
            log.info(f"   Link: {file.get('webViewLink')}")
            
            return {
                'success': True,
                'file_id': file.get('id'),
                'file_name': file.get('name'),
                'web_link': file.get('webViewLink'),
                'folder_id': folder_id
            }
            
        except Exception as e:
            log.error(f"❌ Upload error: {e}")
            import traceback
            log.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            }
