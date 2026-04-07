from typing import Any

from mcp_server.tools.users.base import BaseUserServiceTool


class SearchUsersTool(BaseUserServiceTool):

    @property
    def name(self) -> str:
        return "search_users"

    @property
    def description(self) -> str:
        return "Searches for users in the User Management Service by name, surname, email, or gender."

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Filter by user's first name."},
                "surname": {"type": "string", "description": "Filter by user's surname."},
                "email": {"type": "string", "description": "Filter by user's email address."},
                "gender": {"type": "string", "description": "Filter by user's gender."},
                "limit": {"type": "integer", "description": "Max number of results to return (default 20)."}
            },
            "required": []
        }

    async def execute(self, arguments: dict[str, Any]) -> str:
        return await self._user_client.search_users(**arguments)
