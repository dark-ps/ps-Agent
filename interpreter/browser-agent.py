from __future__ import annotations
import base64, os, time, shutil
from pathlib import Path

# Usage (via TOOL: browser, or directly):
# Python Playwright browser automation tool.
# Opens and controls web pages, inspects page content and interactive elements,
# clicks elements, enters text, presses keys, scrolls, changes viewport size,
# captures screenshots, and records browser sessions.
#
# Functions:
# status() – Check whether Playwright and supported browsers are available.
# open_page() – Open a URL in a browser session.
# inspect_page() – Return the current page URL, title, text, and images.
# inspect_controls() – Find visible buttons, inputs, textareas, selects, and other controls.
# click() – Click an element using a selector.
# type_text() – Enter text into an input or editable element.
# press_key() – Press a keyboard key on an element.
# wait_for() – Wait for an element to reach a specified state.
# scroll() – Scroll the page or bring an element into view.
# set_viewport() – Change the browser viewport dimensions.
# screenshot() – Capture and save a screenshot of the current page.
# record_and_close() – Close the browser and return the recorded video path.
# close() – Close the browser session.
#
# Use this tool when you need to browse and interact with websites,
# inspect their content or controls, automate browser actions,
# take screenshots, or record a browser session.

_SESSIONS={}
_ROOT=Path(__file__).resolve().parents[1]

def _pw():
    try:
        from playwright.sync_api import sync_playwright
        return sync_playwright
    except Exception as e:
        return None

def status():
    sync=_pw()
    return {"available":bool(sync),"reason":None if sync else "Python Playwright is not installed","browsers":_find_browsers()}

def _find_browsers():
    import shutil
    out={}
    for n in ("google-chrome","chromium","chromium-browser","firefox","brave","brave-browser","msedge","microsoft-edge"):
        p=shutil.which(n)
        if p: out[n]=p
    return out

def open_page(url, session="default", headless=True, record_video=False, width=1440, height=900):
    sync=_pw()
    if not sync: return {"ok":False,"error":"Playwright unavailable; install it only if the detected environment permits it."}
    pw=browser=ctx=None
    try:
        if session in _SESSIONS: close(session)
        pw=sync().start()
        kwargs={"headless":bool(headless)}
        executable = next((shutil.which(n) for n in (
            "chromium","chromium-browser","google-chrome","google-chrome-stable",
            "brave","brave-browser","msedge","microsoft-edge"
        ) if shutil.which(n)), None)
        if executable:
            kwargs["executable_path"] = executable
        context_kwargs={"viewport":{"width":int(width),"height":int(height)}}
        if record_video:
            ( _ROOT/"Projects"/"videos" ).mkdir(parents=True, exist_ok=True)
            context_kwargs["record_video_dir"]=str(_ROOT/"Projects"/"videos")
        browser=pw.chromium.launch(**kwargs)
        ctx=browser.new_context(**context_kwargs)
        page=ctx.new_page()
        page.goto(url,wait_until="domcontentloaded",timeout=60000)
        _SESSIONS[session]=(pw,browser,ctx,page,record_video)
        return {"ok":True,"session":session,"url":page.url,"title":page.title()}
    except Exception as e:
        for resource in (ctx,browser,pw):
            if resource:
                try:
                    resource.stop() if resource is pw else resource.close()
                except Exception:pass
        return {"ok":False,"error":f"{type(e).__name__}: {e}"}

def inspect_page(session="default"):
    item=_SESSIONS.get(session)
    if not item:return {"ok":False,"error":"Browser session not found"}
    page=item[3]
    try:
        state=page.evaluate("""() => ({
            viewport:{width:innerWidth,height:innerHeight},
            document:{width:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight},
            images:[...document.images].slice(0,100).map(i=>({alt:i.alt||'',loaded:i.complete&&i.naturalWidth>0,width:i.naturalWidth,height:i.naturalHeight,src:i.currentSrc||i.src}))
        })""")
        return {"ok":True,"url":page.url,"title":page.title(),"text":page.locator("body").inner_text(timeout=10000)[:20000],**state}
    except Exception as e:return {"ok":False,"error":f"{type(e).__name__}: {e}"}

