# Email Marketing Automation System

This project provides an automated system for generating personalized email drafts using AI agents. It leverages the CrewAI framework to analyze customer data and create tailored email content.

## Features

- Automated email draft generation based on company and customer information
- Personalized content for each recipient
- JSON-based configuration for agents and tasks
- Integration with Gmail for draft creation
- Logging of generated email drafts
- Summarization of emails

## Project Structure

- `config/`: Configuration files for agents and tasks
- `crew.py`: Main entry point for the CrewAI system
- `gmail.py`: Gmail API integration
- `write_drafts.py`: Script to generate email drafts
- `summarize_mails.py`: Script to summarize emails
- `descriptions.json`: JSON file containing company and customer information
- `logs/`: Directory for logging generated email drafts

## API branch

- `api.py`: Api for the email marketing automation system
- `respond_drafts.py`: Script to create email drafts for latest emails
- `summarize_mails.py`: Script to summarize emails


