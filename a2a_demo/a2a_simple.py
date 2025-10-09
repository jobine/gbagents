from python_a2a import A2AServer, run_server, TaskStatus, TaskState, AgentCard, AgentSkill
import requests
import re

MCP_SERVER_URL = 'http://localhost:7001'

class MyToolsAgent(A2AServer):
    def __init__(self, agent_card=None, mcp_server_url=MCP_SERVER_URL, message_handler=None, google_a2a_compatible=False, **kwargs):
        super().__init__(agent_card=agent_card)
        self.mcp_server_url = mcp_server_url
        print(f'🛠️ MyToolsAgent initialized with MCP server URL: {self.mcp_server_url}')

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
        
    def handle_task(self, task):
        '''
        Handle a task by checking for tool invocation patterns and calling the appropriate MCP tool.
        '''
        print(f'🔍 Handling task: {task}')

        task_message = task.message or {}
        content = task_message.get('content', '')
        text = content.get('text', '').lower()

        print(f'📝 Task content: {text}')

        # Simple routing logic based on keywords
        if 'calculate' in text or any(op in text for op in ['+', '-', '*', '/']):
            # Extract the calculation expression
            match = re.search(r'calculate\s*(.*)', text)
            expression = match.group(1) if match else text
            response_text = self._call_mcp_tool('calculator', {'input': expression})
        elif 'weather' in text:
            # Extract the city from the text
            match = re.search(r'weather in\s+([a-zA-Z\s]+)', text)
            city = match.group(1).strip() if match else 'London' # Default to London if no city is found
            response_text = self._call_mcp_tool('fetch_current_weather', {'city': city})
        elif 'date' in text or 'time' in text:
            response_text = self._call_mcp_tool('fetch_current_datetime', {})
        else:
            response_text = "I'm not sure how to handle that. I can help with calculations, weather, and the current date/time."
        
        task.artifacts = [{
            'parts': [{
                'type': 'text',
                'text': str(response_text)
            }]
        }]
        task.status = TaskStatus(state=TaskState.COMPLETED)
        print(f'✅ Task completed: {task}')
        return task
    
if __name__ == '__main__':
    port = 7000

    agent_card = AgentCard(
        name='MyToolsAgent',
        description='An agent that uses tools from an MCP server to perform tasks.',
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

    my_tools_agent = MyToolsAgent(agent_card=agent_card, mcp_server_url=MCP_SERVER_URL)

    print(f'🚀 Starting MyToolsAgent server on http://localhost:{port}')
    run_server(my_tools_agent, host='0.0.0.0', port=port)
