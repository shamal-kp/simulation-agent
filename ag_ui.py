import uvicorn
from fastapi import FastAPI
from agent_framework import Agent, chat_middleware, tool

from dotenv import load_dotenv

from agent import base_agent
from agent_framework_ag_ui import add_agent_framework_fastapi_endpoint

load_dotenv(override=True)

app = FastAPI()

agent = base_agent()


STATE_SCHEMA: dict[str, object] = {
    "proverbs": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Ordered list of the user's saved proverbs.",
    }
}

PREDICT_STATE_CONFIG: dict[str, dict[str, str]] = {
    "proverbs": {
        "tool": "update_proverbs",
        "tool_argument": "proverbs",
    }
}

add_agent_framework_fastapi_endpoint(
    app=app,
    agent=agent,
    path="/runtime",
    
    state_schema=STATE_SCHEMA,
    predict_state_config=PREDICT_STATE_CONFIG,
)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8088)
