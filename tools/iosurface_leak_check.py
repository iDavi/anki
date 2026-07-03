# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Measures IOSurface growth caused by overview<->review transitions on macOS
(https://github.com/ankitects/anki/issues/4683).

Paste into Anki's debug console (Ctrl+Shift+;) on macOS with GPU
acceleration enabled. Drives mw.moveToState() directly (same path as the
S key, bypasses any debounce), 40 toggles at 250ms, then reports.

MODE = "none":
    Reproduces the leak. Every transition is a full navigation of mw.web
    and mw.bottomWeb (stdHtml() -> load_url() of a fresh
    _anki/legacyPageData URL), and the surfaces backing the outgoing
    document's compositor layers are never released.

MODE = "recycle_page":
    Destroys and recreates just the QWebEnginePage of mw.web/mw.bottomWeb
    before each transition, keeping the QWebEngineView itself alive.
    Confirmed NOT to stop the leak -- the IOSurfaces are not tied to
    QWebEnginePage/WebContents lifetime.

MODE = "recycle_view":
    Destroys and recreates the whole QWebEngineView (mw.web / mw.bottomWeb)
    instead of just its page. This tears down the view's native platform
    widget along with the page, which is what actually owns the
    RenderWidgetHostView/DelegatedFrameHost compositor on macOS. If the
    leak stops here, the IOSurfaces are pooled at the view/compositor
    level rather than the page level -- i.e. QtWebEngine (or macOS's
    CALayer/IOSurface backing-store pool underneath it) is caching frames
    per top-level widget and failing to trim the pool, independent of
    which WebContents is attached to it.
"""

import os
import re
import subprocess

from aqt import mw
from aqt.main import BottomWebView, MainWebView
from aqt.webview import AnkiWebPage
from PyQt6.QtCore import QTimer, Qt

# "none" | "recycle_page" | "recycle_view"
MODE = "recycle_view"


def iosurface() -> str:
    out = subprocess.run(
        ["footprint", str(os.getpid())], capture_output=True, text=True
    ).stdout
    for line in out.splitlines():
        m = re.match(r"\s*([\d.]+)\s*(KB|MB|GB)\s+.*\s(\d+)\s+IOSurface\s*$", line)
        if m:
            v, u = float(m.group(1)), m.group(2)
            mb = v / 1024 if u == "KB" else v * 1024 if u == "GB" else v
            return f"{mb:.0f} MB in {m.group(3)} surfaces"
    return "no IOSurface line found"


def recycle_page(web) -> None:
    """Destroy the view's QWebEnginePage and install a fresh one.
    Confirmed insufficient to stop the leak; kept for comparison.
    """
    from aqt import colors
    from aqt.theme import theme_manager

    old = web.page()
    new = AnkiWebPage(web._onBridgeCmd, web._kind, web)
    new.setBackgroundColor(theme_manager.qcolor(colors.CANVAS))
    new.open_links_externally = old.open_links_externally
    new.setZoomFactor(old.zoomFactor())
    web.setPage(new)
    web._filterSet = False
    old.deleteLater()


def recycle_view(attr: str) -> None:
    """Destroy the whole QWebEngineView named `attr` on mw (mw.web or
    mw.bottomWeb) and replace it with a fresh instance in the same layout
    slot, updating every cached reference to it.
    """
    old = getattr(mw, attr)
    layout = mw.mainLayout
    index = layout.indexOf(old)
    new = type(old)(mw)  # MainWebView(mw) or BottomWebView(mw)

    layout.removeWidget(old)
    layout.insertWidget(index, new)
    setattr(mw, attr, new)

    if attr == "web":
        new.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        new.setMinimumWidth(400)
        new.setAcceptDrops(True)
        mw.reviewer.web = new
        mw.overview.web = new
        mw.deckBrowser.web = new
    else:  # bottomWeb
        new.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        new.disable_zoom()
        new.requiresCol = False
        mw.reviewer.bottom.web = new
        mw.overview.bottom.web = new

    old.setParent(None)
    old.deleteLater()


print("before:", iosurface())

remaining = 40


def step() -> None:
    global remaining
    if remaining <= 0:
        print("after:", iosurface())
        timer.stop()
        # deleteLater()-ed views/pages and their GPU resources are torn
        # down asynchronously; measure again once that has settled
        QTimer.singleShot(3000, lambda: print("after 40 toggles:", iosurface()))
        return
    if MODE == "recycle_page":
        recycle_page(mw.web)
        recycle_page(mw.bottomWeb)
    elif MODE == "recycle_view":
        recycle_view("web")
        recycle_view("bottomWeb")
    mw.moveToState("review" if mw.state == "overview" else "overview")
    remaining -= 1


timer = QTimer(mw)
timer.timeout.connect(step)
timer.start(250)
