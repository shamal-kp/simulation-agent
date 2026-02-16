"""Patch for https://github.com/azure/azure-sdk-for-python/issues/44884

Fixes OpenTelemetry context detach failure during streaming responses.
Remove this patch once azure-ai-agentserver-core ships the fix.
"""
import importlib
import inspect
import re

mod = importlib.import_module("azure.ai.agentserver.core.server.base")
src_file = inspect.getfile(mod)

with open(src_file, "r") as f:
    src = f.read()

# Replace: token = otel_context.attach(ctx)
# With:    prev_ctx = otel_context.get_current()
#          otel_context.attach(ctx)
src = src.replace(
    "token = otel_context.attach(ctx)",
    "prev_ctx = otel_context.get_current()\n                    otel_context.attach(ctx)",
)

# Replace: otel_context.detach(token)
# With:    otel_context.attach(prev_ctx)
src = src.replace(
    "otel_context.detach(token)",
    "otel_context.attach(prev_ctx)",
)

with open(src_file, "w") as f:
    f.write(src)

print(f"Patched {src_file}")
