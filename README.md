# Gordon College Class Content Monitor

A Python script that monitors class pages for new content and sends Telegram notifications when updates are detected.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install chromium
```

3. Create a `.env` file with your Telegram bot credentials:
```
TG_API_KEY=your_telegram_bot_token
TG_CHAT_ID=your_telegram_chat_id
```

## Getting Telegram Credentials

1. **Bot Token**: Message @BotFather on Telegram to create a new bot and get your token
2. **Chat ID**: 
   - Message your bot first
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find your chat ID in the response

## Usage

Run the script:
```bash
python gc-bot.py
```

The script will:
- Login to your Gordon College account
- Monitor all your class pages for new content
- Send Telegram notifications when new content is detected
- Run continuously with 30-second intervals between checks

## Features

- Automated login
- Class update detection
- Telegram notifications with formatted messages
- Continuous monitoring loop
- Headless browser operation
- Error handling and logging
