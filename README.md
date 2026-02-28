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

### How to use the GUI

The web interface lets you configure and run checks without using the command line.

**1. Start the app**

From the project folder, run:

```bash
streamlit run app.py
```

Your default browser will open to the app (usually at `http://localhost:8501`). Keep this tab open while you use the app.

**2. Configure your search**

In the **Configuration** form, fill in:

- **Restaurant name** – The exact name as on the Disneyland Paris site (e.g. *Auberge de Cendrillon*).
- **Party size** – Number of guests (1–20).
- **Date to check** – Use the date picker for your main date.
- **Extra dates** (optional) – Add more dates as a comma-separated list (e.g. `2026-03-16, 2026-03-17`).
- **Time window** (optional) – Leave blank to see any time, or set e.g. **Time window start** `18:00` and **Time window end** `21:00` for dinner only.
- **Check interval** – Only used when you run continuous monitoring; how often to re-check (in minutes).
- **Auto-book when a slot is found** – If checked, the tool will complete the reservation automatically when it finds a table. If unchecked, it only notifies you.
- **Dry run** – If checked, it will never click “Confirm” (useful to test that availability is detected without actually booking).
- **Show browser when checking** – If checked, a browser window will be visible when you run a check (handy for debugging).

Click **Save configuration** to write these settings to `config.yaml`. You only need to change the form when you want to update your options.

**3. Log in (first time only)**

Click **🔐 Login and save session**.

A separate browser window will open to Disneyland Paris. Log in there with your Disney account when prompted. The app will wait up to 2 minutes. Once you’re logged in, the app saves your session and you can close that browser window. Future checks will reuse this session so you don’t have to log in again (until the session expires—then repeat this step).

**4. Check availability**

Click **🔍 Check availability once**.

The app will run a single check in the background (or in a visible browser if you turned on “Show browser when checking”). When it finishes, the **Result** box will show whether any times were found for your dates. If you have notifications set up (e.g. email or Pushover), you’ll get an alert when a table is available.

**5. Continuous monitoring**

The GUI runs one check per button click. To keep checking every few minutes until a slot appears, use the command line. The app shows the exact command in the **Actions** section:

```bash
python run.py --monitor
```

Run that in a terminal from the project folder. It will keep running until it finds availability (and, if auto-book is on, books it), then exit. You can close the browser tab with the GUI; the monitor runs separately.

---

You can do all of the above from the GUI without editing `config.yaml` by hand. For email or Pushover alerts, add the settings to `config.yaml` (see Configuration reference below) or use the environment variables listed there.

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
