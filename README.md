# Daily Poster Bot

Automatically generates a themed poster for each day's event and sends it to Telegram, ready before you wake up.

## How it works

1. **GitHub Actions** runs the workflow on a daily schedule (cron).
2. The script looks up today's date in the events list (from `Important_Days_November_2026.docx`: national, international and academic observances).
3. **Gemini** generates the poster artwork, themed to that day's event (colours, mood, motifs).
4. The script lays out the final poster: logos at top-left and top-right, a minimal cinematic style, and no brand text.
5. The poster is sent to your **Telegram** chat.

## Poster style

- Logos at top-left and top-right
- No "AICUF SJEC Unit" text
- Cinematic, science-day-reference look, but minimal (a few graphics, not cluttered)
- Colours and motifs change with the event

## Project structure

```
.
├── .github/
│   └── workflows/
│       └── daily-poster.yml    # schedule + run steps
├── assets/
│   ├── logo-left.png
│   └── logo-right.png
├── data/
│   └── events.json             # date → event mapping
├── generate_poster.py          # main script
├── requirements.txt
└── README.md
```

## Setup

### 1. Get your keys

| Secret | Where to get it |
|---|---|
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/) (free tier) |
| `TELEGRAM_BOT_TOKEN` | Message [@BotFather](https://t.me/BotFather) → `/newbot` |
| `TELEGRAM_CHAT_ID` | Message your bot, then open `https://api.telegram.org/bot<TOKEN>/getUpdates` and copy `chat.id` |

### 2. Add them to GitHub

Repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**. Add all three.

### 3. Add your assets

- Put both logos in `assets/`
- Keep `data/events.json` updated with each date and its event

### 4. Enable the workflow

Go to the **Actions** tab and enable workflows. Push to `main` and the schedule starts running.

## Schedule

Cron in GitHub Actions runs in **UTC**. To get the poster by 6:00 AM IST, run it at 00:30 UTC:

```yaml
on:
  schedule:
    - cron: "30 0 * * *"
  workflow_dispatch:
```

`workflow_dispatch` lets you run it manually from the Actions tab for testing.

## Run manually

1. Open the **Actions** tab
2. Select **Daily Poster**
3. Click **Run workflow**

## Run locally

```bash
pip install -r requirements.txt
export GEMINI_API_KEY="your_key"
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"
python generate_poster.py
```

## Updating events

Edit `data/events.json`. When a new month starts, add that month's dates. Format:

```json
{
  "2026-11-14": "Children's Day",
  "2026-11-16": "International Day for Tolerance"
}
```

## Troubleshooting

- **No poster arrived:** check the Actions tab for a failed run and read the logs.
- **Telegram error:** confirm you've sent your bot at least one message, and that the chat ID is correct.
- **Gemini error or rate limit:** the free tier has daily limits. Re-run later or reduce retries.
- **Wrong time:** remember cron is UTC, not IST.
- **No event for today:** add the date to `events.json`.

## Credits

Built by Kay for AICUF SJEC Unit.
