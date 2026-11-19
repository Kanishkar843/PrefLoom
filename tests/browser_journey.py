import subprocess,time,urllib.request,os,secrets,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
root=Path(__file__).resolve().parents[2];report=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',headless=True)
    for name,port in [('PrefLoom',8000)]:
        directory=root/name;assets=directory/'docs/assets';assets.mkdir(exist_ok=True)
        token=secrets.token_urlsafe(32);env=os.environ.copy();env['ADMIN_TOKEN']=token;env['DATABASE_URL']='sqlite:///./.cache/browser-demo.db'
        log=open(directory/'.cache/browser-server.log','w')
        proc=subprocess.Popen([str(directory/'.venv/Scripts/python.exe'),'-m','uvicorn','app.main:app','--host','127.0.0.1','--port',str(port)],cwd=directory,env=env,stdout=log,stderr=log)
        context=browser.new_context(viewport={'width':1440,'height':1000});page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        try:
            for _ in range(20):
                try: page.request.get(f'http://127.0.0.1:{port}/health',timeout=2000);break
                except Exception:
                    if proc.poll() is not None:raise RuntimeError('Server exited; inspect browser-server.log')
                    time.sleep(1)
            page.goto(f'http://127.0.0.1:{port}',wait_until='networkidle')
            if name=='PrefLoom':
                expect(page.locator('#status')).to_have_text('Up to date.',timeout=30000)
                page.locator('input[name=key]').fill('location');page.locator('input[name=value]').fill('Remote');page.get_by_role('button',name='Propose preference',exact=True).click()
                expect(page.get_by_role('button',name='Approve',exact=True)).to_be_visible();page.get_by_role('button',name='Approve',exact=True).click();expect(page.locator('#memory')).to_contain_text('Remote')
                page.locator('#message').fill('python remote');page.get_by_role('button',name='Explore â†’').click();expect(page.locator('#jobs article')).to_have_count(5)
                page.reload(wait_until='networkidle');expect(page.locator('#memory')).to_contain_text('Remote')
                page.locator('#message').fill('python remote');page.get_by_role('button',name='Explore â†’').click();expect(page.locator('#jobs article')).to_have_count(5)
            elif name=='DeltaIndex':
                page.locator('#token').fill(token);page.locator('#seed').click();expect(page.locator('#status')).to_contain_text('Ingest:',timeout=30000);expect(page.locator('#results article').first).to_be_visible()
                page.locator('#seed').click();expect(page.locator('#status')).to_contain_text('"unchanged":120',timeout=30000)
                page.get_by_role('button',name='Explain score').first.click();expect(page.locator('#explanation')).to_contain_text('lexical_rank')
                page.locator('#compare').click();expect(page.locator('#status')).to_contain_text('Compared')
            else:
                page.locator('#token').fill(token);page.locator('#connect').click();expect(page.locator('#status')).to_have_text('Connected.')
                page.locator('#seed').click();expect(page.locator('#status')).to_contain_text('registered')
                page.locator('#run').click();expect(page.locator('#status')).to_contain_text('GATE PASSED',timeout=30000)
                page.locator('#target').select_option('fixture-regressed');page.locator('#run').click();expect(page.locator('#status')).to_contain_text('RELEASE BLOCKED',timeout=30000)
                page.locator('#baseline').select_option(index=1);page.locator('#candidate').select_option(index=0);page.locator('#compare').click();expect(page.locator('#comparison')).to_contain_text('"recall_at_5": -1')
                page.locator('#cases summary').first.click()
            # Never capture the locally generated admin credential.
            if name!='PrefLoom':page.locator('#token').fill('')
            expect(page.locator('#theme')).to_be_enabled(timeout=30000)
            page.screenshot(path=str(assets/'desktop.png'),full_page=True)
            page.locator('#theme').click();page.screenshot(path=str(assets/'light.png'),full_page=True)
            page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(assets/'mobile.png'),full_page=True)
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Mobile horizontal overflow'
            assert not errors,errors
            report.append({'project':name,'browser':'installed Chrome, headless Playwright','status':'PASSED','screenshots':['docs/assets/desktop.png','docs/assets/light.png','docs/assets/mobile.png'],'console_errors':errors})
            print(name+' E2E PASSED',flush=True)
        except Exception as e:
            report.append({'project':name,'status':'FAILED','error':str(e)});print(name+' E2E FAILED: '+str(e),flush=True)
        finally:
            context.close();proc.terminate();proc.wait(timeout=15);log.close()
    browser.close()
Path(__file__).resolve().parents[1].joinpath('docs/browser-report.json').write_text(json.dumps(report,indent=2))
if any(r['status']=='FAILED' for r in report):sys.exit(1)
