# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

"""
Measures IOSurface growth caused by overview<->review transitions on macOS
(https://github.com/ankitects/anki/issues/4683).

Paste into Anki's debug console (Ctrl+Shift+;) on macOS with GPU
acceleration enabled. Drives mw.moveToState() directly (same path as the
S key, bypasses any debounce), 40 toggles at 250ms, then reports.

With RECYCLE_PAGES = False this reproduces the leak: every transition is a
full navigation of mw.web and mw.bottomWeb, and the Chromium GPU compositor
never returns the IOSurfaces that backed the previous document's layers.

With RECYCLE_PAGES = True the QWebEnginePage of both webviews is destroyed
and recreated before each transition. Destroying the page tears down its
WebContents and compositor frame sink, which is what actually releases the
accumulated surfaces. If the IOSurface count stays flat in this mode, the
surfaces are tied to page lifetime rather than document lifetime,
confirming the leak sits in QtWebEngine's per-page compositing path.
"""

import os
import re
import subprocess

from aqt import colors, mw
from aqt.theme import theme_manager
from aqt.webview import AnkiWebPage, AnkiWebView
from PyQt6.QtCore import QTimer

# Destroy/recreate the QWebEnginePage of mw.web and mw.bottomWeb before
# each transition. Toggle to compare leak behaviour with and without.
RECYCLE_PAGES = True


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


def recycle_page(web: AnkiWebView) -> None:
    """Destroy the view's QWebEnginePage and install a fresh one.

    Mirrors AnkiWebView.__init__: the new page reuses the view's bridge
    dispatcher and kind, so reviewer/overview pycmd() handlers keep
    working after the swap. The old page (and with it the render widget
    host / compositor frame sink holding the IOSurfaces) is deleted.
    """
    old = web.page()
    new = AnkiWebPage(web._onBridgeCmd, web._kind, web)
    new.setBackgroundColor(theme_manager.qcolor(colors.CANVAS))
    new.open_links_externally = old.open_links_externally
    new.setZoomFactor(old.zoomFactor())
    web.setPage(new)
    # the swap creates a new focus proxy; force the event filter to be
    # reinstalled on it by the next bridge command
    web._filterSet = False
    old.deleteLater()


print("before:", iosurface())

remaining = 40


def step() -> None:
    global remaining
    if remaining <= 0:
        print("after:", iosurface())
        timer.stop()
        # deleteLater()-ed pages and their GPU resources are torn down
        # asynchronously; measure again once that has settled
        QTimer.singleShot(3000, lambda: print("after 40 toggles:", iosurface()))
        return
    if RECYCLE_PAGES:
        # both of these webviews navigate on every state change; give each
        # a fresh page so the old one's compositor surfaces can be freed.
        # moveToState() below re-renders them, so the blank page is only
        # visible for a frame.
        recycle_page(mw.web)
        recycle_page(mw.bottomWeb)
    mw.moveToState("review" if mw.state == "overview" else "overview")
    remaining -= 1


timer = QTimer(mw)
timer.timeout.connect(step)
timer.start(250)
