const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const base = process.env.BASE_URL || 'http://127.0.0.1:8765';
(async () => {
  const browser = await chromium.launch({ headless: true });
  const results = [], errors = [];
  try {
    for (const width of [390, 1440]) {
      const p = await browser.newPage({ viewport: { width, height: 900 } });
      p.on('pageerror', e => errors.push(e.message));
      await p.goto(base);
      await p.evaluate(() => document.fonts.ready);
      const nav = width === 390 ? '#mobile-nav' : '.desktop-nav';
      if (width === 390) await p.locator('.menu-toggle').click();
      await p.locator(`${nav} a[href="#about"]`).click();
      assert(p.url().endsWith('#about'));
      const destination = await p.locator('#about').evaluate(e => e.getBoundingClientRect().top + scrollY - parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop));
      const intermediate = await p.evaluate(() => scrollY);
      assert(intermediate < destination - 50, 'anchor must not jump to the destination');
      await p.waitForFunction(y => Math.abs(scrollY - y) < 2, destination);
      assert.equal(await p.evaluate(() => document.activeElement.id), 'about');
      // Same hash can be selected again after manually scrolling away.
      await p.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
      if (width === 390) await p.locator('.menu-toggle').click();
      await p.locator(`${nav} a[href="#about"]`).click();
      await p.waitForTimeout(70);
      await p.emulateMedia({ reducedMotion: 'reduce' });
      await p.waitForFunction(y => Math.abs(scrollY - y) < 2, destination);
      await p.emulateMedia({ reducedMotion: 'no-preference' });
      // Native content-size transition, including closing and reversal.
      const faq = p.locator('.faq-list > details').first();
      await faq.scrollIntoViewIfNeeded();
      const height = () => faq.evaluate(e => e.getBoundingClientRect().height);
      const closed = await height();
      await faq.locator(':scope > summary').click();
      await p.waitForTimeout(65);
      const opening = await height();
      await p.waitForTimeout(260);
      const opened = await height();
      assert(opening > closed + 1 && opening < opened - 1, `opening ${closed}/${opening}/${opened}`);
      await faq.locator(':scope > summary').click();
      await p.waitForTimeout(65);
      const closing = await height();
      assert(closing > closed + 1 && closing < opened - 1, `closing ${closed}/${closing}/${opened}`);
      await faq.locator(':scope > summary').evaluate(e => e.dispatchEvent(new MouseEvent('click', { bubbles: true, detail: 1 })));
      await p.waitForTimeout(280);
      assert(await faq.evaluate(e => e.open));
      assert(Math.abs(await height() - opened) < 1);
      await faq.locator(':scope > summary').focus();
      await p.keyboard.press('Enter');
      assert(Math.abs(await height() - closed) < 1, 'keyboard closes immediately');
      await faq.locator(':scope > summary').click();
      await p.waitForTimeout(50);
      await p.emulateMedia({ reducedMotion: 'reduce' });
      assert(Math.abs(await height() - opened) < 1, 'reduced motion finishes accordion');
      await p.emulateMedia({ reducedMotion: 'no-preference' });
      // The same transition works for nested jobs inside the native dialog.
      await p.locator('.service-trigger').first().click();
      const job = p.locator('dialog .job').first();
      const jobClosed = await job.evaluate(e => e.getBoundingClientRect().height);
      await job.locator('summary').click();await p.waitForTimeout(65);
      const jobMiddle = await job.evaluate(e => e.getBoundingClientRect().height);
      await p.waitForTimeout(260);
      const jobOpen = await job.evaluate(e => e.getBoundingClientRect().height);
      assert(jobMiddle > jobClosed && jobMiddle < jobOpen);
      await p.locator('.dialog-close').click();await p.waitForTimeout(70);
      const opacity = await p.locator('dialog').evaluate(e => getComputedStyle(e).opacity);
      assert(+opacity > 0 && +opacity < 1);
      await p.waitForFunction(() => !document.querySelector('dialog').open);
      assert(await p.locator('.service-trigger').first().evaluate(e => e === document.activeElement));
      assert(await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
      results.push({ width, smoothAnchor: true, repeatedAnchor: true, reducedScroll: true, accordion: { closed, opening, opened, closing }, reversal: true, keyboardInstant: true, reducedAccordion: true, nestedJob: true, modalExit: true });
      await p.close();
    }
    assert.deepEqual(errors, []);
    fs.writeFileSync('docs-v2/smooth-checks.json', JSON.stringify({ results, errors }, null, 2));
    console.log(results);
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
