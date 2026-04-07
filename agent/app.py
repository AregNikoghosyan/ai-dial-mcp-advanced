import asyncio
import os

from agent.clients.custom_mcp_client import CustomMCPClient
from agent.clients.mcp_client import MCPClient
from agent.clients.dial_client import DialClient
from agent.models.message import Message, Role


async def main():
    dial_api_key = os.environ.get("DIAL_API_KEY", "")

    all_tools: list[dict] = []
    tool_name_client_map: dict[str, MCPClient | CustomMCPClient] = {}

    # UMS MCP server (our custom server) — CustomMCPClient
    try:
        ums_client = await CustomMCPClient.create("http://localhost:8006/mcp")
        ums_tools = await ums_client.get_tools()
        all_tools.extend(ums_tools)
        for tool in ums_tools:
            tool_name_client_map[tool["function"]["name"]] = ums_client
        print(f"UMS: {len(ums_tools)} tools loaded.")
    except Exception as e:
        print(f"Warning: Could not connect to UMS MCP server: {e}")

    # Remote fetch MCP server — CustomMCPClient
    try:
        fetch_client = await CustomMCPClient.create("https://remote.mcpservers.org/fetch/mcp")
        fetch_tools = await fetch_client.get_tools()
        all_tools.extend(fetch_tools)
        for tool in fetch_tools:
            tool_name_client_map[tool["function"]["name"]] = fetch_client
        print(f"Fetch server: {len(fetch_tools)} tools loaded.")
    except Exception as e:
        print(f"Warning: Could not connect to fetch MCP server: {e}")

    if not all_tools:
        print("No tools available. Check that the MCP server is running.")
        return

    dial_client = DialClient(
        api_key=dial_api_key,
        endpoint="https://ai-proxy.lab.epam.com",
        tools=all_tools,
        tool_name_client_map=tool_name_client_map
    )

    messages: list[Message] = [
        Message(
            role=Role.SYSTEM,
            content=(
                "You are a helpful assistant. Help the user with their requests. "
                "You have access to a User Management Service with tools to search, create, update, and delete users. "
                "You also have web fetch tools. Use them as needed to fulfill user requests."
            )
        )
    ]

    clients = [c for c in tool_name_client_map.values() if isinstance(c, CustomMCPClient)]
    unique_clients = list({id(c): c for c in clients}.values())

    print("\nChat started. Type 'exit' to quit.\n")
    try:
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in ("exit", "quit"):
                break
            if not user_input:
                continue

            messages.append(Message(role=Role.USER, content=user_input))
            ai_message = await dial_client.get_completion(messages)
            messages.append(ai_message)
            print()
    finally:
        for client in unique_clients:
            await client.close()


if __name__ == "__main__":
    asyncio.run(main())


# Check if Arkadiy Dobkin present as a user, if not then search info about him in the web and add him
