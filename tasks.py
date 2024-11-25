from crewai import Task
from textwrap import dedent

class Tasks():
    def filter_emails():
        return Task(
            description=dedent('''
            Filter out non-essential emails like newsletters, marketing emails, and other non-urgent emails
            Use your experience and knowledge to determine if an email is essential or not
            EMAILS: 
            -----
            {emails}
            -----
            Your final answer should be a list of emails that are essential
            '''),
            agent=agent
        )
