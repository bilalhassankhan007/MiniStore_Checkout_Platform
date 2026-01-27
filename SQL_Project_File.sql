/* ============================================================
   Goal: Prove Webhook -> DB -> Order CREATED -> PAID -> Items
   ============================================================ */


/* ---- Webhook Proof: “What webhook events did we receive recently?”
   This shows the latest Stripe events stored by our webhook endpoint.
   You should see checkout.session.completed after stripe trigger / checkout.
*/
SELECT
  id, event_type, event_id, received_at
FROM public.store_stripeevent
ORDER BY received_at DESC
LIMIT 20;


/* ---- Orders Overview: “What are the latest orders and their payment state?”
   This confirms:
   - status is moving created -> paid
   - Stripe session/payment ids are getting saved on our Order record
*/
SELECT
  id, public_id, status, amount_total, currency,
  stripe_checkout_session_id, stripe_payment_intent_id,
  created_at, paid_at
FROM public.store_order
ORDER BY id DESC
LIMIT 20;


/* ---- Order Items (manual): “Show items for one specific order_id”
   Replace 123 with a real store_order.id from the query above.
   This proves what exactly was purchased and the quantity.
*/
SELECT
  oi.id, oi.order_id, oi.product_key, oi.name,
  oi.unit_amount, oi.quantity, oi.line_amount
FROM public.store_orderitem oi
WHERE oi.order_id = 123
ORDER BY oi.id;


/* ---- End-to-End Proof: “Latest orders with their items (join view)”
   This prints the order plus all items in one output.
   One order repeats multiple rows (one per item).
*/
SELECT
  o.public_id,
  o.status,
  o.amount_total,
  o.currency,
  o.created_at,
  o.paid_at,
  o.stripe_payment_intent_id,
  oi.name,
  oi.quantity,
  oi.line_amount
FROM public.store_order o
LEFT JOIN public.store_orderitem oi ON oi.order_id = o.id
ORDER BY o.id DESC, oi.id ASC
LIMIT 50;


/* ---- Admin / Staff Verification: “Confirm demo user permissions”
   This confirms bilal_admin has staff/superuser access for:
   - /admin/
   - staff-only debug pages (if you added them)
*/
SELECT
  id, username, is_staff, is_superuser, last_login
FROM public.auth_user
WHERE username = 'bilal_admin';


/* ---- Key Stripe Event Check: “Do we have checkout.session.completed events?”
   This is the most important event for marking orders PAID in our webhook.
   If this is missing, orders may stay in CREATED.
*/
SELECT
  event_type, received_at
FROM public.store_stripeevent
WHERE event_type = 'checkout.session.completed'
ORDER BY received_at DESC
LIMIT 10;


/* ---- Correlation Check: “Do latest orders have a Stripe session id?”
   Webhook matches orders using stripe_checkout_session_id (primary correlation).
   If NULL, webhook cannot find the order by session_id.
*/
SELECT
  public_id, status, stripe_checkout_session_id
FROM public.store_order
ORDER BY id DESC
LIMIT 10;


/* ---- Quick Metrics: “How many Stripe events are stored?”
   This confirms webhook traffic is landing in DB.
*/
SELECT
  count(*) AS stripe_events
FROM public.store_stripeevent;


/* ---- Quick Metrics: “How many orders are PAID?”
   This confirms how many orders successfully moved to PAID state.
*/
SELECT
  count(*) AS paid_orders
FROM public.store_order
WHERE status = 'paid';


/* ---- Latest Paid Proof: “Show most recent paid order”
   This is the cleanest “success proof” line:
   - paid_at is not null
   - stripe_payment_intent_id exists
*/
SELECT
  public_id, paid_at, stripe_payment_intent_id
FROM public.store_order
WHERE status = 'paid'
ORDER BY paid_at DESC
LIMIT 1;
