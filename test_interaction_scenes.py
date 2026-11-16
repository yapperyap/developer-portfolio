from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser=p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    ctx=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='no-preference')
    page=ctx.new_page()
    page.goto('http://127.0.0.1:8765/',wait_until='networkidle')
    assert page.locator('h1 .hover-word').count()>0,'Text hover needs tight word-sized hit areas'
    page.wait_for_timeout(800)
    # The empty right side of a heading must not trigger its words.
    heading=page.locator('h1'); box=heading.bounding_box()
    page.mouse.move(box['x']+box['width']-8,box['y']+box['height']/2)
    page.wait_for_timeout(500)
    assert heading.evaluate('(e)=>getComputedStyle(e).scale') in ['none','1']
    assert page.locator('h1 .hover-word').first.evaluate('(e)=>getComputedStyle(e).transform')=='none'
    word=page.locator('h1 .hover-word').first
    word.hover(force=True);page.wait_for_timeout(600)
    axes=word.evaluate('(e)=>{const m=new DOMMatrix(getComputedStyle(e).transform);return [m.m11,m.m22,m.m33]}')
    assert min(axes)>1 and max(axes)-min(axes)<.0001,axes
    button=page.locator('#matrix-toggle');button.hover(force=True);page.wait_for_timeout(600)
    axes=button.evaluate('(e)=>{const m=new DOMMatrix(getComputedStyle(e).transform);return [m.m11,m.m22,m.m33]}')
    assert min(axes)>1 and max(axes)-min(axes)<.0001,axes
    assert 'Selected work' not in page.locator('body').inner_text()
    assert 'Yap / Independent developer' not in page.locator('body').inner_text()
    ctx.close()
    print('Uniform XYZ hover, tight word hit areas, and removed labels: PASS')
    ctx=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion='no-preference')
    page=ctx.new_page();page.goto('http://127.0.0.1:8765/',wait_until='networkidle')
    page.evaluate('document.fonts.ready');page.wait_for_timeout(250)
    assert page.locator('#flowdesk').evaluate('(e)=>e.classList.contains("is-pinned")'),'Desktop projects need a scroll hold'
    assert page.locator('#cachebuddy .project-copy').evaluate('(e)=>getComputedStyle(e).opacity')=='0','Off-screen scene must remain hidden'
    flow=page.locator('#flowdesk')
    top=flow.evaluate('(e)=>e.getBoundingClientRect().top+scrollY')
    ys=[]
    for offset in [40,240]:
        page.evaluate('(y)=>scrollTo({top:y,behavior:"instant"})',top+offset)
        page.wait_for_timeout(750)
        ys.append(page.locator('#flowdesk .project-inner').bounding_box()['y'])
    assert abs(ys[1]-ys[0])<1,ys
    assert page.locator('#flowdesk .project-copy').evaluate('(e)=>Number(getComputedStyle(e).opacity)')>.99
    sat_top=page.locator('.sat').evaluate('(e)=>e.getBoundingClientRect().top+scrollY')
    page.evaluate('(y)=>scrollTo({top:y,behavior:"instant"})',sat_top+100)
    page.wait_for_timeout(750)
    assert page.locator('#flowdesk .project-copy').evaluate('(e)=>getComputedStyle(e).opacity')=='0'
    page.emulate_media(reduced_motion='reduce');page.wait_for_timeout(150)
    assert page.locator('.is-pinned').count()==0
    assert page.locator('#cachebuddy .project-copy').evaluate('(e)=>getComputedStyle(e).opacity')=='1'
    ctx.close()
    ctx=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':844})
    page=ctx.new_page();page.goto('http://127.0.0.1:8765/',wait_until='networkidle')
    assert page.locator('#cachebuddy .project-copy').evaluate('(e)=>getComputedStyle(e).opacity')=='1'
    assert page.locator('.is-pinned').count()==0
    ctx.close()
    print('Scroll reveal/hide, real sticky hold, reduced-motion and no-JS fallbacks: PASS')
