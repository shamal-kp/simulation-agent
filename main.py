import os
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv(override=True)

from agent_framework import ai_function, ChatAgent
from agent_framework.azure import AzureAIAgentClient
from azure.ai.agentserver.agentframework import from_agent_framework
from azure.identity import DefaultAzureCredential

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-5.2-chat")
PROJECT_ENDPOINT = os.getenv(
    "PROJECT_ENDPOINT"
)

@ai_function
def get_local_date_time(iana_timezone: str) -> str:
    """Get the current date and time for a given timezone."""
    try:
        tz = ZoneInfo(iana_timezone)
        current_time = datetime.now(tz)
        return f"The current date and time in {iana_timezone} is {current_time.strftime('%A, %B %d, %Y at %I:%M %p %Z')}"
    except Exception as e:
        return f"Error: Unable to get time for timezone '{iana_timezone}'. {e}"


agent = ChatAgent(
    chat_client=AzureAIAgentClient(
        credential=DefaultAzureCredential(),
    ),
    instructions=(
        "You are a helpful assistant that can tell users the current date and time in any location. "
        "When a user asks about the time in a city or location, use the get_local_date_time tool with the appropriate IANA timezone string for that location. "
        "Always include the tool result in your response so the user sees what the tool returned."
    ),
    tools=[get_local_date_time],
    store=True
)

if __name__ == "__main__":
    from_agent_framework(agent).run()
