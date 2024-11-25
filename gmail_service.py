import logging
import sys
import os
import json
from langchain_community.agent_toolkits import GmailToolkit
from langchain_community.tools.gmail.search import GmailSearch
from langchain_community.tools.gmail.utils import (
    get_gmail_credentials,
    build_resource_service
)

from gmail_utils import clean_email_content, get_credentials

sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(level=logging.DEBUG)

TOKEN_FILE = "./credentials/token.json"
SCOPES = ["https://mail.google.com/"]

def gmail_service():
    try:
        # Get credentials
        credentials = get_credentials()

        # Build Gmail API service
        api_resource = build_resource_service(credentials=credentials)

        # Search emails
        search = GmailSearch(api_resource=api_resource)
        emails = search.run("in:inbox after:2024/11/23")

        for email in emails:
            if "body" in email:
                email["body"] = clean_email_content(email["body"])
            if "snippet" in email:
                email["snippet"] = clean_email_content(email["snippet"])


        with open("./logs/emails.json", "w") as f:
            json.dump(emails, f, indent=4)
                    
        logging.info("Emails saved to emails.json")

    except Exception as e:
        if 'invalid_grant' in str(e):
            logging.error("Invalid grant: %s", e)
            os.remove(TOKEN_FILE)
            main()
        else:
            logging.error("An error occurred: %s", e)



if __name__ == "__main__":
    gmail_service()