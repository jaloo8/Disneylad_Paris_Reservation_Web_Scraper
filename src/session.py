"""Browser session handling: load/save storage state for persistent login."""
from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from .config import Config


def get_browser_context(
    config: Config,
    headless: bool = True,
    storage_state_path: Path | None = None,
) -> tuple[sync_playwright, Browser, BrowserContext]:
    """
    Create a Playwright browser and context, reusing saved storage state if present.
    Returns (playwright_instance, browser, context). Caller must close browser and playwright.
    """
    path = storage_state_path or config.storage_state_path
    path = Path(path)
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=headless)
    context_options: dict = {
        "viewport": {"width": 1280, "height": 720},
        "user_agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
    }
    if path.exists():
        context_options["storage_state"] = str(path)
    context = browser.new_context(**context_options)
    return pw, browser, context


def save_storage_state(context: BrowserContext, config: Config) -> None:
    """Persist cookies/localStorage so the next run can skip login."""
    path = Path(config.storage_state_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    context.storage_state(path=str(path))


def ensure_logged_in(
    page: Page,
    config: Config,
    context: BrowserContext,
    login_url_path: str = "/en-gb/account/sign-in/",
) -> bool:
    """
    Navigate to the site and ensure user is logged in. If not, open login page and wait.
    Returns True if already logged in or after user has logged in; caller can then save state.
    """
    base = config.base_url
    page.goto(base, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2000)

    # Heuristic: check for common "sign in" or "my account" links.
    # Disneyland Paris may use "Sign in" / "My account" etc. Adjust selectors after discovery.
    sign_in_selectors = [
        'a[href*="sign-in"]',
        'a[href*="login"]',
        'button:has-text("Sign in")',
        'a:has-text("Sign in")',
        '[data-testid="sign-in"]',
    ]
    for sel in sign_in_selectors:
        try:
            el = page.locator(sel).first
            if el.is_visible(timeout=1000):
                # Might be logged out; go to login and wait for user
                login_url = base.rstrip("/") + "/" + login_url_path.lstrip("/")
                page.goto(login_url, wait_until="domcontentloaded", timeout=30000)
                print("Please log in manually in the browser. Waiting 120 seconds...")
                page.wait_for_timeout(120_000)
                return True
        except Exception:
            continue

    # Assume logged in if we didn't find a sign-in link
    return True
