import os
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

load_dotenv(override=True)

# Optional OpenTelemetry tracing (console exporter). Fall back to no-op tracer if not installed.
try:
    from opentelemetry import trace
    from opentelemetry.sdk.resources import SERVICE_NAME, Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

    resource = Resource.create({SERVICE_NAME: "SeattleHotelAgent"})
    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer(__name__)
    logger.debug("OpenTelemetry tracing enabled (ConsoleSpanExporter)")
except Exception:
    class _NoopSpanCtx:
        def __enter__(self):
            return None

        def __exit__(self, exc_type, exc, tb):
            return False

    class _NoopTracer:
        def start_as_current_span(self, name, **kwargs):
            return _NoopSpanCtx()

    tracer = _NoopTracer()
    logger.debug("OpenTelemetry not available; using no-op tracer")

from agent_framework import ai_function, ChatAgent
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.ai.agentserver.agentframework import from_agent_framework
from azure.identity import DefaultAzureCredential

# Configure these for your Azure OpenAI resource
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")  # e.g., "https://<resource>.openai.azure.com"
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-5.2-chat")


@ai_function
def get_local_date_time(iana_timezone: str) -> str:
    """
    Get the current date and time for a given timezone.
    """
    with tracer.start_as_current_span("get_local_date_time"):
        try:
            tz = ZoneInfo(iana_timezone)
            current_time = datetime.now(tz)
            result = f"The current date and time in {iana_timezone} is {current_time.strftime('%A, %B %d, %Y at %I:%M %p %Z')}"
            logger.info("get_local_date_time returning result")
            return result
        except Exception as e:
            logger.exception("Error in get_local_date_time")
            return f"Error: Unable to get time for timezone '{iana_timezone}'. {str(e)}"


# Create the agent with a local Python tool
agent = ChatAgent(
    chat_client=AzureOpenAIResponsesClient(
        endpoint=AZURE_OPENAI_ENDPOINT,
        deployment_name=MODEL_DEPLOYMENT_NAME,
        credential=DefaultAzureCredential(),
    ),
    instructions=(
        "You are a helpful assistant that can tell users the current date and time in any location. "
        "When a user asks about the time in a city or location, use the get_local_date_time tool with the appropriate IANA timezone string for that location."
    ),
    tools=[get_local_date_time],
)


if __name__ == "__main__":
    try:
        logger.info("Starting Seattle Time Agent server...")
        with tracer.start_as_current_span("agent_server_start"):
            agent_server = from_agent_framework(agent)
            try:
                from agentdev.localdebug import configure_agent_server
                configure_agent_server(agent_server)
                logger.info("Agent inspector endpoints enabled (/agentdev/*)")
            except ImportError:
                logger.debug("agentdev not installed; inspector endpoints disabled")
            agent_server.run()
    except Exception:
        logger.exception("Fatal error running agent server")
        raise
