import asyncio
from typing import Callable, Any
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from core.websocket_manager import ws_manager

def track_agent(agent: ChatAgent, agent_name: str, loop: asyncio.AbstractEventLoop):
    """
    Monkey-patches the agent's Step function with an explicit loop for thread-safe 
    broadcasting back to the FastAPI main thread.
    """
    original_step = agent.step

    def tracked_step(input_message: BaseMessage) -> Any:
        # Wrap in async loop safely for broadcasting before step
        asyncio.run_coroutine_threadsafe(
            ws_manager.broadcast_json("communications_stream", {
                "speaker": "System",
                "text": f"{agent_name} received new internal prompt."
            }),
            loop
        )
        
        # Fire native CAMEL execution
        response = original_step(input_message)
        
        # Intercept output
        asyncio.run_coroutine_threadsafe(
            ws_manager.broadcast_json("thought_stream", {
                "agent": agent_name,
                "message": response.msg.content,
                "tool_calls": str(response.msg.tool_calls) if response.msg.tool_calls else None
            }),
            loop
        )
        return response

    # Override object method instance
    agent.step = tracked_step
    return agent
