"""Keep image geometry stable before lazy images arrive, including slow networks."""
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser=p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context=browser.new_context(viewport={'width':1440,'height':1000})
    context.route('**/*.webp',lambda route:route.abort())
    page=context.new_page()
    page.goto('http://127.0.0.1:8765/',wait_until='networkidle')
    failures=page.locator('img').evaluate_all('''els=>els.flatMap(e=>{
      const r=e.getBoundingClientRect();
      const expected=Number(e.getAttribute('width'))/Number(e.getAttribute('height'));
      return Math.abs(r.width/r.height-expected)>.02 ? [{src:e.getAttribute('src'),width:r.width,height:r.height,expected}] : [];
    })''')
    context.close()
    print('Image reservation problems:',failures)
    assert not failures,'Images must reserve their natural aspect ratio even before loading'
