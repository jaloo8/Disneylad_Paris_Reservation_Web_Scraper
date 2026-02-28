"""
Notifications: console (always), optional email and Pushover.
"""
from __future__ import annotations

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from .config import Config


def notify_console(message: str, title: str | None = None) -> None:
    """Print to console. Title optional (e.g. for availability vs booking)."""
    if title:
        print(f"[{title}] {message}")
    else:
        print(message)


def notify_email(config: Config, subject: str, body: str) -> None:
    """Send email if configured and enabled."""
    email_cfg = config.notifications.email
    if not email_cfg.get("enabled"):
        return
    host = email_cfg.get("smtp_host")
    port = int(email_cfg.get("smtp_port") or 587)
    user = email_cfg.get("smtp_user")
    password = email_cfg.get("smtp_password")
    from_addr = email_cfg.get("from_addr") or user
    to_addr = email_cfg.get("to_addr") or user
    if not all([host, user, password, to_addr]):
        return
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP(host, port) as s:
            s.starttls()
            s.login(user, password)
            s.sendmail(from_addr, to_addr, msg.as_string())
    except Exception as e:
        notify_console(f"Email send failed: {e}", "Notifier")


def notify_pushover(config: Config, title: str, message: str) -> None:
    """Send Pushover notification if configured."""
    import urllib.request
    import urllib.parse

    push = config.notifications.pushover
    if not push.get("enabled"):
        return
    user_key = push.get("user_key")
    api_token = push.get("api_token")
    if not user_key or not api_token:
        return
    data = urllib.parse.urlencode({
        "token": api_token,
        "user": user_key,
        "title": title,
        "message": message,
    }).encode()
    try:
        req = urllib.request.Request("https://api.pushover.net/1/messages", data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            if r.status != 200:
                notify_console(f"Pushover returned {r.status}", "Notifier")
    except Exception as e:
        notify_console(f"Pushover failed: {e}", "Notifier")


def notify_availability_found(
    config: Config,
    date: str,
    times: list[str],
    restaurant: str,
) -> None:
    """Notify when availability is found (console + optional email/Pushover)."""
    msg = f"Availability at {restaurant} on {date}: {', '.join(times)}"
    notify_console(msg, "Availability")
    notify_email(
        config,
        subject=f"DLP: Table available – {restaurant} ({date})",
        body=msg,
    )
    notify_pushover(config, "DLP table available", msg)


def notify_booking_made(
    config: Config,
    restaurant: str,
    date: str,
    time_slot: str,
    confirmation_details: str,
) -> None:
    """Notify when a booking was completed."""
    msg = f"Booked {restaurant} on {date} at {time_slot}. {confirmation_details}"
    notify_console(msg, "Booking")
    notify_email(
        config,
        subject=f"DLP: Reservation confirmed – {restaurant}",
        body=msg,
    )
    notify_pushover(config, "DLP reservation confirmed", msg)


def notify_error(config: Config, context: str, error: str) -> None:
    """Notify on failure (e.g. login expired, selector broken)."""
    msg = f"DLP checker failed ({context}): {error}"
    notify_console(msg, "Error")
    # Optional: also send push/email so user knows to re-login
    notify_pushover(config, "DLP checker error", msg)
