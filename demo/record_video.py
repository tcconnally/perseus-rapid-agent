"""Record the Perseus Memory Agent demo video for Google Cloud Hackathon."""
import time, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

PROJECT = Path("/opt/data/webui/minions/.minions-data/workspace/perseus-rapid-agent")
HTML = PROJECT / "demo" / "demo_terminal.html"
VIDEO_DIR = PROJECT / "demo" / "video_output"
OUTPUT = PROJECT / "demo" / "demo_video.mp4"

VIDEO_DIR.mkdir(parents=True, exist_ok=True)
for f in VIDEO_DIR.glob("*"): f.unlink()

TOTAL = 170
print(f"Recording: {HTML} ({TOTAL}s)")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width": 1280, "height": 720}, record_video_dir=str(VIDEO_DIR), record_video_size={"width": 1280, "height": 720})
    page = ctx.new_page()
    page.goto(f"file://{HTML}", wait_until="networkidle")
    time.sleep(TOTAL)
    ctx.close()
    browser.close()

webm = next(VIDEO_DIR.glob("*.webm"))
print(f"WebM: {webm.stat().st_size / 1024:.0f} KB")

subprocess.run(["ffmpeg", "-y", "-i", str(webm), "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(OUTPUT)], capture_output=True, timeout=120, check=True)
print(f"MP4: {OUTPUT} ({OUTPUT.stat().st_size / 1024:.0f} KB)")
print("✅ Done")
