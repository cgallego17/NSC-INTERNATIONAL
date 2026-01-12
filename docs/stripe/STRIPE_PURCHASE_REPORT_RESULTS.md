# Stripe Purchases Report (DB)

Generated at (UTC): 2026-01-11T03:06:23.856704+00:00

## Summary

- StripeEventCheckout.count = 58
- StripeEventCheckout.by_status = [{'status': 'expired', 'c': 33}, {'status': 'created', 'c': 19}, {'status': 'paid', 'c': 6}]
- Order.count = 0

## Paid checkouts

paid_checkouts = 6

---

### Checkout #46

- stripe_session_id: `cs_live_a1mpr8pEUWLIKSZFHCp4qFipyrLf9QMPdoARdia3tZ4lZ1gy4kHGgtHJaN`
- created_at: `2026-01-07 22:18:56.528045+00:00`
- paid_at: `2026-01-07 22:21:38.379594+00:00`
- payment_mode: `plan`
- amount_total: `4841.24`
- currency: `usd`
- user: `aldo.martinez` (aldomartinez145@gmail.com)
- event: `2026 NCS Caribbean World Series` (id=2)
- has_order: `False`
- players_count: `1`
  - players:
    - Aldo Martinez (player_id=17)

#### Breakdown
```json
{
  "players_total": "1795.00",
  "hotel_room_base": "2384.00",
  "hotel_services_total": "0.00",
  "hotel_iva": "0.00",
  "hotel_ish": "0.00",
  "hotel_total_taxes": "662.24",
  "hotel_nights": "8",
  "hotel_total": "3046.24",
  "no_show_fee": "0.00",
  "subtotal": "4841.24",
  "discount_percent": 0,
  "total": "4841.24"
}
```

#### Hotel rooms (from hotel_cart_snapshot)
- rooms_count: `1`
  - room_id=4 check_in=2026-07-22 check_out=2026-07-30 guests=4

---

### Checkout #41

- stripe_session_id: `cs_live_a1ACdbtCSKjMahxwvhA9qkNcUeRUgAW5Du0513KkjNDrOEBb07yU6ihvTj`
- created_at: `2026-01-07 20:00:56.899735+00:00`
- paid_at: `2026-01-07 20:03:39.627653+00:00`
- payment_mode: `plan`
- amount_total: `5752.88`
- currency: `usd`
- user: `maribel.hernandez` (maribelcastillo001@gmail.com)
- event: `2026 Latin American World Series` (id=1)
- has_order: `False`
- players_count: `2`
  - players:
    - Zeymar Hernandez (player_id=27)
    - Zulian Hernandez (player_id=26)

#### Breakdown
```json
{
  "players_total": "3590.00",
  "hotel_room_base": "1884.72",
  "hotel_services_total": "0.00",
  "hotel_iva": "0.00",
  "hotel_ish": "0.00",
  "hotel_total_taxes": "278.16",
  "hotel_nights": "8",
  "hotel_total": "2162.88",
  "no_show_fee": "0.00",
  "subtotal": "5752.88",
  "discount_percent": 0,
  "total": "5752.88"
}
```

#### Hotel rooms (from hotel_cart_snapshot)
- rooms_count: `1`
  - room_id=1 check_in=2026-06-20 check_out=2026-06-28 guests=4

---

### Checkout #20

- stripe_session_id: `cs_live_a1DL0c5zsltqNl480DgIRNHWm7WgRHePpQFKCae0ju6Caeq36qF96qHfPy`
- created_at: `2026-01-07 02:01:42.090956+00:00`
- paid_at: `2026-01-07 02:02:52.574819+00:00`
- payment_mode: `plan`
- amount_total: `1500.00`
- currency: `usd`
- user: `victor.balderas` (vicvadar@gmail.com)
- event: `2026 NCS Caribbean World Series` (id=2)
- has_order: `False`
- players_count: `1`
  - players:
    - Jacob Balderas (player_id=35)

#### Breakdown
```json
{
  "players_total": "1500.00",
  "hotel_room_base": "0.00",
  "hotel_services_total": "0.00",
  "hotel_iva": "0.00",
  "hotel_ish": "0.00",
  "hotel_total": "0.00",
  "no_show_fee": "0.00",
  "subtotal": "1500.00",
  "discount_percent": 0,
  "total": "1500.00"
}
```

#### Hotel rooms (from hotel_cart_snapshot)
- rooms_count: `0`

---

### Checkout #18

