"""Project title destinations, description hover, and image-attached halos."""
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser=p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    ctx=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='no-preference')
    page=ctx.new_page();page.goto('http://127.0.0.1:8765/',wait_until='networkidle')
    assert page.locator('.project h2 a').count()==4,'Each project title must be a real link'
    for article in page.locator('.project').all():
        title=article.locator('h2 a')
        assert title.get_attribute('href')==article.locator('.links a').first.get_attribute('href')
        title.evaluate('e=>e.scrollIntoView({block:"center",behavior:"instant"})')
        page.wait_for_timeout(850);title.hover(force=True)
        assert title.evaluate('e=>getComputedStyle(e).textDecorationLine')=='none'
    brand=page.locator('header .wordmark');brand.hover(force=True)
    assert brand.evaluate('e=>getComputedStyle(e).textDecorationLine')=='none'
    # No independently painted article glow may remain after the image fades.
    assert page.locator('.project').first.evaluate('e=>getComputedStyle(e,"::before").content')=='none'
    for article in page.locator('.project').all():
        word=article.locator('.description .hover-word').first
        word.evaluate('e=>e.scrollIntoView({block:"center",behavior:"instant"})')
        page.mouse.move(1,50);page.wait_for_timeout(850)
        word.hover(force=True);page.wait_for_timeout(120)
        middle=word.evaluate('e=>new DOMMatrix(getComputedStyle(e).transform).m11')
        page.wait_for_timeout(450)
        end=word.evaluate('e=>new DOMMatrix(getComputedStyle(e).transform).m11')
        assert 1<middle<end,(article.get_attribute('id'),middle,end)
        page.mouse.move(1,50);page.wait_for_timeout(500)
        assert abs(word.evaluate('e=>new DOMMatrix(getComputedStyle(e).transform).m11')-1)<.001
        print('Description hover:',article.get_attribute('id'),'PASS')
    halo=page.locator('#cachebuddy .image-halo')
    halo.evaluate('e=>e.scrollIntoView({block:"center",behavior:"instant"})')
    page.wait_for_timeout(900)
    pulse=halo.evaluate('''e=>{const a=document.getAnimations().find(a=>a.animationName==='ambient-breathe' && a.effect.target===e);if(!a)return null;const values=a.effect.getKeyframes().map(k=>Number(k.opacity));return {duration:a.effect.getTiming().duration,amplitude:Math.max(...values)-Math.min(...values),state:a.playState}}''')
    assert pulse and pulse['state']=='running' and 0<pulse['amplitude']<=.05 and pulse['duration']>=12000,pulse
    frame=halo.locator('.product-window');frame.hover(force=True);page.wait_for_timeout(800)
    scales=halo.evaluate('''e=>({glow:new DOMMatrix(getComputedStyle(e,'::before').transform).m11,image:new DOMMatrix(getComputedStyle(e.querySelector('.product-window')).transform).m11})''')
    assert scales['glow']>1 and abs(scales['glow']-scales['image'])<.0001,scales
    page.evaluate('scrollTo({top:0,behavior:"instant"})');page.wait_for_timeout(900)
    assert halo.evaluate('e=>getComputedStyle(e).opacity')=='0'
    page.emulate_media(reduced_motion='reduce');page.wait_for_timeout(100)
    assert all(s=='paused' for s in page.evaluate('document.getAnimations().filter(a=>a.animationName==="ambient-breathe").map(a=>a.playState)'))
    ctx.close()
    print('All project titles match Open destinations; title/logo hover never underlines: PASS')
