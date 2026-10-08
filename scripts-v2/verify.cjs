// Browser acceptance against dist; --export captures the authoring prototype.
const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const base = process.env.BASE_URL || "http://127.0.0.1:8765";
const exporting = process.argv.includes("--export");
const widths = [
  320, 360, 390, 600, 768, 900, 1024, 1199, 1200, 1440, 1600, 1920,
];
const results = { widths: [], errors: [], localFailures: [], formRequests: [] };

async function ready(page) {
  await page.evaluate(() =>
    document
      .querySelectorAll("img")
      .forEach((image) => (image.loading = "eager")),
  );
  await page.waitForFunction(() =>
    [...document.images].every(
      (image) => image.complete && image.naturalWidth > 0,
    ),
  );
  // Async portrait decoding can finish after load; screenshots must wait for pixels.
  await page.evaluate(() =>
    Promise.all([...document.images].map((image) => image.decode())),
  );
  await page.evaluate(() => document.fonts.ready);
}
async function enlarge(page) {
  await page.evaluate(() => {
    const elements = [...document.querySelectorAll("body *")];
    const sizes = elements.map((el) =>
      parseFloat(getComputedStyle(el).fontSize),
    );
    elements.forEach((el, i) => (el.style.fontSize = `${sizes[i] * 2}px`));
  });
}
async function noOverflow(page, state) {
  assert(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
    state,
  );
}
async function main() {
  const browser = await chromium.launch({ headless: true });
  results.browser = browser.version();
  const page = async (options) => {
    const p = await browser.newPage(options);
    p.on("pageerror", (error) => results.errors.push(error.message));
    p.on("response", (response) => {
      if (response.url().startsWith(base) && response.status() >= 400)
        results.localFailures.push(response.url());
    });
    return p;
  };
  try {
    for (const width of widths) {
      const p = await page({
        viewport: { width, height: 1000 },
        reducedMotion: "reduce",
      });
      await p.goto(base);
      await ready(p);
      await noOverflow(p, `${width}: closed`);
      assert.equal(await p.locator(".job").count(), 33);
      assert.equal(await p.locator("#team .team-member").count(), 5);
      assert.equal(await p.locator("#reviews .attribution").count(), 7);
      const teamColumns = await p.locator(".team-list").evaluate((el) =>
        getComputedStyle(el).gridTemplateColumns.split(" ").length,
      );
      assert.equal(teamColumns, width >= 1200 ? 5 : width >= 768 ? 3 : 1);
      assert(
        await p.evaluate(
          () =>
            document.fonts.check("16px Manrope") &&
            document.fonts.check("16px Golos"),
        ),
      );
      if (exporting && [390, 768, 1440].includes(width)) {
        await p.locator("#location").scrollIntoViewIfNeeded();
        // The lazy iframe starts loading only when it approaches the viewport.
        const map = p.frameLocator('iframe[src*="map-widget"]');
        await map.locator("canvas").first().waitFor({ state: "visible", timeout: 20000 });
        await map.getByText("© Яндекс", { exact: true }).waitFor({ timeout: 20000 });
        await p.waitForTimeout(2000); // Allow the loaded map tiles to paint.
        // Keep the WebGL map in view: scrolling away can clear its canvas.
        await p.screenshot({
          path: `output-v2/mockups/home-${width}.png`,
          fullPage: true,
        });
        for (const id of [
          "top",
          "services",
          "about",
          "team",
          "reviews",
          "booking",
          "location",
        ]) {
          await p
            .locator(`#${id}`)
            .screenshot({ path: `output-v2/mockups/${id}-${width}.png` });
        }
      }
      const geometry = () =>
        p.locator(".service-card").evaluateAll((cards) =>
          cards.map((card) => {
            const r = card.getBoundingClientRect();
            return {
              x: r.x,
              y: r.y + scrollY,
              width: r.width,
              height: r.height,
            };
          }),
        );
      const before = await geometry();
      await p.locator(".service-trigger").first().click();
      await p.locator("dialog .job>summary").first().click();
      assert.deepEqual(
        await geometry(),
        before,
        `${width}: modal changes catalog geometry`,
      );
      await noOverflow(p, `${width}: modal`);
      if (exporting && [390, 768, 1440].includes(width)) {
        await p.screenshot({
          path: `output-v2/mockups/service-expanded-${width}.png`,
        });
      }
      await enlarge(p);
      await noOverflow(p, `${width}: text200 modal`);
      assert(
        await p
          .locator("dialog")
          .evaluate((el) => el.scrollWidth <= el.clientWidth + 1),
      );
      await p.keyboard.press("Escape");
      await noOverflow(p, `${width}: text200 closed`);
      assert(await p.locator("#team").evaluate((el) =>
        [...el.querySelectorAll("h2,h3,p")].every((item) =>
          item.scrollWidth <= item.clientWidth + 1 &&
          getComputedStyle(item).overflowY === "visible"),
      ), `${width}: team text200 clipped`);
      if (exporting && [320, 390, 1440].includes(width))
        await p.screenshot({
          path: `output-v2/review/text200-${width}.png`,
          fullPage: true,
        });
      results.widths.push({
        width,
        closed: true,
        modal: true,
        geometryStable: true,
        text200: true,
      });
      await p.close();
    }
    const p = await page({
      viewport: { width: 390, height: 950 },
      reducedMotion: "reduce",
    });
    await p.goto(base);
    await ready(p);
    await p.keyboard.press("Tab");
    assert(
      await p.locator(".skip").evaluate((el) => el === document.activeElement),
    );
    await p.keyboard.press("Enter");
    await p.waitForFunction(() => document.activeElement.id === "main");
    await p.locator(".menu-toggle").focus();
    await p.keyboard.press("Enter");
    await p.locator('#mobile-nav a[href="#team"]').focus();
    await p.keyboard.press("Enter");
    await p.waitForFunction(() => document.activeElement.id === "team");
    assert(p.url().endsWith("#team"));
    assert(await p.locator("#mobile-nav").isHidden());
    await p.goto(`${base}/#team`);
    await ready(p);
    assert(await p.locator("#team").evaluate((el) =>
      Math.abs(el.getBoundingClientRect().top) < innerHeight / 2,
    ));
    let jobs = 0;
    for (const trigger of await p.locator(".service-trigger").all()) {
      await trigger.focus();
      await p.keyboard.press("Enter");
      for (const job of await p.locator("dialog .job").all()) {
        await job.locator("summary").click();
        assert(await job.evaluate((el) => el.open));
        jobs++;
        await job.locator("summary").click();
        assert(await job.evaluate((el) => !el.open));
      }
      await p.keyboard.press("Escape");
      assert(await trigger.evaluate((el) => el === document.activeElement));
    }
    assert.equal(jobs, 33);
    results.jobs = jobs;
    await p.locator(".service-trigger").first().click();
    for (const key of ["Tab", "Shift+Tab"]) {
      for (let i = 0; i < 25; i++) {
        await p.keyboard.press(key);
        assert(
          await p
            .locator("dialog")
            .evaluate((el) => el.contains(document.activeElement)),
        );
      }
    }
    await p.mouse.click(3, 3);
    assert(await p.locator("dialog").evaluate((el) => !el.open));
    for (let i = 0; i < 8; i++) {
      await p.locator(".service-trigger").first().click();
      await p.keyboard.press("Escape");
    }
    assert(
      await p.evaluate(
        () =>
          !document.documentElement.classList.contains("service-modal-open"),
      ),
    );
    await p.goto(base);
    await p.locator(".service-trigger").first().click();
    await p.goBack();
    await p.waitForFunction(() => !document.querySelector("dialog").open);
    await p.goForward();
    await p.waitForFunction(() => document.querySelector("dialog").open);
    await p.locator("dialog .service-content > [data-service]").first().click();
    assert(await p.locator(".form-context").isVisible());
    await p.locator("#clear-service").click();
    assert(await p.locator(".form-context").isHidden());
    p.on("request", (request) => {
      if (
        request.frame() === p.mainFrame() &&
        (request.method() !== "GET" ||
          ["fetch", "xhr"].includes(request.resourceType()))
      )
        results.formRequests.push(request.url());
    });
    await p.locator("[type=submit]").click();
    assert.equal(
      await p.locator("#phone").getAttribute("aria-invalid"),
      "true",
    );
    await p.locator("#phone").fill("+7 999 123 45 67");
    await p.locator("#name").fill("Проверка");
    await p.locator("#request").fill("Тест без отправки");
    await p.locator("#consent").check();
    await p.locator("[type=submit]").click();
    assert.equal(
      await p.locator(".form-message").getAttribute("data-state"),
      "checked",
    );
    await p.locator(".demo-states>summary").click();
    for (const state of ["success", "sending", "idle", "error"]) {
      await p.locator(`[data-demo=${state}]`).click();
      assert.equal(
        await p.locator(".form-message").getAttribute("data-state"),
        state,
      );
    }
    await p.locator(".retry").click();
    await p.waitForFunction(
      () => document.querySelector(".form-message").dataset.state === "checked",
    );
    assert.equal(await p.locator("#name").inputValue(), "Проверка");
    assert.equal(await p.locator("#request").inputValue(), "Тест без отправки");
    assert.deepEqual(results.formRequests, []);
    await p.goto(`${base}/#%`);
    await p.waitForTimeout(30);
    await p.close();
    const nojs = await page({
      javaScriptEnabled: false,
      viewport: { width: 320, height: 950 },
    });
    await nojs.goto(base);
    assert(await nojs.locator("[type=submit]").isDisabled());
    assert.equal(await nojs.locator("#team .team-member").count(), 5);
    assert(await nojs.locator(".team-notice").isVisible());
    for (const card of await nojs.locator(".service-card").all()) {
      await card.locator(":scope > summary").click();
      assert(await card.evaluate((el) => el.open));
      for (const job of await card.locator(".job").all()) {
        await job.locator("summary").click();
        assert(await job.evaluate((el) => el.open));
      }
      await noOverflow(nojs, "no-JS expanded");
      await card.locator(":scope > summary").click();
    }
    await nojs.close();
    const fallback = await page({ viewport: { width: 390, height: 950 } });
    await fallback.route("https://yandex.ru/**", (route) => route.abort());
    await fallback.goto(base);
    await fallback.locator(".contact-route").click();
    assert(fallback.url().endsWith("#location"));
    for (const selector of [
      ".location-address",
      ".location-phone",
      ".location-copy .btn",
    ])
      assert(await fallback.locator(selector).isVisible());
    await fallback.close();
    if (exporting) {
      const components = await page({
        viewport: { width: 1440, height: 1000 },
        reducedMotion: "reduce",
      });
      await components.goto(`${base}/components.html`);
      await ready(components);
      await components.screenshot({
        path: "output-v2/mockups/components-1440.png",
        fullPage: true,
      });
      await components.close();
    }
    Object.assign(results, {
      focusAndHistory: true,
      demoForm: true,
      noJS: true,
      demoTeam: true,
      mapFallback: true,
    });
    assert.deepEqual(results.errors, []);
    assert.deepEqual(results.localFailures, []);
    fs.writeFileSync(
      `docs-v2/${exporting ? "export" : "browser"}-checks.json`,
      JSON.stringify(results, null, 2) + "\n",
    );
    console.log(
      `Browser: ${widths.length} widths, 33 jobs, text200, keyboard, history, demo form and no-JS passed.`,
    );
  } finally {
    await browser.close();
  }
}
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
