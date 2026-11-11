const motion = matchMedia('(prefers-reduced-motion: reduce)');
const stage = matchMedia('(width > 48rem)');
const sections = [...document.querySelectorAll('[data-project]')];
const previews = [...document.querySelectorAll('[data-preview]')];
const projectLinks = [...document.querySelectorAll('.stage-links a')];
let activeProject = 'dinnerplate';
let pendingFrame = 0;

function updatePreview() {
  pendingFrame = 0;
  if (!stage.matches) return;

  const triggerLine = innerHeight * 0.43;
  let nextProject = sections[0].dataset.project;
  for (const section of sections) {
    if (section.getBoundingClientRect().top <= triggerLine) {
      nextProject = section.dataset.project;
    }
  }

  if (nextProject === activeProject) return;
  activeProject = nextProject;

  for (const preview of previews) {
    preview.classList.toggle('is-active', preview.dataset.preview === activeProject);
  }
  for (const link of projectLinks) {
    if (link.hash === '#' + activeProject) {
      link.setAttribute('aria-current', 'location');
    } else {
      link.removeAttribute('aria-current');
    }
  }
}

function schedulePreview() {
  if (!pendingFrame && stage.matches) {
    pendingFrame = requestAnimationFrame(updatePreview);
  }
}

addEventListener('scroll', schedulePreview, { passive: true });
addEventListener('resize', schedulePreview, { passive: true });
stage.addEventListener('change', schedulePreview);
schedulePreview();

if (!motion.matches && 'IntersectionObserver' in window) {
  const reveal = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      entry.target.classList.add('revealed');
      reveal.unobserve(entry.target);
    }
  }, { threshold: 0.12 });

  for (const target of document.querySelectorAll('[data-reveal]')) {
    reveal.observe(target);
  }
}
