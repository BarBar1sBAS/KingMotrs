// Additional acceptance checks for the approved v2 refinement.
const { chromium } = require("playwright");
const fs = require("fs");
const assert = require("node:assert/strict");
(async () => {
  const browser = await chromium.launch({ headless: true });
  const results = {};
  const errors = [];
  try {
    const p = await browser.newPage({ viewport: { width: 390, height: 844 } });
    p.on("pageerror", (e) => errors.push(e.message));
    await p.goto(process.env.BASE_URL || "http://127.0.0.1:8765");
    await p.evaluate(() => document.fonts.ready);
    results.anchors = await p.evaluate(() =>
      [...document.querySelectorAll('a[href^="#"]')].every((a) =>
        document.getElementById(decodeURIComponent(a.hash.slice(1))),
      ),
    );
    assert(results.anchors);
    let opened = 0;
    for (const id of await p
      .locator(".job")
      .evaluateAll((es) => es.map((e) => e.id))) {
      await p.evaluate((id) => (location.hash = id), id);
      await p.waitForFunction(
        (id) =>
          document.getElementById(id).open &&
          document.querySelector("dialog").open,
        id,
      );
      opened++;
      await p.keyboard.press("Escape");
    }
    results.deepLinks = opened;
    assert.equal(opened, 33);
    let details = 0;
    for (const selector of [
      ".review-more",
      ".faq-list details",
      ".secondary-panel",
      ".demo-states",
      ".sitemap",
    ]) {
      for (const d of await p.locator(selector).all()) {
        await d.locator(":scope > summary").click();
        assert(await d.evaluate((e) => e.open));
        details++;
      }
    }
    results.nonServiceDisclosures = details;
    for (let i = 0; i < 10; i++) {
      await p.locator(".menu-toggle").click();
      await p.locator(".menu-toggle").click();
    }
    await p.waitForFunction(() => document.querySelector("#mobile-nav").hidden);
    results.menuCycles = await p
      .locator("#mobile-nav")
      .evaluate((e) => e.hidden);
    assert(results.menuCycles);
    await p.locator(".menu-toggle").click();
    await p.locator('#mobile-nav a[href="#reviews"]').click();
    await p.waitForFunction(() => document.activeElement.id === "reviews");
    results.menuAnchorFocus = true;
    await p.locator("#phone").fill("123");
    await p.locator("button[type=submit]").click();
    assert.equal(
      await p.locator("#phone").getAttribute("aria-invalid"),
      "true",
    );
    await p.locator("#phone").fill("+7 999 123 45 67");
    await p.locator("button[type=submit]").click();
    assert.equal(
      await p.locator("#consent").getAttribute("aria-invalid"),
      "true",
    );
    await p.locator("#name").fill("Проверка");
    await p.locator("#request").fill("Проверка демонстрационной формы");
    await p.locator("#consent").check();
    await p.locator("[data-demo=sending]").click();
    await p.locator("[data-demo=idle]").click();
    await p.waitForTimeout(850);
    assert.equal(
      await p.locator(".form-message").getAttribute("data-state"),
      "idle",
    );
    results.formCancellation = true;
    await p.locator("[data-demo=error]").click();
    await p.locator(".retry").click();
    await p.waitForTimeout(850);
    results.formPreserved =
      (await p.locator("#name").inputValue()) === "Проверка" &&
      (await p.locator("#request").inputValue()) ===
        "Проверка демонстрационной формы";
    assert(results.formPreserved);
    await p.emulateMedia({ reducedMotion: "reduce" });
    results.reducedMotion =
      (await p.locator(".brand-intro").evaluate((e) => e.hidden)) &&
      (await p.evaluate(() =>
        document.getAnimations().every((a) => a.playState !== "running"),
      ));
    assert(results.reducedMotion);
    await p.close();
    const denied = await browser.newPage();
    await denied.addInitScript(() =>
      Object.defineProperty(window, "sessionStorage", {
        get() {
          throw new Error("denied");
        },
      }),
    );
    await denied.goto(process.env.BASE_URL || "http://127.0.0.1:8765");
    results.storageDenied =
      (await denied.locator(".brand-intro").evaluate((e) => e.hidden)) &&
      (await denied.locator(".hero .btn").isVisible());
    assert(results.storageDenied);
    await denied.close();
    const nojs = await browser.newPage({
      javaScriptEnabled: false,
      viewport: { width: 320, height: 844 },
    });
    await nojs.goto(process.env.BASE_URL || "http://127.0.0.1:8765");
    results.noJsDisabled = await nojs.locator("[type=submit]").isDisabled();
    assert(results.noJsDisabled);
    await nojs.close();
    results.text200 = [];
    for (const w of [320, 390, 768, 1024, 1440, 1920]) {
      const q = await browser.newPage({
        viewport: { width: w, height: 1000 },
        reducedMotion: "reduce",
      });
      await q.goto(process.env.BASE_URL || "http://127.0.0.1:8765");
      await q.evaluate(async () => {
        await document.fonts.ready;
        const es = [...document.querySelectorAll("body *")],
          sizes = es.map((e) => parseFloat(getComputedStyle(e).fontSize));
        es.forEach((e, i) => (e.style.fontSize = sizes[i] * 2 + "px"));
      });
      const ok = await q.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      );
      assert(ok);
      results.text200.push({ width: w, closedPage: ok });
      if (w === 320)
        await q.screenshot({
          path: "output-v2/review/closed-text200-320.png",
          fullPage: true,
        });
      await q.close();
    }
    results.errors = errors;
    assert.deepEqual(errors, []);
    fs.writeFileSync(
      "docs-v2/polish-checks.json",
      JSON.stringify(results, null, 2),
    );
    console.log(results);
  } finally {
    await browser.close();
  }
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
