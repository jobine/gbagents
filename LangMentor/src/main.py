import gradio as gr
from agents.conversation_agent import ConversationAgent
from agents.hotel_checkin_agent import HotelCheckInAgent
from utils.logger import LOG

conversation_agent = ConversationAgent()
hotel_checkin_agent = HotelCheckInAgent()

def handle_conversation(user_input, history):
    LOG.debug(f'[Chat history]: {history}')

    bot_message = conversation_agent.chat_with_history(user_input)

    LOG.info(f'[Bot message]: {bot_message}')

    return bot_message

def handle_scenario(user_input, history, scenario):
    agents = {
        '酒店入住': hotel_checkin_agent,
    }

    return agents[scenario].respond(user_input)


if __name__ == "__main__":
    # Build the Gradio app
    with gr.Blocks(title='Language Mentor') as lang_mentor_app:
        with gr.Tab('对话'):
            gr.Markdown('## 英语对话练习')
            normal_chatbot = gr.Chatbot(
                placeholder='<strong>我是你的英语私教 Ming，</strong><br/><br/>请开始对话吧！',
                height=800,
                type='messages'
            )

            gr.ChatInterface(
                fn=handle_conversation,
                chatbot=normal_chatbot,
                submit_btn='发送',
                type='messages'
            )

        with gr.Tab('场景对话'):
            gr.Markdown('## 场景对话练习')
            scenario_chatbot = gr.Chatbot(
                placeholder='<strong>请选择一个场景开始对话</strong>',
                height=800,
                type='messages'
            )

            scenario_selector = gr.Dropdown(
                choices=['酒店入住'],
                label='选择场景',
                value='酒店入住'
            )

            gr.ChatInterface(
                fn=handle_scenario,
                chatbot=scenario_chatbot,
                # inputs=[gr.Textbox(label='输入内容'), scenario_selector],
                additional_inputs=scenario_selector,
                submit_btn='发送',
                type='messages'
            )

    # Launch the Gradio app
    lang_mentor_app.launch(
        share=False,
        server_name='127.0.0.1',
        # share=True,
        # server_name='0.0.0.0',
        server_port=7860
    )

