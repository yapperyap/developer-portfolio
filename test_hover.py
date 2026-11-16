"""Real-pointer hover regression: smooth growth and reversal on site content."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

SCALE = '''e=>{const s=getComputedStyle(e);const m=new DOMMatrix(s.transform);return Math.hypot(m.a,m.b)*(s.scale==='none'?1:parseFloat(s.scale))}'''
SAMPLE = '''e=>{
  const a=e.getAnimations().find(a=>a instanceof CSSTransition && ['scale','transform'].includes(a.transitionProperty));
  if(!a) return null;
  const read=()=>{const s=getComputedStyle(e),m=new DOMMatrix(s.transform);return Math.hypot(m.a,m.b)*(s.scale==='none'?1:parseFloat(s.scale))};
  const duration=a.effect.getTiming().duration;
  a.pause();a.currentTime=duration/2;const middle=read();
  a.currentTime=duration;const end=read();a.finish();
  return {middle,end,duration};
}'''
results=[]
with sync_playwright() as p:
    b=p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    ctx=b.new_context(viewport={'width':1440,'height':1000},reduced_motion='no-preference')
    page=ctx.new_page()
    for route in ['', 'site-notice.html']:
        page.goto('http://127.0.0.1:8765/'+route,wait_until='networkidle')
        page.evaluate('document.fonts.ready')
        page.wait_for_timeout(700)
        # Freeze independent decorative loops, not the pointer feedback under test.
        page.evaluate('document.getAnimations().filter(a=>a.animationName).forEach(a=>a.pause())')
        targets=page.locator('.hover-word,.button:visible,.product-window')
        for element in targets.all():
            element.evaluate('e=>e.scrollIntoView({block:"center",behavior:"instant"})')
            page.mouse.move(1,50)
            page.wait_for_timeout(30)
            baseline=element.evaluate(SCALE)
            element.hover(force=True)
            grow=element.evaluate(SAMPLE)
            label=element.evaluate('e=>e.tagName+" "+(e.textContent.trim().slice(0,45)||e.className)')
            assert grow is not None,('No grow transition',label)
            assert baseline<grow['middle']<grow['end'],(label,baseline,grow)
            page.mouse.move(1,50)
            shrink=element.evaluate(SAMPLE)
            assert shrink is not None,('No shrink transition',label)
            assert baseline<shrink['middle']<grow['end'],(label,shrink,grow)
            assert abs(shrink['end']-baseline)<.001,(label,shrink,baseline)
            results.append({'route':route,'target':label,'grow':grow,'shrink':shrink})
            Path('/home/user/.hermes/cache/scratch/hover-results.json').write_text(json.dumps(results,indent=2))
    # Touch/reduced-motion users do not get sticky or animated enlargement.
    page.emulate_media(reduced_motion='reduce')
    heading=page.locator('h1 .hover-word').first
    page.mouse.move(1,50)
    heading.evaluate('e=>e.scrollIntoView({block:"center",behavior:"instant"})')
    baseline=heading.evaluate(SCALE)
    heading.hover(force=True)
    assert heading.evaluate(SCALE)==baseline
    ctx.close()
print('Smooth hover growth and return verified for',len(results),'text/image/button targets across both pages.')
