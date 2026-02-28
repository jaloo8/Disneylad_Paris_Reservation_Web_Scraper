"""
Main runner: load session, check availability, optionally book, notify.
"""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

from .config import Config
from .session import get_browser_context, save_storage_state, ensure_logged_in
from .checker import check_availability, check_availability_for_all_dates
from .booker import book_slot
from .notifier import (
    notify_availability_found,
    notify_booking_made,
    notify_console,
    notify_error,
)


def run_once(config: Config, headless: bool = True) -> bool:
    """
    Run one cycle: check availability for all configured dates.
    If any slot is found and auto_book is True, book the first slot and notify.
    Returns True if we booked (or would have in dry run), False otherwise.
    """
    pw = None
    browser = None
    try:
        pw, browser, context = get_browser_context(config, headless=headless)
        page = context.new_page()

        ensure_logged_in(page, config)
        save_storage_state(context, config)

        results = check_availability_for_all_dates(page, config)

        for result in results:
            if result.available_times:
                notify_availability_found(
                    config,
                    result.date,
                    result.available_times,
                    config.restaurant,
                )
                if config.auto_book and result.available_times:
                    first_slot = result.available_times[0]
                    # Re-run search for this date so the page shows the slot buttons
                    check_availability(page, config, result.date)
                    book_result = book_slot(page, config, first_slot, result.date)
                    if book_result.success:
                        notify_booking_made(
                            config,
                            config.restaurant,
                            result.date,
                            first_slot,
                            book_result.confirmation_details,
                        )
                        return True
                    else:
                        notify_console(book_result.message, "Booker")
                else:
                    return True  # found availability, alerted
            else:
                notify_console(f"No availability for {result.date}" + (f": {result.raw_text}" if result.raw_text else ""), "Check")

        return False
    except Exception as e:
        notify_error(config, "run_once", str(e))
        raise
    finally:
        if browser:
            browser.close()
        if pw:
            pw.stop()


def run_login_only(config: Config, headless: bool = False) -> None:
    """Open browser, go to login, wait for user to log in, save session."""
    pw = None
    browser = None
    try:
        pw, browser, context = get_browser_context(config, headless=headless)
        page = context.new_page()
        ensure_logged_in(page, config)
        save_storage_state(context, config)
        notify_console("Session saved. You can close the browser and run the checker.", "Login")
    finally:
        if browser:
            browser.close()
        if pw:
            pw.stop()


def run_monitor(config: Config, headless: bool = True) -> None:
    """Loop: check every poll_interval_minutes (with jitter) until a slot is found and handled."""
    interval_sec = config.poll_interval_minutes * 60
    jitter = config.poll_jitter_seconds
    attempt = 0
    while True:
        attempt += 1
        notify_console(f"Check attempt {attempt}", "Monitor")
        try:
            if run_once(config, headless=headless):
                notify_console("Availability found and handled. Exiting monitor.", "Monitor")
                return
        except Exception:
            pass
        delay = interval_sec + random.randint(-jitter, jitter)
        delay = max(60, delay)
        notify_console(f"Next check in {delay // 60} minutes.", "Monitor")
        import time
        time.sleep(delay)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Disneyland Paris Restaurant Availability Checker & Auto-Booker",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config.yaml"),
        help="Path to config.yaml",
    )
    parser.add_argument(
        "--show-browser",
        action="store_true",
        help="Show browser window (default: headless)",
    )
    parser.add_argument(
        "--login-only",
        action="store_true",
        help="Only log in and save session, then exit",
    )
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Keep checking every poll_interval_minutes until availability found",
    )
    args = parser.parse_args()

    try:
        config = Config.load(args.config)
        config.validate()
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        return 1
    except ValueError as e:
        print(e, file=sys.stderr)
        return 1

    headless = not args.show_browser

    if args.login_only:
        run_login_only(config, headless=headless)
        return 0

    if args.monitor:
        run_monitor(config, headless=headless)
        return 0

    run_once(config, headless=headless)
    return 0


if __name__ == "__main__":
    sys.exit(main())
