from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser=p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context=browser.new_context(reduced_motion='no-preference')
    page=context.new_page()
    page.goto('http://127.0.0.1:8765/',wait_until='networkidle')
    page.evaluate('document.fonts.ready')
    toggle=page.locator('#matrix-toggle')
    assert toggle.inner_text()=='Toggle Motion'
    for width,height in [(320,720),(360,800),(390,844),(600,1000),(768,1024),(820,1180),(1024,1366),(1440,1000),(1920,1080)]:
        page.set_viewport_size({'width':width,'height':height})
        checks=page.evaluate('''()=>{
          const header=document.querySelector('.header-inner');
          const controls=Array.from(header.querySelectorAll('a,button,summary')).filter(e=>e.getClientRects().length && getComputedStyle(e).visibility!=='hidden');
          const ys=controls.map(e=>{const r=e.getBoundingClientRect();return r.y+r.height/2});
          const title=document.querySelector('#dinnerplate-title').getBoundingClientRect();
          const body=document.querySelector('#dinnerplate .description').getBoundingClientRect();
          const motion=getComputedStyle(document.querySelector('#matrix-toggle'));
          const other=getComputedStyle(document.querySelector('nav .button'));
          return {singleRow:Math.max(...ys)-Math.min(...ys)<5,aligned:Math.abs(title.left-body.left)<1 && body.top>=title.bottom,
           matching:motion.fontFamily===other.fontFamily && motion.borderRadius===other.borderRadius,
           overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+1};
        }''')
        assert checks['singleRow'],(width,checks)
        assert checks['aligned'],(width,checks)
        assert checks['matching'],(width,checks)
        assert not checks['overflow'],(width,checks)
    page.set_viewport_size({'width':1440,'height':1000})
    mask=page.locator('.image-halo').first.evaluate('(e)=>getComputedStyle(e,"::before").maskImage')
    assert '62.5% 62.5%' in mask,mask
    for selector,property in [('.project h2','textShadow'),('.button','boxShadow'),('.product-window','boxShadow')]:
        assert page.locator(selector).first.evaluate('(e,p)=>getComputedStyle(e)[p]',property)!='none'
    image=page.locator('.product-window').first
    image.evaluate('(e)=>e.scrollIntoView({block:"center",behavior:"instant"})')
    page.mouse.move(2,500)
    page.wait_for_timeout(750)
    before=image.evaluate('(e)=>getComputedStyle(e).transform')
    image.hover(force=True)
    page.wait_for_timeout(800)
    during=image.evaluate('(e)=>getComputedStyle(e).transform')
    assert during!=before,(before,during)
    page.mouse.move(2,500)
    page.wait_for_timeout(800)
    after=image.evaluate('(e)=>getComputedStyle(e).transform')
    assert after==before,(before,after)
    names=page.evaluate('document.getAnimations().map(a=>a.animationName)')
    assert 'button-bob' in names,names
    toggle.click(force=True)
    assert toggle.inner_text()=='Toggle Motion'
    assert page.locator('html').get_attribute('data-motion-paused')=='true'
    assert all(state=='paused' for state in page.evaluate('''()=>document.getAnimations().filter(a=>['ambient-breathe','content-float','visual-float','button-bob'].includes(a.animationName)).map(a=>a.playState)'''))
    context.close()
    print('Header, Toggle Motion styling, Dinnerplate alignment, expanded halos, shadows, hover return and shared motion pause: PASS')
