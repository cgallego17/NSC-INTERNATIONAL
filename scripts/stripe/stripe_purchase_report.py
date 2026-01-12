from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from django.db.models import Count

from apps.accounts.models import Order, Player, StripeEventCheckout


def _json_dumps(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False, default=str)


def generate_report(output_path: str) -> Path:
    """Generate a Markdown report for paid StripeEventCheckout purchases."""

    out = Path(output_path)

    lines: list[str] = []
    lines.append("# Stripe Purchases Report (DB)")
    lines.append("")
    lines.append(f"Generated at (UTC): {datetime.now(timezone.utc).isoformat()}")
    lines.append("")

    total_checkouts = StripeEventCheckout.objects.count()
    by_status = list(
        StripeEventCheckout.objects.values("status")
        .annotate(c=Count("id"))
        .order_by("-c")
    )
    order_count = Order.objects.count()

    lines.append("## Summary")
    lines.append("")
    lines.append(f"- StripeEventCheckout.count = {total_checkouts}")
    lines.append(f"- StripeEventCheckout.by_status = {by_status}")
    lines.append(f"- Order.count = {order_count}")

    paid_qs = (
        StripeEventCheckout.objects.filter(status="paid")
        .select_related("user", "event")
        .order_by("-created_at")
    )

    lines.append("")
    lines.append("## Paid checkouts")
    lines.append("")
    lines.append(f"paid_checkouts = {paid_qs.count()}")

    missing_orders: list[StripeEventCheckout] = []

    for c in paid_qs:
        has_order = Order.objects.filter(stripe_checkout=c).exists()
        if not has_order:
            missing_orders.append(c)

        # Players included in purchase
        players = list(
            Player.objects.filter(id__in=(c.player_ids or [])).select_related("user")
        )

        # Rooms in snapshot
        cart = c.hotel_cart_snapshot or {}
        rooms = [
            v
            for v in cart.values()
            if isinstance(v, dict) and (v.get("type") == "room")
        ]
        rooms_sorted = sorted(rooms, key=lambda x: x.get("room_order", 999999))

        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(f"### Checkout #{c.id}")
        lines.append("")
        lines.append(f"- stripe_session_id: `{c.stripe_session_id}`")
        lines.append(f"- created_at: `{c.created_at}`")
        lines.append(f"- paid_at: `{c.paid_at}`")
        lines.append(f"- payment_mode: `{c.payment_mode}`")
        lines.append(f"- amount_total: `{c.amount_total}`")
        lines.append(f"- currency: `{c.currency}`")
        lines.append(f"- user: `{c.user.username}` ({c.user.email})")
        event_title = getattr(c.event, "title", "")
        lines.append(f"- event: `{event_title}` (id={c.event_id})")
        lines.append(f"- has_order: `{has_order}`")

        lines.append(f"- players_count: `{len(players)}`")
        if players:
            lines.append("  - players:")
            for p in players:
                u = p.user
                lines.append(
                    f"    - {(u.get_full_name() or u.username)} (player_id={p.id})"
                )

        lines.append("")
        lines.append("#### Breakdown")
        lines.append("```json")
        lines.append(_json_dumps(c.breakdown or {}))
        lines.append("```")

        lines.append("")
        lines.append("#### Hotel rooms (from hotel_cart_snapshot)")
        lines.append(f"- rooms_count: `{len(rooms_sorted)}`")
        for r in rooms_sorted:
            lines.append(
                "  - "
                + f"room_id={r.get('room_id')} "
                + f"check_in={r.get('check_in')} "
                + f"check_out={r.get('check_out')} "
                + f"guests={r.get('guests')}"
            )
            agn = r.get("additional_guest_names")
            if agn:
                lines.append(f"    - additional_guest_names: {agn}")
            agd = r.get("additional_guest_details")
            if agd:
                if isinstance(agd, list):
                    lines.append(f"    - additional_guest_details_count: {len(agd)}")
                else:
                    lines.append("    - additional_guest_details_count: n/a")

    lines.append("")
    lines.append("## Paid checkouts missing Order")
    lines.append("")
    lines.append(f"missing_count = {len(missing_orders)}")
    if missing_orders:
        lines.append("")
        for c in missing_orders:
            lines.append(
                f"- checkout_id={c.id} session={c.stripe_session_id} user={c.user_id} event={c.event_id} paid_at={c.paid_at}"
            )

    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out
