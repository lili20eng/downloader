# Downloader

A lightweight web-based media downloader built with **Flask** and **yt-dlp**, with an optional **Telegram Mini App** launcher.

The application supports downloading media in **video and audio formats**, with a bilingual (Persian/English) web interface and a background job queue.

## ✨ Features

- 🎥 Download videos in available qualities
- 🎵 Extract audio as MP3 (192 kbps)
- 🔗 Generate a download link for use with IDM / ADM
- 🖼️ Display media thumbnail and title before downloading
- 📊 Show available video qualities and approximate file sizes
- ⚡ Background download queue with configurable concurrency
- 🔄 Download status polling via job ID
- 🧹 Automatically removes old downloaded files and stale jobs
- 🌐 Bilingual web interface (Persian / English) with RTL/LTR switching, remembers your language choice
- 🎨 8 selectable color themes (dark, boy, girl, autumn, spring, ocean, light, telegram), saved locally
- 🤖 Telegram bot that opens the downloader as a Web App (multi-language welcome: fa, en, ru, ar)
- 📲 Deep Telegram Mini App integration: auto-adapts to the user's Telegram theme, haptic feedback on buttons, in-app link opening
- 🚀 Ready for deployment on Railway (Nixpacks) or Render (Docker)
- 📱 Responsive interface for mobile and desktop

## 🛠️ Technologies

- Python
- Flask
- yt-dlp
- FFmpeg
- Gunicorn
- Nixpacks / Docker
- Telegram Bot API

## 📁 Project Structure

```text
downloader/
├── app.py
├── telegram_bot.py
├── Procfile
├── Dockerfile
├── nixpacks.toml
├── requirements.txt
├── LICENSE
├── .gitignore
└── templates/
    └── index.html
```

## 🚀 Run Locally

Clone the repository:

```bash
git clone https://github.com/taisizlar/downloader.git
cd downloader
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Make sure **FFmpeg** is installed and available on your system.

Start the application:

```bash
python app.py
```

The application will run on:

```text
http://localhost:8080
```

The Telegram bot is optional — it only activates if `BOT_TOKEN` and `WEBAPP_URL` are set (see below). Without them, the web app runs normally on its own.

## ⚙️ Environment Variables

| Variable         | Required | Description                                                        |
|------------------|----------|----------------------------------------------------------------------|
| `PORT`           | No       | Port to bind to (defaults to `8080`)                                 |
| `BOT_TOKEN`      | No       | Telegram bot token. If unset, the Telegram integration is disabled.  |
| `WEBAPP_URL`     | No       | Public URL of the deployed app, used as the Telegram Web App target. |
| `WEBHOOK_SECRET` | No       | Secret path segment for the Telegram webhook (defaults to `hook`).   |

On startup, if `BOT_TOKEN` and `WEBAPP_URL` are both set, the app automatically registers the Telegram webhook at:

```text
<WEBAPP_URL>/telegram/webhook/<WEBHOOK_SECRET>
```

## 🔌 API Endpoints

| Method | Endpoint                    | Description                                              |
|--------|------------------------------|-----------------------------------------------------------|
| GET    | `/`                          | Web interface                                              |
| POST   | `/api/formats`               | Body: `{ "url": "..." }` — returns title, thumbnail, available formats |
| POST   | `/api/download`              | Body: `{ "url", "format_id", "mode" }` — queues a download, returns `job_id` |
| GET    | `/api/status/<job_id>`       | Returns job status (`queued`, `processing`, `done`, `error`) and download link when done |
| GET    | `/api/file/<job_id>`         | Downloads the finished file                                |
| POST   | `/telegram/webhook/<secret>` | Telegram webhook receiver (secret must match `WEBHOOK_SECRET`) |

## ☁️ Deploy on Railway

This project is configured for Railway deployment using Nixpacks.

1. Create a new project on Railway.
2. Connect your GitHub repository.
3. Select the `downloader` repository.
4. Set environment variables if you want the Telegram bot enabled.
5. Deploy the application.

The included `nixpacks.toml` installs FFmpeg automatically during the build, and the `Procfile` runs it with Gunicorn.

## 🐳 Deploy on Render (Docker)

A `Dockerfile` is included for deploying on **Render**:

1. Create a new **Web Service** on Render.
2. Connect your GitHub repository.
3. Choose **Docker** as the environment (Render will detect the `Dockerfile` automatically).
4. Set environment variables (`BOT_TOKEN`, `WEBAPP_URL`, `WEBHOOK_SECRET`) if you want the Telegram bot enabled.
5. Deploy.

To test the Docker build locally first:

```bash
docker build -t downloader .
docker run -p 8080:8080 -e PORT=8080 downloader
```

## 🤖 Telegram Bot & Mini App

When configured, the bot replies to any incoming message (including `/start`) with a localized welcome message and a button that opens the downloader inside Telegram as a **Web App**. Supported languages are auto-detected from the user's Telegram client: Persian, English, Russian, and Arabic, falling back to English.

Inside the Mini App, the interface automatically:
- Adopts Telegram's theme colors (`themeParams`) and stays in sync if the user switches theme
- Expands to full height on open
- Triggers haptic feedback on button taps
- Opens the final download link using Telegram's in-app browser (`openLink`)

## 🎧 Audio Downloads

The downloader extracts the best available audio and converts it to:

```text
MP3 — 192 kbps
```

## 🎬 Video Downloads

Available video qualities are detected automatically from the source. The application lists available resolutions and merges the selected video format with the best available audio when necessary.

## 🔗 IDM / ADM Support

Once a download finishes, the app exposes a direct file URL that can be copied into download managers such as:

- IDM
- ADM

## ⚙️ Configuration

The main settings are defined in `app.py`:

```python
MAX_CONCURRENT_DOWNLOADS = 2
FILE_TTL_SECONDS = 3 * 60 * 60
MAX_FILE_AGE_CHECK_INTERVAL = 600
```

These control the maximum number of simultaneous downloads and the automatic cleanup interval for old files and stale jobs.

## ⚠️ Notes

This project is intended for downloading content that you have permission to download.

Availability of formats and downloads depends on the source website and the capabilities of `yt-dlp`.

## 📄 License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

See the `LICENSE` file for the full license text.
