import uvicorn
import requests
from python_a2a.mcp import FastMCP, text_response, create_fastapi_app
from datetime import datetime


OPENWEATHER_API_KEY = '02b0e704df560205c74d6d1065c7303d'

# 1. Create FastMCP instance
utility_mcp = FastMCP(
    name='My tools',
    description='A set of useful tools for various tasks.',
    version='1.0.0',
)

# 2. Define tool function calculator and register it with the MCP instance
@utility_mcp.tool(
    name='calculator',
    description='Performs basic arithmetic operations. e.g., "5 * 3 + 2"',
)
def calculator(input: str) -> str:
    try:
        result = eval(
            input, 
            {'__builtins__': None}, 
            {'abs': abs, 
             'max': max,
             'min': min,
             'pow': pow,
             'sum': sum,
             'round': round})
        
        return text_response(f'Calculation result: {input} = {result}')
    except Exception as e:
        return text_response(f'Error in calculation: {str(e)}')
    
# 3. Define tool function fetch current datetime and register it with the MCP instance
@utility_mcp.tool(
    name='fetch_current_datetime',
    description='Fetches the current date and time.',
)
def fetch_current_datetime() -> str:
    now = datetime.now()
    return text_response(
        f'Current date: {now.strftime("%Y-%m-%d")}\\n'
        f'Current time: {now.strftime("%H:%M:%S")}\\n'
        f'weekday: {now.strftime("%A")}'
    )

# 4. Define tool function fetch current weather for a given city information and register it with the MCP instance
@utility_mcp.tool(
    name='fetch_current_weather',
    description='Fetches the current weather for a given city. e.g., "London"',
)
def fetch_current_weather(city: str) -> str:
    try:
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric'
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            return text_response(f'Error fetching {city} weather data: {data.get("message", "Unknown error")}')

        weather_desc = data['weather'][0]['description']
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        feels_like = data['main']['feels_like']
        
        return text_response(
            f'Current weather in {city}:\\n'
            f'Description: {weather_desc}\\n'
            f'Temperature: {temp}°C\\n'
            f'Humidity: {humidity}%\\n'
            f'Wind Speed: {wind_speed} m/s'
            f'Feels Like: {feels_like}°C'
        )
    except Exception as e:
        return text_response(f'Error fetching weather data: {str(e)}')
    


# 5. Create FastAPI app from the MCP instance
if __name__ == '__main__':
    port = 7001
    print(f'Starting My tools MCP server at http://localhost:{port}')

    app = create_fastapi_app(utility_mcp)
    
    # 6. Run the FastAPI app with Uvicorn
    uvicorn.run(app, host='0.0.0.0', port=port)
                