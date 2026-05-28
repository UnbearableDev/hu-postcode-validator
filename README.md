# Hungarian Postcode & Address Validator

> MCP server that validates Hungarian postcodes and addresses. Powered by the official Magyar Posta catalog and KSH (Hungarian Central Statistics Office) settlement data. **Pennies per call.**

**Built by [Unbearable Labs](https://github.com/UnbearableDev).** Pay-per-event pricing — only billed when a tool is actually called.

---

## Available on

- [Apify Actor Store](https://apify.com/unbearable_dev/hu-postcode-validator) — primary, metered usage (PPE)
- MCPize — *pending submission*
- MCP.so — *pending submission*
- PulseMCP — *pending submission*
- Smithery — *pending submission*
- Glama — *pending submission*

**Newsletter:** [Unbearable TechTips Weekly](https://unbearabletechtips.com) · **All Actors:** [github.com/UnbearableDev](https://github.com/UnbearableDev)

## What it does

Point any MCP-capable client (Claude Desktop, Cursor, n8n, Make, Zapier, custom agents) at this server and get fast, structured answers to Hungarian address questions:

- **Validate** a `(postcode, city)` pair before storing it in your DB
- **Look up** the settlement and county for any HU postcode
- **Find** all postcodes that serve a given city (handy for Budapest: 23 districts, 100+ postcodes)
- **List** every postcode in a Hungarian county
- **Map** Budapest district numbers (1–23 or I–XXIII) to their postcode ranges

## Tools

| Tool | Purpose | Price |
|------|---------|-------|
| `lookup_postcode(postcode)` | Settlement + county + (if BP) district for a 4-digit HU postcode | $0.001 |
| `lookup_city(city)` | All postcodes for a city (diacritic-insensitive — `gyor` matches `Győr`) | $0.001 |
| `validate_address(postcode, city)` | yes/no + corrected suggestion if mismatch | $0.001 |
| `budapest_district_lookup(district)` | Budapest I-XXIII (or 1-23) → list of postcodes in that district | $0.001 |
| `list_postcodes_in_county(county_name)` | Bulk listing — every postcode in a county | $0.005 |

## Example responses

**`lookup_postcode(1102)`**
```json
{
  "postcode": 1102,
  "found": true,
  "matches": [
    {
      "postcode": 1102,
      "settlement": "Budapest",
      "settlement_part": "X. kerület",
      "county": "Budapest"
    }
  ],
  "budapest_district": "X."
}
```

**`validate_address(1102, "Szeged")`**
```json
{
  "valid": false,
  "reason": "city_mismatch",
  "postcode": 1102,
  "city": "Szeged",
  "expected_settlements": ["Budapest"]
}
```

**`budapest_district_lookup(14)` (or `"XIV"`)** returns all postcodes in District XIV.

## Pricing

| Event | USD per call |
|-------|--------------|
| `lookup-call` (most tools) | $0.001 |
| `bulk-call` (`list_postcodes_in_county`) | $0.005 |

Effectively a free utility for occasional use; meaningful at high call volumes.

## Data sources

- **Magyar Posta official postal catalog** (`Iranyitoszam-Internet_uj.xlsx`) — postcode → settlement mapping
- **KSH (Hungarian Central Statistical Office) settlement registry** — county / district / KSH code per settlement, via the open [`tamas-ferenci/IrszHnk`](https://github.com/tamas-ferenci/IrszHnk) compilation

Coverage: 3,484 postcode-settlement entries spanning 2,962 unique postcodes (1011–9985), all 19 Hungarian counties + Budapest. Refreshed quarterly.

## Connecting from Claude Desktop

```json
{
  "mcpServers": {
    "hu-postcode": {
      "transport": "streamable-http",
      "url": "https://YOUR-ACTOR-URL.apify.actor/mcp"
    }
  }
}
```

## What's NOT covered

- Street-level address validation (no clean public data source post-2022 KEKKH restrictions)
- Fuzzy / Levenshtein city-name matching (v1.1)
- Non-Hungarian addresses (consider another MCP for those)

## Source / contact

Issues and ideas: `unbearabledev@gmail.com` or the GitHub org [`UnbearableDev`](https://github.com/UnbearableDev).
