import os
import time
import uuid
import threading
import queue
from flask import Flask, request, jsonify, send_file, render_template

import yt_dlp

app = Flask(__name__)

DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

MAX_CONCURRENT_DOWNLOADS = 2
FILE_TTL_SECONDS = 3 * 60 * 60
MAX_FILE_AGE_CHECK_INTERVAL = 600

jobs = {}
job_queue = queue.Queue()
active_downloads = 0
lock = threading.Lock()


def worker_loop():
    global active_downloads
    while True:
        job_id, url, format_id, mode = job_queue.get()
        with lock:
            active_downloads += 1
        jobs[job_id] = {"status": "processing"}
        try:
            run_download(job_id, url, format_id, mode)
        finally:
            with lock:
                active_downloads -= 1
            job_queue.task_done()


def cleanup_loop():
    while True:
        time.sleep(MAX_FILE_AGE_CHECK_INTERVAL)
        now = time.time()
        for fname in os.listdir(DOWNLOAD_DIR):
            fpath = os.path.join(DOWNLOAD_DIR, fname)
            try:
                if now - os.path.getmtime(fpath) > FILE_TTL_SECONDS:
                    os.remove(fpath)
            except OSError:
                pass
        stale_jobs = [jid for jid, j in jobs.items()
                      if j.get("status") == "done" and now - j.get("done_at", now) > FILE_TTL_SECONDS]
        for jid in stale_jobs:
            jobs.pop(jid, None)


for _ in range(MAX_CONCURRENT_DOWNLOADS):
    threading.Thread(target=worker_loop, daemon=True).start()
threading.Thread(target=cleanup_loop, daemon=True).start()


def run_download(job_id, url, format_id, mode):
    output_template = os.path.join(DOWNLOAD_DIR, f"{job_id}.%(ext)s")
    ydl_opts = {
        "outtmpl": output_template,
        "noplaylist": True,
        "quiet": True,
    }
    if format_id == "audio":
        ydl_opts["format"] = "bestaudio/best"
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
    elif format_id:
        ydl_opts["format"] = f"{format_id}+bestaudio/{format_id}/best"
        ydl_opts["merge_output_format"] = "mp4"
    else:
        ydl_opts["format"] = "bestvideo+bestaudio/best"
        ydl_opts["merge_output_format"] = "mp4"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        candidates = [
            f for f in os.listdir(DOWNLOAD_DIR)
            if f.startswith(job_id) and not f.endswith(".part") and not f.endswith(".ytdl")
        ]
        if not candidates:
            raise FileNotFoundError("download finished but no output file was found")

        def rank(fname):
            if format_id == "audio":
                return 0 if fname.endswith(".mp3") else 1
            return 0 if fname.endswith(".mp4") else 1

        candidates.sort(key=rank)
        filename = os.path.join(DOWNLOAD_DIR, candidates[0])

        jobs[job_id] = {
            "status": "done",
            "file": filename,
            "title": info.get("title", job_id),
            "mode": mode,
            "done_at": time.time(),
        }
    except Exception as e:
        jobs[job_id] = {"status": "error", "error": str(e)}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/formats", methods=["POST"])
def get_formats():
    data = request.get_json(force=True)
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "url required"}), 400
    try:
        with yt_dlp.YoutubeDL({"quiet": True, "noplaylist": True}) as ydl:
            info = ydl.extract_info(url, download=False)
        formats = []
        for f in info.get("formats", []):
            if f.get("vcodec") == "none":
                continue
            height = f.get("height")
            filesize = f.get("filesize") or f.get("filesize_approx")
            has_audio = f.get("acodec") not in (None, "none")
            formats.append({
                "format_id": f["format_id"],
                "label": f"{height}p" if height else f.get("format_note", f["format_id"]),
                "ext": f.get("ext"),
                "filesize": filesize,
                "height": height or 0,
                "has_audio": has_audio,
            })
        seen = {}
        for f in formats:
            key = f["height"]
            if key not in seen or (f["filesize"] or 0) > (seen[key]["filesize"] or 0):
                seen[key] = f
        formats = sorted(seen.values(), key=lambda x: x["height"], reverse=True)
        return jsonify({"title": info.get("title"), "thumbnail": info.get("thumbnail"), "formats": formats})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/api/download", methods=["POST"])
def start_download():
    data = request.get_json(force=True)
    url = data.get("url", "").strip()
    format_id = data.get("format_id")
    mode = data.get("mode", "direct")
    if not url:
        return jsonify({"error": "url required"}), 400

    job_id = uuid.uuid4().hex
    position = job_queue.qsize()
    jobs[job_id] = {"status": "queued", "position": position}
    job_queue.put((job_id, url, format_id, mode))
    return jsonify({"job_id": job_id})


@app.route("/api/status/<job_id>")
def status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "not found"}), 404
    result = dict(job)
    if result.get("status") == "done":
        result["link"] = request.host_url.rstrip("/") + f"/api/file/{job_id}"
    return jsonify(result)


@app.route("/api/file/<job_id>")
def get_file(job_id):
    job = jobs.get(job_id)
    if not job or job.get("status") != "done":
        return jsonify({"error": "not ready"}), 404
    return send_file(job["file"], as_attachment=True, download_name=os.path.basename(job["file"]), conditional=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, threaded=True)
