# Yap’s developer portfolio

Live site: https://yapperyap.github.io/developer-portfolio/

A static GitHub Pages portfolio featuring Dinnerplate.party, FlowDesk, SAT Study Room, and CacheBuddy. Expanded image-derived ambient gradients use eased radial masks, with a separate image-matched halo behind every screenshot, including both Dinnerplate editors. Halos fade and move with their image wrappers, match image-hover growth, and pulse very slightly over 18 seconds when motion is enabled; no static section glow remains. Soft masks and dither prevent hard section boundaries. A centered 1120px grid aligns copy and native-proportion images. Project titles link to the same destinations as their Open buttons without underlines, and the Yap wordmark never underlines. Project launch buttons say Open; accessible icon-only GitHub links use the locally served official Octicons mark. Slow gradient pulses and tiny sway/bounce loops complement viewport-triggered reveals, native sticky project holds, and subtle scroll-linked image zoom. These animations use transforms, independent transform properties, or opacity—not layout—and never intercept scrolling. With motion enabled, project copy and screenshots reveal on entry and hide again off screen; projects that fit the viewport hold for 65svh of additional scroll. Motion off or no JavaScript keeps all content visible in normal flow. Image frames, actual text words, and buttons enlarge uniformly on X/Y/Z and shrink smoothly on exit without reflow. Empty paragraph and heading frames are not hover targets. Text/button scale transitions remain independent of scroll/float animations. Reduced motion disables effects by default, but Toggle Motion explicitly enables them for the current visit; touch-only devices skip hover enlargement. Run `python test_hover.py` to verify real-pointer growth, intermediate transition states, and smooth return across both pages. Toggle Motion controls the effects and the half-speed Matrix background; the new decorative effects respect reduced motion and stay static without JavaScript. View-timeline image zoom is progressive; unsupported browsers keep the same scene layout without that zoom. The single-row phone header uses a native disclosure menu with Escape, focus-return, outside-click, and link-close enhancements.

## Preview locally

Run `python3 -m http.server 8000 --directory docs` from the repository root, then open http://localhost:8000. The site has no build step or runtime dependencies.

GitHub Pages publishes the `/docs` directory from `main`. All assets, including licensed fonts, are served locally; no JavaScript is required for content or navigation. The optional background uses a small local script with no continuous animation loop, external requests, or storage. The [site notice](docs/site-notice.html) describes privacy, accessibility, and font licenses. Keep redesign changes on the local preview branch until manual approval; pushing changes to `main` can publish the site.

## Checks

Run `python3 test_portfolio.py` for project entries, destinations, local assets, accessibility attributes, and anchors. Run `node --test test_matrix.cjs` for scroll speed, initial state, pause/resume, and bounded draw work. With Playwright installed, the local server on port 8765, and the headed automation profile exposing loopback CDP on port 9222, run `python test_layout.py` for full-bleed sections, gradient overlap, column and navigation alignment, mobile stacking, natural image ratios, and overflow at 14 widths from 320–2560px. Run `python test_image_reservation.py` to block image requests and verify that slow or unloaded screenshots keep their correct geometry. Browser QA also covers keyboard navigation, no-JavaScript use, console errors, gradient-seam pixel sampling, and axe-core accessibility checks.

Additional browser checks: `python test_scroll_icons.py` verifies the 25% halo extension, every image halo, icon-only GitHub links with accessible names, exact Open labels, real scroll-linked transforms, pause behavior, and reduced-motion fallback. `python test_polish.py`, `python test_motion.py`, and `python test_menu.py` cover hover return, shared motion controls, single-row portrait headers, and the native mobile menu with and without JavaScript.

`python test_interaction_scenes.py` checks uniform XYZ scaling, tight text hover hit areas, removed labels, reveal/hide behavior, real sticky holds, and accessibility fallbacks. `python test_scene_qa.py` checks keyboard reachability, every pinned project’s actual content bounds at phone/tablet/desktop sizes, accessibility scans, and viewport screenshots.

`python test_project_links_glows.py` verifies every project title matches its Open destination, title/logo hover styling, real-time description hover on all projects, tiny image-halo pulses, matched image/glow hover scaling, scene fade-out, and reduced-motion pause.

## Design references

- [Vercel Web Interface Guidelines](https://github.com/vercel-labs/web-interface-guidelines)
- [Awesome Web Design](https://github.com/brandonhimpfen/awesome-web-design)
- [Anthropic frontend-design skill](https://github.com/anthropics/skills/tree/main/skills/frontend-design)
- [Vercel web-design-guidelines skill](https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines)
- [TasteSkill](https://github.com/Leonxlnx/taste-skill), used for typography selection, grid, palette, motion, and copy/browser auditing; the portfolio preserves real project content and pins scenes only when their measured content fits the viewport.

Optional development skills are kept locally in `.agents/skills/`; local tooling and audit outputs are excluded from publication. Apple’s general principles of typography, space, and product-led presentation inform this original composition; no Apple branding or proprietary assets are used.
