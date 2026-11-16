from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser=p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context=browser.new_context(reduced_motion='reduce')
    page=context.new_page()
    for width in [320,390,600,760]:
        page.set_viewport_size({'width':width,'height':900})
        page.goto('http://127.0.0.1:8765/',wait_until='networkidle')
        summary=page.locator('.mobile-menu summary')
        summary.click()
        menu=page.locator('.mobile-menu')
        assert menu.get_attribute('open') is not None
        panel=page.locator('.mobile-menu nav').bounding_box()
        assert panel['x']>=0 and panel['x']+panel['width']<=page.evaluate('document.documentElement.clientWidth')+1
        assert page.locator('.mobile-menu nav a:visible').count()==3
        page.keyboard.press('Escape')
        assert menu.get_attribute('open') is None
        assert summary.evaluate('(e)=>e===document.activeElement')
        summary.click()
        page.locator('.mobile-menu a[href="#work"]').click()
        assert menu.get_attribute('open') is None
        assert page.url.endswith('#work')
        print('Menu open, bounds, Escape, focus return and link close:',width,'PASS')
    page.set_viewport_size({'width':1440,'height':1000})
    page.goto('http://127.0.0.1:8765/',wait_until='networkidle')
    assert not page.locator('.mobile-menu').is_visible()
    assert page.locator('header > .header-inner > nav a:visible').count()==3
    context.close()
    context=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
    page=context.new_page()
    page.goto('http://127.0.0.1:8765/',wait_until='networkidle')
    page.locator('.mobile-menu summary').click()
    assert page.locator('.mobile-menu nav a:visible').count()==3
    assert page.locator('#matrix-toggle').is_hidden()
    print('No-JavaScript mobile navigation: PASS')
    context.close()
    page=browser.contexts[0].new_page()
    page.goto('http://127.0.0.1:8765/',wait_until='networkidle')
    page.locator('img').evaluate_all('(els)=>els.forEach(e=>e.loading="eager")')
    page.wait_for_function('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)')
    page.evaluate('document.fonts.ready')
    for name,width,height in [('mobile',390,844),('desktop',1440,1000)]:
        page.set_viewport_size({'width':width,'height':height})
        # Decode and paint lazy images before full-page capture; complete/naturalWidth
        # alone do not ensure an off-screen, async-decoded image has painted.
        for image in page.locator('.product-window img').all():
            image.evaluate('async e=>{await e.decode();e.scrollIntoView({block:"center",behavior:"instant"})}')
            page.wait_for_timeout(100)
        page.evaluate('scrollTo({top:0,behavior:"instant"})')
        page.wait_for_timeout(600)
        page.screenshot(path=f'/home/user/.hermes/cache/scratch/polish-{name}.png',full_page=True,animations='disabled')
    print('Headed local preview:',page.url)
