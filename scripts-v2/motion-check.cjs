// Motion contract: interruption, keyboard bypass, visible content and lifecycle.
const { chromium } = require("playwright");
const assert = require("node:assert/strict"),
  fs = require("fs");

(async () => {
  const browser = await chromium.launch({ headless: true });
  const results = [],
    errors = [];
  try {
    for (const width of [390, 1440]) {
      let p;
      async function freshSession() {
        if (p) await p.close();
        p = await browser.newPage({ viewport: { width, height: 900 } });
        p.on("pageerror", (e) => errors.push(e.message));
        await p.goto(process.env.BASE_URL || "http://127.0.0.1:8765", { waitUntil: "domcontentloaded" });
      }
      await freshSession();
      const initial = await p.evaluate(() => ({
        count: document.getAnimations().length,
        cta: getComputedStyle(document.querySelector(".hero-actions")).opacity,
      }));
      assert(initial.count >= 7);
      assert.equal(initial.cta, "1");
      await p.waitForTimeout(60);
      await p.emulateMedia({ reducedMotion: "reduce" });
      await p.waitForFunction(() =>
        document.getAnimations().every((a) => a.playState !== "running"),
      );
      assert(await p.locator(".brand-intro").evaluate((e) => e.hidden));
      await freshSession();
      await p.waitForTimeout(850);
      assert(await p.locator(".brand-intro").evaluate((e) => e.hidden));
      await p.reload();
      assert(await p.locator(".brand-intro").evaluate((e) => e.hidden));
      // Explicit scroll, not anchor navigation: cards should reveal once and remain readable.
      await p.evaluate(() =>
        window.scrollTo(0, document.querySelector("#services").offsetTop),
      );
      await p.waitForTimeout(80);
      const masks = await p
        .locator(".service-media")
        .evaluateAll((es) => es.filter((e) => e.getAnimations().length).length);
      assert(masks > 0);
      await p.emulateMedia({ reducedMotion: "reduce" });
      await p.waitForTimeout(30);
      assert(
        await p
          .locator(".service-media")
          .evaluateAll((es) =>
            es.every((e) => getComputedStyle(e).clipPath === "none"),
          ),
      );
      await p.emulateMedia({ reducedMotion: "no-preference" });
      await p.evaluate(() => window.scrollTo(0, 0));
      await p.waitForTimeout(50);
      await p.evaluate(() =>
        window.scrollTo(0, document.querySelector("#services").offsetTop),
      );
      await p.waitForTimeout(60);
      assert.equal(
        await p
          .locator(".service-media")
          .first()
          .evaluate((e) => e.getAnimations().length),
        0,
      );
      // Keyboard opens instantly; pointer opens and closes with matched backdrop transitions.
      const trigger = p.locator(".service-trigger").first();
      await trigger.focus();
      await p.keyboard.press("Enter");
      assert.equal(
        await p.locator("dialog").evaluate((e) => getComputedStyle(e).opacity),
        "1",
      );
      await p.keyboard.press("Escape");
      await trigger.click();
      await p.waitForTimeout(280);
      await p.locator(".dialog-close").click();
      await p.waitForTimeout(35);
      assert(
        await p
          .locator("dialog")
          .evaluate((e) => e.open && e.classList.contains("motion-closed")),
      );
      // Reverse the in-flight exit using the same service, as a history change can do.
      await p.evaluate(() =>
        openService(
          document.querySelector("#service-maintenance"),
          null,
          null,
          true,
        ),
      );
      await p.waitForTimeout(300);
      assert(
        await p
          .locator("dialog")
          .evaluate((e) => e.open && !e.classList.contains("motion-closed")),
      );
      await p.keyboard.press("Escape");
      assert(await p.locator("dialog").evaluate((e) => !e.open));
      assert(await trigger.evaluate((e) => document.activeElement === e));
      await trigger.click();
      await p.locator(".dialog-close").click();
      await p.emulateMedia({ reducedMotion: "reduce" });
      assert(await p.locator("dialog").evaluate((e) => !e.open));
      assert(
        await p.evaluate(
          () =>
            !document.documentElement.classList.contains("service-modal-open"),
        ),
      );
      await p.emulateMedia({ reducedMotion: "no-preference" });
      if (width === 390) {
        // Click events without Playwright's stability waits stress reversals at 40ms intervals.
        await p.evaluate(() => {
          const b = document.querySelector(".menu-toggle");
          b.dispatchEvent(
            new MouseEvent("click", { bubbles: true, detail: 1 }),
          );
        });
        await p.waitForTimeout(40);
        await p.evaluate(() =>
          document
            .querySelector(".menu-toggle")
            .dispatchEvent(
              new MouseEvent("click", { bubbles: true, detail: 1 }),
            ),
        );
        await p.waitForTimeout(40);
        await p.evaluate(() =>
          document
            .querySelector(".menu-toggle")
            .dispatchEvent(
              new MouseEvent("click", { bubbles: true, detail: 1 }),
            ),
        );
        await p.waitForTimeout(260);
        assert(
          await p
            .locator("#mobile-nav")
            .evaluate((e) => !e.hidden && getComputedStyle(e).opacity === "1"),
        );
        await p.keyboard.press("Escape");
        assert(await p.locator("#mobile-nav").evaluate((e) => e.hidden));
      }
      // Each remaining scroll scene cancels when motion preference changes mid-flight.
      for (const selector of [
        ".about-image",
        ".service-steps",
        ".reviews-layout",
      ]) {
        await p.evaluate(
          (sel) =>
            window.scrollTo(
              0,
              document.querySelector(sel).getBoundingClientRect().top +
                scrollY -
                180,
            ),
          selector,
        );
        await p.waitForTimeout(60);
        await p.emulateMedia({ reducedMotion: "reduce" });
        await p.waitForFunction(() =>
          document.getAnimations().every((a) => a.playState !== "running"),
        );
        await p.emulateMedia({ reducedMotion: "no-preference" });
      }
      await freshSession();
      await p.evaluate(() =>
        dispatchEvent(new PageTransitionEvent("pagehide")),
      );
      assert(
        await p.evaluate(() =>
          document.getAnimations().every((a) => a.playState !== "running"),
        ),
      );
      assert(await p.locator(".brand-intro").evaluate((e) => e.hidden));
      results.push({
        width,
        introAnimations: initial.count,
        ctaImmediate: true,
        masks,
        oneShot: true,
        keyboardInstant: true,
        reverseExit: true,
        reducedCancels: true,
        pagehideClean: true,
      });
      await p.close();
    }
    assert.deepEqual(errors, []);
    fs.writeFileSync(
      "docs-v2/motion-checks.json",
      JSON.stringify({ results, errors }, null, 2),
    );
    console.log(results);
  } finally {
    await browser.close();
  }
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
