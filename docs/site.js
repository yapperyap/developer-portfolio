/* Native navigation and visible content remain usable without JavaScript. */
(() => {
  'use strict';
  const menu = document.querySelector('.mobile-menu');
  if (menu) {
    menu.addEventListener('click', event => {
      if (event.target.closest('a')) menu.open = false;
    });
    document.addEventListener('click', event => {
      if (!menu.contains(event.target)) menu.open = false;
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && menu.open) {
        menu.open = false;
        menu.querySelector('summary').focus();
      }
    });
    matchMedia('(min-width: 761px)').addEventListener('change', event => {
      if (event.matches) menu.open = false;
    });
  }

  // Wrap words, not full-width paragraphs: whitespace and semantic elements stay
  // intact, and empty layout space no longer acts as a text-hover target.
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      const parent = node.parentElement;
      return parent && /\S/.test(node.data) &&
        parent.closest('h1,h2,h3,p,.wordmark') &&
        !parent.closest('.button,.hover-word,script,style')
        ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
    }
  });
  const textNodes = [];
  while (walker.nextNode()) textNodes.push(walker.currentNode);
  for (const node of textNodes) {
    const fragment = document.createDocumentFragment();
    for (const part of node.data.match(/\S+|\s+/g)) {
      if (/\S/.test(part)) {
        const word = document.createElement('span');
        word.className = 'hover-word';
        word.textContent = part;
        fragment.append(word);
      } else fragment.append(document.createTextNode(part));
    }
    node.replaceWith(fragment);
  }

  // Native sticky positioning provides a short scroll runway without consuming
  // wheel/touch events. Tall layouts stay in normal flow, so nothing is trapped.
  const root = document.documentElement;
  const projects = Array.from(document.querySelectorAll('.project'));
  const pieces = Array.from(document.querySelectorAll('.intro h1,.intro-bottom > p,.intro-actions,.project-copy,.image-halo,.about > h2,.about > div'));
  if (!projects.length || !('IntersectionObserver' in window)) return;
  pieces.forEach(piece => piece.classList.add('scene-piece'));
  let observer;
  let pending = false;
  function layoutScenes() {
    pending = false;
    if (observer) observer.disconnect();
    const enabled = root.dataset.motionPaused === 'false';
    delete root.dataset.scrollScenes;
    for (const project of projects) {
      project.classList.remove('is-pinned', 'scene-candidate');
      project.style.removeProperty('--scene-height');
    }
    if (!enabled) return;
    const header = document.querySelector('.site-header');
    const headerHeight = header ? header.getBoundingClientRect().height : 0;
    const available = innerHeight - headerHeight;
    if (available >= 600) {
      for (const project of projects) {
        project.classList.add('scene-candidate');
        const panel = project.querySelector('.project-inner');
        const height = panel.offsetHeight;
        project.classList.remove('scene-candidate');
        if (height <= available + 1) {
          project.style.setProperty('--scene-height', height + 'px');
          project.classList.add('is-pinned');
        }
      }
    }
    for (const piece of pieces) {
      const box = piece.getBoundingClientRect();
      piece.classList.toggle('is-revealed', box.bottom > headerHeight && box.top < innerHeight * .94);
    }
    observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (entry.intersectionRatio >= .12) entry.target.classList.add('is-revealed');
        else if (!entry.isIntersecting) entry.target.classList.remove('is-revealed');
      }
    }, { rootMargin: `-${headerHeight}px 0px -6% 0px`, threshold: [0, .12] });
    root.dataset.scrollScenes = 'true';
    root.classList.add('scene-setup');
    void root.offsetHeight; // Establish initial hidden poses before transitions.
    root.classList.remove('scene-setup');
    pieces.forEach(piece => observer.observe(piece));
  }
  function scheduleLayout() {
    if (!pending) { pending = true; requestAnimationFrame(layoutScenes); }
  }
  new MutationObserver(scheduleLayout).observe(root, { attributes: true, attributeFilter: ['data-motion-paused'] });
  addEventListener('resize', scheduleLayout, { passive: true });
  if (document.fonts) document.fonts.ready.then(scheduleLayout);
  if ('ResizeObserver' in window) {
    const sizes = new ResizeObserver(scheduleLayout);
    projects.forEach(project => sizes.observe(project.querySelector('.project-inner')));
  }
  layoutScenes();
})();
