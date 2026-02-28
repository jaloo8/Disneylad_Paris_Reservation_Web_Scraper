# Disneyland Paris Restaurant Availability Checker & Auto-Booker

A self-hosted tool that checks Disneyland Paris restaurant availability for your chosen date(s), time range, and party size—and optionally **automatically books** when a slot is found. Uses browser automation and a saved login so you don’t have to keep logging in or clicking through the site.

**Disclaimer:** This project is unofficial and not affiliated with Disneyland Paris or The Walt Disney Company. Use at your own risk. Respect the site’s terms of use and rate limits.

## Features

- **Check availability** for one or more dates, with optional time window and party size
- **Alert-only mode:** notify you (console + optional email/Pushover) when a table is available
- **Auto-book mode:** complete the reservation when a slot is found (optional dry run)
- **Saved session:** log in once; subsequent runs reuse cookies so you don’t re-enter credentials
- **Monitor mode:** keep checking every N minutes until availability is found
- **Web UI:** configure and run everything from your browser (no command line required for daily use)

## Requirements

- Python 3.10+
- Chromium (installed via Playwright)

## Setup

1. **Clone and install dependencies**

   ```bash
   cd Disneylad_Paris_Reservation_Web_Scraper
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Config**

   Copy the example config and edit it:

   ```bash
   cp config.example.yaml config.yaml
   ```

   Set at least:

   - `restaurant` – name (or ID) of the restaurant
   - `dates` – list of dates in `YYYY-MM-DD`
   - Optionally `time_start` / `time_end`, `party_size`, `auto_book`, `dry_run`, and notification settings (see `config.example.yaml`).

3. **First-time login**

   In the Web UI, click **Login and save session**; or run `python run.py --login-only --show-browser`. A browser will open—log in to Disneyland Paris when prompted. The session is saved so you don’t have to log in again (until it expires).

### Web UI (recommended)

Run the app in your browser so you can set options and run checks without using the command line:

```bash
streamlit run app.py
```

Your browser will open to the app. There you can:

- **Set options** in the form (restaurant, date, party size, time window, auto-book, dry run) and click **Save configuration**.
- Click **Login and save session** once to log in to Disneyland Paris in a pop-up browser; the session is saved for future runs.
- Click **Check availability once** to run a single check and see the result in the page.
- For continuous monitoring, the app shows the command to run in a terminal (`python run.py --monitor`).

No need to edit YAML for basic use—everything can be done from the UI.

## Usage (command line)

- **Single check (headless):**

  ```bash
  python run.py
  ```

- **Single check with browser visible (debugging):**

  ```bash
  python run.py --show-browser
  ```

- **Monitor mode** – keep checking every `poll_interval_minutes` until availability is found:

  ```bash
  python run.py --monitor
  ```

- **Login only** (e.g. after session expired):

  ```bash
  python run.py --login-only --show-browser
  ```

- **Custom config path:**

  ```bash
  python run.py --config path/to/config.yaml
  ```

You can also run the package as a module:

```bash
python -m src
python -m src --monitor --show-browser
```

## Scheduling (cron)

To run a check on a schedule (e.g. every 15 minutes) instead of using `--monitor`:

```bash
# Edit crontab
crontab -e

# Example: every 15 minutes
*/15 * * * * cd /path/to/Disneylad_Paris_Reservation_Web_Scraper && python run.py
```

Use a reasonable interval (e.g. 5–15 minutes) to avoid hammering the site. The config options `poll_interval_minutes` and `poll_jitter_seconds` apply when using `--monitor`; cron runs are independent of those.

## Configuration reference

| Option | Description |
|--------|-------------|
| `base_url` | Disneyland Paris base URL (default: en-gb). |
| `restaurant` | Restaurant name or ID. |
| `dates` | List of dates (`YYYY-MM-DD`). |
| `time_start` / `time_end` | Optional 24h time window (e.g. `"18:00"`, `"21:00"`). |
| `party_size` | Number of guests. |
| `auto_book` | If `true`, book the first available slot when found. |
| `dry_run` | If `true`, never click confirm (only check and notify). |
| `poll_interval_minutes` | Used in `--monitor` (default: 10). |
| `poll_jitter_seconds` | Jitter added to interval (default: 60). |
| `notifications` | Optional `email` and/or `pushover` (see `config.example.yaml`). |

Secrets (e.g. `smtp_password`, Pushover `api_token`) can be set via environment variables: `NOTIFY_SMTP_PASSWORD`, `NOTIFY_PUSHOVER_TOKEN`.

## If the site changes

Disneyland Paris may change URLs or page structure. The code uses a small set of selectors and URLs in `src/dlp_flow.py`. If checks or booking stop working:

1. Open the Disneyland Paris dining page in a browser and note the exact URLs and button/input selectors.
2. Update `src/dlp_flow.py` (and optionally `docs/DISCOVERY.md`) with the new paths and selectors.

See `docs/DISCOVERY.md` for what to document when testing manually.

## Project layout

- `app.py` – **Web UI** (`streamlit run app.py`)
- `run.py` – CLI entrypoint (`python run.py`)
- `config.example.yaml` – example config
- `src/` – main code
  - `config.py` – load config
  - `session.py` – browser session and login
  - `dlp_flow.py` – URLs and selectors for DLP
  - `checker.py` – availability check
  - `booker.py` – auto-book a slot
  - `notifier.py` – console, email, Pushover
  - `runner.py` – CLI and run loop
- `docs/DISCOVERY.md` – notes for updating selectors/URLs
