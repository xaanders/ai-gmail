from gmail import GmailHandler
from crew import EmailCrew
import json

def respond_drafts(gmail_handler):
    # Initialize EmailCrew
    email_crew = EmailCrew()
    valid = gmail_handler.check_token_status()['valid']
    if not valid:
        return {'error': 'Gmail token expired'}
    
    emails = gmail_handler.get_todays_emails()
    # Generate email drafts
    email_responses = email_crew.respond_to_emails(emails[:3])
    
    # Convert CrewOutput to string and then parse as JSON
    email_responses_str = str(email_responses)
    try:
        print('Parsing email responses')
        email_responses_json = json.loads(email_responses_str)

        for email in email_responses_json:
            gmail_handler.create_draft(email)
            print(f"Email sent to {email['to']}")

        # Save the drafts to a file
        with open('./logs/email_responses.json', 'w') as f:
            json.dump(email_responses_json, f, indent=2)

    except json.JSONDecodeError:
        # If the output isn't valid JSON, save as raw text
        print('Saving email responses as raw text')
        with open('./logs/email_responses.json', 'w') as f:
            f.write(email_responses_str)
    
    print("\nEmail responses have been generated and saved to ./logs/email_responses.json")
