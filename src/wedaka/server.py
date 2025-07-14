"""WeDaka MCP Server - Employee Clock-in System"""

import asyncio
import json
from typing import Any, Sequence
from datetime import datetime, date

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

from .api_client import WedakaApiClient
from .models import LoginResponse, TimeLogResponse, SearchTimelogResponse


# Global API client instance
api_client: WedakaApiClient = None


async def get_api_client() -> WedakaApiClient:
    """Get or create API client instance"""
    global api_client
    if api_client is None:
        api_client = WedakaApiClient()
    return api_client


server = Server("wedaka")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="wedaka_login",
            description="Employee login (uses environment variables for credentials)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="wedaka_clock_in",
            description="Clock in (上班打卡)",
            inputSchema={
                "type": "object",
                "properties": {
                    "note": {
                        "type": "string",
                        "description": "Additional notes (optional)"
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="wedaka_clock_out",
            description="Clock out (下班打卡)",
            inputSchema={
                "type": "object",
                "properties": {
                    "note": {
                        "type": "string", 
                        "description": "Additional notes (optional)"
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="wedaka_get_timelog",
            description="Get employee time log records for a specific month",
            inputSchema={
                "type": "object",
                "properties": {
                    "month": {
                        "type": "integer",
                        "description": "Month (1-12)",
                        "minimum": 1,
                        "maximum": 12
                    },
                    "year": {
                        "type": "integer",
                        "description": "Year (e.g., 2024)",
                        "minimum": 2020,
                        "maximum": 2030
                    }
                },
                "required": ["month", "year"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any]
) -> list[types.TextContent]:
    """Handle tool calls"""
    
    try:
        if name == "wedaka_login":
            client = await get_api_client()
            response = await client.login()
            
            if response.success:
                result = {
                    "success": True,
                    "message": response.message,
                    "empId": response.empId,
                    "empName": response.empName,
                    "token": response.token,
                    "phoneUuid": response.phoneUuid
                }
            else:
                result = {
                    "success": False,
                    "message": response.message
                }
            
            return [types.TextContent(
                type="text",
                text=f"Login result: {json.dumps(result, ensure_ascii=False, indent=2)}"
            )]
        
        elif name == "wedaka_clock_in":
            note = arguments.get("note")
            
            client = await get_api_client()
            response = await client.insert_time_log(
                log_type="上班",
                note=note
            )
            
            result = {
                "success": response.success,
                "message": response.message,
                "logId": response.logId,
                "logTime": response.logTime
            }
            
            return [types.TextContent(
                type="text", 
                text=f"Clock in result: {json.dumps(result, ensure_ascii=False, indent=2)}"
            )]
        
        elif name == "wedaka_clock_out":
            note = arguments.get("note")
            
            client = await get_api_client()
            response = await client.insert_time_log(
                log_type="下班",
                note=note
            )
            
            result = {
                "success": response.success,
                "message": response.message,
                "logId": response.logId,
                "logTime": response.logTime
            }
            
            return [types.TextContent(
                type="text",
                text=f"Clock out result: {json.dumps(result, ensure_ascii=False, indent=2)}"
            )]
        
        elif name == "wedaka_get_timelog":
            month = arguments["month"]
            year = arguments["year"]
            
            client = await get_api_client()
            response = await client.search_timelog(month, year)
            
            if response.success:
                result = {
                    "success": True,
                    "message": response.message,
                    "totalRecords": len(response.data) if response.data else 0,
                    "records": [record.dict() for record in response.data] if response.data else []
                }
            else:
                result = {
                    "success": False,
                    "message": response.message
                }
            
            return [types.TextContent(
                type="text",
                text=f"Time log query result: {json.dumps(result, ensure_ascii=False, indent=2)}"
            )]
        
        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error executing tool {name}: {str(e)}"
        )]


async def async_main():
    """Async main entry point for the server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="wedaka",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def main():
    """Entry point for the CLI script"""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()