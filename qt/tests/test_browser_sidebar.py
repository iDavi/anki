# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from typing import Any, cast

from mock import MagicMock

from aqt.browser.sidebar.searchbar import SidebarSearchBar
from aqt.qt import QApplication, QTimer, QWidget

_app: QApplication | None = None


def _search_bar_with_mocks(
    timer: MagicMock,
) -> tuple[SidebarSearchBar, MagicMock]:
    global _app
    _app = QApplication.instance() or QApplication([])

    sidebar = QWidget()
    sidebar.col = MagicMock()  # type: ignore[attr-defined]
    sidebar.col.tr.browsing_sidebar_filter.return_value = "Filter"  # type: ignore[attr-defined]
    sidebar.search_for = MagicMock()  # type: ignore[attr-defined]

    search_bar = SidebarSearchBar(cast(Any, sidebar))
    search_bar.timer = cast(QTimer, timer)
    return search_bar, sidebar.search_for  # type: ignore[attr-defined]


def test_clearing_sidebar_filter_happens_immediately() -> None:
    timer = MagicMock()
    timer.isActive.return_value = True
    search_bar, search_for = _search_bar_with_mocks(timer)

    search_bar.onTextChanged("")

    timer.stop.assert_called_once_with()
    timer.start.assert_not_called()
    search_for.assert_called_once_with("")


def test_sidebar_filter_search_remains_debounced() -> None:
    timer = MagicMock()
    timer.isActive.side_effect = [False, True]
    search_bar, search_for = _search_bar_with_mocks(timer)

    search_bar.onTextChanged("overdue")
    search_bar.onTextChanged("overdue!")

    timer.start.assert_called_once_with()
    timer.stop.assert_not_called()
    search_for.assert_not_called()
