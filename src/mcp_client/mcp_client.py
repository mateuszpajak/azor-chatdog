import asyncio
import atexit
import json
import logging
import os
import threading
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import TextContent

logger = logging.getLogger(__name__)

class McpClient:

    _instance: "McpClient | None" = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        enabled = os.getenv("MCP_ENABLED", "false").lower() == "true"
        jar_path = os.getenv("MCP_SERVER_JAR_PATH", "")

        self._jar_path = jar_path
        self._enabled = enabled and bool(jar_path)
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._exit_stack: AsyncExitStack | None = None
        self._session: ClientSession | None = None

        if self._enabled:
            self._start()
            atexit.register(self.stop)

    @property
    def enabled(self) -> bool:
        return self._enabled

    def _start(self):
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._thread.start()
        self._run(self._connect(), timeout=30)

    async def _connect(self):
        self._exit_stack = AsyncExitStack()
        server_params = StdioServerParameters(
            command="java",
            args=["-jar", self._jar_path],
        )
        transport = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        read_stream, write_stream = transport
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )
        await self._session.initialize()
        logger.info("MCP session initialized via SDK")

    def list_tools(self) -> list[dict]:
        result = self._run(self._session.list_tools())
        return [
            {
                "name": tool.name,
                "description": tool.description or "",
                "inputSchema": tool.inputSchema,
            }
            for tool in result.tools
        ]

    def call_tool(self, name: str, arguments: dict | None = None) -> str:
        result = self._run(self._session.call_tool(name, arguments or {}))
        texts = [part.text for part in result.content if isinstance(part, TextContent)]
        return "\n".join(texts) if texts else json.dumps(result.model_dump())

    def stop(self):
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
            if self._thread:
                self._thread.join(timeout=5)
            self._loop.close()
            self._loop = None
            self._thread = None
        self._exit_stack = None
        self._session = None

    def _run(self, coro, timeout=30):
        if not self._loop:
            raise RuntimeError("MCP event loop not running")
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=timeout)
