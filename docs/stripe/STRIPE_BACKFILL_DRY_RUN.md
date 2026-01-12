# Stripe Backfill (Orders + Reservations + Event Registrations)

Generated at (UTC): 2026-01-11T03:55:24.430842+00:00
Mode: DRY-RUN

Paid checkouts found: 6

---

## Checkout #46

- stripe_session_id: `cs_live_a1mpr8pEUWLIKSZFHCp4qFipyrLf9QMPdoARdia3tZ4lZ1gy4kHGgtHJaN`
- user: `aldo.martinez` (aldomartinez145@gmail.com)
- event_id: `2`
- amount_total: `4841.24` usd
- payment_mode: `plan`
- paid_at: `2026-01-07 22:21:38.379594+00:00`
- order: MISSING
- order: WOULD_CREATE
- player_ids: [17]
- attendance:
  - EXISTS(player_id=17, user_id=32)
- room_items_count: 1
- reservations:
  - EXISTS(reservation_id=5)

---

## Checkout #41

- stripe_session_id: `cs_live_a1ACdbtCSKjMahxwvhA9qkNcUeRUgAW5Du0513KkjNDrOEBb07yU6ihvTj`
- user: `maribel.hernandez` (maribelcastillo001@gmail.com)
- event_id: `1`
- amount_total: `5752.88` usd
- payment_mode: `plan`
- paid_at: `2026-01-07 20:03:39.627653+00:00`
- order: MISSING
- order: WOULD_CREATE
- player_ids: [26, 27]
- attendance:
  - EXISTS(player_id=26, user_id=45)
  - EXISTS(player_id=27, user_id=46)
- room_items_count: 1
- reservations:
  - WOULD_CREATE(room_id=1 2026-06-20->2026-06-28)

---

## Checkout #20

- stripe_session_id: `cs_live_a1DL0c5zsltqNl480DgIRNHWm7WgRHePpQFKCae0ju6Caeq36qF96qHfPy`
- user: `victor.balderas` (vicvadar@gmail.com)
- event_id: `2`
- amount_total: `1500.00` usd
- payment_mode: `plan`
- paid_at: `2026-01-07 02:02:52.574819+00:00`
- order: MISSING
- order: WOULD_CREATE
- player_ids: [35]
- attendance:
  - EXISTS(player_id=35, user_id=60)
- room_items_count: 0

---

## Checkout #18

- stripe_session_id: `cs_live_a1lXEJisMRtKWQOEoktBsRvZpD49verbGs6mrfNoFCPpCGxrQ4fXs5IoDd`
- user: `luis.tovar` (luistovar0316@gmail.com)
- event_id: `6`
- amount_total: `10.00` usd
- payment_mode: `plan`
- paid_at: `2026-01-06 07:18:07.011491+00:00`
- order: MISSING
- order: WOULD_CREATE
- player_ids: [36]
- attendance:
  - EXISTS(player_id=36, user_id=61)
- room_items_count: 0

---

## Checkout #17

- stripe_session_id: `cs_live_a17Yo8l59fneF5HdzqcfSKqjCLiY7j6Vw7stvXKt9ewUIqFtnEwK3mxuRs`
- user: `luis.tovar` (luistovar0316@gmail.com)
- event_id: `5`
- amount_total: `5.00` usd
- payment_mode: `now`
- paid_at: `2026-01-06 06:43:15.781036+00:00`
- order: MISSING
- order: WOULD_CREATE
- player_ids: [37]
- attendance:
  - EXISTS(player_id=37, user_id=62)
- room_items_count: 0

---

## Checkout #16

- stripe_session_id: `cs_live_a1IkxC9Vy6w6tTAG5p7t4KtiS2eSgAvxSD7PMN7ZQjCFmmfGL8rtHNZZrw`
- user: `luis.tovar` (luistovar0316@gmail.com)
- event_id: `5`
- amount_total: `5.00` usd
- payment_mode: `now`
- paid_at: `2026-01-06 06:01:02.632526+00:00`
- order: MISSING
- order: WOULD_CREATE
- player_ids: [36]
- attendance:
  - EXISTS(player_id=36, user_id=61)
- room_items_count: 0

# Totals

- checkouts_seen: 6
- orders_created: 0
- orders_existing: 0
- attendances_created: 0
- attendances_existing: 7
- reservations_created: 0
- reservations_existing: 1
- errors: 0
