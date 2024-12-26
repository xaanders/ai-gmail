from gmail import GmailHandler
from crew import EmailCrew
import json

def main():

    # Load company and customer information
    with open('descriptions.json', 'r') as f:
        descriptions = json.load(f)
    
    # Initialize EmailCrew
    email_crew = EmailCrew()
    gmail_handler = GmailHandler()
    
    # Generate email drafts
    email_drafts = email_crew.create_email_drafts(
        descriptions['company_description'],
        descriptions['customers']
    )
    
    # Convert CrewOutput to string and then parse as JSON
    email_drafts_str = str(email_drafts)
    try:
        email_drafts_json = json.loads(email_drafts_str)

        for email in email_drafts_json:
            gmail_handler.create_draft(email)
            print(f"Draft email created for {email['to']}")

        # Save the drafts to a file
        with open('./logs/email_drafts.json', 'w') as f:
            json.dump(email_drafts_json, f, indent=2)

    except json.JSONDecodeError:
        # If the output isn't valid JSON, save as raw text
        
        with open('./logs/email_drafts.json', 'w') as f:
            f.write(email_drafts_str)
    
    print("\nEmail drafts have been generated and saved to ./logs/email_drafts.json")

if __name__ == "__main__":
    main()
