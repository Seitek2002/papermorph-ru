#!/usr/bin/env python3
"""Step by step (`--advance: manual` in a book's lib/book.css): a small lesson played headless in Chromium.

    uv run --with playwright engine/check_advance.py

No server is needed: the check answers every request itself with this engine, pages written here and a real MP3 from
Math Notebook. With the setting, it checks that a step ends by holding its last frame (the clock stands still, its
captions clear, a Continue button shows) and goes on with the button, Space, Enter, → or a tap on the stage, each to
the next step from its start; that a question step still waits for its answer and its done() goes straight on; that
← on a held step goes back one; that the last step ends the chapter with no hold. Without the setting, the chapter plays
through from step to step as before.
"""
import asyncio
from pathlib import Path
from urllib.parse import urlparse

from playwright.async_api import async_playwright

ENGINE = Path(__file__).resolve().parent
CLIP = ENGINE.parent / "site/math-notebook/ch01/audio/en/intro.mp3"   # longer than the beat: the beat's end stops it
PAGE = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>advance check</title><link rel="stylesheet" href="../lib/engine.css">%s</head>
<body>
<script src="../lib/engine.js"></script>
<script>
'use strict';
const CHAPTER = { number: 1, title: 'Step by step', minutes: 1, language: 'en' };
window.TIMINGS = { a: { dur: 1, marks: {}, cues: [[0, 'The first line.']] } };
const disc = x => (m, D) => { const p = panel(0); show(mk('circle', { cx: x, cy: 450, r: 40, fill: '#f0b45a' }, p), 0, .3); };
const BEATS = [
  ['a', 'One', disc(300)],
  ['b', 'Two', disc(500), { dur: 1 }],
  ['c', 'Three', disc(700), { dur: 1 }],
  ['d', 'Four', disc(900), { dur: 1 }],
  ['q', 'Ask', disc(1100), { dur: .5, ask: done => { window.DONE = done; } }],
  ['e', 'Five', disc(1300), { dur: 1 }],
  ['f', 'Six', disc(1400), { dur: 1 }],
  ['g', 'Last', disc(1500), { dur: 1 }],
].map(([id, title, run, extra]) => ({ id, title, run, ...extra }));
boot();
</script>
</body>
</html>"""
MANUAL = "<style>:root { --advance: manual; }</style>"


def answer(page_html):
    async def route(route):
        path = urlparse(route.request.url).path.split("/__advance__/")[1]
        if path == "ch01/":
            await route.fulfill(content_type="text/html", body=page_html)
        elif path.startswith("lib/"):
            await route.fulfill(path=ENGINE / path[4:])
        elif path.startswith("ch01/audio/en/"):
            await route.fulfill(path=CLIP)
        else:
            await route.fulfill(status=404, body="")
    return route


async def open_page(browser, page_html):
    page = await browser.new_page(viewport={"width": 1640, "height": 1000})
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" and "404" not in m.text else None)
    await page.route("**/__advance__/**", answer(page_html))
    await page.goto("http://advance.invalid/__advance__/ch01/")
    await page.wait_for_function("typeof P !== 'undefined' && typeof BEATS !== 'undefined'")
    return page, errors


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])

        page, errors = await open_page(browser, PAGE % MANUAL)
        js = page.evaluate
        button = "document.querySelector('#ui .card.next button')"

        async def held_on(i):
            await page.wait_for_function(f"P.i === {i} && P.held", timeout=8000)

        async def went_on(i, how):
            await page.wait_for_function(f"P.i === {i} && !P.held", timeout=3000)
            assert await js("P.playing && !P.waiting"), f"{how}: the next step does not play"
            assert await js(f"!{button}"), f"{how}: the Continue button stayed"

        assert await js("bookSetting('--advance')") == "manual"
        await js("setCaptions(true, false)")
        await page.locator("#cover").click()
        await held_on(0)
        t = await js("P.t")
        await page.wait_for_timeout(700)
        assert await js("P.t") == t, "the clock ran on while the step was held"
        assert await js("P.waiting && P.playing && !P.done")
        assert await js("$('caption').hidden"), "the step's last caption stayed while it was held"
        assert await js(f"{button}?.textContent") == "ContinueEnter"
        assert await js("$('frame').classList.contains('is-playing')") is False
        print("PASS a held step: the clock stands still, its caption is cleared, Continue shows")

        await page.locator("#ui .card.next button").click()
        await went_on(1, "the button")
        await held_on(1)
        await page.keyboard.press("Space")
        await went_on(2, "Space")
        await held_on(2)
        await page.keyboard.press("Enter")
        await went_on(3, "Enter")
        await held_on(3)
        await page.keyboard.press("ArrowRight")
        await went_on(4, "→")
        print("PASS the button, Space, Enter and → each go on to the next step")

        await page.wait_for_function("P.i === 4 && P.waiting", timeout=3000)
        assert not await js("P.held") and not await js(button), "a question step was held as a plain step"
        await page.keyboard.press("Space")
        await page.wait_for_timeout(300)
        assert await js("P.i === 4 && P.waiting"), "Space left a question step that waits for its answer"
        await js("DONE()")
        await went_on(5, "a question's done()")
        print("PASS a question step waits for its answer; its done() goes straight on")

        await held_on(5)
        box = await js("(() => { const r = $('stage').getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 3]; })()")
        await page.mouse.click(*box)
        await went_on(6, "a tap on the stage")
        await held_on(6)
        await page.keyboard.press("ArrowLeft")
        await went_on(5, "← on a held step")
        await held_on(5)
        await page.keyboard.press("ArrowRight")
        await went_on(6, "→ after ←")
        await held_on(6)
        await page.keyboard.press("ArrowRight")
        await page.wait_for_function("P.done", timeout=8000)
        assert await js("P.i === 7 && !P.held && !P.playing"), "the last step did not end the chapter"
        assert not await js(button), "the last step was held"
        print("PASS a tap goes on; ← on a held step goes back one; the last step ends the chapter with no hold")
        assert not errors, errors

        page, errors = await open_page(browser, PAGE % "")
        js = page.evaluate
        assert await js("bookSetting('--advance')") == ""
        await page.locator("#cover").click()
        await page.wait_for_function("P.i === 3", timeout=8000)
        assert await js("!P.held"), "a step was held without the setting"
        print("PASS without the setting the chapter plays through from step to step")
        assert not errors, errors
        await browser.close()


asyncio.run(main())
