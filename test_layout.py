"""Browser regression checks. Run with Playwright installed and local server at :8765."""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    page = browser.contexts[0].new_page()
    failures = []
    for width in [320, 360, 390, 640, 700, 768, 820, 960, 1000, 1024, 1280, 1440, 1920, 2560]:
        page.set_viewport_size({'width': width, 'height': 1000})
        page.goto('http://127.0.0.1:8765/', wait_until='networkidle')
        page.locator('img').evaluate_all('(els)=>els.forEach(e=>e.loading="eager")')
        page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)')
        issues = page.evaluate('''() => {
          const issues=[];
          const width=document.documentElement.clientWidth;
          if(document.documentElement.scrollWidth > width+1) issues.push('horizontal overflow');
          for(const article of document.querySelectorAll('article')) {
            const r=article.getBoundingClientRect();
            if(Math.abs(r.x)>1 || Math.abs(r.width-width)>1) issues.push(article.id+': background not full bleed');
            const style=getComputedStyle(article);
            if(style.backgroundColor!=='rgba(0, 0, 0, 0)') issues.push(article.id+': opaque section blocks neighboring gradients');
            if(style.isolation==='isolate') issues.push(article.id+': isolated section prevents gradient merging');
            if(getComputedStyle(article,'::before').content!=='none') issues.push(article.id+': static section glow remains');
            for(const halo of article.querySelectorAll('.image-halo')) {
              const glow=getComputedStyle(halo,'::before');
              if(parseFloat(glow.height)<halo.clientHeight*1.4) issues.push(article.id+': image halo does not extend past its frame');
            }
          }
          for(const node of document.querySelectorAll('h1,h2,h3,.button,.project-visual')){
            const r=node.getBoundingClientRect();
            if(r.left < -1 || r.right > width+1) issues.push(node.tagName+': off-screen content');
            // Image containers intentionally include out-of-frame decorative halos.
            // Check text overflow on text/controls, not a pseudo-element's paint bounds.
            if(node.matches('h1,h2,h3,.button') && node.scrollWidth>node.clientWidth+1) issues.push(node.tagName+': internal text overflow');
          }
          if(!document.querySelector('header #matrix-toggle')) issues.push('motion control is not in the top bar');
          for(const title of document.querySelectorAll('.project h2')) {
            const r=title.getBoundingClientRect();
            if(title.clientHeight > parseFloat(getComputedStyle(title).lineHeight)+1) issues.push(title.textContent+': project title wraps');
            if(title.scrollWidth > title.clientWidth+1) issues.push(title.textContent+': project title overflows');
          }
          const nav=document.querySelector('nav').getBoundingClientRect();
          const header=document.querySelector('.header-inner').getBoundingClientRect();
          if(nav.right>header.right+1) issues.push('navigation not aligned to content edge');
          for(const img of document.images) {
            const s=getComputedStyle(img),r=img.getBoundingClientRect();
            const w=r.width-parseFloat(s.borderLeftWidth)-parseFloat(s.borderRightWidth);
            const h=r.height-parseFloat(s.borderTopWidth)-parseFloat(s.borderBottomWidth);
            if(Math.abs(w/h-img.naturalWidth/img.naturalHeight)>.02) issues.push(img.getAttribute('src')+': distorted aspect ratio');
          }
          if(innerWidth<=700){
            const a=document.querySelector('.music-window').getBoundingClientRect();
            const b=document.querySelector('.photo-window').getBoundingClientRect();
            if(b.top<a.bottom-1) issues.push('mobile screenshots overlap');
            if(Math.abs(a.width-b.width)>1) issues.push('mobile screenshots have mismatched widths');
          }
          const lefts=Array.from(document.querySelectorAll('.project-copy')).map(e=>e.getBoundingClientRect().left);
          if(Math.max(...lefts)-Math.min(...lefts)>1) issues.push('project copy columns misaligned');
          return issues;
        }''')
        failures.extend(f'{width}px: {issue}' for issue in issues)
        print(width, issues or 'PASS')
    page.close()
    assert not failures, '\n'.join(failures)
