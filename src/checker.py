"""
Availability checker: navigate to DLP dining, run search, parse available slots.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout

from .config import Config
from .dlp_flow import (
    SELECTOR_AVAILABLE_SLOTS,
    SELECTOR_DATE_INPUT,
    SELECTOR_NO_AVAILABILITY,
    SELECTOR_PARTY_SIZE,
    SELECTOR_RESTAURANT_INPUT,
    SELECTOR_SEARCH_BUTTON,
    dining_url,
)


@dataclass
class AvailabilityResult:
    """Result of an availability check for one date."""

    date: str
    available_times: list[str]
    raw_text: str = ""


def _fill_restaurant(page: Page, restaurant: str) -> None:
    """Try to set restaurant by input, select, or search."""
    for sel in [
        'input[name*="restaurant"]',
        'select[name*="restaurant"]',
        '[data-testid="restaurant-select"]',
        'input[placeholder*="restaurant" i]',
    ]:
        try:
            loc = page.locator(sel).first
            if loc.count() > 0:
                loc.fill(restaurant)
                return
            loc.select_option(label=restaurant)
            return
        except Exception:
            continue
    # Fallback: type into first visible text input if we have a search
    try:
        page.get_by_placeholder(re.compile("restaurant|search", re.I)).first.fill(restaurant)
    except Exception:
        pass


def _fill_date(page: Page, date: str) -> None:
    """Set date in first date input found."""
    for sel in ['input[type="date"]', 'input[name*="date"]', '[data-testid="date-input"]']:
        try:
            loc = page.locator(sel).first
            if loc.count() > 0:
                loc.fill(date)
                return
        except Exception:
            continue


def _fill_party_size(page: Page, party_size: int) -> None:
    """Set party size."""
    for sel in [
        'input[name*="guest"]',
        'input[name*="party"]',
        'select[name*="guest"]',
        'select[name*="party"]',
    ]:
        try:
            loc = page.locator(sel).first
            if loc.count() > 0:
                loc.fill(str(party_size))
                return
            loc.select_option(value=str(party_size))
            return
        except Exception:
            continue


def _click_search(page: Page) -> None:
    """Click search / check availability button."""
    for sel in [
        'button[type="submit"]',
        'button:has-text("Search")',
        'button:has-text("Check availability")',
        'button:has-text("Rechercher")',
        '[data-testid="search-availability"]',
    ]:
        try:
            loc = page.locator(sel).first
            if loc.count() > 0 and loc.is_visible(timeout=2000):
                loc.click()
                return
        except Exception:
            continue


def _parse_available_times(page: Page) -> list[str]:
    """Extract list of available time strings from the results area."""
    times: list[str] = []
    # Try structured slots
    for sel in [
        SELECTOR_AVAILABLE_SLOTS,
        'button[class*="slot"]',
        'a[class*="slot"]',
        '[data-time]',
        '[data-testid="time-slot"]',
    ]:
        try:
            locs = page.locator(sel)
            n = locs.count()
            for i in range(n):
                node = locs.nth(i)
                text = node.inner_text(timeout=1000).strip()
                # Normalize time-like strings (e.g. "19:00", "7:00 PM")
                if re.search(r"\d{1,2}:\d{2}", text) or re.search(r"\d{1,2}\s*(?:am|pm)", text, re.I):
                    if text and text not in times:
                        times.append(text)
            if times:
                return times
        except Exception:
            continue
    # Fallback: any text that looks like a time in the main content
    try:
        body = page.locator("main, [role=main], .content, #content, body").first
        raw = body.inner_text(timeout=3000)
        for part in re.findall(r"\b(\d{1,2}:\d{2}(?:\s*[ap]m)?)\b", raw, re.I):
            if part not in times:
                times.append(part.strip())
    except Exception:
        pass
    return times


def _has_no_availability_message(page: Page) -> bool:
    """Return True if the page clearly says no availability."""
    try:
        for sel in [
            SELECTOR_NO_AVAILABILITY,
            ':text("No availability")',
            ':text("no tables")',
            ':text("Aucune disponibilité")',
        ]:
            if page.locator(sel).first.is_visible(timeout=500):
                return True
    except Exception:
        pass
    return False


def check_availability(page: Page, config: Config, date: str) -> AvailabilityResult:
    """
    Navigate to dining, fill form for the given date, submit, and return available times.
    Uses config for base_url, restaurant, party_size. time_start/time_end can be applied
    when parsing (filter times in range) in the caller if needed.
    """
    url = dining_url(config.base_url)
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_load_state("networkidle", timeout=15000)
    page.wait_for_timeout(2000)

    _fill_restaurant(page, config.restaurant)
    page.wait_for_timeout(500)
    _fill_date(page, date)
    _fill_party_size(page, config.party_size)
    page.wait_for_timeout(500)
    _click_search(page)

    page.wait_for_load_state("networkidle", timeout=20000)
    page.wait_for_timeout(3000)

    if _has_no_availability_message(page):
        return AvailabilityResult(date=date, available_times=[], raw_text="No availability")

    times = _parse_available_times(page)

    # Optional: filter by config.time_start / config.time_end (simple string compare or parse)
    if config.time_start or config.time_end:
        filtered = []
        for t in times:
            # Normalize to 24h for comparison if needed
            if _time_in_range(t, config.time_start, config.time_end):
                filtered.append(t)
        times = filtered

    return AvailabilityResult(date=date, available_times=times)


def _time_in_range(time_str: str, start: str | None, end: str | None) -> bool:
    """Return True if time_str is within [start, end]. Simple HH:MM comparison."""
    if not start and not end:
        return True
    # Parse HH:MM or H:MM
    m = re.search(r"(\d{1,2}):(\d{2})", time_str)
    if not m:
        return True
    h, mi = int(m.group(1)), int(m.group(2))
    t_minutes = h * 60 + mi
    if start:
        sm = re.search(r"(\d{1,2}):(\d{2})", start)
        if sm:
            start_min = int(sm.group(1)) * 60 + int(sm.group(2))
            if t_minutes < start_min:
                return False
    if end:
        em = re.search(r"(\d{1,2}):(\d{2})", end)
        if em:
            end_min = int(em.group(1)) * 60 + int(em.group(2))
            if t_minutes > end_min:
                return False
    return True


def check_availability_for_all_dates(page: Page, config: Config) -> list[AvailabilityResult]:
    """Run availability check for each date in config. Returns list of results."""
    results: list[AvailabilityResult] = []
    for date in config.dates:
        try:
            res = check_availability(page, config, date)
            results.append(res)
        except PlaywrightTimeout as e:
            results.append(AvailabilityResult(date=date, available_times=[], raw_text=str(e)))
        except Exception as e:
            results.append(AvailabilityResult(date=date, available_times=[], raw_text=str(e)))
    return results
