# Copyright: Ankitects Pty Ltd and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

from unittest.mock import MagicMock

from aqt.browser.sidebar.item import SidebarItem
from aqt.browser.sidebar.tree import SidebarTreeView


def sidebar_with_item(expanded, auto_expanding):
    # SidebarTreeView requires a running app, so use a stand-in
    item = SidebarItem("Due", "")
    item.expanded = expanded
    sidebar = MagicMock()
    sidebar.current_search = "overdue"
    sidebar._auto_expanding = auto_expanding
    sidebar.model.return_value.item_for_index.return_value = item
    return sidebar, item


def test_user_collapse_while_filtered_updates_saved_state():
    sidebar, item = sidebar_with_item(expanded=True, auto_expanding=False)

    SidebarTreeView._on_collapse(sidebar, MagicMock())

    assert item.expanded is False


def test_auto_expansion_of_matches_does_not_update_saved_state():
    sidebar, item = sidebar_with_item(expanded=False, auto_expanding=True)

    SidebarTreeView._on_expansion(sidebar, MagicMock())

    assert item.expanded is False
