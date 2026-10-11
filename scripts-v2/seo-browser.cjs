const { chromium } = require("playwright");
const fs = require("fs");
const assert = require("node:assert/strict");
(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const p = await browser.newPage({
      viewport: { width: 390, height: 844 },
      reducedMotion: "reduce",
    });
    // The first-party test is independent of the external map's availability.
    await p.route("https://yandex.ru/**", (r) => r.abort());
    const errors = [];
    p.on("pageerror", (e) => errors.push(e.message));
    await p.goto(process.env.BASE_URL || "http://127.0.0.1:8765");
    const ids = await p
      .locator(".service-card, .job")
      .evaluateAll((es) => es.map((e) => e.id));
    assert.equal(ids.length, 38);
    for (const id of ids) {
      await p.evaluate((id) => {
        location.hash = id;
      }, id);
      await p.waitForFunction(
        (id) =>
          document.querySelector("dialog").open &&
          (id.startsWith("service-") || document.getElementById(id).open),
        id,
      );
      assert(await p.locator("#" + id).isVisible());
      await p.keyboard.press("Escape");
      assert.equal(await p.locator("dialog").evaluate((d) => d.open), false);
    }
    const nojs = await browser.newPage({
      javaScriptEnabled: false,
      viewport: { width: 390, height: 844 },
    });
    await nojs.route("https://yandex.ru/**", (r) => r.abort());
    await nojs.goto(process.env.BASE_URL || "http://127.0.0.1:8765");
    assert(await nojs.locator('[type="submit"]').isDisabled());
    assert(await nojs.locator('.menu-toggle').isHidden());
    assert(await nojs.locator('#mobile-nav').isVisible());
    await nojs.locator('#mobile-nav a[href="#reviews"]').click();
    assert.equal(new URL(nojs.url()).hash, '#reviews');
    for (const group of await nojs.locator(".service-card").all()) {
      await group.locator(":scope > summary").click();
      for (const job of await group.locator(".job").all()) {
        await job.locator(":scope > summary").click();
        assert(await job.locator(".job-body").isVisible());
        await job.locator(":scope > summary").click();
      }
      await group.locator(":scope > summary").click();
    }
    const faqDetails = await nojs.locator(".faq-list details").all();
    for (const details of faqDetails) {
      await details.locator(":scope > summary").click();
      assert(await details.evaluate((d) => d.open));
    }
    assert(await nojs.locator("#reviews .text-link").isVisible());
    assert.equal(await nojs.locator("#reviews iframe").count(), 1);
    assert.equal(await nojs.locator(".review-card").count(), 7);
    const legacyIds = ["service-parts", "service-tires", "service-wash", "detail-besplatnaya-diagnostika-avtomobilya"];
    for (const id of legacyIds) {
      await p.goto((process.env.BASE_URL || "http://127.0.0.1:8765") + "/legal.html");
      await p.goto((process.env.BASE_URL || "http://127.0.0.1:8765") + "/#" + id);
      if (id !== "service-wash") {
        await p.waitForFunction(id => document.querySelector("dialog").open && document.activeElement.id === id, id);
        assert(await p.locator("dialog #" + id).isVisible());
        await p.keyboard.press("Escape");
        assert.equal(new URL(p.url()).hash, "#services");
      } else {
        await p.waitForFunction(() => document.activeElement.id === "service-wash");
        assert.equal(await p.locator("dialog").evaluate(d => d.open), false);
      }
      // Chromium's native fragment navigation reveals details without JS.
      await nojs.goto((process.env.BASE_URL || "http://127.0.0.1:8765") + "/#" + id);
      assert(await nojs.locator("#" + id).isVisible());
    }
    assert.deepEqual(errors, []);
    const result = {
      date: new Date().toISOString().slice(0, 10),
      deep_links_open_and_close: 38,
      nojs_jobs_readable: 32,
      nojs_faq_details_open: faqDetails.length,
      nojs_navigation: true,
      nojs_reviews_link: true,
      nojs_review_cards: 7,
      nojs_submit_disabled: true,
      legacy_links_js_and_nojs: legacyIds.length,
      errors,
    };
    fs.writeFileSync(
      "docs-v2/seo-browser-checks.json",
      JSON.stringify(result, null, 2),
    );
    console.log(result);
  } finally {
    await browser.close();
  }
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
