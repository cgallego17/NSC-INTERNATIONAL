from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from django.db import transaction

from apps.accounts.models import Order, StripeEventCheckout


@dataclass
class BackfillStats:
    checkouts_seen: int = 0
    orders_created: int = 0
    orders_existing: int = 0
    attendances_created: int = 0
    attendances_existing: int = 0
    reservations_created: int = 0
    reservations_existing: int = 0
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


def backfill_paid_checkouts(*, apply: bool, output_md_path: str) -> Path:
    """Backfill Orders + attendance + hotel reservations for paid Stripe checkouts.

    - Idempotent: does not duplicate Order/Attendance/Reservation when already present.
    - Does NOT decrement HotelRoom stock (safer for historical backfills).

    Writes a Markdown report to `output_md_path`.
    """

    from apps.accounts.models import Player
    from apps.accounts.views_private import _create_order_from_stripe_checkout
    from apps.events.models import EventAttendance
    from apps.locations.models import (
        HotelReservation,
        HotelReservationService,
        HotelRoom,
        HotelService,
    )

    stats = BackfillStats()
    lines: list[str] = []

    qs = (
        StripeEventCheckout.objects.filter(status="paid")
        .select_related("user", "event")
        .order_by("-created_at")
    )

    lines.append("# Stripe Backfill (Orders + Reservations + Event Registrations)")
    lines.append("")
    lines.append(f"Generated at (UTC): {datetime.now(timezone.utc).isoformat()}")
    lines.append(f"Mode: {'APPLY' if apply else 'DRY-RUN'}")
    lines.append("")
    lines.append(f"Paid checkouts found: {qs.count()}")

    for checkout in qs:
        stats.checkouts_seen += 1
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append(f"## Checkout #{checkout.id}")
        lines.append("")
        lines.append(f"- stripe_session_id: `{checkout.stripe_session_id}`")
        lines.append(f"- user: `{checkout.user.username}` ({checkout.user.email})")
        lines.append(f"- event_id: `{checkout.event_id}`")
        lines.append(f"- amount_total: `{checkout.amount_total}` {checkout.currency}")
        lines.append(f"- payment_mode: `{checkout.payment_mode}`")
        lines.append(f"- paid_at: `{checkout.paid_at}`")

        try:
            # 1) Order
            order = Order.objects.filter(stripe_checkout=checkout).first()
            if order:
                stats.orders_existing += 1
                lines.append(
                    f"- order: EXISTS (id={order.id}, order_number={getattr(order, 'order_number', '')})"
                )
            else:
                lines.append("- order: MISSING")
                if apply:
                    with transaction.atomic():
                        order = _create_order_from_stripe_checkout(checkout)
                    stats.orders_created += 1
                    lines.append(
                        f"- order: CREATED (id={order.id}, order_number={getattr(order, 'order_number', '')})"
                    )
                else:
                    lines.append("- order: WOULD_CREATE")

            # 2) Event attendance confirmations
            player_ids: list[int] = list(checkout.player_ids or [])
            lines.append(f"- player_ids: {player_ids}")

            attendance_actions: list[str] = []
            for player_id in player_ids:
                player = (
                    Player.objects.filter(id=player_id).select_related("user").first()
                )
                if not player or not getattr(player, "user", None):
                    attendance_actions.append(
                        f"SKIP(player_id={player_id}: no player.user)"
                    )
                    continue
                player_user = player.user

                exists = EventAttendance.objects.filter(
                    event=checkout.event, user=player_user
                ).exists()
                if exists:
                    stats.attendances_existing += 1
                    attendance_actions.append(
                        f"EXISTS(player_id={player_id}, user_id={player_user.id})"
                    )
                    continue

                if not apply:
                    attendance_actions.append(
                        f"WOULD_CREATE(player_id={player_id}, user_id={player_user.id})"
                    )
                    continue

                with transaction.atomic():
                    EventAttendance.objects.update_or_create(
                        event=checkout.event,
                        user=player_user,
                        defaults={"status": "confirmed"},
                    )
                stats.attendances_created += 1
                attendance_actions.append(
                    f"CREATED(player_id={player_id}, user_id={player_user.id})"
                )

            if attendance_actions:
                lines.append("- attendance:")
                for a in attendance_actions:
                    lines.append(f"  - {a}")

            # 3) Hotel reservations
            room_items = _iter_room_items(checkout.hotel_cart_snapshot)
            lines.append(f"- room_items_count: {len(room_items)}")

            reservation_actions: list[str] = []
            for item in room_items:
                room_id = item.get("room_id")
                check_in_s = item.get("check_in")
                check_out_s = item.get("check_out")

                if not room_id or not check_in_s or not check_out_s:
                    reservation_actions.append(
                        f"SKIP(room_id={room_id} check_in={check_in_s} check_out={check_out_s})"
                    )
                    continue

                try:
                    check_in = datetime.strptime(check_in_s, "%Y-%m-%d").date()
                    check_out = datetime.strptime(check_out_s, "%Y-%m-%d").date()
                except Exception:
                    reservation_actions.append(
                        f"SKIP(room_id={room_id}: invalid dates {check_in_s}..{check_out_s})"
                    )
                    continue

                session_id = str(checkout.stripe_session_id or "")
                existing = (
                    HotelReservation.objects.filter(
                        user=checkout.user,
                        room_id=room_id,
                        check_in=check_in,
                        check_out=check_out,
                    )
                    .filter(notes__icontains=session_id)
                    .first()
                )
                if not existing and order:
                    existing = HotelReservation.objects.filter(
                        order=order,
                        user=checkout.user,
                        room_id=room_id,
                        check_in=check_in,
                        check_out=check_out,
                    ).first()

                if existing:
                    stats.reservations_existing += 1
                    if order and not existing.order_id and apply:
                        with transaction.atomic():
                            existing.order = order
                            existing.save(update_fields=["order"])
                        reservation_actions.append(
                            f"EXISTS(reservation_id={existing.id}) + ASSIGNED_ORDER(order_id={order.id})"
                        )
                    else:
                        reservation_actions.append(
                            f"EXISTS(reservation_id={existing.id})"
                        )
                    continue

                if not apply:
                    reservation_actions.append(
                        f"WOULD_CREATE(room_id={room_id} {check_in_s}->{check_out_s})"
                    )
                    continue

                room = (
                    HotelRoom.objects.select_related("hotel").filter(id=room_id).first()
                )
                if not room:
                    reservation_actions.append(
                        f"SKIP(room_id={room_id}: room not found)"
                    )
                    continue

                additional_guest_details = item.get("additional_guest_details") or []
                additional_guest_names = item.get("additional_guest_names") or []

                additional_guest_names_text = ""
                additional_guest_details_json: list[dict[str, Any]] = []

                if (
                    isinstance(additional_guest_details, list)
                    and additional_guest_details
                ):
                    additional_guest_details_json = additional_guest_details
                    names_with_dates: list[str] = []
                    for g in additional_guest_details_json:
                        name = (g.get("name") or "").strip()
                        if not name:
                            continue
                        birth_date = (g.get("birth_date") or "").strip()
                        names_with_dates.append(
                            f"{name} ({birth_date})" if birth_date else name
                        )
                    additional_guest_names_text = "\n".join(names_with_dates)
                elif (
                    isinstance(additional_guest_names, list) and additional_guest_names
                ):
                    additional_guest_names_text = "\n".join(
                        [
                            n
                            for n in additional_guest_names
                            if isinstance(n, str) and n.strip()
                        ]
                    )
                    additional_guest_details_json = [
                        {
                            "name": n.strip(),
                            "type": "adult",
                            "birth_date": "",
                            "email": "",
                        }
                        for n in additional_guest_names
                        if isinstance(n, str) and n.strip()
                    ]

                with transaction.atomic():
                    reservation = HotelReservation.objects.create(
                        hotel=room.hotel,
                        room=room,
                        user=checkout.user,
                        order=order,
                        guest_name=(
                            checkout.user.get_full_name() or checkout.user.username
                        ),
                        guest_email=checkout.user.email,
                        guest_phone=getattr(
                            getattr(checkout.user, "profile", None), "phone", ""
                        )
                        or "",
                        number_of_guests=int(item.get("guests", 1) or 1),
                        check_in=check_in,
                        check_out=check_out,
                        status="confirmed",
                        notes=f"Reserva pagada vía Stripe session {checkout.stripe_session_id}",
                        additional_guest_names=additional_guest_names_text,
                        additional_guest_details_json=additional_guest_details_json,
                    )

                    # Attach services (best-effort)
                    for service_data in item.get("services", []) or []:
                        service_id = (service_data or {}).get("service_id")
                        qty = int((service_data or {}).get("quantity", 1) or 1)
                        if not service_id:
                            continue
                        service = HotelService.objects.filter(
                            id=service_id, hotel=room.hotel, is_active=True
                        ).first()
                        if not service:
                            continue
                        HotelReservationService.objects.get_or_create(
                            reservation=reservation,
                            service=service,
                            defaults={"quantity": qty},
                        )

                    # Compute total if available
                    if hasattr(reservation, "calculate_total"):
                        try:
                            reservation.total_amount = reservation.calculate_total()
                            reservation.save(update_fields=["total_amount"])
                        except Exception:
                            pass

                stats.reservations_created += 1
                reservation_actions.append(
                    f"CREATED(reservation_id={reservation.id}, room_id={room_id})"
                )

            if reservation_actions:
                lines.append("- reservations:")
                for r in reservation_actions:
                    lines.append(f"  - {r}")

        except Exception as e:
            stats.errors += 1
            lines.append("- ERROR:")
            lines.append(f"```\n{e}\n```")

    lines.append("")
    lines.append("# Totals")
    lines.append("")
    lines.append(f"- checkouts_seen: {stats.checkouts_seen}")
    lines.append(f"- orders_created: {stats.orders_created}")
    lines.append(f"- orders_existing: {stats.orders_existing}")
    lines.append(f"- attendances_created: {stats.attendances_created}")
    lines.append(f"- attendances_existing: {stats.attendances_existing}")
    lines.append(f"- reservations_created: {stats.reservations_created}")
    lines.append(f"- reservations_existing: {stats.reservations_existing}")
    lines.append(f"- errors: {stats.errors}")

    out = Path(output_md_path)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out
