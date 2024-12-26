from gmail import GmailHandler
from crew import EmailCrew
import json

def main():

    # Load company and customer information
    email_crew = EmailCrew()
    gmail_handler = GmailHandler()
    
    emails = gmail_handler.get_todays_emails()
    filtered_emails = [email for email in emails[:8] if email['sender'] != 'needdd3@gmail.com']
    email_crew.analyze_emails(filtered_emails)

if __name__ == "__main__":
    main()
