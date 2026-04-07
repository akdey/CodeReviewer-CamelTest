import asyncio
from typing import Any, Optional, Union, Type
from pydantic import BaseModel
from camel.agents import ChatAgent
from camel.messages import BaseMessage
from camel.responses import ChatAgentResponse
from core.websocket_manager import ws_manager

class ObservedChatAgent(ChatAgent):
    """
    A ChatAgent subclass that intercepts the step() method to broadcast 
    agent thoughts and tool calls to a WebSocket in a thread-safe manner.
    """
    
    def __init__(self, *args, agent_name: str, loop: asyncio.AbstractEventLoop, **kwargs):
        super().__init__(*args, **kwargs)
        self._agent_name = agent_name
        self._loop = loop

    def step(
        self, 
        input_message: Union[BaseMessage, str], 
        response_format: Optional[Type[BaseModel]] = None
    ) -> ChatAgentResponse:
        """
        Overrides the native step() to add real-time broadcasting.
        """
        # 1. Inform the frontend that the agent has received a prompt/instruction
        asyncio.run_coroutine_threadsafe(
            ws_manager.broadcast_json("communications_stream", {
                "speaker": "System",
                "text": f"{self._agent_name} logic sequence initiated."
            }),
            self._loop
        )

        # 2. Call the original CAMEL step execution
        # Note: We call super().step() to ensure all internal CAMEL logic (memory, tools, etc.) is preserved.
        response = super().step(input_message, response_format)

        # 3. Intercept the output and broadcast it
        # Extract content and tool calls for the thought stream
        content = getattr(response.msg, "content", str(response.msg))
        tool_calls = getattr(response.msg, "tool_calls", None)
        
        asyncio.run_coroutine_threadsafe(
            ws_manager.broadcast_json("thought_stream", {
                "agent": self._agent_name,
                "message": content,
                "tool_calls": str(tool_calls) if tool_calls else None
            }),
            self._loop
        )

        return response
