# Stripe Backfill (Additional Guests -> HotelReservation)

Generated at (UTC): 2026-01-11T04:46:51.888561+00:00
Mode: APPLY

Paid checkouts (with hotel_cart_snapshot) found: 2

---

## Checkout #46

- stripe_session_id: `cs_live_a1mpr8pEUWLIKSZFHCp4qFipyrLf9QMPdoARdia3tZ4lZ1gy4kHGgtHJaN`
- user_id: `31`
- event_id: `2`
- paid_at: `2026-01-07 22:21:38.379594+00:00`
- room_items_count: 1
  - SKIP(room_id=4 2026-07-22->2026-07-30): snapshot has no additional guest data

---

## Checkout #41

- stripe_session_id: `cs_live_a1ACdbtCSKjMahxwvhA9qkNcUeRUgAW5Du0513KkjNDrOEBb07yU6ihvTj`
- user_id: `44`
- event_id: `1`
- paid_at: `2026-01-07 20:03:39.627653+00:00`
- room_items_count: 1
  - SKIP(room_id=1 2026-06-20->2026-06-28): snapshot has no additional guest data

---

# Legacy Notes Backfill

Legacy candidate reservations: 2
- UPDATED(reservation_id=4)
- UPDATED(reservation_id=3)

# Totals

- checkouts_seen: 2
- room_items_seen: 2
- reservations_found: 0
- reservations_missing_data: 2
- reservations_updated: 2
- reservations_skipped_already_has_data: 0
- reservations_skipped_no_snapshot_data: 2
- errors: 0
