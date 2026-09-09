"""Capture the page for review at real viewports.

Desktop Chrome will not open a window narrower than about 500px, so a
--window-size=390 headless capture is a wider layout clipped to 390. This
drives the installed Chrome through Playwright with an emulated viewport and
asserts, inside the page, that nothing overflows; the numbers go to
.impeccable/review/capture-log.json next to the images. Serve docs/ on
http://localhost:8765 first (python -m http.server 8765 --directory docs).
"""
import sys, time, json
from playwright.sync_api import sync_playwright
out = ".impeccable/review"
url = "http://localhost:8765/?v=" + str(int(time.time()))
log = []
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    for name, w, h, full in [("hero-repro", 1440, 900, False), ("desktop", 1440, 900, True), ("mobile", 390, 844, True)]:
        pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1, is_mobile=(w < 700), has_touch=(w < 700))
        pg.goto(url, wait_until="networkidle"); pg.wait_for_timeout(1800)
        m = pg.evaluate("""() => ({vw: document.documentElement.clientWidth, sw: document.documentElement.scrollWidth,
            over: [...document.querySelectorAll('p,h1,.legend,.axis,.rail,.flap')].filter(e=>e.getBoundingClientRect().right>document.documentElement.clientWidth+0.5).length,
            stamp: document.getElementById('stamp').textContent})""")
        pg.screenshot(path=f"{out}/{name}.png", full_page=full)
        log.append({"capture": name, **m}); pg.close()
    b.close()
open(f"{out}/capture-log.json", "w").write(json.dumps(log, indent=1))
print(json.dumps(log))
