import json
import random
import os
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from utils.session_history import get_session_history
from utils.logger import LOG
from utils.string_utils import clean_thinking

class ScenarioAgent:
    def __init__(self, scenario_name):
        self.name = scenario_name
        self.prompt_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, os.path.pardir, 'prompts', f'{scenario_name}.md')
        self.greetings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, os.path.pardir, 'content', 'greetings', f'{scenario_name}.json')
        
        self.prompt = self.load_prompt()
        self.greetings = self.load_greetings()

        self.create_chatbot()

    def load_prompt(self):
        try:
            with open(self.prompt_file, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except FileNotFoundError:
            raise ValueError(f'Prompt file {self.prompt_file} not found.')

    def load_greetings(self):
        try:
            with open(self.greetings_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            raise ValueError(f'Intro file {self.greetings_file} not found.')
        except json.JSONDecodeError:
            raise ValueError(f'Error decoding JSON from {self.greetings_file}.')
        
    def create_chatbot(self):
        system_prompt = ChatPromptTemplate.from_messages([
            MessagesPlaceholder(variable_name='messages'),
            ('system', self.prompt)
        ])

        self.chatbot = system_prompt | ChatOllama(
            model='qwen3',
            max_tokens=8192,
            temperature=0.8
        )

        self.chatbot_with_history = RunnableWithMessageHistory(self.chatbot, get_session_history)

    def start_new_session(self, session_id: str='default_session'):
        if session_id is None or session_id.strip() == '':
            session_id = self.name

        history = get_session_history(session_id)
        LOG.debug(f'[history]: {history}')

        if not history.messages:
            greeting = random.choice(self.greetings)
            history.add_message(AIMessage(content=greeting))
            return greeting
        else:
            return history.messages[-1].content

    def chat_with_history(self, user_input: str, session_id: str='default_session'):
        if session_id is None or session_id.strip() == '':
            session_id = self.name

        response = self.chatbot_with_history.invoke(
            [
                HumanMessage(content=user_input),
            ], 
            {
                'configurable': {
                    'session_id': session_id,
                }
            }
        )

        return clean_thinking(response.content)
