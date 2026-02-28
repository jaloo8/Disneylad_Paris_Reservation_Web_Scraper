"""
Disneyland Paris reservation flow: URLs and selectors.

Update these after first run when you have the real site structure.
See docs/DISCOVERY.md for what to note.
"""
from __future__ import annotations

# Base paths (relative to config.base_url)
PATH_DINING = "/dining/"
PATH_SIGN_IN = "/account/sign-in/"

# Selectors for availability search form (adjust after discovery)
SELECTOR_RESTAURANT_INPUT = 'input[name*="restaurant"], select[name*="restaurant"], [data-testid="restaurant-select"]'
SELECTOR_DATE_INPUT = 'input[name*="date"], input[type="date"], [data-testid="date-input"]'
SELECTOR_TIME_START = 'input[name*="time"], select[name*="time"]'
SELECTOR_PARTY_SIZE = 'input[name*="guest"], select[name*="guest"], input[name*="party"]'
SELECTOR_SEARCH_BUTTON = 'button[type="submit"], button:has-text("Search"), button:has-text("Check availability"), [data-testid="search-availability"]'

# Selectors for results
SELECTOR_NO_AVAILABILITY = '[class*="no-avail"], :text("No availability"), :text("no tables")'
SELECTOR_AVAILABLE_SLOTS = '[data-testid="time-slot"], button[class*="slot"], a[class*="slot"], .availability-slot'
SELECTOR_SLOT_TIME = ".time, [data-time]"

# Selectors for booking confirmation
SELECTOR_CONFIRM_BUTTON = 'button:has-text("Confirm"), button:has-text("Book"), [data-testid="confirm-booking"]'
SELECTOR_CONFIRMATION_MESSAGE = '[class*="confirmation"], :text("confirmed"), :text("Confirmation")'


def dining_url(base_url: str) -> str:
    return base_url.rstrip("/") + PATH_DINING


def sign_in_url(base_url: str) -> str:
    return base_url.rstrip("/") + PATH_SIGN_IN
