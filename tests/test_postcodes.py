"""Pytest cases for hu-postcode-validator data correctness.

Regression guard for the Szeged sub-postcode data gap (6720-6728 were missing
from the Települések sheet — only present in Szeged u. street sheet). Covers
all 5 multi-postcode HU cities + a couple of multi-area cities that load via
the normal path (Hódmezővásárhely, Makó).
"""

from __future__ import annotations

import pytest

from postcode import tools


# ── Szeged sub-postcodes (the original bug) ─────────────────────────────

@pytest.mark.asyncio
@pytest.mark.parametrize("pc", [6720, 6724, 6728])
async def test_lookup_szeged_subpostcode_resolves(pc: int) -> None:
    result = await tools.lookup_postcode(pc)
    sc = result["structuredContent"]
    assert sc["found"] is True, f"Szeged sub-postcode {pc} should resolve"
    assert any(m["settlement"] == "Szeged" for m in sc["matches"]), (
        f"{pc} should map to Szeged, got {sc['matches']}"
    )


@pytest.mark.asyncio
async def test_lookup_szeged_main_postcode() -> None:
    """Main postcode must keep working (no regression)."""
    result = await tools.lookup_postcode(6700)
    sc = result["structuredContent"]
    assert sc["found"] is True
    assert any(m["settlement"] == "Szeged" for m in sc["matches"])


@pytest.mark.asyncio
async def test_validate_address_szeged_subpostcode() -> None:
    """6720 + 'Szeged' must validate (was returning invalid before fix)."""
    result = await tools.validate_address(6720, "Szeged")
    sc = result["structuredContent"]
    assert sc["valid"] is True, f"Expected valid, got {sc}"


# ── Other 4 cities with the same sub-postcode pattern ───────────────────

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "pc,city",
    [
        (3525, "Miskolc"),    # Miskolc internal
        (4025, "Debrecen"),   # Debrecen internal
        (7621, "Pécs"),       # Pécs internal
        (9021, "Győr"),       # Győr internal
    ],
)
async def test_other_multi_postcode_cities(pc: int, city: str) -> None:
    result = await tools.lookup_postcode(pc)
    sc = result["structuredContent"]
    assert sc["found"] is True, f"{city} sub-postcode {pc} should resolve"
    assert any(m["settlement"] == city for m in sc["matches"]), (
        f"{pc} should map to {city}, got {sc['matches']}"
    )


# ── Regression: multi-area cities that load via Települések ─────────────

@pytest.mark.asyncio
async def test_regression_hodmezovasarhely() -> None:
    """Hódmezővásárhely has 6800/6805/6806 in Települések — must still work."""
    result = await tools.lookup_postcode(6805)
    sc = result["structuredContent"]
    assert sc["found"] is True
    assert any(m["settlement"] == "Hódmezővásárhely" for m in sc["matches"])


@pytest.mark.asyncio
async def test_regression_mako() -> None:
    """Makó has 6900 + 6903 in Települések — must still work."""
    result = await tools.lookup_postcode(6903)
    sc = result["structuredContent"]
    assert sc["found"] is True
    assert any(m["settlement"] == "Makó" for m in sc["matches"])


@pytest.mark.asyncio
async def test_regression_budapest_synthesis() -> None:
    """Budapest entries synthesized from Bp.u. — must still work."""
    result = await tools.lookup_postcode(1102)
    sc = result["structuredContent"]
    assert sc["found"] is True
    assert any(m["settlement"] == "Budapest" for m in sc["matches"])
