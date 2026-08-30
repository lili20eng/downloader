# Downloader

A lightweight web-based media downloader built with **Flask** and **yt-dlp**.

The application supports downloading media in **video and audio formats**, with a simple Persian web interface.

## ✨ Features

- 🎥 Download videos in available qualities
- 🎵 Extract audio as MP3
- 🔗 Generate a download link for use with IDM / ADM
- 🖼️ Display media thumbnail and title before downloading
- 📊 Show available video qualities and approximate file sizes
- ⚡ Background download queue
- 🔄 Download status polling
- 🧹 Automatically removes old downloaded files
- 🚀 Ready for deployment on Railway
- 📱 Responsive interface for mobile and desktop

## 🛠️ Technologies

- Python
- Flask
- yt-dlp
- FFmpeg
- Gunicorn
- Nixpacks

## 📁 Project Structure

```text
downloader/
├── app.py
├── Procfile
├── nixpacks.toml
├── requirements.txt
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

## ☁️ Deploy on Railway

This project is configured for Railway deployment.

1. Create a new project on Railway.
2. Connect your GitHub repository.
3. Select the `downloader` repository.
4. Railway will detect the project configuration.
5. Deploy the application.

The included `nixpacks.toml` installs FFmpeg automatically during the build.

## 🎧 Audio Downloads

The downloader can extract the best available audio and convert it to:

```text
MP3 — 192 kbps
```

## 🎬 Video Downloads

Available video qualities are detected automatically from the source.

The application lists available video resolutions and uses the selected format together with the best available audio when necessary.

## 🔗 IDM / ADM Support

The application can also provide the generated file URL so it can be copied into download managers such as:

- IDM
- ADM

## ⚙️ Configuration

The main settings are defined in `app.py`.

For example:

```python
MAX_CONCURRENT_DOWNLOADS = 2
FILE_TTL_SECONDS = 3 * 60 * 60
MAX_FILE_AGE_CHECK_INTERVAL = 600
```

These control the maximum number of simultaneous downloads and automatic cleanup of old files.

## ⚠️ Notes

This project is intended for downloading content that you have permission to download.

Availability of formats and downloads depends on the source website and the capabilities of `yt-dlp`.

## 📄 License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

See the `LICENSE` file for the full license text.
