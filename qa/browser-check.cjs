const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const output = path.resolve(__dirname, '../.site-qa');
fs.mkdirSync(output, { recursive: true });
const base = process.env.FINSKILLS_PREVIEW_URL || 'http://127.0.0.1:5188';
const catalog = JSON.parse(fs.readFileSync(path.resolve(__dirname, '../dist/data/catalog.json'), 'utf8'));
const total = catalog.skills.length;
const failures = [];
const checks = [];
const check = name => checks.push(name);
const row = id => '.skill-row[data-skill-id="' + id + '"]';

(async () => {
  const browser = await chromium.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: true
  });
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' });
    await context.addInitScript(() => {
      Object.defineProperty(navigator, 'clipboard', { configurable: true, value: {
        writeText: async text => { if (window.__denyClipboard) throw new Error('QA denied'); window.__copiedExample = text; }
      } });
    });
    const page = await context.newPage();
    page.on('pageerror', error => failures.push(error.message));
    page.on('console', message => { if (message.type() === 'error') failures.push(message.text()); });
    const count = async n => { await page.waitForFunction(n => document.querySelectorAll('.skill-row').length === n, n); };
    await page.goto(base, { waitUntil: 'networkidle' });
    await count(total);
    assert.equal(await page.locator('html').getAttribute('lang'), 'zh-CN');
    await page.screenshot({ path: path.join(output, 'home-zh-desktop.png') });
    check('Chinese catalog loads every catalog skill');

    await page.locator('#search').fill('Discounted cash flow valuation model');
    await page.locator(row('dcf-model')).waitFor();
    assert((await page.locator('.skill-row').count()) < total);
    await page.locator('#search').fill('被投企业经营与契约监测');
    await page.locator(row('portfolio-monitoring')).waitFor();
    assert((await page.locator('.skill-row').count()) < total);
    await page.locator('#search').fill('no-such-skill-xyz');
    await page.locator('.empty-state').waitFor();
    await page.locator('[data-reset]').click();
    await count(total);
    check('Both languages are searchable; empty state and reset work');

    for (const [category, expected] of [...new Set(catalog.skills.map(s => s.category))].map(category => [category, catalog.skills.filter(s => s.category === category).length])) {
      await page.locator('[data-category="' + category + '"]').click();
      await count(expected);
    }
    await page.locator('#clear-filters').click();
    for (const [workflow, expected] of Object.entries({earnings:['earnings','research','valuation'],valuation:['valuation','earnings'],portfolio:['portfolio']}).map(([key,categories]) => [key,catalog.skills.filter(s => categories.includes(s.category)).length])) {
      await page.locator('[data-workflow="' + workflow + '"]').click();
      await count(expected);
      assert.equal(new URL(page.url()).searchParams.get('workflow'), workflow);
    }
    await page.locator('#clear-workflow').click();
    await count(total);
    check('All category filters and three task bundles match the catalog');

    for (const source of catalog.sources) {
      await page.locator('#source-filter').selectOption(source.repository);
      await count(catalog.skills.filter(s => s.repository === source.repository).length);
      assert.equal(new URL(page.url()).searchParams.get('repo'), source.repository);
    }
    await page.reload({waitUntil:'networkidle'});
    assert.equal(await page.locator('#source-filter').inputValue(), catalog.sources.at(-1).repository);
    await page.locator('#clear-filters').click();
    await count(total);
    assert.equal(await page.locator('.source-card').count(), catalog.sources.length);
    const sourceLinks = await page.locator('.source-repository-link').evaluateAll(links => links.map(a => a.href));
    for (const source of catalog.sources) assert(sourceLinks.includes(source.repository + '/tree/' + source.commit));
    await page.locator('[data-repository]').first().click();
    await count(catalog.skills.filter(s => s.repository === catalog.sources[0].repository).length);
    await page.locator('#clear-filters').click();
    await count(total);
    check('Repository filters persist, source cards link to pinned originals and reset works');

    await page.locator(row('dcf-model') + ' [data-save]').click();
    assert.equal(await page.locator('#saved-count').innerText(), '1');
    await page.locator('#saved-header').click();
    await count(1);
    await page.reload({ waitUntil: 'networkidle' });
    await count(1);
    await page.locator(row('dcf-model') + ' [data-save]').click();
    await page.locator('.empty-state').waitFor();
    assert.equal(await page.locator('#saved-count').innerText(), '0');
    await page.locator('#clear-filters').click();
    await count(total);
    check('Shortlist persists across reload and removes items correctly');

    for (const id of ['equity-earnings-update', 'earnings-preview', 'initiating-coverage', 'catalyst-calendar']) {
      await page.locator(row(id) + ' [data-compare]').click();
    }
    assert.equal(await page.locator('[data-compare][aria-pressed="true"]').count(), 3);
    assert.match(await page.locator('#toast').innerText(), /最多比较三个/);
    await page.locator('#compare-open').click();
    assert.equal(await page.locator('#compare-dialog[open]').count(), 1);
    assert.equal(await page.locator('.comparison-table thead th').count(), 4);
    assert.match(await page.locator('.comparison-table').innerText(), /尚未执行验证/);
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('#compare-dialog[open]').count(), 0);
    await page.locator('#compare-clear').click();
    assert.equal(await page.locator('#compare-bar').isVisible(), false);
    check('Comparison supports three items, shows boundaries and closes with Escape');

    for (const skill of catalog.skills) {
      await page.locator(row(skill.id) + ' .skill-title').click();
      assert.equal(await page.locator('#detail-title').innerText(), skill.name);
      const links = await page.locator('#detail-dialog a').evaluateAll(links => links.map(a => a.href));
      assert(links.includes(skill.sourceUrl) && links.includes(skill.repository) && links.includes(skill.licenseUrl));
      assert(links.includes(skill.repository + '/tree/' + skill.commit));
      assert(links.every(url => url.startsWith('https://github.com/')));
      assert.match(await page.locator('#detail-dialog').innerText(), /实际执行尚未验证/);
      await page.locator('#copy-example').click();
      assert.equal(await page.evaluate(() => window.__copiedExample), skill.example);
      await page.keyboard.press('Escape');
    }
    await page.locator(row('dcf-model') + ' .skill-title').click();
    await page.evaluate(() => { window.__denyClipboard = true; });
    await page.locator('#copy-example').click();
    assert.equal(await page.evaluate(() => window.getSelection().toString()), catalog.skills.find(s => s.id === 'dcf-model').example);
    await page.keyboard.press('Escape');
    check('All catalog details retain valid pinned source, author and license links; copying and fallback work');

    await page.locator('#language-toggle').click();
    assert.equal(await page.locator('html').getAttribute('lang'), 'en');
    await page.reload({ waitUntil: 'networkidle' });
    await count(total);
    assert.equal(await page.locator('html').getAttribute('lang'), 'en');
    for (const skill of catalog.skills) {
      await page.locator(row(skill.id) + ' .skill-title').click();
      assert.equal(await page.locator('#detail-title').innerText(), skill.nameEn);
      const text = await page.locator('#detail-dialog').innerText();
      assert(text.includes(skill.methodEn) && text.includes(skill.exampleEn));
      assert(!/[\u4e00-\u9fff]/.test(text));
      await page.keyboard.press('Escape');
    }
    await page.locator('#search').fill('财报');
    await page.waitForFunction(total => document.querySelectorAll('.skill-row').length > 0 && document.querySelectorAll('.skill-row').length < total, total);
    const searchCount = await page.locator('.skill-row').count();
    await page.reload({ waitUntil: 'networkidle' });
    await count(searchCount);
    assert.equal(await page.locator('#search').inputValue(), '财报');
    await page.locator('#clear-filters').click();
    await count(total);
    await page.evaluate(() => { document.activeElement.blur(); });
    await page.keyboard.press('/');
    assert.equal(await page.locator('#search').evaluate(node => node === document.activeElement), true);
    await page.locator('#sort').selectOption('name');
    const names = await page.locator('.skill-title').allTextContents();
    assert.deepEqual(names, [...names].sort((a, b) => a.localeCompare(b, 'en')));
    await page.locator('#sort').selectOption('curated');
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.screenshot({ path: path.join(output, 'home-en-desktop.png') });
    await page.locator('#catalog').scrollIntoViewIfNeeded();
    await page.screenshot({ path: path.join(output, 'catalog-en-desktop.png') });
    check('English details are fully translated; language, search URL, keyboard shortcut and sorting work');

    for (const selector of ['#standards-bottom', '#about-button']) {
      await page.locator(selector).click();
      assert.equal(await page.locator('#info-dialog[open]').count(), 1);
      assert(!/[\u4e00-\u9fff]/.test(await page.locator('#info-dialog').innerText()));
      if (selector === '#about-button') {
        const licenseHrefs = await page.locator('#info-dialog a').evaluateAll(links => links.map(a => a.getAttribute('href')));
        assert.equal(licenseHrefs.length, catalog.sources.length);
        for (const licenseHref of licenseHrefs) assert.equal((await context.request.get(base + licenseHref)).status(), 200);
      }
      await page.keyboard.press('Escape');
    }
    check('Inclusion criteria and author/license attribution are visible in English');
    await page.locator('#sources').scrollIntoViewIfNeeded();
    await page.screenshot({ path: path.join(output, 'sources-en-desktop.png') });

    for (const width of [360, 390, 768, 1024, 1440]) {
      for (const language of ['zh', 'en']) {
        const mobile = await context.newPage();
        mobile.on('pageerror', error => failures.push(error.message));
        await mobile.setViewportSize({ width, height: 844 });
        await mobile.goto(base + '?lang=' + language, { waitUntil: 'networkidle' });
        await mobile.waitForSelector('.skill-row');
        const overflow = await mobile.evaluate(() => ({ width: innerWidth, scroll: document.documentElement.scrollWidth }));
        assert(overflow.scroll <= overflow.width + 1, JSON.stringify({ language, ...overflow }));
        if (width === 390) {
          await mobile.screenshot({ path: path.join(output, 'home-' + language + '-mobile.png') });
          await mobile.locator(row('portfolio-monitoring') + ' .skill-title').click();
          const bounds = await mobile.locator('#detail-dialog').boundingBox();
          assert(bounds.x >= 0 && bounds.x + bounds.width <= width + 1);
          await mobile.screenshot({ path: path.join(output, 'detail-' + language + '-mobile.png') });
          await mobile.keyboard.press('Escape');
          await mobile.locator('[data-category="valuation"]').click();
          assert.equal(await mobile.locator('.skill-row').count(), catalog.skills.filter(s => s.category === 'valuation').length);
        }
        await mobile.close();
      }
    }
    check('Chinese and English layouts fit five viewport widths; mobile detail and filtering work');

    const retry = await context.newPage();
    let attempts = 0;
    await retry.route('**/data/catalog.json', async route => {
      if (attempts++ === 0) await route.fulfill({ status: 503, contentType: 'application/json', body: '{}' });
      else await route.continue();
    });
    await retry.goto(base);
    await retry.locator('#retry-catalog').waitFor();
    await retry.locator('#retry-catalog').click();
    await retry.waitForFunction(total => document.querySelectorAll('.skill-row').length === total, total);
    await retry.close();
    check('A failed catalog request can be retried successfully');
    assert.deepEqual(failures, []);
    const report = { status: 'passed', checks, consoleErrors: failures, screenshotDirectory: output, browser: await browser.version() };
    fs.writeFileSync(path.join(output, 'browser-report.json'), JSON.stringify(report, null, 2));
    console.log(JSON.stringify(report, null, 2));
    await context.close();
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
