"""
Disneyland Paris Reservation Checker — Web UI (Streamlit).
Run with: streamlit run app.py
"""
from __future__ import annotations

import io
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st
import yaml

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import Config
from src.restaurants import (
    RESTAURANT_OPTIONS,
    display_to_name,
    name_to_display,
)

CONFIG_PATH = Path("config.yaml")
EXAMPLE_CONFIG_PATH = Path("config.example.yaml")
OTHER_LABEL = "— Other (type name below) —"
RESTAURANT_CHOICES = RESTAURANT_OPTIONS + [OTHER_LABEL]


def load_config_dict() -> dict | None:
    """Load existing config as dict for form prefill, or None if missing."""
    if not CONFIG_PATH.exists():
        return None
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_config_dict(data: dict) -> None:
    """Write config dict to config.yaml."""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True)


def run_with_captured_stdout(run_fn):
    """Run a function with stdout captured; return (success, output_text)."""
    buf = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = buf
    try:
        run_fn()
        return True, buf.getvalue()
    except Exception as e:
        sys.stdout = old_stdout
        return False, buf.getvalue() + f"\nError: {e}"
    finally:
        sys.stdout = old_stdout


def main():
    st.set_page_config(
        page_title="Disneyland Paris Reservations",
        page_icon="🏰",
        layout="centered",
    )

    st.title("🏰 Disneyland Paris Restaurant Checker")
    st.caption(
        "Check availability and optionally auto-book. Configure below, then use the actions."
    )

    existing = load_config_dict() or {}

    with st.form("config_form"):
        st.subheader("Configuration")
        saved_restaurant = existing.get("restaurant", "")
        default_choice = name_to_display(saved_restaurant) if saved_restaurant else RESTAURANT_CHOICES[0]
        if default_choice not in RESTAURANT_CHOICES:
            default_choice = OTHER_LABEL
        restaurant_choice = st.selectbox(
            "Restaurant",
            options=RESTAURANT_CHOICES,
            index=RESTAURANT_CHOICES.index(default_choice) if default_choice in RESTAURANT_CHOICES else RESTAURANT_CHOICES.index(OTHER_LABEL),
            help="Select a table-service restaurant. Names match the official Disneyland Paris site.",
        )
        custom_restaurant = st.text_input(
            "Custom restaurant name (only if you chose \"Other\" above)",
            value=saved_restaurant if (not name_to_display(saved_restaurant) and saved_restaurant) else "",
            placeholder="e.g. exact name from the website",
            help="Leave blank unless you selected Other.",
        )
        if restaurant_choice == OTHER_LABEL:
            restaurant = (custom_restaurant or "").strip()
        else:
            restaurant = display_to_name(restaurant_choice)
        col1, col2 = st.columns(2)
        with col1:
            party_size = st.number_input(
                "Party size",
                min_value=1,
                max_value=20,
                value=existing.get("party_size", 2),
            )
        with col2:
            poll_minutes = st.number_input(
                "Check interval (minutes) when monitoring",
                min_value=5,
                max_value=60,
                value=existing.get("poll_interval_minutes", 10),
            )
        dates_existing = existing.get("dates") or []
        first_date = None
        if dates_existing:
            try:
                first_date = datetime.strptime(dates_existing[0], "%Y-%m-%d").date()
            except (ValueError, TypeError):
                pass
        primary_date = st.date_input(
            "Date to check",
            value=first_date,
            help="Primary date for availability.",
        )
        extra_dates_str = st.text_input(
            "Extra dates (optional)",
            value=", ".join(dates_existing[1:]) if len(dates_existing) > 1 else "",
            placeholder="YYYY-MM-DD, YYYY-MM-DD",
            help="Comma-separated list of additional dates.",
        )
        time_start = st.text_input(
            "Time window start (optional)",
            value=existing.get("time_start") or "",
            placeholder="18:00",
            help="24-hour format. Leave empty for any time.",
        )
        time_end = st.text_input(
            "Time window end (optional)",
            value=existing.get("time_end") or "",
            placeholder="21:00",
        )
        auto_book = st.checkbox(
            "Auto-book when a slot is found",
            value=existing.get("auto_book", False),
            help="If unchecked, you will only be notified.",
        )
        dry_run = st.checkbox(
            "Dry run (never click Confirm)",
            value=existing.get("dry_run", False),
            help="Use when testing: check and notify but do not complete booking.",
        )
        show_browser = st.checkbox(
            "Show browser window when checking",
            value=False,
            help="Useful for debugging; leave unchecked for background checks.",
        )
        submitted = st.form_submit_button("Save configuration")

    if submitted:
        dates = []
        if primary_date:
            dates.append(primary_date.isoformat())
        for part in (extra_dates_str or "").replace(" ", "").split(","):
            part = part.strip()
            if part:
                dates.append(part)
        if not dates:
            dates = existing.get("dates", ["2026-03-15"])
        data = {
            "base_url": existing.get("base_url", "https://www.disneylandparis.com/en-gb"),
            "restaurant": restaurant,
            "dates": dates,
            "time_start": time_start.strip() or None,
            "time_end": time_end.strip() or None,
            "party_size": party_size,
            "auto_book": auto_book,
            "dry_run": dry_run,
            "poll_interval_minutes": poll_minutes,
            "poll_jitter_seconds": existing.get("poll_jitter_seconds", 60),
            "notifications": existing.get("notifications") or {},
        }
        save_config_dict(data)
        st.success("Configuration saved to config.yaml.")

    st.divider()
    st.subheader("Actions")

    if not CONFIG_PATH.exists():
        st.warning(
            "Save your configuration first (fill the form and click **Save configuration**). "
            "You can also copy `config.example.yaml` to `config.yaml` and edit it."
        )
    else:
        try:
            config = Config.load(CONFIG_PATH)
            config.validate()
        except FileNotFoundError:
            st.error("Config file not found.")
        except ValueError as e:
            st.error(f"Invalid config: {e}")
        else:
            col_login, col_check, col_monitor = st.columns(3)
            with col_login:
                if st.button("🔐 Login and save session", use_container_width=True):
                    st.info("Opening browser — please log in to Disneyland Paris when prompted. This may take up to 2 minutes.")
                    with st.spinner("Waiting for you to log in…"):
                        from src.runner import run_login_only
                        ok, out = run_with_captured_stdout(
                            lambda: run_login_only(config, headless=not show_browser)
                        )
                    if out.strip():
                        st.text_area("Login output", value=out, height=80, disabled=True, key="login_out")
                    st.success("Session saved. You can now run checks without logging in again.")

            with col_check:
                if st.button("🔍 Check availability once", use_container_width=True):
                    with st.spinner("Checking availability…"):
                        from src.runner import run_once
                        ok, out = run_with_captured_stdout(
                            lambda: run_once(config, headless=not show_browser)
                        )
                    st.text_area("Result", value=out or "(no output)", height=200, disabled=True)
                    if ok:
                        st.success("Check finished.")
                    else:
                        st.error("Check failed. See output above.")

            with col_monitor:
                st.caption("Continuous monitoring (runs in terminal)")
            st.info(
                "To keep checking every few minutes until a slot is found, run this in a terminal from the project folder:"
            )
            st.code("python run.py --monitor", language="bash")

    st.divider()
    with st.expander("About"):
        st.markdown(
            """
            - **First time:** Click **Login and save session**, log in when the browser opens, then use **Check availability once** or the command line to monitor.
            - **Auto-book** is optional; when off, you only get notified when a table is available.
            - This tool is **unofficial** and not affiliated with Disneyland Paris. Use at your own risk.
            """
        )


if __name__ == "__main__":
    main()
