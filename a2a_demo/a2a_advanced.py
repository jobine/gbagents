import requests
import json
from python_a2a import A2AServer, run_server, TaskStatus, TaskState, AgentCard, AgentSkill
from openai import OpenAI

MCP_SERVER_URL = 'http://localhost:7001'
MODEL_NAME = 'gpt-5-mini'

openai_client = OpenAI()

class OpenAIEnhancedAgent(A2AServer):
    def __init__(self, agent_card=None, mcp_server_url=MCP_SERVER_URL):
        super().__init__(agent_card=agent_card)
        self.mcp_server_url = mcp_server_url
        print(f'🛠️ OpenAIEnhancedAgent initialized with MCP server URL: {self.mcp_server_url}')

    def _call_mcp_tool(self, tool_name, tool_params):
        '''
        An auxiliary function to call a tool from the MCP server.
        '''
        if not self.mcp_server_url:
            return 'MCP server URL is not set.'

        try:
            print(f'📞 Calling MCP tool: {tool_name} with params: {tool_params}')
            response = requests.post(f'{self.mcp_server_url}/tools/{tool_name}', json=tool_params)
            response.raise_for_status()
            tool_response = response.json()
            print(f'✅ Received response from MCP tool {tool_name}: {tool_response}')

            if tool_response.get('content'):
                parts = tool_response['content']
                if isinstance(parts, list) and len(parts) > 0 and 'text' in parts[0]:
                    return parts[0]['text']
                
                return 'Tool succeeded but no text content found.'
        except requests.RequestException as e:
            error_msg = f'Error calling MCP tool {tool_name}: {e}'
            print(f'❌ {error_msg}')
            return error_msg
        except Exception as e_json:
            error_msg = f'Error parsing JSON response from MCP tool {tool_name}: {e_json}'
            print(f'❌ {error_msg}')
            return error_msg
        
    def _get_openai_response(self, prompt, tools=None, max_retries=3):
        '''
        Call OpenAI API with retries.
        '''
        for attempt in range(max_retries):
            try:
                response = openai_client.responses.create(
                    model=MODEL_NAME,
                    input=[
                        {
                            'role': 'user',
                            'content': [
                                {'type': 'input_text', 'text': prompt},
                            ]
                        }
                    ],
                    tools=tools or [],
                    tool_choice='auto' if tools else None,
                )

                # print(f' OpenAI API model dump: {response.model_dump_json()} ')

                message_text = ''
                tool_calls = []

                for item in getattr(response, 'output', []):
                    item_type = getattr(item, 'type', None)

                    if item_type == 'message':
                        for part in getattr(item, 'content', []):
                            if getattr(part, 'type', None) == 'output_text':
                                message_text += getattr(part, 'text', '\\n')
                        continue

                    if item_type == 'function_call':
                        tool_calls.append({
                            'name': getattr(item, 'name', None),
                            'arguments': json.loads(getattr(item, 'arguments', None)),
                            'call_id': getattr(item, 'call_id', None),
                        })
                        continue

                return {
                    'message': message_text,
                    'tool_calls': tool_calls,
                    'usage': response.usage,
                }
            except Exception as e:
                print(f'❌ OpenAI API call failed on attempt {attempt + 1}/{max_retries}: {e}')
        return None
        
    def handle_task(self, task):
        '''
        Handle a task by checking for tool invocation patterns and calling the appropriate MCP tool.
        '''
        task_message = task.message or {}
        content = task_message.get('content', {})
        text = content.get('text', '')

        print(f'📝 Task content: {text}')

        # Define tools metadata for OpenAI
        tools = [
            {
                'type': 'function',
                'name': 'calculator',
                'description': 'Performs basic arithmetic operations. e.g., "5 * 3 + 2"',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'input': {
                            'type': 'string',
                            'description': 'The arithmetic expression to calculate.',
                        },
                    },
                    'required': ['input'],
                    'additionalProperties': False,
                },
                'strict': True
            },
            {
                'type': 'function',
                'name': 'fetch_current_weather',
                'description': 'Fetches the current weather for a given city. e.g., "London"',
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'city': {
                            'type': 'string',
                            'description': 'The city to fetch the weather for.',
                        },
                    },
                    'required': ['city'],
                    'additionalProperties': False,
                },
                'strict': True
            },
            {
                'type': 'function',
                'name': 'fetch_current_datetime',
                'description': 'Fetches the current date and time.',
                'parameters': {
                    'type': 'object',
                    'properties': {},
                    'required': [],
                    'additionalProperties': False,
                },
                'strict': True
            },
        ]

        # Let OpenAI choose the tool and call it
        try:
            response = self._get_openai_response(prompt=text, tools=tools)
            if response is None:
                task.status = TaskStatus(state=TaskState.FAILED, message='Failed to get response from OpenAI.')
                return task
            
            message_text = response.get('message', '')
            tool_calls = response.get('tool_calls', [])

            print(f'🤖 OpenAI output text: {message_text}')
            print(f'🔧 OpenAI tool calls: {tool_calls}')

            # If OpenAI decided to call a tool, handle it
            if tool_calls:
                for tool_call in tool_calls:
                    tool_name = tool_call.get('name')
                    tool_args = tool_call.get('arguments', {})

                    if tool_name and hasattr(self, '_call_mcp_tool'):
                        tool_response = self._call_mcp_tool(tool_name, tool_args)
                        message_text += f'\n\n[Tool {tool_name} with arguments {tool_args} response]: {tool_response}'

                # Provide a final prompt to OpenAI to summarize the tool results
                prompt = f'{text}\n\n{message_text}\n\nProvide a final concise answer based on the above information.'
                final_response = self._get_openai_response(prompt=prompt)
                print(f'🔄 Final OpenAI response after tool calls: {final_response}')
                if final_response:
                    message_text = final_response.get('message', message_text)
        except Exception as e:
            message_text = f'Error processing task: {str(e)}'
            print(f'❌ OpenAI API call failed: {message_text}')

        # Finalize the task
        task.artifacts = [{
            'parts': [{
                'type': 'text',
                'text': message_text or 'No response generated.'
            }]
        }]
        task.status = TaskStatus(state=TaskState.COMPLETED)
        print(f'✅ Task completed: {task}')
        return task

if __name__ == '__main__':
    port = 7000
    agent_card = AgentCard(
        name='OpenAI Enhanced Agent',
        description=f'An agent that uses OpenAI {MODEL_NAME} with tool integration for calculations, weather, and datetime.',
        url=f'http://localhost:{port}',
        version='1.0.0',
        skills=[
            AgentSkill(
                name='Calculator', 
                description='Performs calculations.',
                examples=['Calculate 5 * 3 + 2', 'What is the sum of 10 and 20?']
            ),
            AgentSkill(
                name='FetchCurrentDatetime', 
                description='Fetches the current date and time.',
                examples=['What is the current date and time?', 'Tell me the current time.']
            ),
            AgentSkill(
                name='FetchCurrentWeather',
                description='Fetches the current weather for a given city.',
                examples=['What is the weather like in New York?', 'Tell me the weather in San Francisco.']
            )
        ]
    )

    agent = OpenAIEnhancedAgent(agent_card=agent_card, mcp_server_url=MCP_SERVER_URL)
    print(f'🚀 Starting OpenAI Enhanced Agent server on http://localhost:{port}')
    run_server(agent, host='0.0.0.0', port=port)
