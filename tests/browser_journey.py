"""Single-worker React browser journey; owns only its isolated test server."""

import os, sys, time, socket, subprocess, json
from pathlib import Path
from uuid import uuid4
from playwright.sync_api import sync_playwright, expect

root = Path(__file__).resolve().parents[1]
assets = root / "docs/assets"
assets.mkdir(exist_ok=True)
(root / ".cache").mkdir(exist_ok=True)
with socket.socket() as s:
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
env = {
    **os.environ,
    "DATABASE_URL": os.getenv(
        "BROWSER_DATABASE_URL", "sqlite:///./.cache/browser-" + str(uuid4()) + ".db"
    ),
    "AGENT_MODE": "offline",
}
log = (root / ".cache/browser-react.log").open("w")
proc = subprocess.Popen(
    [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
    ],
    cwd=root,
    env=env,
    stdout=log,
    stderr=log,
)
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=os.getenv(
                "CHROME_PATH", "C:/Program Files/Google/Chrome/Application/chrome.exe"
            ),
            headless=True,
        )
        context = browser.new_context(
            viewport={"width": 1536, "height": 1040}, reduced_motion="reduce"
        )
        page = context.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        for _ in range(60):
            try:
                if page.request.get(f"http://127.0.0.1:{port}/health", timeout=1000).ok:
                    break
            except Exception:
                time.sleep(0.2)
        page.goto(f"http://127.0.0.1:{port}", wait_until="networkidle")
        expect(page.get_by_text("Your workspace is ready.")).to_be_visible()
        page.locator("input[name=key]").fill("location")
        page.locator("input[name=value]").fill("Remote")
        page.get_by_role("button", name="Propose preference", exact=True).click()
        expect(page.get_by_role("button", name="Approve", exact=True)).to_be_visible()
        page.get_by_role("button", name="Approve", exact=True).click()
        expect(page.locator("#memory")).to_contain_text("Remote")
        page.get_by_label("Profile summary").fill(
            "Python engineer with 3 years SQL and remote work"
        )
        page.get_by_role("button", name="Extract & propose profile").click()
        page.get_by_role("button", name="Approve", exact=True).click()
        expect(page.locator(".context")).to_contain_text("python")
        page.locator("#message").fill("discover and compare python remote roles")
        page.get_by_role("button", name="Explore →").click()
        expect(page.locator("#jobs article")).to_have_count(5)
        expect(page.locator("#status")).to_contain_text("3 validated")
        page.reload(wait_until="networkidle")
        expect(page.locator("#memory")).to_contain_text("Remote")
        expect(page.locator(".conversation")).to_contain_text("discover and compare")
        page.locator("#message").fill("python remote")
        page.route(
            "**/chat/stream",
            lambda route: route.fulfill(
                status=503,
                content_type="application/json",
                body='{"detail":"Intentional test outage"}',
            ),
            times=1,
        )
        page.get_by_role("button", name="Explore →").click()
        expect(page.get_by_role("alert")).to_contain_text("Intentional test outage")
        page.get_by_role("button", name="Retry", exact=True).click()
        expect(page.locator("#jobs article")).to_have_count(5)
        expect(page.get_by_role("alert")).to_have_count(0)
        page.get_by_role("button", name="Compare roles", exact=True).click()
        expect(page.locator("#jobs article")).to_have_count(2)
        page.get_by_role("button", name="History", exact=True).click()
        expect(page.get_by_role("dialog")).to_contain_text("Version 1")
        page.get_by_role("button", name="Close history").click()
        page.screenshot(path=str(assets / "desktop.png"), full_page=True)
        page.get_by_role("button", name="Change theme").click()
        page.screenshot(path=str(assets / "light.png"), full_page=True)
        page.set_viewport_size({"width": 390, "height": 844})
        page.screenshot(path=str(assets / "mobile.png"), full_page=True)
        assert page.evaluate("document.documentElement.scrollWidth<=innerWidth"), (
            "Horizontal overflow"
        )
        assert not errors, errors
        browser.close()
    (root / "docs/browser-report.json").write_text(
        json.dumps(
            {
                "status": "PASSED",
                "frontend": "React + TypeScript",
                "journeys": [
                    "fresh session",
                    "memory approval",
                    "profile extraction approval",
                    "multi-step search",
                    "reload persistence",
                    "error retry",
                    "comparison",
                    "memory history",
                    "dark/light",
                    "390px responsive",
                ],
                "console_errors": errors,
            },
            indent=2,
        )
    )
    print("PrefLoom React browser journey PASSED")
finally:
    proc.terminate()
    proc.wait(timeout=15)
    log.close()
