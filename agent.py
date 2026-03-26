from __future__ import annotations

from textwrap import dedent
from typing import Annotated

from agent_framework import Agent, chat_middleware, tool
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity import DefaultAzureCredential
from pydantic import Field

@chat_middleware
async def simple_chat_middleware(context, next):
    print(f"Processing {len(context.messages)} chat messages")

    await next()
    print("Chat processing completed")
    print(f"Full message history: {context.kwargs}")

@tool(
    name="get_weather",
    description="Share a quick weather update for a location. Use this to render the frontend weather card.",
)
def get_weather(
    location: Annotated[str, Field(description="The city or region to describe. Use fully spelled out names.")],
) -> str:
    """Return a short natural language weather summary."""
    normalized = location.strip().title() or "the requested location"
    return (
        f"The weather in {normalized} is mild with a light breeze. "
        "Skies are mostly clear—perfect for planning something fun."
    )

INSTRUCTIONS = dedent(
            """
            You play the role of a simulating a persona. Read the state to know information about yourself. When asked questions, respond as that persona.
            """.strip()
        )

def base_agent() -> Agent:
    return Agent(
        name="persona_agent",
        description="Persona simulator",
        instructions=INSTRUCTIONS,
        
        tools=[],
        middleware=[],
        
        client=AzureAIAgentClient(
            credential=DefaultAzureCredential(),
        ),
        store=True
    )