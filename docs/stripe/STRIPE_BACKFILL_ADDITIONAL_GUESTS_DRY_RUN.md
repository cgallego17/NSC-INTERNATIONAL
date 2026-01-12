# Stripe Backfill (Additional Guests -> HotelReservation)

Generated at (UTC): 2026-01-11T04:46:42.113306+00:00
Mode: DRY-RUN

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
- WOULD_UPDATE(reservation_id=4):
  - additional_guest_names=
Mathias Gallego (2013-11-11)
  - additional_guest_details_json=[
  {
    "name": "Mathias Gallego",
    "type": "child",
    "birth_date": "2013-11-11",
    "email": "ASD@ASD.COM"
  }
]
- WOULD_UPDATE(reservation_id=3):
  - additional_guest_names=
Mathias Gallego
Ana (2000-02-20)
Venus (2013-02-02)
  - additional_guest_details_json=[
  {
    "name": "Mathias Gallego",
    "type": "child",
    "birth_date": "",
    "email": ""
  },
  {
    "name": "Ana",
    "type": "adult",
    "birth_date": "2000-02-20",
    "email": ""
  },
  {
    "name": "Venus",
    "type": "child",
    "birth_date": "2013-02-02",
    "email": ""
  }
]

# Totals

- checkouts_seen: 2
- room_items_seen: 2
- reservations_found: 0
- reservations_missing_data: 2
- reservations_updated: 0
- reservations_skipped_already_has_data: 0
- reservations_skipped_no_snapshot_data: 2
- errors: 0
