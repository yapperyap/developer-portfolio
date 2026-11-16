from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser=p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context=browser.new_context(viewport={'width':1920,'height':1080},reduced_motion='no-preference')
    page=context.new_page()
    page.goto('http://127.0.0.1:8765/',wait_until='networkidle')
    page.evaluate('document.fonts.ready')
    frame=page.locator('.project-inner').first.bounding_box()
    assert frame['width']<=1121,'Content should stay inside a centered 1120px column'
    client_width=page.evaluate('document.documentElement.clientWidth')
    assert abs(frame['x']-(client_width-frame['width'])/2)<1
    animations=page.evaluate('''()=>document.getAnimations().map(a=>({name:a.animationName,duration:a.effect.getTiming().duration,state:a.playState}))''')
    for name in ['ambient-breathe','content-float','visual-float','button-bob']:
        matches=[a for a in animations if a['name']==name]
        assert matches and all(a['duration']>=10000 for a in matches),name
    samples=page.evaluate('''()=>{
      return [['ambient-breathe','.image-halo','opacity','::before'],['content-float','.project-copy','translate',null],['visual-float','.project-visual','translate',null]].map(([name,selector,property,pseudo])=>{
        const element=document.querySelector(selector);
        const animation=document.getAnimations().find(a=>a.animationName===name && a.effect.target===element);
        animation.currentTime=0;
        const start=getComputedStyle(element,pseudo)[property];
        animation.currentTime=animation.effect.getTiming().duration/2;
        const middle=getComputedStyle(element,pseudo)[property];
        return {name,start,middle};
      });
    }''')
    assert all(s['start']!=s['middle'] for s in samples),samples
    print('Rendered animation samples:',samples)
    toggle=page.locator('#matrix-toggle')
    toggle.hover(force=True)  # Hover freezes the tiny button bob before clicking.
    toggle.click()
    assert page.locator('html').get_attribute('data-motion-paused')=='true'
    assert all(a['state']=='paused' for a in page.evaluate('''()=>document.getAnimations().filter(a=>['ambient-breathe','content-float','visual-float','button-bob'].includes(a.animationName)).map(a=>({state:a.playState}))'''))
    toggle.click()
    assert page.locator('html').get_attribute('data-motion-paused')=='false'
    page.emulate_media(reduced_motion='reduce')
    # The user's explicit enabled choice overrides later OS changes for this visit.
    assert page.locator('html').get_attribute('data-motion-paused')=='false'
    page.reload(wait_until='networkidle')
    assert page.locator('html').get_attribute('data-motion-paused')=='true'
    assert all(state=='paused' for state in page.evaluate('document.getAnimations().filter(a=>a.animationName).map(a=>a.playState)'))
    context.close()
    print('Centered content, slow pulse/float, shared pause and reduced-motion checks: PASS')
