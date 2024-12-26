from crewai import Agent, Task, Crew
from dotenv import load_dotenv
import os
import yaml

class EmailCrew:
    def __init__(self):
        load_dotenv()
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.agents = self._load_agents()
        self.tasks = self._load_tasks()

    def _load_yaml(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)

    def _load_agents(self):
        agents_config = self._load_yaml('config/agents.yaml')
        agents = {}
        for agent_name, config in agents_config.items():
            if config:  # Skip commented out agents
                agents[agent_name] = Agent(
                    role=config['role'],
                    goal=config['goal'],
                    backstory=config['backstory'],
                    allow_delegation=False,
                    verbose=True,
                    llm="gpt-3.5-turbo"
                )
        return agents

    def _load_tasks(self):
        tasks_config = self._load_yaml('config/tasks.yaml')
        tasks = {}
        for task_name, config in tasks_config.items():
            if config:  # Skip commented out tasks
                tasks[task_name] = Task(
                    description=config['description'],
                    agent=self.agents[config['agent']],
                    expected_output=config['expected_output']
                )
        return tasks

    def analyze_emails(self, emails_content):
        crew = Crew(
            agents=[self.agents['email_filter_agent']],
            tasks=[self.tasks['filter_task']],
            verbose=True,
            output_file='logs/summarize.json',
        )
        
        result = crew.kickoff(inputs={'emails': emails_content})
        return result

    def create_email_drafts(self, company_info, customers):
        context = {
            'company_info': company_info,
            'customers': customers,
            'output_format': 'json'
        }
        
        crew = Crew(
            agents=[self.agents['email_draft_agent']],
            tasks=[self.tasks['draft_emails_task']],
            verbose=True,
            output_file='logs/email_drafts.json',
        )
        
        result = crew.kickoff(inputs=context)
        return result