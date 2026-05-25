"""Smoke test for hu-postcode-validator.

Calls the tool functions directly (bypasses Apify Standby + MCP transport).
Run from project root: `.venv/bin/python tests/smoke.py`
"""

import asyncio
import sys
from pathlib import Path

# Make `postcode` package importable when run from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from postcode import tools


async def main():
    # Patch Actor.charge to no-op (we're not in Actor context)
    from unittest.mock import patch, AsyncMock

    print("=" * 70)
    print("HU-POSTCODE-VALIDATOR SMOKE TEST")
    print("=" * 70)

    cases = [
        ("lookup_postcode(1102)", lambda: tools.lookup_postcode(1102)),
        ("lookup_postcode('1102')", lambda: tools.lookup_postcode("1102")),
        ("lookup_postcode(2000) [Szentendre]", lambda: tools.lookup_postcode(2000)),
        ("lookup_postcode(6700) [Szeged]", lambda: tools.lookup_postcode(6700)),
        ("lookup_postcode(9999) [bad — out of range edge]", lambda: tools.lookup_postcode(9999)),
        ("lookup_postcode(5000) [valid range, may not exist]", lambda: tools.lookup_postcode(5000)),
        ("lookup_postcode('abc') [invalid]", lambda: tools.lookup_postcode("abc")),
        ("lookup_city('Szeged')", lambda: tools.lookup_city("Szeged")),
        ("lookup_city('szeged') [lowercase]", lambda: tools.lookup_city("szeged")),
        ("lookup_city('Gyor') [no diacritic]", lambda: tools.lookup_city("Gyor")),
        ("lookup_city('Győr') [diacritic]", lambda: tools.lookup_city("Győr")),
        ("lookup_city('Atlantis') [no match]", lambda: tools.lookup_city("Atlantis")),
        ("validate_address(1102, 'Budapest')", lambda: tools.validate_address(1102, "Budapest")),
        ("validate_address(1102, 'Szeged') [mismatch]", lambda: tools.validate_address(1102, "Szeged")),
        ("validate_address(9999, 'Anywhere') [bad pc]", lambda: tools.validate_address(9999, "Anywhere")),
        ("list_postcodes_in_county('Pest')", lambda: tools.list_postcodes_in_county("Pest")),
        ("list_postcodes_in_county('Csongrád-Csanád')", lambda: tools.list_postcodes_in_county("Csongrád-Csanád")),
        ("list_postcodes_in_county('Mordor') [invalid]", lambda: tools.list_postcodes_in_county("Mordor")),
        ("budapest_district_lookup(10)", lambda: tools.budapest_district_lookup(10)),
        ("budapest_district_lookup('X')", lambda: tools.budapest_district_lookup("X")),
        ("budapest_district_lookup('XXIII')", lambda: tools.budapest_district_lookup("XXIII")),
        ("budapest_district_lookup(99) [out of range]", lambda: tools.budapest_district_lookup(99)),
    ]

    passed = 0
    failed = 0
    for label, fn in cases:
        try:
            result = await fn()
            text = result["text"]
            sc = result["structuredContent"]
            print(f"\n[{label}]")
            print(f"  text: {text}")
            # Print a compact view of structuredContent
            if "matches" in sc and isinstance(sc["matches"], list) and sc["matches"]:
                # Show first 3 matches max
                preview = sc["matches"][:3]
                print(f"  matches[0..{min(3, len(sc['matches']))}]: {preview}")
                if len(sc["matches"]) > 3:
                    print(f"  ...({len(sc['matches'])} total)")
            else:
                preview = {k: v for k, v in sc.items() if k != "matches"}
                print(f"  data: {preview}")
            passed += 1
        except Exception as e:
            print(f"\n[{label}]")
            print(f"  ❌ EXCEPTION: {type(e).__name__}: {e}")
            failed += 1

    print("\n" + "=" * 70)
    print(f"PASSED: {passed}  FAILED: {failed}  TOTAL: {passed + failed}")
    print("=" * 70)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
