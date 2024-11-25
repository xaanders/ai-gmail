import re
import uuid
import os
import json
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

TOKEN_FILE = "./credentials/token.json"
SCOPES = ["https://mail.google.com/"]

def clean_email_content(content):
    """Clean email content by removing links, URLs, and problematic characters."""
    import re
    
    if not content:
        return ""
    
    try:
        # Convert content to string if it isn't already
        content = str(content)
        
        # Remove URLs with various patterns
        content = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', content)
        content = re.sub(r'(?:https?://)?(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+(?:/\S*)?', '', content)
        
        # Remove email addresses
        content = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '', content)
        
        # Remove click tracking links
        content = re.sub(r'Click here[^.]*\.', '', content, flags=re.IGNORECASE)
        content = re.sub(r'(?:click|tap|follow|visit|check out)(?:\s+\w+){0,3}\s+(?:link|here|button)', '', content, flags=re.IGNORECASE)
        
        # Remove common link text patterns
        content = re.sub(r'\[.*?\]', '', content)  # Remove markdown-style links
        content = re.sub(r'\(.*?\)', '', content)  # Remove parenthetical links
        
        # Remove problematic Unicode characters
        content = re.sub(r'[\u034f\u200b\U0001f4f0-\U0001f4ff]', '', content)
        
        # Replace Unicode punctuation with ASCII
        replacements = {
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
            '–': '-',
            '—': '-',
            '…': '...',
            '\u200b': '',
            '\xa0': ' ',
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        # Clean up whitespace
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\r\n|\r|\n', '\n', content)
        
        # Ensure ASCII-only output
        content = content.encode('ascii', 'ignore').decode('ascii')
        
        # Final cleanup
        content = re.sub(r' +', ' ', content)
        content = '\n'.join(line.strip() for line in content.split('\n') if line.strip())
        
        # Remove any remaining empty brackets or parentheses
        content = re.sub(r'\[\s*\]', '', content)
        content = re.sub(r'\(\s*\)', '', content)
        
        return content.strip()
        
    except Exception as e:
        print(f"Error cleaning content: {str(e)}")
        return content.encode('ascii', 'ignore').decode('ascii').strip()


def get_credentials():
    """Retrieve credentials, reusing token.json if available."""
    credentials = None
    
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, 'r') as token:
                cred_data = json.load(token)
            
            credentials = Credentials.from_authorized_user_info(
                info=cred_data,
                scopes=SCOPES
            )
            
            if not credentials.expired:
                logging.info("Using existing valid token")
                return credentials
                
            if credentials.expired and not credentials.refresh_token:
                logging.warning("Token expired and no refresh token, forcing new authentication")
                os.remove(TOKEN_FILE)
                credentials = None
            elif credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                
        except Exception as e:
            logging.error("Failed to load or refresh credentials: %s", e)
            if os.path.exists(TOKEN_FILE):
                os.remove(TOKEN_FILE)
            credentials = None

    if not credentials or not credentials.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            "./credentials/credentials.json",
            SCOPES
        )
        
        credentials = flow.run_local_server(
            port=8080,
            authorization_prompt_message='Please authorize access to Gmail',
            success_message='Authorization complete! You can close this window.',
            open_browser=True
        )
        
        # Debug log to see what we're getting
        logging.debug("New credentials obtained: %s", credentials.to_json())
        
    # Always save the current state of credentials
    try:
        cred_json = credentials.to_json()
        # Debug log to see what we're saving
        logging.debug("Saving credentials to file: %s", cred_json)
        with open(TOKEN_FILE, "w") as token:
            token.write(cred_json)
        logging.info("Credentials saved to %s", TOKEN_FILE)
    except Exception as e:
        logging.error("Failed to save credentials: %s", e)

    return credentials
