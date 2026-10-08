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
    assert.equal(ids.length, 39);
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
    await nojs.locator('#mobile-nav a[href="#team"]').click();
    assert.equal(new URL(nojs.url()).hash, '#team');
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
    await nojs.locator(".review-more > summary").click();
    assert.equal(await nojs.locator(".attribution:visible").count(), 7);
    assert.deepEqual(errors, []);
    const result = {
      date: new Date().toISOString().slice(0, 10),
      deep_links_open_and_close: 39,
      nojs_jobs_readable: 33,
      nojs_faq_details_open: faqDetails.length,
      nojs_navigation: true,
      nojs_reviews_visible: 7,
      nojs_submit_disabled: true,
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
