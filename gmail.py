from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import json
from datetime import datetime, timedelta
import base64
import email
import logging

TOKEN_FILE='./credentials/token.json'

class GmailHandler:
    def __init__(self):
        self.SCOPES = [
            "https://mail.google.com/",
            "https://www.googleapis.com/auth/gmail.compose",  # For creating drafts
            "https://www.googleapis.com/auth/gmail.modify"    # For creating/modifying emails
        ]
        self.credentials = None


    def authenticate(self):
        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE, 'r') as token:
                    cred_data = json.load(token)
                
                self.credentials = Credentials.from_authorized_user_info(
                    info=cred_data,
                    scopes=self.SCOPES
                )
                
                if self.credentials and self.credentials.valid and not self.credentials.expired:
                    logging.info("Using existing valid token")
                    return
                
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    try:
                        logging.info("Refreshing token")
                        self.credentials.refresh(Request())
                        return
                    except Exception as e:
                        logging.warning(f"Failed to refresh token: {e}")
                        self.credentials = None
                
            except Exception as e:
                logging.error("Failed to load or refresh credentials: %s", e)
                if os.path.exists(TOKEN_FILE):
                    os.remove(TOKEN_FILE)
                self.credentials = None

        # Only reach here if we need new credentials
        if not self.credentials or not self.credentials.valid:
            credentials_path = "./credentials/credentials.json"
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(
                "credentials.json is required for initial authentication. "
                "Please place it in the ./credentials/ directory"
            )
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path,
                self.SCOPES
            )
            
            self.credentials = flow.run_local_server(
                port=8080,
                authorization_prompt_message='Please authorize access to Gmail',
                success_message='Authorization complete! You can close this window.',
                open_browser=True
            )
        
        try:
            cred_json = self.credentials.to_json()
            with open(TOKEN_FILE, "w") as token:
                token.write(cred_json)
            logging.info("Credentials saved to %s", TOKEN_FILE)
        except Exception as e:
            logging.error("Failed to save credentials: %s", e)

    def get_todays_emails(self):
        logging.info("Authenticated " + str(self.credentials))
        service = build('gmail', 'v1', credentials=self.credentials)
        logging.info("Service built " + str(service))
        # Get today's date in RFC 3339 format
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        query = f'after:{int(today.timestamp())}'

        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])

        emails = []
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            
            # Extract email details
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'No Sender')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'No Date')

            # Get email body
            if 'parts' in msg['payload']:
                parts = msg['payload']['parts']
                body = self._get_body_from_parts(parts)
            else:
                body = self._get_body_from_payload(msg['payload'])

            emails.append({
                'subject': subject,
                'sender': sender,
                'date': date,
                'body': self.clean_email_content(body)
            })

        self.save_emails_to_json(emails)

        return emails[:3]

    def create_draft(self, email_data):
        """Create a draft email in Gmail"""
        self.authenticate()
        logging.info("Authenticated " + str(self.credentials))
        try:
            service = build('gmail', 'v1', credentials=self.credentials)
            
            message = {
                'raw': self._create_message(
                    to=email_data['to'],
                    subject=email_data['subject'],
                    message_text=email_data['body']
                )
            }
            
            draft = service.users().drafts().create(
                userId='me',
                body={'message': message}
            ).execute()
            
            logging.info(f"Draft created with ID: {draft['id']}")
            return draft
            
        except Exception as e:
            logging.error(f"An error occurred while creating draft: {e}")
            raise

    """"""""""""""""""""""""""""HELPERS"""""""""""""""""""""""""""
    def _get_body_from_parts(self, parts):
        body = ""
        for part in parts:
            if part.get('mimeType') == 'text/plain':
                body = self._decode_body(part['body'].get('data', ''))
            elif 'parts' in part:
                body = self._get_body_from_parts(part['parts'])
            return body


    def _get_body_from_payload(self, payload):
        if payload.get('mimeType') == 'text/plain':
            return self._decode_body(payload['body'].get('data', ''))
        return ""

    def _decode_body(self, data):
        if not data:
            return ""
        return base64.urlsafe_b64decode(data.encode('UTF-8')).decode('UTF-8')

    def _create_message(self, to, subject, message_text):
        """Create a message for an email"""
        from email.mime.text import MIMEText
        import base64
        
        message = MIMEText(message_text)
        message['to'] = to
        message['subject'] = subject
        
        # Encode the message in base64url format
        raw = base64.urlsafe_b64encode(message.as_bytes())
        return raw.decode()

    def clean_email_content(self, content):
        """Clean email content by removing links, URLs, email addresses, and unnecessary characters."""
        import re
        import unicodedata

        if not content or "<html" in content:
            return ""

        try:
            # Convert content to string if not already
            content = str(content)
            # Remove zero-width and special whitespace characters
            content = re.sub(r'(&zwnj;|&#8199;|&#847;|\u200c|\u200b|\u2063)', '', content)
            # Remove HTML tags, attributes, and styles
            content = re.sub(r'<[^>]*>', '', content)
            content = re.sub(r'style="[^"]*"', '', content)
            content = re.sub(r'class="[^"]*"', '', content)
            content = re.sub(r'id="[^"]*"', '', content)
            # Remove URLs
            content = re.sub(r'(https?://|www\.)\S+', '', content)

            # Remove email addresses
            content = re.sub(r'[\w.-]+@[\w.-]+\.\w+', '', content)

            # Remove click tracking links and phrases
            content = re.sub(r'(click|tap|follow|visit|check out).{0,30}(link|here|button)', '', content, flags=re.IGNORECASE)

            # Remove markdown-style links and parentheses
            content = re.sub(r'\[.*?\]', '', content)
            content = re.sub(r'\(.*?\)', '', content)

            # Normalize Unicode characters
            content = unicodedata.normalize('NFKD', content)

            # Replace problematic Unicode punctuation
            replacements = {
                '"': '"',
                '"': '"',
                '‘': "'",
                '’': "'",
                '–': '-',
                '—': '-',
                '…': '...',
            }
            for old, new in replacements.items():
                content = content.replace(old, new)

            # Clean up whitespace
            content = re.sub(r'\s+', ' ', content).strip()

            # Ensure ASCII output if necessary
            content = content.encode('ascii', 'ignore').decode('ascii')

            # Remove empty brackets or parentheses
            content = re.sub(r'\[\s*\]|\(\s*\)', '', content)

            return content.strip()

        except Exception as e:
            logging.error(f"Error cleaning content: {str(e)}")
            return content.encode('ascii', 'ignore').decode('ascii').strip()

    def save_emails_to_json(self, emails):
        os.makedirs('./logs', exist_ok=True)
        with open('./logs/emails.json', 'w', encoding='utf-8') as f:
            json.dump(emails, f, ensure_ascii=False, indent=2)
        
    def get_authorization_url(self):
        """Get the Gmail authorization URL"""
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                './credentials/credentials.json',
                self.SCOPES
            )
            # Set the redirect URI to your callback endpoint
            flow.redirect_uri = 'http://127.0.0.1:5000/auth/gmail/callback'
            
            authorization_url, _ = flow.authorization_url(
                # Request offline access to get refresh token
                access_type='offline',
                # Force approval prompt to ensure getting refresh token
                prompt='consent',
                # Set token expiration to 600 seconds (10 minutes)
                token_expiry='600',
                include_granted_scopes='true'
            )
            
            # Store the flow object for later use
            self._flow = flow
            return authorization_url
            
        except Exception as e:
            logging.error("Failed to get authorization URL: %s", e)
            raise

    def handle_oauth_callback(self, auth_code):
        """Handle the OAuth callback and save credentials"""
        try:
            if not hasattr(self, '_flow'):
                raise ValueError("Authorization flow not initialized")
            
            # Fetch token with specific expiration
            self._flow.fetch_token(
                code=auth_code,
                # Set token expiration to 600 seconds (10 minutes)
                expires_in=600
            )
            self.credentials = self._flow.credentials
            
            # Save the credentials
            cred_json = self.credentials.to_json()
            os.makedirs('./credentials', exist_ok=True)
            with open(TOKEN_FILE, "w") as token:
                token.write(cred_json)
            
            logging.info("Credentials saved successfully")
            
        except Exception as e:
            logging.error("Failed to handle OAuth callback: %s", e)
            raise
        
    def check_token_status(self):
        """Check token status and time until expiration"""
        if not self.credentials:
            return {
                'valid': False,
                'message': 'No credentials found'
            }
        
        if not self.credentials.valid:
            return {
                'valid': False,
                'message': 'Invalid credentials'
            }
        
        if self.credentials.expiry:
            time_until_expiry = (self.credentials.expiry - datetime.now()).total_seconds()
            return {
                'valid': True,
                'expires_in': time_until_expiry,
                'message': f'Token expires in {time_until_expiry:.0f} seconds'
            }
        
        return {
            'valid': True,
            'message': 'Token has no expiration'
        }
        