def inspect_controls(session="default"):
    item=_SESSIONS.get(session)
    if not item:return {"ok":False,"error":"Browser session not found"}
    page=item[3]
    try:
        controls=page.locator('button, input, textarea, select, [contenteditable="true"], [role="button"], [role="textbox"]')
        result=[]
        for index in range(min(controls.count(),100)):
            el=controls.nth(index)
            try:
                if not el.is_visible():continue
                result.append({
                    "tag":el.evaluate('(e) => e.tagName.toLowerCase()'),
                    "type":el.get_attribute('type') or '',
                    "role":el.get_attribute('role') or '',
                    "aria_label":el.get_attribute('aria-label') or '',
                    "placeholder":el.get_attribute('placeholder') or '',
                    "name":el.get_attribute('name') or '',
                    "text":(el.inner_text(timeout=1000) or '').strip()[:160],
                    "selector_index":index,
                })
            except Exception:continue
        return {"ok":True,"url":page.url,"controls":result}
    except Exception as e:return {"ok":False,"error":f"{type(e).__name__}: {e}"}

def click(selector, session="default"):
    item=_SESSIONS.get(session)
    if not item:return {"ok":False,"error":"Browser session not found"}
    try:
        item[3].locator(selector).first.click(timeout=20000)
        return {"ok":True,"url":item[3].url}
    except Exception as e:return {"ok":False,"error":f"{type(e).__name__}: {e}"}

def type_text(selector, text, session="default"):
    item=_SESSIONS.get(session)
    if not item:return {"ok":False,"error":"Browser session not found"}
    try:
        item[3].locator(selector).first.fill(str(text),timeout=20000)
        return {"ok":True}
    except Exception as e:return {"ok":False,"error":f"{type(e).__name__}: {e}"}

def press_key(selector, key="Enter", session="default"):
    item=_SESSIONS.get(session)
    if not item:return {"ok":False,"error":"Browser session not found"}
    try:
        item[3].locator(selector).first.press(str(key),timeout=20000)
        return {"ok":True,"url":item[3].url}
    except Exception as e:return {"ok":False,"error":f"{type(e).__name__}: {e}"}

def wait_for(selector, session="default", state="visible", timeout=15000):
    item=_SESSIONS.get(session)
    if not item:return {"ok":False,"error":"Browser session not found"}
    try:
        item[3].locator(selector).first.wait_for(state=state,timeout=int(timeout))
        return {"ok":True,"state":state,"url":item[3].url}
    except Exception as e:return {"ok":False,"error":f"{type(e).__name__}: {e}"}

def scroll(selector=None, direction="down", amount=650, session="default"):
    item=_SESSIONS.get(session)
    if not item:return {"ok":False,"error":"Browser session not found"}
    try:
        page=item[3]
        if selector:
            target=page.locator(selector).first
            target.scroll_into_view_if_needed(timeout=15000)
        else:
            delta=abs(int(amount)) * (-1 if str(direction).lower()=="up" else 1)
            page.evaluate("delta => window.scrollBy(0, delta)",delta)
        return {"ok":True,"url":page.url}
    except Exception as e:return {"ok":False,"error":f"{type(e).__name__}: {e}"}

def set_viewport(width=1440, height=900, session="default"):
    item=_SESSIONS.get(session)
    if not item:return {"ok":False,"error":"Browser session not found"}
    try:
        item[3].set_viewport_size({"width":int(width),"height":int(height)})
        return {"ok":True,"viewport":{"width":int(width),"height":int(height)},"url":item[3].url}
    except Exception as e:return {"ok":False,"error":f"{type(e).__name__}: {e}"}

def screenshot(path="Projects/browser.png", session="default", full_page=True):
    item=_SESSIONS.get(session)
    if not item:return {"ok":False,"error":"Browser session not found"}
    target=(_ROOT/path).resolve()
    if _ROOT not in target.parents and target != _ROOT:return {"ok":False,"error":"Path escapes project root"}
    target.parent.mkdir(parents=True,exist_ok=True)
    try:
        item[3].screenshot(path=str(target),full_page=bool(full_page))
        return {"ok":target.exists(),"path":str(target.relative_to(_ROOT)),"size":target.stat().st_size if target.exists() else 0}
    except Exception as e:return {"ok":False,"error":f"{type(e).__name__}: {e}"}

def record_and_close(session="default"):
    item=_SESSIONS.get(session)
    if not item:return {"ok":False,"error":"Browser session not found"}
    pw,browser,ctx,page,recording=item
    try:
        url=page.url
        video=page.video if recording else None
        page.close(); ctx.close()
        video_path=video.path() if video else None
        browser.close(); pw.stop()
        _SESSIONS.pop(session,None)
        videos=sorted((_ROOT/"Projects"/"videos").glob("*"),key=lambda p:p.stat().st_mtime,reverse=True) if (_ROOT/"Projects"/"videos").exists() else []
        return {"ok":True,"url":url,"video":str(Path(video_path).relative_to(_ROOT)) if video_path else None}
    except Exception as e:return {"ok":False,"error":f"{type(e).__name__}: {e}"}

def close(session="default"):
    return record_and_close(session)
