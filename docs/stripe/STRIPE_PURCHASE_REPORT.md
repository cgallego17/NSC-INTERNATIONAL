# Stripe Purchase Report (Paid Checkouts)

Este documento contiene comandos para:
- Listar compras **pagadas** (`StripeEventCheckout.status = 'paid'`)
- Ver **qué compraron** (evento, jugadores incluidos, hotel/habitaciones, desglose de cobros)
- Validar por qué el módulo **Orders Management** está vacío (cuando existen pagos `paid` pero no se han creado `Order`)

> Nota: Estos comandos consultan la BD local del proyecto (lo que tenga configurado el `DJANGO_SETTINGS_MODULE` actual).

---

## 1) Listar todos los checkouts pagados

### Windows (PowerShell)
```powershell
python manage.py shell -c "from apps.accounts.models import StripeEventCheckout; qs=StripeEventCheckout.objects.filter(status='paid').order_by('-created_at'); print('paid_checkouts=', qs.count()); [print(c.id, c.status, c.stripe_session_id, c.payment_mode, c.amount_total, c.user_id, c.event_id, c.paid_at) for c in qs]"
```

### Linux/Mac (bash)
```bash
python manage.py shell <<'PY'
from apps.accounts.models import StripeEventCheckout
qs = StripeEventCheckout.objects.filter(status='paid').order_by('-created_at')
print('paid_checkouts=', qs.count())
for c in qs:
    print(c.id, c.status, c.stripe_session_id, c.payment_mode, c.amount_total, c.user_id, c.event_id, c.paid_at)
PY
```

---

## 2) Reporte detallado: ¿Qué compró cada checkout pagado?

Este reporte imprime:
- Checkout + Stripe session
- Evento
- Usuario
- Modo de pago y total
- Jugadores incluidos (`player_ids` -> `Player`)
- Desglose (`breakdown`)
- Habitaciones/hotel (desde `hotel_cart_snapshot`)

### Windows (PowerShell)
```powershell
python manage.py shell -c "from apps.accounts.models import StripeEventCheckout, Player; qs=StripeEventCheckout.objects.filter(status='paid').select_related('user','event').order_by('-created_at'); print('paid_checkouts=', qs.count());
for c in qs:
    print(''); print('====================');
    print('checkout_id=', c.id, 'session=', c.stripe_session_id);
    print('event=', getattr(c.event,'title',c.event_id), 'event_id=', c.event_id);
    print('user=', c.user.username, c.user.email);
    print('payment_mode=', c.payment_mode, 'amount_total=', c.amount_total, 'currency=', c.currency);
    players = list(Player.objects.filter(id__in=(c.player_ids or [])).select_related('user'));
    print('players=', [ (p.user.get_full_name() or p.user.username) for p in players ]);
    bd = c.breakdown or {};
    print('breakdown.players_total=', bd.get('players_total'), 'hotel_total=', bd.get('hotel_total'), 'hotel_buy_out_fee=', bd.get('hotel_buy_out_fee'), 'service_fee_amount=', bd.get('service_fee_amount'), 'discount_percent=', bd.get('discount_percent'), 'total=', bd.get('total'));
    cart = c.hotel_cart_snapshot or {};
    rooms = [v for v in cart.values() if isinstance(v, dict) and v.get('type')=='room'];
    print('rooms_count=', len(rooms));
    for r in sorted(rooms, key=lambda x: x.get('room_order', 999999)):
        print('  room_id=', r.get('room_id'), 'check_in=', r.get('check_in'), 'check_out=', r.get('check_out'), 'guests=', r.get('guests'), 'additional_guest_names=', r.get('additional_guest_names'))"
```

### Linux/Mac (bash)
```bash
python manage.py shell <<'PY'
from apps.accounts.models import StripeEventCheckout, Player

qs = StripeEventCheckout.objects.filter(status='paid').select_related('user','event').order_by('-created_at')
print('paid_checkouts=', qs.count())

for c in qs:
    print('\n====================')
    print('checkout_id=', c.id, 'session=', c.stripe_session_id)
    print('event=', getattr(c.event,'title',c.event_id), 'event_id=', c.event_id)
    print('user=', c.user.username, c.user.email)
    print('payment_mode=', c.payment_mode, 'amount_total=', c.amount_total, 'currency=', c.currency)

    players = list(Player.objects.filter(id__in=(c.player_ids or [])).select_related('user'))
    print('players=', [ (p.user.get_full_name() or p.user.username) for p in players ])

    bd = c.breakdown or {}
    print(
        'breakdown.players_total=', bd.get('players_total'),
        'hotel_total=', bd.get('hotel_total'),
        'hotel_buy_out_fee=', bd.get('hotel_buy_out_fee'),
        'service_fee_amount=', bd.get('service_fee_amount'),
        'discount_percent=', bd.get('discount_percent'),
        'total=', bd.get('total'),
    )

    cart = c.hotel_cart_snapshot or {}
    rooms = [v for v in cart.values() if isinstance(v, dict) and v.get('type')=='room']
    print('rooms_count=', len(rooms))
    for r in sorted(rooms, key=lambda x: x.get('room_order', 999999)):
        print('  room_id=', r.get('room_id'), 'check_in=', r.get('check_in'), 'check_out=', r.get('check_out'), 'guests=', r.get('guests'), 'additional_guest_names=', r.get('additional_guest_names'))
PY
```

---

## 3) Validación: ¿existen `Order` para los checkouts pagados?

Si este reporte dice que hay `paid` pero `Order.count=0`, entonces el panel “Orders Management” no tendrá nada que mostrar.

### Windows (PowerShell)
```powershell
python manage.py shell -c "from apps.accounts.models import StripeEventCheckout, Order; qs=StripeEventCheckout.objects.filter(status='paid').order_by('-created_at'); print('paid_checkouts=', qs.count()); missing=[];
for c in qs:
    has_order = Order.objects.filter(stripe_checkout=c).exists();
    if not has_order: missing.append(c.id);
    print(c.id, c.stripe_session_id, 'has_order='+str(has_order));
print('paid_without_order=', len(missing)); print('missing_ids=', missing)"
```

---

## 4) (Opcional) Backfill: crear `Order` desde checkouts pagados

> Ejecuta primero el DRY RUN para validar.

### DRY RUN
```bash
python manage.py shell -c "from apps.accounts.models import StripeEventCheckout, Order; qs=StripeEventCheckout.objects.filter(status='paid').order_by('-created_at'); to_create=[c for c in qs if not Order.objects.filter(stripe_checkout=c).exists()]; print('will_create_orders_for=', len(to_create)); [print(c.id, c.stripe_session_id, c.user_id, c.event_id, c.paid_at) for c in to_create]"
```

### Ejecutar creación de órdenes
```bash
python manage.py shell -c "from apps.accounts.models import StripeEventCheckout, Order; from apps.accounts.views_private import _create_order_from_stripe_checkout; qs=StripeEventCheckout.objects.filter(status='paid').order_by('-created_at'); created=0;
for c in qs:
    if Order.objects.filter(stripe_checkout=c).exists():
        continue
    o=_create_order_from_stripe_checkout(c)
    created += 1
    print('CREATED', o.id, o.order_number, 'from checkout', c.id, c.stripe_session_id)
print('TOTAL_CREATED=', created); print('Order.count=', Order.objects.count())"
```
