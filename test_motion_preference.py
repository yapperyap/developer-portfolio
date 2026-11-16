"""System motion default + explicit per-visit user override, tested in Chromium."""
from playwright.sync_api import sync_playwright, expect
URL='http://127.0.0.1:8765/'
with sync_playwright() as p:
    browser=p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    for preference in ['reduce','no-preference']:
        ctx=browser.new_context(viewport={'width':1440,'height':1000},reduced_motion=preference)
        page=ctx.new_page()
        page.goto(URL,wait_until='networkidle')
        toggle=page.locator('#matrix-toggle')
        assert toggle.get_attribute('aria-pressed')==str(preference=='no-preference').lower(),preference
        assert page.locator('html').get_attribute('data-motion-paused')==str(preference=='reduce').lower()
        # Without manual input, live accessibility changes control the site.
        page.emulate_media(reduced_motion='no-preference' if preference=='reduce' else 'reduce')
        expect(toggle).to_have_attribute('aria-pressed',str(preference=='reduce').lower())
        page.emulate_media(reduced_motion=preference)
        expect(toggle).to_have_attribute('aria-pressed',str(preference=='no-preference').lower())
        if preference=='reduce':
            toggle.click()
            assert toggle.get_attribute('aria-pressed')=='true'
            assert 'content-float' in page.evaluate('document.getAnimations().map(a=>a.animationName)')
            read_scale='''e=>{const s=getComputedStyle(e),m=new DOMMatrix(s.transform);return Math.hypot(m.a,m.b)*(s.scale==='none'?1:parseFloat(s.scale))}'''
            for selector in ['#dinnerplate-title .hover-word','.product-window','#dinnerplate .links .button']:
                target=page.locator(selector).first
                target.evaluate('e=>e.scrollIntoView({block:"center",behavior:"instant"})')
                page.mouse.move(1,50)
                page.wait_for_timeout(800)
                target.hover(force=True)
                page.wait_for_timeout(120)
                middle=target.evaluate(read_scale)
                page.wait_for_timeout(800)
                end=target.evaluate(read_scale)
                assert 1<middle<end,(selector,middle,end)
                page.mouse.move(1,50)
                page.wait_for_timeout(800)
                assert abs(target.evaluate(read_scale)-1)<.001
                print('Reduced-motion explicit opt-in: real-time hover',selector,middle,'->',end,'-> 1')
            # Explicit choice is not silently revoked by later OS changes.
            page.emulate_media(reduced_motion='no-preference')
            page.emulate_media(reduced_motion='reduce')
            assert toggle.get_attribute('aria-pressed')=='true'
            toggle.hover(force=True)
            toggle.click()
        else:
            toggle.hover(force=True)
            toggle.click()
        assert toggle.get_attribute('aria-pressed')=='false'
        assert all(state=='paused' for state in page.evaluate('document.getAnimations().filter(a=>a.animationName).map(a=>a.playState)'))
        page.emulate_media(reduced_motion='no-preference')
        assert toggle.get_attribute('aria-pressed')=='false'
        page.emulate_media(reduced_motion=preference)
        page.reload(wait_until='networkidle')
        assert toggle.get_attribute('aria-pressed')==str(preference=='no-preference').lower()
        ctx.close()
        print('System default, live preference updates, manual override, off state and reload:',preference,'PASS')
