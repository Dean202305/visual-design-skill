// Optional: use a host-provided Playwright; no dependency install or network.
const assert = require('node:assert/strict');
const {execFileSync} = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {chromium} = require(process.env.VISUAL_DESIGN_PLAYWRIGHT_MODULE || 'playwright');
const script = path.resolve(__dirname, '../skills/visual-design/scripts/design_audit.py');
const python = process.env.PYTHON || 'python3';
const collector = execFileSync(python, [script, 'collector'], {encoding: 'utf8'});
const output = process.env.AUDIT_EVIDENCE_DIR || fs.mkdtempSync(path.join(os.tmpdir(), 'design-audit-browser-'));
fs.mkdirSync(output, {recursive: true});

(async () => {
  const options = {headless: true};
  if (process.env.VISUAL_DESIGN_BROWSER_CHANNEL) options.channel = process.env.VISUAL_DESIGN_BROWSER_CHANNEL;
  const browser = await chromium.launch(options);
  try {
    const page = await browser.newPage({viewport: {width: 1440, height: 900}});
    await page.setContent(`<!doctype html><html><style>
      body{font:16px system-ui;background:#fff;color:#171717}p{font-size:12px}
      .hidden{opacity:0}.digits{font-variant-numeric:tabular-nums}
    </style><body><h1>A real heading</h1><p>A project caption</p>
      <p class="digits">12345</p><div class="hidden"><p>hidden ancestor text</p></div>
      <textarea>private-editable-text</textarea><input value="private-input-value">
      <div contenteditable>private-editable-div</div><div id="host"></div>
      <script>document.querySelector('#host').attachShadow({mode:'open'}).innerHTML='<p>shadow text</p>'</script>
      <img alt="example" width="20" height="20" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20'%3E%3C/svg%3E">
    </body></html>`, {waitUntil: 'load'});
    const clean = await page.evaluate('(' + collector + ')()');
    assert.equal(clean.viewport.width, 1440);
    assert.equal(clean.images[0].status, 'loaded');
    assert.equal(clean.coverage.shadow_hosts, 1);
    const saved = JSON.stringify(clean);
    for (const secret of ['hidden ancestor text', 'private-editable-text', 'private-input-value', 'private-editable-div', 'shadow text']) {
      assert.ok(!saved.includes(secret), secret + ' must not enter evidence');
    }
    assert.ok(clean.text.some(row => row.sample === '12345' && row.numeric_variant.includes('tabular-nums')));
    fs.writeFileSync(path.join(output, 'desktop.json'), JSON.stringify(clean, null, 2));
    await page.screenshot({path: path.join(output, 'desktop.png')});
    await page.setViewportSize({width: 390, height: 844});
    await page.setContent('<!doctype html><body><p>Mobile view</p><div style="width:2500px">Intentional wide region</div><img width="32" height="32" src="data:image/png;base64,AA==">', {waitUntil: 'load'});
    const bad = await page.evaluate('(' + collector + ')()');
    assert.equal(bad.viewport.width, 390);
    assert.ok(bad.horizontal_overflow > 2000);
    assert.equal(bad.images[0].status, 'broken');
    fs.writeFileSync(path.join(output, 'mobile-broken.json'), JSON.stringify(bad, null, 2));
    await page.screenshot({path: path.join(output, 'mobile-broken.png')});
    let exitStatus = 0;
    try { execFileSync(python, [script, 'check', path.join(output, 'mobile-broken.json')], {stdio: 'pipe'}); }
    catch (error) {
      exitStatus = error.status;
      const report = JSON.parse(error.stdout.toString());
      assert.equal(report.failures[0].kind, 'broken_image');
      fs.writeFileSync(path.join(output, 'mobile-report.json'), JSON.stringify(report, null, 2));
    }
    assert.equal(exitStatus, 1);
    const cleanReport = JSON.parse(execFileSync(python, [script, 'check', path.join(output, 'desktop.json'), '--min-text', '14'], {encoding: 'utf8'}));
    assert.equal(cleanReport.status, 'needs_review');
    assert.ok(cleanReport.review.some(row => row.kind === 'below_project_text_threshold'));
    assert.equal(cleanReport.failures.length, 0);
    fs.writeFileSync(path.join(output, 'desktop-report.json'), JSON.stringify(cleanReport, null, 2));
    console.log(JSON.stringify({ok: true, views: ['1440x900', '390x844'], output}, null, 2));
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
