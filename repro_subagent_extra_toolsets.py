"""Repro: create_deep_agent(subagent_extra_toolsets=...) works now.

The value is forwarded into the subagent's own create_deep_agent() call
via the agent_factory, which reads cfg.get("toolsets") and passes them
to create_deep_agent(extra_toolsets=...). The subagent now receives the
toolsets correctly.

Run: uv run python repro_subagent_extra_toolsets.py
"""

import asyncio

from pydantic_ai.messages import ModelResponse, TextPart, ToolCallPart
from pydantic_ai.models.function import AgentInfo, FunctionModel
from pydantic_ai.toolsets.function import FunctionToolset
from pydantic_ai_backends import StateBackend
from pydantic_deep import DeepAgentDeps, create_deep_agent

sentinel = FunctionToolset(id="sentinel-extra")

@sentinel.tool_plain
def sentinel_tool() -> str:
    return "extra toolset the subagent should have received"

subagent_tools: list[str] = []

def subagent_model(messages: list, info: AgentInfo) -> ModelResponse:
    subagent_tools[:] = [t.name for t in info.function_tools]
    return ModelResponse(parts=[TextPart("done")])

def main_model(messages: list, info: AgentInfo) -> ModelResponse:
    if not any(hasattr(p, "tool_name") and p.tool_name == "task" for m in messages for p in m.parts):
        args = {"description": "work", "subagent_type": "worker", "mode": "sync"}
        return ModelResponse(parts=[ToolCallPart(tool_name="task", args=args)])
    return ModelResponse(parts=[TextPart("done")])

async def main() -> None:
    agent = create_deep_agent(
        model=FunctionModel(main_model),
        subagents=[{
            "name": "worker",
            "description": "a worker",
            "instructions": "work",
            "model": FunctionModel(subagent_model),
        }],
        subagent_extra_toolsets=[sentinel],
        include_subagents=True,
        include_memory=False,
        # Disable stuck loop detection to avoid ModelRetry on identical task calls
        stuck_loop_detection=False,
    )
    await agent.run("delegate", deps=DeepAgentDeps(backend=StateBackend()))

    print("SUBAGENT TOOLS:")
    print("  sentinel_tool present:", "sentinel_tool" in subagent_tools)
    if "sentinel_tool" in subagent_tools:
        print("  SUCCESS: subagent_extra_toolsets now works!")
    else:
        print("  subagent_tools:", sorted(subagent_tools))

if __name__ == "__main__":
    asyncio.run(main())
