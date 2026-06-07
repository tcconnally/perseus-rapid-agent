"""Record demo video using Playwright's video recording.

Opens the terminal-styled HTML demo page, lets the JavaScript auto-type
the conversation for 160 seconds, and records it as an MP4 video.

Output: demo/demo_video.webm → converts to demo/demo_video.mp4 via ffmpeg
"""

import os, sys, time, subprocess

from playwright.sync_api import sync_playwright

DEMO_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(DEMO_DIR, 'demo_terminal.html')
VIDEO_DIR = os.path.join(DEMO_DIR, 'video_output')
WEBM_PATH = os.path.join(VIDEO_DIR, 'demo.webm')
MP4_PATH = os.path.join(DEMO_DIR, 'demo_video.mp4')

# Clean up
os.makedirs(VIDEO_DIR, exist_ok=True)
for f in os.listdir(VIDEO_DIR):
    os.remove(os.path.join(VIDEO_DIR, f))

print('🎬 Starting demo recording...')
print(f'   HTML: {HTML_PATH}')
print(f'   Duration: ~160 seconds')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={'width': 1280, 'height': 720},
        record_video_dir=VIDEO_DIR,
        record_video_size={'width': 1280, 'height': 720},
    )
    page = context.new_page()

    # Load the demo page
    page.goto(f'file://{HTML_PATH}', wait_until='networkidle')
    print('   Page loaded, waiting for animation...')

    # Wait for all typing to complete (155s total + 3s buffer)
    time.sleep(160)

    print('   Animation complete, finalizing video...')
    context.close()
    browser.close()

# Find the webm file Playwright created
webm_files = [f for f in os.listdir(VIDEO_DIR) if f.endswith('.webm')]
if not webm_files:
    print('❌ No webm file found!')
    sys.exit(1)

actual_webm = os.path.join(VIDEO_DIR, webm_files[0])
print(f'   WebM recorded: {actual_webm}')
print(f'   Size: {os.path.getsize(actual_webm) / 1024 / 1024:.1f} MB')

# Convert to MP4 with ffmpeg
print('🎥 Converting to MP4...')
result = subprocess.run([
    'ffmpeg', '-y',
    '-i', actual_webm,
    '-c:v', 'libx264',
    '-preset', 'fast',
    '-crf', '23',
    '-pix_fmt', 'yuv420p',
    '-movflags', '+faststart',
    MP4_PATH,
], capture_output=True, text=True, timeout=120)

if result.returncode == 0:
    mp4_size = os.path.getsize(MP4_PATH)
    print(f'✅ Video ready: {MP4_PATH}')
    print(f'   Size: {mp4_size / 1024 / 1024:.1f} MB')
else:
    print(f'❌ FFmpeg error: {result.stderr[-500:]}')
    sys.exit(1)
