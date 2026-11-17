
"""Tests for wallpaper rights verification."""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from app.services.rights import evaluate_wallpaper_rights


NOW = datetime(2026, 11, 14, 10, 0, tzinfo=timezone.utc)


def make_rights_record(**overrides):
    """Create a valid rights record for isolated service tests."""

    values = {
        "rights_type": "artwork",
        "rights_holder_name": "Original Artist",
        "license_name": "Written Permission",
        "status": "verified",
        "public_display_allowed": True,
        "commercial_use_allowed": True,
        "downloads_allowed": True,
        "modifications_allowed": True,
        "attribution_required": False,
        "required_credit": None,
        "territory_scope": "worldwide",
        "granted_at": NOW - timedelta(days=30),
        "expires_at": None,
    }

    values.update(overrides)
    return SimpleNamespace(**values)


def test_valid_rights_allow_public_display():
    record = make_rights_record()

    decision = evaluate_wallpaper_rights(
        [record],
        {"artwork"},
        "display",
        now=NOW,
    )

    assert decision.allowed is True
    assert decision.reasons == ()


def test_missing_character_permission_blocks_display():
    artwork = make_rights_record()

    decision = evaluate_wallpaper_rights(
        [artwork],
        {"artwork", "character_ip"},
        "display",
        now=NOW,
    )

    assert decision.allowed is False
    assert any("character_ip" in reason for reason in decision.reasons)


def test_pending_rights_block_display():
    record = make_rights_record(status="pending")

    decision = evaluate_wallpaper_rights(
        [record],
        {"artwork"},
        "display",
        now=NOW,
    )

    assert decision.allowed is False


def test_expired_rights_block_display():
    record = make_rights_record(
        expires_at=NOW - timedelta(days=1),
    )

    decision = evaluate_wallpaper_rights(
        [record],
        {"artwork"},
        "display",
        now=NOW,
    )

    assert decision.allowed is False
    assert any("expired" in reason for reason in decision.reasons)


def test_download_requires_download_permission():
    record = make_rights_record(downloads_allowed=False)

    decision = evaluate_wallpaper_rights(
        [record],
        {"artwork"},
        "download",
        now=NOW,
    )

    assert decision.allowed is False


def test_commercial_use_requires_permission():
    record = make_rights_record(commercial_use_allowed=False)

    decision = evaluate_wallpaper_rights(
        [record],
        {"artwork"},
        "commercial",
        now=NOW,
    )

    assert decision.allowed is False


def test_modifications_require_permission():
    record = make_rights_record(modifications_allowed=False)

    decision = evaluate_wallpaper_rights(
        [record],
        {"artwork"},
        "modify",
        now=NOW,
    )

    assert decision.allowed is False


def test_missing_required_attribution_blocks_display():
    record = make_rights_record(
        attribution_required=True,
        required_credit=" ",
    )

    decision = evaluate_wallpaper_rights(
        [record],
        {"artwork"},
        "display",
        now=NOW,
    )

    assert decision.allowed is False
    assert any("attribution" in reason for reason in decision.reasons)


def test_restricted_territory_blocks_public_display():
    record = make_rights_record(territory_scope="restricted")

    decision = evaluate_wallpaper_rights(
        [record],
        {"artwork"},
        "display",
        now=NOW,
    )

    assert decision.allowed is False
    assert any("worldwide" in reason for reason in decision.reasons)


def test_future_grant_date_blocks_display():
    record = make_rights_record(
        granted_at=NOW + timedelta(days=1),
    )

    decision = evaluate_wallpaper_rights(
        [record],
        {"artwork"},
        "display",
        now=NOW,
    )

    assert decision.allowed is False
    assert any("not effective yet" in reason for reason in decision.reasons)


def test_empty_rights_records_block_display():
    decision = evaluate_wallpaper_rights(
        [],
        {"artwork"},
        "display",
        now=NOW,
    )

    assert decision.allowed is False


def test_naive_current_time_is_rejected():
    record = make_rights_record()

    with pytest.raises(ValueError, match="timezone-aware"):
        evaluate_wallpaper_rights(
            [record],
            {"artwork"},
            "display",
            now=datetime(2026, 11, 14, 10, 0),
        )
