"""Real-time hover in the automation profile; regular-browser prefs may differ."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

READ='''e=>{const s=getComputedStyle(e),m=new DOMMatrix(s.transform);return {scale:Math.hypot(m.a,m.b)*(s.scale==='none'?1:parseFloat(s.scale)),hover:e.matches(':hover'),animations:e.getAnimations().map(a=>({name:a.animationName||a.transitionProperty,state:a.playState,time:String(a.currentTime)}))}}'''
with sync_playwright() as p:
    browser=p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    previews=[t for t in browser.contexts[0].pages if t.url.startswith('http://127.0.0.1:8765/') and 'site-notice' not in t.url]
    page=previews[0] if previews else browser.contexts[0].new_page()
    page.goto('http://127.0.0.1:8765/',wait_until='networkidle')
    toggle=page.locator('#matrix-toggle')
    if toggle.get_attribute('aria-pressed')=='false':toggle.click()
    results=[]
    for selector in ['h1 .hover-word','#dinnerplate-title .hover-word','#dinnerplate .description .hover-word','.product-window','#matrix-toggle']:
        element=page.locator(selector).first
        element.evaluate('e=>e.scrollIntoView({block:"center",behavior:"instant"})')
        page.mouse.move(1,50)
        page.wait_for_timeout(900)
        before=element.evaluate(READ)
        box=element.bounding_box()
        page.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2)
        page.wait_for_timeout(110)
        growing=element.evaluate(READ)
        page.wait_for_timeout(800)
        grown=element.evaluate(READ)
        page.mouse.move(1,50)
        page.wait_for_timeout(110)
        shrinking=element.evaluate(READ)
        page.wait_for_timeout(800)
        returned=element.evaluate(READ)
        record={'selector':selector,'before':before,'growing':growing,'grown':grown,'shrinking':shrinking,'returned':returned}
        results.append(record)
        Path('/home/user/.hermes/cache/scratch/visible-hover-results.json').write_text(json.dumps(results,indent=2))
        assert growing['hover'] and before['scale']<growing['scale']<grown['scale'],record
        assert before['scale']<shrinking['scale']<grown['scale'],record
        assert abs(returned['scale']-before['scale'])<.001,record
        print(selector,':',*[round(r['scale'],5) for r in [before,growing,grown,shrinking,returned]])
    page.evaluate('scrollTo({top:0,behavior:"instant"})')
    page.mouse.move(1,50)
    print('Real-time tight-text/image/button hover with decorative motion enabled: PASS')
