from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser=p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    context=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='no-preference')
    page=context.new_page()
    page.goto('http://127.0.0.1:8765/',wait_until='networkidle')
    page.evaluate('document.fonts.ready')
    mask=page.locator('.image-halo').first.evaluate('(e)=>getComputedStyle(e,"::before").maskImage')
    assert '62.5% 62.5%' in mask,mask
    assert page.locator('.product-window').count()==page.locator('.image-halo').count()==5
    for frame in page.locator('.product-window').all():
        assert frame.evaluate('(e)=>getComputedStyle(e.closest(".image-halo"),"::before").content')!='none'
        assert 'url(' in frame.evaluate('(e)=>getComputedStyle(e.closest(".image-halo"),"::before").backgroundImage')
    for link in page.locator('a[href^="https://github.com/yapperyap"]').all():
        assert link.inner_text().strip()==''
        assert link.get_attribute('aria-label')
        assert link.locator('img.github-mark').count()==1
    for link in page.locator('.project .links a:first-child').all():
        assert link.inner_text().strip()=='Open'
        assert link.get_attribute('aria-label').startswith('Open ')
    target=page.locator('#flowdesk .project-inner')
    top=target.evaluate('(e)=>e.getBoundingClientRect().top+scrollY')
    page.evaluate('(y)=>scrollTo({top:y,behavior:"instant"})',top-980)
    page.wait_for_timeout(160)
    before=page.locator('#flowdesk .project-copy').evaluate('(e)=>getComputedStyle(e).opacity')
    scale_before=page.locator('#flowdesk .project-visual').evaluate('(e)=>getComputedStyle(e).scale')
    page.evaluate('(y)=>scrollTo({top:y,behavior:"instant"})',top-100)
    page.wait_for_timeout(850)
    after=page.locator('#flowdesk .project-copy').evaluate('(e)=>getComputedStyle(e).opacity')
    scale_after=page.locator('#flowdesk .project-visual').evaluate('(e)=>getComputedStyle(e).scale')
    assert before!=after,(before,after)
    assert scale_before!=scale_after,(scale_before,scale_after)
    print('Scroll reveal opacity:',before,'->',after)
    print('Scroll image scale:',scale_before,'->',scale_after)
    toggle=page.locator('#matrix-toggle')
    toggle.hover(force=True)
    toggle.click()
    assert target.evaluate('(e)=>getComputedStyle(e).transform')=='none'
    assert not page.evaluate('document.getAnimations().some(a=>["project-arrive","image-travel"].includes(a.animationName))')
    page.emulate_media(reduced_motion='reduce')
    assert target.evaluate('(e)=>getComputedStyle(e).transform')=='none'
    assert not page.evaluate('document.getAnimations().some(a=>["project-arrive","image-travel"].includes(a.animationName))')
    context.close()
    print('Expanded halos, per-image glows, accessible GitHub icons, Open labels, scroll-linked motion/pause: PASS')
