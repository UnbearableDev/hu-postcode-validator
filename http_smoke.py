"""HTTP-MCP smoke for hu-postcode-validator running locally on port 3000."""
import asyncio
import sys
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main():
    endpoint = "http://localhost:3000/mcp"
    print(f"Connecting to {endpoint}...")
    async with streamablehttp_client(endpoint) as (read, write, _):
        async with ClientSession(read, write) as session:
            init = await session.initialize()
            print(f"Server: {init.serverInfo.name} v{init.serverInfo.version}")
            print(f"Protocol: {init.protocolVersion}")

            tools = await session.list_tools()
            print(f"\nTools registered: {len(tools.tools)}")
            for t in tools.tools:
                print(f"  - {t.name}")

            print("\n--- calling lookup_postcode(1102) ---")
            r = await session.call_tool("lookup_postcode", {"postcode": 1102})
            sc = r.structuredContent or {}
            print(f"  text:    {r.content[0].text if r.content else '(none)'}")
            print(f"  postcode: {sc.get('postcode')}, found: {sc.get('found')}")
            print(f"  bp_district: {sc.get('budapest_district')}")
            if sc.get('matches'):
                m = sc['matches'][0]
                print(f"  first match: {m.get('settlement')}, {m.get('settlement_part')}, county={m.get('county')}")

            print("\n--- calling budapest_district_lookup(14) ---")
            r2 = await session.call_tool("budapest_district_lookup", {"district_number": 14})
            sc2 = r2.structuredContent or {}
            print(f"  text:    {r2.content[0].text if r2.content else '(none)'}")
            print(f"  district: {sc2.get('district')}, count: {sc2.get('postcode_count')}")
            print(f"  postcodes (first 5): {sc2.get('postcodes', [])[:5]}")

            print("\n--- calling validate_address(1102, 'Budapest') ---")
            r3 = await session.call_tool("validate_address", {"postcode": 1102, "city": "Budapest"})
            sc3 = r3.structuredContent or {}
            print(f"  valid: {sc3.get('valid')}, matched: {sc3.get('matched_settlement')}")

            print("\n--- calling list_postcodes_in_county('Csongrád-Csanád') ---")
            r4 = await session.call_tool("list_postcodes_in_county", {"county_name": "Csongrád-Csanád"})
            sc4 = r4.structuredContent or {}
            print(f"  text: {r4.content[0].text if r4.content else '(none)'}")
            print(f"  unique_postcode_count: {sc4.get('unique_postcode_count')}")

            print("\nAll HTTP MCP calls succeeded.")
            return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
