"""Real MCP-over-HTTP smoke test against a running Actor."""
import asyncio
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main(endpoint: str):
    print(f"Connecting to {endpoint}...")
    async with streamablehttp_client(endpoint) as (read, write, _):
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            print(f"Initialized. Server: {init.serverInfo.name} v{init.serverInfo.version}")
            print(f"Protocol: {init.protocolVersion}")
            print()

            tools = await session.list_tools()
            print(f"--- tools/list ---")
            print(f"{len(tools.tools)} tools advertised:")
            for t in tools.tools:
                print(f"  - {t.name}")
            print()

            # Call audit_compose with the bad fixture
            yaml_text = Path('tests/fixtures/bad-compose.yml').read_text()
            print(f"--- tools/call audit_compose ---")
            print(f"Sending {len(yaml_text)} bytes of compose YAML...")
            result = await session.call_tool(
                'audit_compose',
                {'compose_yaml': yaml_text},
            )
            if result.isError:
                print(f"ERROR: {result.content}")
                return 1

            sc = result.structuredContent or {}
            summary = sc.get('summary', {})
            print(f"text:      {result.content[0].text if result.content else '(no content)'}")
            print(f"total:     {summary.get('total_findings')}")
            print(f"severity:  {summary.get('by_severity')}")
            print(f"category:  {summary.get('by_category')}")
            print(f"services:  {summary.get('services_with_findings')}")
            print()

            # Also test list_checks
            print(f"--- tools/call list_checks ---")
            result2 = await session.call_tool('list_checks', {})
            sc2 = result2.structuredContent or {}
            print(f"text:      {result2.content[0].text if result2.content else '(no content)'}")
            print(f"categories: {len(sc2.get('categories', []))}")
            print(f"checks:     {len(sc2.get('checks', []))}")
            return 0


if __name__ == '__main__':
    endpoint = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:3000/mcp'
    sys.exit(asyncio.run(main(endpoint)))
