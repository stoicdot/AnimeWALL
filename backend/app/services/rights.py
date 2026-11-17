
"""Permission checks for publishing and distributing wallpapers."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal, Sequence

from app.models.wallpaper_rights import WallpaperRights


RightsPurpose = Literal[
    "display",
    "download",
    "commercial",
    "modify",
]


@dataclass(frozen=True)
class RightsDecision:
    """Result of evaluating a wallpaper's rights records."""

    allowed: bool
    reasons: tuple[str, ...]


def evaluate_wallpaper_rights(
    rights_records: Sequence[WallpaperRights],
    required_rights_types: set[str],
    purpose: RightsPurpose = "display",
    *,
    now: datetime | None = None,
) -> RightsDecision:
    """Check whether recorded permissions satisfy a requested use.

    Initial policy:
    - Every wallpaper must have artwork rights.
    - Every required rights type must have a record.
    - Every attached rights record must be verified.
    - Permission must be currently effective and unexpired.
    - Only worldwide permissions are accepted for public publishing.
    - Required attribution must have credit text.
    """

    if purpose not in {
        "display",
        "download",
        "commercial",
        "modify",
    }:
        raise ValueError(f"Unsupported rights purpose: {purpose}")

    if not required_rights_types:
        raise ValueError("At least one required rights type must be provided.")

    required_types = set(required_rights_types)
    required_types.add("artwork")

    records = list(rights_records)
    reasons: list[str] = []

    current_time = now or datetime.now(timezone.utc)

    if current_time.tzinfo is None or current_time.utcoffset() is None:
        raise ValueError("'now' must be timezone-aware.")

    # Every required rights type must have a record.
    available_types = {record.rights_type for record in records}
    missing_types = required_types - available_types

    for rights_type in sorted(missing_types):
        reasons.append(f"Missing required rights record: {rights_type}.")

    if not records:
        reasons.append("No rights records are attached to this wallpaper.")

    for record in records:
        holder = record.rights_holder_name or "Unknown rights holder"
        prefix = f"{record.rights_type} rights from {holder}"

        if record.status != "verified":
            reasons.append(f"{prefix} are not verified.")

        if not record.license_name.strip():
            reasons.append(f"{prefix} have no license name.")

        if not record.public_display_allowed:
            reasons.append(f"{prefix} do not permit public display.")

        # A worldwide site cannot safely assume restricted or unknown
        # territorial permissions apply to every visitor.
        if record.territory_scope != "worldwide":
            reasons.append(
                f"{prefix} do not have worldwide permission."
            )

        if record.granted_at is None:
            reasons.append(f"{prefix} have no recorded grant date.")
        else:
            granted_at = record.granted_at

            if granted_at.tzinfo is None or granted_at.utcoffset() is None:
                reasons.append(f"{prefix} have an invalid grant timestamp.")
            elif granted_at > current_time:
                reasons.append(f"{prefix} are not effective yet.")

        if record.expires_at is not None:
            expires_at = record.expires_at

            if expires_at.tzinfo is None or expires_at.utcoffset() is None:
                reasons.append(f"{prefix} have an invalid expiry timestamp.")
            elif expires_at <= current_time:
                reasons.append(f"{prefix} have expired.")

        if record.attribution_required and not (
            record.required_credit and record.required_credit.strip()
        ):
            reasons.append(f"{prefix} require missing attribution text.")

        if purpose == "download" and not record.downloads_allowed:
            reasons.append(f"{prefix} do not permit downloads.")

        if purpose == "commercial" and not record.commercial_use_allowed:
            reasons.append(f"{prefix} do not permit commercial use.")

        if purpose == "modify" and not record.modifications_allowed:
            reasons.append(f"{prefix} do not permit modifications.")

    return RightsDecision(
        allowed=len(reasons) == 0,
        reasons=tuple(reasons),
    )