- stripe_session_id: `cs_live_a1lXEJisMRtKWQOEoktBsRvZpD49verbGs6mrfNoFCPpCGxrQ4fXs5IoDd`
- created_at: `2026-01-06 07:17:32.327002+00:00`
- paid_at: `2026-01-06 07:18:07.011491+00:00`
- payment_mode: `plan`
- amount_total: `10.00`
- currency: `usd`
- user: `luis.tovar` (luistovar0316@gmail.com)
- event: `Test 2` (id=6)
- has_order: `False`
- players_count: `1`
  - players:
    - Test Test (player_id=36)

#### Breakdown
```json
{
  "players_total": "10.00",
  "hotel_room_base": "0.00",
  "hotel_services_total": "0.00",
  "hotel_iva": "0.00",
  "hotel_ish": "0.00",
  "hotel_total": "0.00",
  "no_show_fee": "0.00",
  "subtotal": "10.00",
  "discount_percent": 0,
  "total": "10.00"
}
```

#### Hotel rooms (from hotel_cart_snapshot)
- rooms_count: `0`

---

### Checkout #17

- stripe_session_id: `cs_live_a17Yo8l59fneF5HdzqcfSKqjCLiY7j6Vw7stvXKt9ewUIqFtnEwK3mxuRs`
- created_at: `2026-01-06 06:42:15.527010+00:00`
- paid_at: `2026-01-06 06:43:15.781036+00:00`
- payment_mode: `now`
- amount_total: `5.00`
- currency: `usd`
- user: `luis.tovar` (luistovar0316@gmail.com)
- event: `TEST` (id=5)
- has_order: `False`
- players_count: `1`
  - players:
    - Test Test2 (player_id=37)

#### Breakdown
```json
{
  "players_total": "5.00",
  "hotel_room_base": "0.00",
  "hotel_services_total": "0.00",
  "hotel_iva": "0.00",
  "hotel_ish": "0.00",
  "hotel_total": "0.00",
  "no_show_fee": "0.00",
  "subtotal": "5.00",
  "discount_percent": 0,
  "total": "5.00"
}
```

#### Hotel rooms (from hotel_cart_snapshot)
- rooms_count: `0`

---

### Checkout #16

- stripe_session_id: `cs_live_a1IkxC9Vy6w6tTAG5p7t4KtiS2eSgAvxSD7PMN7ZQjCFmmfGL8rtHNZZrw`
- created_at: `2026-01-06 06:00:26.759055+00:00`
- paid_at: `2026-01-06 06:01:02.632526+00:00`
- payment_mode: `now`
- amount_total: `5.00`
- currency: `usd`
- user: `luis.tovar` (luistovar0316@gmail.com)
- event: `TEST` (id=5)
- has_order: `False`
- players_count: `1`
  - players:
    - Test Test (player_id=36)

#### Breakdown
```json
{
  "players_total": "5.00",
  "hotel_room_base": "0.00",
  "hotel_services_total": "0.00",
  "hotel_iva": "0.00",
  "hotel_ish": "0.00",
  "hotel_total": "0.00",
  "no_show_fee": "0.00",
  "subtotal": "5.00",
  "discount_percent": 0,
  "total": "5.00"
}
```

#### Hotel rooms (from hotel_cart_snapshot)
- rooms_count: `0`

## Paid checkouts missing Order

missing_count = 6

- checkout_id=46 session=cs_live_a1mpr8pEUWLIKSZFHCp4qFipyrLf9QMPdoARdia3tZ4lZ1gy4kHGgtHJaN user=31 event=2 paid_at=2026-01-07 22:21:38.379594+00:00
- checkout_id=41 session=cs_live_a1ACdbtCSKjMahxwvhA9qkNcUeRUgAW5Du0513KkjNDrOEBb07yU6ihvTj user=44 event=1 paid_at=2026-01-07 20:03:39.627653+00:00
- checkout_id=20 session=cs_live_a1DL0c5zsltqNl480DgIRNHWm7WgRHePpQFKCae0ju6Caeq36qF96qHfPy user=38 event=2 paid_at=2026-01-07 02:02:52.574819+00:00
- checkout_id=18 session=cs_live_a1lXEJisMRtKWQOEoktBsRvZpD49verbGs6mrfNoFCPpCGxrQ4fXs5IoDd user=22 event=6 paid_at=2026-01-06 07:18:07.011491+00:00
- checkout_id=17 session=cs_live_a17Yo8l59fneF5HdzqcfSKqjCLiY7j6Vw7stvXKt9ewUIqFtnEwK3mxuRs user=22 event=5 paid_at=2026-01-06 06:43:15.781036+00:00
- checkout_id=16 session=cs_live_a1IkxC9Vy6w6tTAG5p7t4KtiS2eSgAvxSD7PMN7ZQjCFmmfGL8rtHNZZrw user=22 event=5 paid_at=2026-01-06 06:01:02.632526+00:00
