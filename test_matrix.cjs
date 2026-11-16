const assert = require('node:assert/strict');
const { test } = require('node:test');
const { createRainGlyphs, advanceScroll } = require('./docs/matrix.js');
const vm = require('node:vm');
const fs = require('node:fs');

test('Motion follows accessibility defaults until the user explicitly toggles it', () => {
  for (const reducedMotion of [false, true]) {
    const handlers = {};
    const root = { dataset: {} };
    const toggle = { hidden: true, setAttribute(name, value) { this[name] = value; }, addEventListener(name, fn) { handlers[name] = fn; } };
    const context = { setTransform() {}, clearRect() {}, fillText() {} };
    vm.runInNewContext(fs.readFileSync(require.resolve('./docs/matrix.js'), 'utf8'), {
      document: { documentElement: root, hidden: false, querySelector: selector => selector === '#matrix-toggle' ? toggle : { getContext: () => context }, addEventListener() {} },
      matchMedia: () => ({ matches: reducedMotion, addEventListener(name, fn) { handlers.preference = fn; } }),
      scrollY: 0, innerWidth: 390, innerHeight: 844, devicePixelRatio: 1,
      requestAnimationFrame: () => 1, addEventListener() {}
    });
    assert.equal(toggle['aria-pressed'], String(!reducedMotion), `accessibility default with reducedMotion=${reducedMotion}`);
    assert.equal(toggle.textContent, 'Toggle Motion');
    assert.equal(root.dataset.motionPaused, String(reducedMotion));
    handlers.preference({ matches: !reducedMotion });
    assert.equal(root.dataset.motionPaused, String(!reducedMotion));
    handlers.preference({ matches: reducedMotion });
    handlers.click();
    assert.equal(toggle['aria-pressed'], String(reducedMotion));
    assert.equal(toggle.textContent, 'Toggle Motion');
    assert.equal(root.dataset.motionPaused, String(!reducedMotion));
    handlers.preference({ matches: !reducedMotion });
    assert.equal(root.dataset.motionPaused, String(!reducedMotion), 'manual choice survives accessibility changes');
    handlers.click();
    assert.equal(toggle['aria-pressed'], String(!reducedMotion));
  }
});

test('Scroll rain eases toward the latest position and then stops', () => {
  let position = 0;
  const next = advanceScroll(position, 500, 16);
  assert.ok(next > 0 && next < 500);
  for (let frame = 0; frame < 120; frame++) position = advanceScroll(position, 500, 16);
  assert.equal(position, 500);
  assert.equal(advanceScroll(500, 500, 16), 500);
  assert.ok(advanceScroll(500, 0, 16) < 500);
});

test('Matrix glyph positions respond to scroll and reverse deterministically', () => {
  const start = createRainGlyphs(1440, 900, 0, false);
  const scrolled = createRainGlyphs(1440, 900, 500, false);
  assert.ok(start.length > 0);
  assert.notDeepEqual(start, scrolled);
  assert.deepEqual(start, createRainGlyphs(1440, 900, 0, false));
});

test('Rain moves at half its original scroll speed and refreshes its characters', () => {
  const start = createRainGlyphs(1440, 900, 0, false);
  const next = createRainGlyphs(1440, 900, 1, false);
  const column = start[0].x;
  const originalSpeed = 1.1 + (104729 % 65521 % 9) * 0.16;
  assert.ok(Math.abs((next.find(g => g.x === column).y - start[0].y) - originalSpeed * 0.5) < 1e-8);
  const later = createRainGlyphs(1440, 900, 64, false);
  assert.notEqual(start[0].character, later.find(g => g.x === column).character);
});

test('Reduced motion freezes the background regardless of scroll position', () => {
  assert.deepEqual(createRainGlyphs(390, 844, 0, true), createRainGlyphs(390, 844, 1400, true));
});

test('Glyphs remain within a bounded viewport and draw work stays bounded', () => {
  for (const [width, height] of [[320, 900], [390, 844], [1440, 900], [3840, 2160]]) {
    const glyphs = createRainGlyphs(width, height, 1000000, false);
    assert.ok(glyphs.length <= 4000);
    assert.ok(glyphs.every(g => g.x >= 0 && g.x <= width && g.y >= -20 && g.y <= height + 20));
    assert.ok(glyphs.every(g => g.opacity >= 0 && g.opacity <= 1));
  }
});
