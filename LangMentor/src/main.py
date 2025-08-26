import os
import gradio as gr
from agents.conversation_agent import ConversationAgent
from agents.scenario_agent import ScenarioAgent
from utils.logger import LOG


conversation_agent = ConversationAgent()

scenario_agents = {
    'hotel_checkin': ScenarioAgent('hotel_checkin'),
}


def handle_conversation(user_input, history):
    LOG.debug(f'[Chat history]: {history}')

    bot_message = conversation_agent.chat_with_history(user_input)

    LOG.info(f'[Bot message]: {bot_message}')

    return bot_message


def get_scenario_intro(name: str):
    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, 'content', 'intro', f'{name}.md')

    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        raise ValueError(f'Intro file {filepath} not found.')


def handle_scenario(user_input, history, name):
    bot_message = scenario_agents[name].chat_with_history(user_input, session_id=name)
    
    LOG.info(f'[Scenario Bot message]: {bot_message}')
    
    return bot_message


def create_gradio_app():
    # Build the Gradio app
    with gr.Blocks(title='Language Mentor') as lang_mentor_app:
        with gr.Tab('场景对话'):
            gr.Markdown('## 场景对话练习')

            scenario_selector = gr.Radio(
                choices=[
                    ('酒店入住', 'hotel_checkin'),
                    ('求职面试', 'job_interview'),
                ],
                label='选择场景',
                value='酒店入住'
            )

            scenario_home = gr.Markdown()
            scenario_chatbot = gr.Chatbot(
                placeholder='<strong>请选择一个场景开始对话</strong>',
                height=600,
                type='messages'
            )

            def start_new_scenario_chatbot(scenario_name):
                greeting = scenario_agents[scenario_name].start_new_session(session_id=scenario_name)

                return gr.Chatbot(
                    value=[{
                        'role': 'assistant',
                        'content': greeting
                    }],
                    height=400,
                    type='messages',
                )
            
            scenario_selector.change(
                fn=lambda x: (get_scenario_intro(x), start_new_scenario_chatbot(x)),
                inputs=scenario_selector,
                outputs=[scenario_home, scenario_chatbot]
            )

            gr.ChatInterface(
                fn=handle_scenario,
                chatbot=scenario_chatbot,
                additional_inputs=scenario_selector,
                submit_btn='发送',
                type='messages'
            )
    
        with gr.Tab('对话'):
            gr.Markdown('## 英语对话练习')
            normal_chatbot = gr.Chatbot(
                placeholder='<strong>我是你的英语私教 Ming，</strong><br/><br/>请开始对话吧！',
                height=600,
                type='messages'
            )

            gr.ChatInterface(
                fn=handle_conversation,
                chatbot=normal_chatbot,
                submit_btn='发送',
                type='messages'
            )

    return lang_mentor_app


if __name__ == "__main__":
    # Launch the Gradio app
    lang_mentor_app = create_gradio_app()

    lang_mentor_app.launch(
        share=False,
        server_name='127.0.0.1',
        # share=True,
        # server_name='0.0.0.0',
        server_port=7860
    )
