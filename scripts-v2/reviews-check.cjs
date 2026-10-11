const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const base = process.env.BASE_URL || "http://127.0.0.1:8765";

(async () => {
  const browser = await chromium.launch();
  const results = [];
  try {
    for (const width of [390, 1440]) {
      const page = await browser.newPage({ viewport: { width, height: 1000 } });
      await page.goto(base);
      const rail = page.locator(".reviews-rail");
      await page.locator(".reviews-next").click();
      await page.waitForTimeout(50);
      await page.emulateMedia({ reducedMotion: "reduce" });
      await page.waitForFunction(() => matchMedia("(prefers-reduced-motion: reduce)").matches);
      await page.waitForTimeout(100);
      const position = await rail.evaluate(el => el.scrollLeft);
      await page.waitForTimeout(250);
      assert(Math.abs(await rail.evaluate(el => el.scrollLeft) - position) < 1, `${width}: reduced motion stops scrolling`);
      await rail.focus();
      await page.keyboard.press("Home");
      await page.waitForFunction(() => document.querySelector(".reviews-prev").disabled);
      for (let i = 0; i < 8; i++) {
        await page.locator(".reviews-next").click();
        await page.waitForFunction(() => !document.querySelector(".reviews-prev").disabled);
        await page.locator(".reviews-prev").click();
        await page.waitForFunction(() => document.querySelector(".reviews-prev").disabled);
      }
      await rail.scrollIntoViewIfNeeded();
      const box = await rail.boundingBox();
      await page.mouse.move(box.x + box.width / 2, Math.max(1, box.y) + 80);
      await page.mouse.wheel(400, 0);
      await page.waitForFunction(() => document.querySelector(".reviews-rail").scrollLeft > 0);
      await page.waitForTimeout(600); // Finish the browser's wheel/snap gesture.
      await page.setViewportSize({ width: width === 390 ? 1440 : 390, height: 1000 });
      await page.waitForTimeout(200); // The browser re-snaps after layout changes.
      await rail.focus();
      await page.keyboard.press("End");
      await page.waitForFunction(() => document.querySelector(".reviews-next").disabled);
      assert(await page.locator(".review-card").evaluateAll(cards => cards.every(el => el.scrollWidth <= el.clientWidth + 1)));
      results.push({ width, reducedMotionStops: true, rapidReverse: true, nativeWheel: true, resize: true, fullTextFits: true });
      await page.close();
    }
    fs.writeFileSync("docs-v2/reviews-carousel-checks.json", JSON.stringify(results, null, 2) + "\n");
    console.log(results);
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
