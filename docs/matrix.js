/* Scroll-driven decoration. No timers, network access, or persistent state. */
(function () {
  'use strict';
  function createRainGlyphs(width, height, scroll, reducedMotion) {
    const glyphs = [];
    const spacing = Math.max(24, width / 110);
    const characters = '01{}[]<>/+=:ABCDEF';
    const distance = reducedMotion ? 0 : scroll;
    const phase = Math.floor(distance / 32);
    for (let column = 0; column * spacing + 4 < width; column++) {
      const seed = (column * 7919 + 104729) % 65521;
      const length = 20 + seed % 16;
      const cycle = height + length * 20;
      const speed = 1.1 + (seed % 9) * 0.16;
      const head = ((seed * 3.17 + distance * speed) % cycle + cycle) % cycle;
      for (let row = 0; row < length; row++) {
        const y = head - row * 20;
        if (y < -20 || y > height + 20) continue;
        glyphs.push({
          x: column * spacing + 4,
          y,
          character: characters[((seed + row * 13 + phase) % characters.length + characters.length) % characters.length],
          opacity: row === 0 ? 1 : (1 - row / length) * 0.65
        });
      }
    }
    return glyphs;
  }

  function advanceScroll(current, target, elapsed) {
    if (Math.abs(target - current) < 0.25) return target;
    return current + (target - current) * (1 - Math.exp(-Math.min(elapsed, 50) / 90));
  }

  if (typeof module !== 'undefined' && module.exports) module.exports = { createRainGlyphs, advanceScroll };
  if (typeof document === 'undefined') return;
  const canvas = document.querySelector('#matrix-background');
  const toggle = document.querySelector('#matrix-toggle');
  if (!canvas || !toggle) return;
  const context = canvas.getContext('2d', { alpha: true });
  if (!context) return;
  const preference = matchMedia('(prefers-reduced-motion: reduce)');
  let paused = preference.matches;
  let frozenScroll = scrollY;
  let visualScroll = scrollY;
  let targetScroll = scrollY;
  let lastTime = 0;
  let frame = 0;
  let width = 0;
  let height = 0;
  let pixelRatio = 1;

  function draw(timestamp) {
    frame = 0;
    if (!paused) visualScroll = advanceScroll(visualScroll, targetScroll, lastTime ? timestamp - lastTime : 16);
    lastTime = timestamp;
    context.clearRect(0, 0, width, height);
    context.font = '13px ui-monospace, monospace';
    const glyphs = createRainGlyphs(width, height, paused ? frozenScroll : visualScroll, false);
    for (const glyph of glyphs) {
      context.fillStyle = glyph.opacity === 1 ? '#c6ffd5' : `rgba(46, 240, 110, ${glyph.opacity})`;
      context.fillText(glyph.character, glyph.x, glyph.y);
    }
    if (!paused && Math.abs(targetScroll - visualScroll) > 0.01 && !document.hidden) frame = requestAnimationFrame(draw);
    else lastTime = 0;
  }
  function schedule() {
    if (!frame && !document.hidden) frame = requestAnimationFrame(draw);
  }
  function resize() {
    width = innerWidth;
    height = innerHeight;
    pixelRatio = Math.min(devicePixelRatio || 1, 2);
    canvas.width = Math.round(width * pixelRatio);
    canvas.height = Math.round(height * pixelRatio);
    context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
    schedule();
  }
  function updateToggle() {
    toggle.hidden = false;
    toggle.setAttribute('aria-pressed', String(!paused));
    toggle.textContent = paused ? 'Matrix: paused' : 'Matrix: scroll';
  }
  toggle.addEventListener('click', () => {
    if (!paused) frozenScroll = visualScroll;
    paused = !paused;
    targetScroll = scrollY;
    updateToggle();
    schedule();
  });
  preference.addEventListener('change', () => {
    paused = preference.matches;
    frozenScroll = scrollY;
    visualScroll = scrollY;
    targetScroll = scrollY;
    updateToggle();
    schedule();
  });
  addEventListener('scroll', () => { targetScroll = scrollY; if (!paused) schedule(); }, { passive: true });
  addEventListener('resize', resize, { passive: true });
  document.addEventListener('visibilitychange', () => { if (!document.hidden) schedule(); });
  updateToggle();
  resize();
})();
