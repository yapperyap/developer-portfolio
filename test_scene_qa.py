import json, urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.connect_over_cdp('http://127.0.0.1:9222')
    ctx=b.new_context(reduced_motion='no-preference')
    page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    reports=[]
    for width,height in [(320,720),(390,844),(820,1180),(1440,1000)]:
        page.set_viewport_size({'width':width,'height':height})
        page.goto('http://127.0.0.1:8765/',wait_until='networkidle')
        page.evaluate('document.fonts.ready');page.wait_for_timeout(150)
        count=page.locator('a,button,summary').evaluate_all('es=>es.filter(e=>e.getClientRects().length&&!e.hidden).length')
        problems=[]
        for i in range(count):
            page.keyboard.press('Tab');page.wait_for_timeout(70)
            check=page.evaluate('''()=>{const e=document.activeElement,r=e.getBoundingClientRect(),h=document.querySelector('header').getBoundingClientRect().bottom,p=e.closest('.scene-piece');return {name:e.getAttribute('aria-label')||e.textContent.trim(),tag:e.tagName,top:r.top,bottom:r.bottom,header:h,inHeader:!!e.closest('header'),opacity:p?getComputedStyle(p).opacity:'1'}}''')
            if check['tag']!='BODY' and (check['top'] < (0 if check['inHeader'] or check['name']=='Skip to content' else check['header'])-1 or check['bottom']>height+1 or float(check['opacity'])<.99):problems.append(check)
        reports.append({'width':width,'pinCount':page.locator('.is-pinned').count(),'keyboardProblems':problems})
        print('Keyboard / scene fit',width,reports[-1])
        assert not problems
        # Verify actual child bounds, not just the sticky panel's nominal height.
        for article in page.locator('.project.is-pinned').all():
            y=article.evaluate('(e)=>e.getBoundingClientRect().top+scrollY+100')
            page.evaluate('y=>scrollTo({top:y,behavior:"instant"})',y)
            page.wait_for_timeout(900)
            clipped=article.evaluate('''e=>{const h=document.querySelector('header').getBoundingClientRect().bottom;return [...e.querySelectorAll('.project-copy,.product-window')].map(n=>({kind:n.className,top:n.getBoundingClientRect().top,bottom:n.getBoundingClientRect().bottom})).filter(r=>r.top<h-2||r.bottom>innerHeight+2)}''')
            assert not clipped,(width,article.get_attribute('id'),clipped)
        print('All pinned project content fits:',width)
    axe=urllib.request.urlopen('https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.3/axe.min.js',timeout=20).read().decode()
    for path in ['','site-notice.html']:
        page.goto('http://127.0.0.1:8765/'+path,wait_until='networkidle');page.add_script_tag(content=axe)
        violations=page.evaluate('async()=> (await axe.run(document,{runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21aa"]}})).violations.map(v=>({id:v.id,targets:v.nodes.map(n=>n.target)}))')
        assert not violations,violations
        print('Accessibility',path or 'portfolio',violations)
    page.goto('http://127.0.0.1:8765/',wait_until='networkidle')
    page.locator('.product-window img').evaluate_all('async es=>Promise.all(es.map(async e=>{e.loading="eager";await e.decode()}))')
    for name,width,height,project in [('desktop-dinner',1440,1000,'#dinnerplate'),('desktop-flow',1440,1000,'#flowdesk'),('mobile-flow',390,844,'#flowdesk')]:
        page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(200)
        y=page.locator(project).evaluate('(e)=>e.getBoundingClientRect().top+scrollY+40')
        page.evaluate('y=>scrollTo({top:y,behavior:"instant"})',y);page.wait_for_timeout(1100)
        page.screenshot(path='/home/user/.hermes/cache/scratch/scene-'+name+'.png')
    Path('/home/user/.hermes/cache/scratch/scene-qa.json').write_text(json.dumps(reports,indent=2))
    assert not errors,errors
    ctx.close()
    print('No browser errors; desktop and phone scene screenshots saved.')
