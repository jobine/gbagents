import re
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from utils.logger import LOG

# Message history store
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

def clean_thinking(text):
    patterns = [
        r'<think>.*?</think>', # 移除<think>标签内容
    ]

    cleaned_text = text

    for pattern in patterns:
        cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.DOTALL | re.MULTILINE)

    # cleaned_text = re.sub(r'\n{3, }', '\n\n', cleaned_text)
    cleaned_text = cleaned_text.strip()
    
    return cleaned_text

class ConversationAgent:
    def __init__(self):
        self.name = 'Conversation Agent'

        # Load system prompt
        with open('prompts/conversation_prompt.txt', 'r', encoding='utf-8') as file:
            self.system_prompt = file.read().strip()

        self.prompt = ChatPromptTemplate.from_messages([
            MessagesPlaceholder(variable_name="messages"),
            (
                'system',
                self.system_prompt
            )
        ])

        self.chat_bot = self.prompt | ChatOllama(
            model='qwen3',
            max_tokens=8192,
            temperature=0.8
        )

        self.chat_bot_with_history = RunnableWithMessageHistory(
            self.chat_bot,
            get_session_history
        )

        self.config = {
            'configurable': {
                'session_id': 'default_session',
            }
        }

    def chat(self, user_input: str) -> str:
        response = self.chat_bot.invoke([
            HumanMessage(content=user_input),
        ])

        return response.content
    
    def chat_with_history(self, user_input: str) -> str:
        response = self.chat_bot_with_history.invoke([
            HumanMessage(content=user_input),
        ], self.config)

        LOG.debug(response)

        return clean_thinking(response.content)
