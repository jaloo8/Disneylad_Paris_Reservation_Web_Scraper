# Disneyland Paris Booking Flow (Discovery)

This doc describes the URLs and UI/API flow for restaurant reservations so selectors can be updated if the site changes.

## URL flow (to be confirmed on first run)

- **Base:** `https://www.disneylandparis.com/en-gb`
- **Login:** Often under `/account/sign-in/` or linked from the main site. Log in before searching.
- **Dining / Restaurants:** The site may expose dining under paths like:
  - `/dining/` (listing)
  - `/dining/restaurants/` or per-restaurant pages
- **Check availability:** After selecting a restaurant, date, time range, and party size, the site shows available slots or "no availability". This may be a form submit or an in-page API call.
- **Book:** Clicking a time slot typically leads to a confirmation step; then "Confirm" completes the reservation.

## What to note when testing manually

1. Exact URL when you land on "restaurant reservations" or "book a table".
2. How you pick the restaurant (dropdown, search, list with links).
3. Form fields: date picker, time (or meal period), party size.
4. After submitting: where does "no availability" vs list of times appear (selector or API response)?
5. After clicking a time: what is the confirm button selector and any modal/captcha?

## API interception (optional)

If the site uses internal APIs (e.g. XHR/fetch) for availability, we can use Playwright's `page.route()` or `page.on("response")` to capture JSON and avoid brittle DOM parsing. Update `src/dlp_flow.py` to use intercepted responses when you have the request URL and response shape.
