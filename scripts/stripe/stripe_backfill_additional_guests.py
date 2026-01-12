from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from django.db import transaction
from django.db.models import Q

from apps.accounts.models import StripeEventCheckout


@dataclass
class BackfillStats:
    checkouts_seen: int = 0
    room_items_seen: int = 0
    reservations_found: int = 0
    reservations_missing_data: int = 0
    reservations_updated: int = 0
    reservations_skipped_already_has_data: int = 0
    reservations_skipped_no_snapshot_data: int = 0
    errors: int = 0


def _json(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False, default=str)


def _iter_room_items(hotel_cart_snapshot: Any) -> list[dict[str, Any]]:
    if not isinstance(hotel_cart_snapshot, dict):
        return []
    rooms = [
        v
        for v in hotel_cart_snapshot.values()
        if isinstance(v, dict) and v.get("type") == "room"
    ]
    return sorted(rooms, key=lambda x: x.get("room_order", 999999))


def _normalize_guest_payload(item: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    """Return (additional_guest_names_text, additional_guest_details_json)."""

    details = item.get("additional_guest_details")
    names = item.get("additional_guest_names")

    if isinstance(details, list) and details:
        cleaned_details: list[dict[str, Any]] = []
        names_with_dates: list[str] = []
        for g in details:
            if not isinstance(g, dict):
                continue
            name = str(g.get("name") or "").strip()
            if not name:
                continue
            birth_date = str(g.get("birth_date") or "").strip()
            email = str(g.get("email") or "").strip()
            g_type = str(g.get("type") or "adult").strip() or "adult"

            cleaned = {
                "name": name,
                "type": g_type,
                "birth_date": birth_date,
                "email": email,
            }
            cleaned_details.append(cleaned)
            names_with_dates.append(f"{name} ({birth_date})" if birth_date else name)

        return "\n".join(names_with_dates), cleaned_details

    if isinstance(names, list) and names:
        cleaned_names = [str(n).strip() for n in names if str(n).strip()]
        details_json = [
            {"name": n, "type": "adult", "birth_date": "", "email": ""}
            for n in cleaned_names
        ]
        return "\n".join(cleaned_names), details_json

    return "", []


def _parse_legacy_notes(notes_text: str) -> tuple[str, list[dict[str, Any]]]:
    """Parse legacy notes format into (names_text, details_json).

    Expected patterns:
    - Selected players/children: ...
    - Additional adults: ...
    - Additional children: ...
    """

    if not notes_text or not isinstance(notes_text, str):
        return "", []

    if (
        "Selected players/children:" not in notes_text
        and "Additional adults:" not in notes_text
        and "Additional children:" not in notes_text
    ):
        return "", []

    def _split_outside_parens(s: str) -> list[str]:
        """Split by '|' or ',' but ignore separators inside parentheses."""
        out: list[str] = []
        buf: list[str] = []
        depth = 0
        for ch in s:
            if ch == "(":
                depth += 1
            elif ch == ")" and depth > 0:
                depth -= 1

            if depth == 0 and ch in ["|", ","]:
                token = "".join(buf).strip()
                if token:
                    out.append(token)
                buf = []
                continue

            buf.append(ch)

        token = "".join(buf).strip()
        if token:
            out.append(token)
        return out

    def _parse_person(token: str, *, default_type: str) -> dict[str, str] | None:
        # token examples:
        # - "Mathias Gallego (2013-11-11, ASD@ASD.COM)"
        # - "Ana (2000-02-20)"
        # - "Venus (2013-02-02)"
        t = str(token or "").strip()
        if not t:
            return None

        m = re.match(r"^(?P<name>[^()]+?)\s*(?:\((?P<meta>[^)]*)\))?$", t)
        if not m:
            name = t
            meta = ""
        else:
            name = (m.group("name") or "").strip()
            meta = (m.group("meta") or "").strip()

        if not name:
            return None

        birth_date = ""
        email = ""
        if meta:
            # meta can be "YYYY-MM-DD" or "YYYY-MM-DD, email"
            parts = [p.strip() for p in meta.split(",") if p.strip()]
            for p in parts:
                if re.match(r"^\d{4}-\d{2}-\d{2}$", p):
                    birth_date = p
                elif "@" in p and "." in p:
                    email = p

        return {
            "name": name,
            "type": default_type,
            "birth_date": birth_date,
            "email": email,
        }

    details: list[dict[str, Any]] = []

    # Selected players/children
    players_match = re.search(r"Selected players/children:\s*([^|]+)", notes_text)
    if players_match:
        players_str = players_match.group(1).strip()
        for tok in _split_outside_parens(players_str):
            person = _parse_person(tok, default_type="child")
            if person:
                details.append(person)

    # Additional adults
    adults_match = re.search(r"Additional adults:\s*([^|]+)", notes_text)
    if adults_match:
        adults_str = adults_match.group(1).strip()
        for tok in _split_outside_parens(adults_str):
            person = _parse_person(tok, default_type="adult")
            if person:
                details.append(person)

    # Additional children
    children_match = re.search(r"Additional children:\s*([^|]+)", notes_text)
    if children_match:
        children_str = children_match.group(1).strip()
        for tok in _split_outside_parens(children_str):
            person = _parse_person(tok, default_type="child")
            if person:
                details.append(person)

    # Deduplicate (keep first occurrence)
    seen: set[str] = set()
    cleaned_details: list[dict[str, Any]] = []
    for d in details:
        name = str(d.get("name") or "").strip()
        if not name or name in seen:
            continue
        seen.add(name)
        cleaned_details.append(d)

    if not cleaned_details:
        return "", []

    names_text = "\n".join(
        [
            f"{d['name']} ({d['birth_date']})" if d.get("birth_date") else d["name"]
            for d in cleaned_details
            if d.get("name")
        ]
    )
    return names_text, cleaned_details


def backfill(*, apply: bool, output_md_path: str) -> Path:
    from apps.locations.models import HotelReservation

    stats = BackfillStats()
    lines: list[str] = []

    qs = (
        StripeEventCheckout.objects.filter(status="paid")
        .exclude(Q(hotel_cart_snapshot__isnull=True) | Q(hotel_cart_snapshot={}))
        .select_related("user", "event")
        .order_by("-created_at")
    )

    lines.append("# Stripe Backfill (Additional Guests -> HotelReservation)")
    lines.append("")
    lines.append(f"Generated at (UTC): {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"Mode: {'APPLY' if apply else 'DRY-RUN'}")
    lines.append("")
    lines.append(f"Paid checkouts (with hotel_cart_snapshot) found: {qs.count()}")

    for checkout in qs:
        stats.checkouts_seen += 1
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(f"## Checkout #{checkout.id}")
        lines.append("")
        lines.append(f"- stripe_session_id: `{checkout.stripe_session_id}`")
        lines.append(f"- user_id: `{checkout.user_id}`")
        lines.append(f"- event_id: `{checkout.event_id}`")
        lines.append(f"- paid_at: `{checkout.paid_at}`")

        room_items = _iter_room_items(checkout.hotel_cart_snapshot)
        lines.append(f"- room_items_count: {len(room_items)}")

        for item in room_items:
            stats.room_items_seen += 1
            room_id = item.get("room_id")
            check_in_s = item.get("check_in")
            check_out_s = item.get("check_out")

            if not room_id or not check_in_s or not check_out_s:
                lines.append(
                    f"  - SKIP(room_id={room_id} check_in={check_in_s} check_out={check_out_s}): missing identifiers"
                )
                continue

            try:
                check_in = datetime.strptime(str(check_in_s), "%Y-%m-%d").date()
                check_out = datetime.strptime(str(check_out_s), "%Y-%m-%d").date()
            except Exception as e:
                stats.errors += 1
                lines.append(
                    f"  - ERROR(room_id={room_id} {check_in_s}->{check_out_s}): invalid dates ({e})"
                )
                continue

            names_text, details_json = _normalize_guest_payload(item)
            if not names_text and not details_json:
                stats.reservations_skipped_no_snapshot_data += 1
                lines.append(
                    f"  - SKIP(room_id={room_id} {check_in}->{check_out}): snapshot has no additional guest data"
                )
                continue

            session_id = str(checkout.stripe_session_id or "")

            reservation = (
                HotelReservation.objects.filter(
                    user_id=checkout.user_id,
                    room_id=room_id,
                    check_in=check_in,
                    check_out=check_out,
                )
                .filter(notes__icontains=session_id)
                .order_by("-created_at")
                .first()
            )

            if not reservation and checkout.order_id:
                reservation = (
                    HotelReservation.objects.filter(
                        order_id=checkout.order_id,
                        user_id=checkout.user_id,
                        room_id=room_id,
                        check_in=check_in,
                        check_out=check_out,
                    )
                    .order_by("-created_at")
                    .first()
                )

            if not reservation:
                lines.append(
                    f"  - NOT_FOUND(room_id={room_id} {check_in}->{check_out}): no matching HotelReservation"
                )
                continue

            stats.reservations_found += 1

            has_any = bool((reservation.additional_guest_names or "").strip()) or bool(
                reservation.additional_guest_details_json
            )
            if has_any:
                stats.reservations_skipped_already_has_data += 1
                lines.append(
                    f"  - EXISTS(reservation_id={reservation.id}): already has additional guest data, skipping"
                )
                continue

            stats.reservations_missing_data += 1

            if not apply:
                lines.append(
                    f"  - WOULD_UPDATE(reservation_id={reservation.id} room_id={room_id}):\n"
                    f"    - additional_guest_names=\n{names_text}\n"
                    f"    - additional_guest_details_json={_json(details_json)}"
                )
                continue

            with transaction.atomic():
                reservation.additional_guest_names = names_text
                reservation.additional_guest_details_json = details_json
                reservation.save(
                    update_fields=[
                        "additional_guest_names",
                        "additional_guest_details_json",
                    ]
                )

            stats.reservations_updated += 1
            lines.append(
                f"  - UPDATED(reservation_id={reservation.id} room_id={room_id})"
            )

    # Second pass: legacy reservations where additional guests exist only in notes
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("# Legacy Notes Backfill")
    lines.append("")

    legacy_qs = HotelReservation.objects.filter(
        Q(additional_guest_names__isnull=True) | Q(additional_guest_names=""),
        additional_guest_details_json=[],
    ).filter(
        Q(notes__icontains="Selected players/children:")
        | Q(notes__icontains="Additional adults:")
        | Q(notes__icontains="Additional children:")
    )

    lines.append(f"Legacy candidate reservations: {legacy_qs.count()}")

    for r in legacy_qs.order_by("-created_at"):
        names_text, details_json = _parse_legacy_notes(r.notes or "")
        if not names_text and not details_json:
            continue

        stats.reservations_missing_data += 1

        if not apply:
            lines.append(
                f"- WOULD_UPDATE(reservation_id={r.id}):\n"
                f"  - additional_guest_names=\n{names_text}\n"
                f"  - additional_guest_details_json={_json(details_json)}"
            )
            continue

        with transaction.atomic():
            r.additional_guest_names = names_text
            r.additional_guest_details_json = details_json
            r.save(
                update_fields=[
                    "additional_guest_names",
                    "additional_guest_details_json",
                ]
            )

        stats.reservations_updated += 1
        lines.append(f"- UPDATED(reservation_id={r.id})")

    lines.append("")
    lines.append("# Totals")
    lines.append("")
    lines.append(f"- checkouts_seen: {stats.checkouts_seen}")
    lines.append(f"- room_items_seen: {stats.room_items_seen}")
    lines.append(f"- reservations_found: {stats.reservations_found}")
    lines.append(f"- reservations_missing_data: {stats.reservations_missing_data}")
    lines.append(f"- reservations_updated: {stats.reservations_updated}")
    lines.append(
        f"- reservations_skipped_already_has_data: {stats.reservations_skipped_already_has_data}"
    )
    lines.append(
        f"- reservations_skipped_no_snapshot_data: {stats.reservations_skipped_no_snapshot_data}"
    )
    lines.append(f"- errors: {stats.errors}")

    out = Path(output_md_path)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Backfill HotelReservation additional guests from StripeEventCheckout.hotel_cart_snapshot"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Persist changes (otherwise dry-run)",
    )
    parser.add_argument(
        "--output",
        default="STRIPE_BACKFILL_ADDITIONAL_GUESTS.md",
        help="Output Markdown report path (relative to repo root)",
    )
    args = parser.parse_args()

    out = backfill(apply=bool(args.apply), output_md_path=str(args.output))
    print(f"Wrote report: {out}")


if __name__ == "__main__":
    main()
