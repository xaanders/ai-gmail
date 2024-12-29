from gmail import GmailHandler
from crew import EmailCrew
import json

def summarize_mails(gmail_handler):

    # Load company and customer information
    email_crew = EmailCrew()
    # Check if the token is valid

    emails = gmail_handler.get_todays_emails()
    try:
        analysis = email_crew.analyze_emails(emails[1:4])
    except Exception as e:
        return {'error': str(e)}
    
    return {'status': 'success', 'analysis': str(analysis)}

