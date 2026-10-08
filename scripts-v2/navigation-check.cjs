// URL ownership: browser navigation must not be rewritten by dialog cleanup.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const base = process.env.BASE_URL || 'http://127.0.0.1:8765';
(async () => {
  const browser = await chromium.launch();
  const errors = [];
  try {
    const p = await browser.newPage({ reducedMotion: 'reduce' });
    p.on('pageerror', e => errors.push(e.message));
    await p.route('https://**/*', r => r.abort());
    async function hash(value) {
      await p.evaluate(value => { location.hash = value; }, value);
      await p.waitForFunction(value => {
        const target = document.querySelector(value);
        return value.startsWith('#service-')
          ? document.querySelector('dialog').open && target.querySelector('.service-content') === null
          : document.activeElement === target;
      }, value);
    }
    async function closedAt(value) {
      await p.waitForFunction(() => !document.querySelector('dialog').open);
      assert.equal(new URL(p.url()).hash, value);
      assert.equal(await p.locator('.service-card > .service-content').count(), 6);
      assert.equal(await p.locator('html').evaluate(e => e.classList.contains('service-modal-open')), false);
    }
    await p.goto(base + '/#about');
    await p.locator('.service-trigger').first().click();
    await p.keyboard.press('Escape');
    await closedAt('#about');
    await hash('#contacts');
    await hash('#service-repair');
    await p.keyboard.press('Escape');
    await closedAt('#contacts');

    // Switching groups preserves the section, but restores focus to the current group.
    await hash('#service-maintenance');
    await hash('#service-repair');
    await p.keyboard.press('Escape');
    await closedAt('#contacts');
    assert(await p.locator('#service-repair .service-trigger').evaluate(e => e === document.activeElement));

    // Back/Forward also traverses an entry without a fragment.
    await p.goto(base + '/');
    await p.locator('.service-trigger').first().click();
    await p.goBack();
    await closedAt('');
    await p.goForward();
    await p.waitForFunction(() => document.querySelector('dialog').open);
    assert.equal(new URL(p.url()).hash, '#service-maintenance');
    await hash('#service-repair');
    await p.goBack();
    await p.waitForFunction(() => document.querySelector('#service-maintenance .service-content') === null);
    assert.equal(new URL(p.url()).hash, '#service-maintenance');
    await p.goForward();
    await p.waitForFunction(() => document.querySelector('#service-repair .service-content') === null);
    assert.equal(new URL(p.url()).hash, '#service-repair');
    await p.keyboard.press('Escape');
    await closedAt('#services');

    // Fresh entry has no remembered section. Lifecycle cleanup preserves the URL.
    await p.goto(base + '/legal.html');
    await p.goto(base + '/#detail-remont-dvigatelya');
    await p.waitForFunction(() => document.querySelector('dialog').open);
    const directURL = p.url();
    await p.evaluate(() => dispatchEvent(new PageTransitionEvent('pagehide', { persisted: true })));
    assert.equal(p.url(), directURL);
    await p.evaluate(() => dispatchEvent(new PageTransitionEvent('pageshow', { persisted: true })));
    await p.waitForFunction(() => document.querySelector('dialog').open && document.querySelector('#detail-remont-dvigatelya').open);
    assert.equal(p.url(), directURL);
    await p.keyboard.press('Escape');
    await closedAt('#services');

    // A real leave-and-return covers the browser's history restoration path too.
    await hash('#service-repair');
    await p.goto(base + '/legal.html');
    await p.goBack();
    await p.waitForFunction(() => document.querySelector('dialog').open);
    assert.equal(new URL(p.url()).hash, '#service-repair');
    await p.keyboard.press('Escape');
    await closedAt('#services');

    await hash('#service-repair');
    await p.locator('dialog .job > summary').first().click();
    await p.locator('dialog [data-service]').first().click();
    await closedAt('#booking');
    assert(await p.locator('.form-context').isVisible());
    await p.waitForFunction(() => document.activeElement.id === 'booking');
    assert.equal(await p.locator('#replay-intro').count(), 0);
    assert.deepEqual(errors, []);
    const result = { staleHash: true, groupSwitch: true, backForward: true, directEntry: true,
      lifecycleEvents: true, realLeaveAndReturn: true, bookingContext: true, errors };
    fs.writeFileSync('docs-v2/navigation-checks.json', JSON.stringify(result, null, 2) + '\n');
    console.log(result);
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
