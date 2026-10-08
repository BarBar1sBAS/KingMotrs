const { chromium } = require("playwright");

(async () => {
  const b = await chromium.launch({ headless: true });
  try {
    for (const width of [1440, 390]) {
      const height = width === 390 ? 844 : 900;
      const c = await b.newContext({
        viewport: { width, height },
        recordVideo: { dir: "output-v2/video", size: { width, height } },
      });
      const p = await c.newPage();
      await p.goto(process.env.BASE_URL || "http://127.0.0.1:8765");
      await p.evaluate(async () => {
        await document.fonts.ready;
        document.querySelectorAll("img").forEach((i) => (i.loading = "eager"));
        await Promise.all(
          [...document.images].map((i) => i.decode().catch(() => {})),
        );
      });
      await p.waitForTimeout(900);
      // Start a new intro session after warming the image/font cache.
      await p.evaluate(() => sessionStorage.removeItem("km-intro-v2"));
      await p.reload({ waitUntil: "domcontentloaded" });
      await p.waitForTimeout(1400);
      const bottom = await p
        .locator("#reviews")
        .evaluate((e) => e.offsetTop + e.offsetHeight);
      for (let y = 0; y < bottom; y += 350) {
        await p.mouse.wheel(0, 350);
        await p.waitForTimeout(500);
      }
      await p.waitForTimeout(700);
      await p.locator(".service-trigger").first().click();
      await p.waitForTimeout(500);
      await p.locator(".service-dialog .job>summary").first().click();
      await p.waitForTimeout(650);
      await p.locator(".dialog-close").click();
      await p.waitForTimeout(650);
      if (width === 390) {
        await p.evaluate(() => window.scrollTo(0, 0));
        await p.locator(".menu-toggle").click();
        await p.waitForTimeout(450);
        await p.locator(".menu-toggle").click();
        await p.waitForTimeout(450);
      }
      const video = p.video();
      await c.close();
      await video.saveAs(`output-v2/video/KingMotors-motion-${width}.webm`);
      await video.delete();
    }
    // Four-times slower first-screen scene and dialog for visual transition review.
    const c = await b.newContext({
      viewport: { width: 1440, height: 900 },
      recordVideo: {
        dir: "output-v2/video",
        size: { width: 1440, height: 900 },
      },
    });
    const p = await c.newPage();
    await p.goto(process.env.BASE_URL || "http://127.0.0.1:8765", { waitUntil: "domcontentloaded" });
    await p.evaluate(() => {
      clearTimeout(introTimer);
      introTimer = setTimeout(stopIntro, 3280);
      document.getAnimations().forEach((a) => a.updatePlaybackRate(0.25));
    });
    await p.waitForTimeout(3600);
    await p.locator(".service-trigger").first().click();
    await p.evaluate(() =>
      document.getAnimations().forEach((a) => a.updatePlaybackRate(0.25)),
    );
    await p.waitForTimeout(1200);
    const v = p.video();
    await c.close();
    await v.saveAs("output-v2/video/KingMotors-motion-slow.webm");
    await v.delete();
    console.log("Recorded desktop, mobile and 4x slow motion.");
  } finally {
    await b.close();
  }
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
