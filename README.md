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

1. **Clone the repo and go into the folder**

   ```bash
   cd Disneylad_Paris_Reservation_Web_Scraper
   ```

2. **Optional: use a virtual environment** (recommended so dependencies don’t conflict with other projects)

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # On Windows: .venv\Scripts\activate
   ```

3. **Install Python dependencies**

   Use the same Python you’ll run the app with (`python3` if you’re not in a venv):

   ```bash
   pip install -r requirements.txt
   # or: python3 -m pip install -r requirements.txt
   ```

4. **Install Chromium for Playwright**

   The checker opens a real browser; Playwright needs its own Chromium:

   ```bash
   playwright install chromium
   # or: python3 -m playwright install chromium
   ```

   If you see permission or path errors, try: `python3 -m playwright install chromium`.

5. **Verify setup**

   - **CLI:** `python3 run.py --help` should print usage.
   - **GUI:** `python3 -m streamlit run app.py` should open the app in your browser. If you get “command not found: streamlit”, use `python3 -m streamlit run app.py` (that uses the Python that has Streamlit installed).

6. **Config**

   Copy the example config and edit it, or use the GUI to set everything:

   ```bash
   cp config.example.yaml config.yaml
   ```

   Set at least:

   - `restaurant` – name (or ID) of the restaurant
   - `dates` – list of dates in `YYYY-MM-DD`
   - Optionally `time_start` / `time_end`, `party_size`, `auto_book`, `dry_run`, and notification settings (see `config.example.yaml`).

7. **First-time login**

   In the Web UI, click **Login and save session**; or run `python run.py --login-only --show-browser`. A browser will open—log in to Disneyland Paris when prompted. The session is saved so you don’t have to log in again (until it expires).

### How to use the GUI

The web interface lets you configure and run checks without using the command line.

**1. Start the app**

From the project folder, run:

```bash
python3 -m streamlit run app.py
```

(If `streamlit` is on your PATH you can use `streamlit run app.py` instead.)

Your default browser will open to the app (usually at `http://localhost:8501`). Keep this tab open while you use the app.

**2. Configure your search**

In the **Configuration** form, fill in:

- **Restaurant** – Choose from a dropdown of table-service restaurants (by park area and hotel). If yours isn’t listed, select *Other* and type the exact name from the Disneyland Paris site.
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

## Troubleshooting & debugging

Use these when something doesn’t work or you want to see what the tool is doing.

### Run with the browser visible

To watch the browser instead of running headless:

- **GUI:** In the config form, check **Show browser when checking**, then click **Check availability once** or **Login and save session**.
- **CLI:** Add `--show-browser`:
  ```bash
  python3 run.py --show-browser
  python3 run.py --login-only --show-browser
  python3 run.py --monitor --show-browser
  ```

You’ll see the same pages the script uses (login, dining search, results), which helps debug login issues, captchas, or wrong selectors.

### “Streamlit” or “playwright” not found

- Use the module form so the correct Python is used:
  - **GUI:** `python3 -m streamlit run app.py`
  - **Playwright:** `python3 -m playwright install chromium`
- If you use a virtual environment, activate it first (`source .venv/bin/activate` or Windows equivalent), then run the commands above.

### Login / session issues

- **“Check failed” or errors right after opening the site:** Your saved session may have expired. Run **Login and save session** again (GUI or `python3 run.py --login-only --show-browser`) and log in when the browser opens.
- **Session file:** Logins are stored in `playwright/storage_state.json`. Deleting that file forces a fresh login on the next run.
- If the site shows a captcha or “suspicious activity”, log in once manually with the browser visible (`--show-browser`), then try again headless.

### Check fails or finds no times

- Run **once** with **Show browser when checking** (or `--show-browser`) and watch the flow: does it open the right page, fill the form, and click search? If the layout has changed, the script may not find the right buttons or fields.
- Use **Dry run** when testing: it will report availability but never click “Confirm”, so you can confirm behaviour without booking.
- Output from a check is shown in the GUI **Result** box, or in the terminal when using the CLI. Read the message for “No availability” vs “Could not find…” (selector/flow issue).

### When the Disneyland Paris site changes

If the site is redesigned, the built-in selectors may break. See **If the site changes** below and `docs/DISCOVERY.md` for how to find new URLs and selectors and update `src/dlp_flow.py`.

### Quick reference: useful commands

| Goal | Command |
|------|--------|
| Start the GUI | `python3 -m streamlit run app.py` |
| One-off check (no window) | `python3 run.py` |
| One-off check (see browser) | `python3 run.py --show-browser` |
| Login only, save session | `python3 run.py --login-only --show-browser` |
| Monitor until a slot is found | `python3 run.py --monitor` |
| Install Chromium | `python3 -m playwright install chromium` |

## If the site changes

Disneyland Paris may change URLs or page structure. The code uses a small set of selectors and URLs in `src/dlp_flow.py`. If checks or booking stop working:

1. Open the Disneyland Paris dining page in a browser and note the exact URLs and button/input selectors.
2. Update `src/dlp_flow.py` (and optionally `docs/DISCOVERY.md`) with the new paths and selectors.

See `docs/DISCOVERY.md` for what to document when testing manually.

## Project layout

- `app.py` – **Web UI** (`python3 -m streamlit run app.py`)
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
