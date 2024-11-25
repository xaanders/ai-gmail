from agents import Agent
from tasks import Tasks
from gmail_service import gmail_service

filter_agent = Agent.email_filter_agent()

emails = gmail_service()

filter_task = Tasks.filter_emails(filter_agent, emails)

