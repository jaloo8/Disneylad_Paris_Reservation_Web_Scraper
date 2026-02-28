"""
Auto-booker: when a slot is available, click it and complete the reservation flow.
"""
from __future__ import annotations

from dataclasses import dataclass

from playwright.sync_api import Page

from .config import Config
from .dlp_flow import SELECTOR_CONFIRM_BUTTON, SELECTOR_AVAILABLE_SLOTS


@dataclass
class BookingResult:
    """Result of an attempt to book."""

    success: bool
    message: str
    confirmation_details: str = ""


def book_slot(
    page: Page,
    config: Config,
    time_slot: str,
    date: str,
) -> BookingResult:
    """
    Click the given time slot and proceed to confirm. If dry_run is True, do not click confirm.
    Returns BookingResult with success and any confirmation details captured.
    """
    if config.dry_run:
        return BookingResult(
            success=False,
            message=f"Dry run: would book {time_slot} on {date} (confirm not clicked)",
        )

    # Find and click the slot that matches time_slot text
    for sel in [
        SELECTOR_AVAILABLE_SLOTS,
        'button[class*="slot"]',
        'a[class*="slot"]',
        '[data-time]',
        '[data-testid="time-slot"]',
    ]:
        try:
            locs = page.locator(sel)
            for i in range(locs.count()):
                node = locs.nth(i)
                if time_slot in node.inner_text(timeout=1000):
                    node.click()
                    break
            else:
                continue
            break
        except Exception:
            continue
    else:
        return BookingResult(success=False, message=f"Could not find slot button for {time_slot}")

    page.wait_for_load_state("networkidle", timeout=15000)
    page.wait_for_timeout(2000)

    # Click Confirm / Book
    for sel in [
        SELECTOR_CONFIRM_BUTTON,
        'button:has-text("Confirm")',
        'button:has-text("Book")',
        'button:has-text("Confirmer")',
        '[data-testid="confirm-booking"]',
    ]:
        try:
            btn = page.locator(sel).first
            if btn.count() > 0 and btn.is_visible(timeout=3000):
                btn.click()
                break
        except Exception:
            continue
    else:
        return BookingResult(
            success=False,
            message="Clicked slot but could not find Confirm/Book button. Site may have changed.",
        )

    page.wait_for_load_state("networkidle", timeout=15000)
    page.wait_for_timeout(3000)

    # Try to capture confirmation message or reference
    confirmation = ""
    try:
        for sel in [
            '[class*="confirmation"]',
            ':text("confirmed")',
            ':text("Confirmation")',
            '[data-testid="confirmation"]',
        ]:
            el = page.locator(sel).first
            if el.count() > 0:
                confirmation = el.inner_text(timeout=1000).strip()[:500]
                break
    except Exception:
        pass

    return BookingResult(
        success=True,
        message=f"Booked {time_slot} on {date}",
        confirmation_details=confirmation or "Check My Bookings on the site.",
    )
