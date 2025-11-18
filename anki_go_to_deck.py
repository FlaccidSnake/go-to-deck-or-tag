import json
from aqt import mw
from aqt.gui_hooks import browser_will_show_context_menu
from aqt.qt import QTreeWidgetItemIterator, QTimer, QWebEnginePage

def expand_and_select_legacy(browser, deck_name):
    """Legacy method for Anki < 2.1.50 (Qt-based sidebar)"""
    try:
        tree = browser.form.searchTree
    except AttributeError:
        return False

    iterator = QTreeWidgetItemIterator(tree)
    while iterator.value():
        item = iterator.value()
        if item.text(0) == deck_name:
            parent = item.parent()
            while parent:
                parent.setExpanded(True)
                parent = parent.parent()
            tree.setCurrentItem(item)
            item.setSelected(True)
            tree.scrollToItem(item)
            return True
        iterator += 1
    return False

def filter_sidebar_modern_paste(browser, deck_name):
    """
    Modern method: Copies deck name to clipboard and triggers Paste 
    into the sidebar search box.
    """
    try:
        sidebar_web = browser.sidebar.web
    except AttributeError:
        return

    # 1. Get the leaf name (e.g. "Child" from "Parent::Child")
    leaf_name = deck_name.split("::")[-1]
    
    # 2. Copy to system Clipboard
    mw.app.clipboard().setText(leaf_name)

    # 3. JS: Focus the input and Select All (to overwrite existing text)
    # This mimics hitting Ctrl+Shift+F
    js_code = """
    (function() {
        var input = document.querySelector("input[type='text']") || document.querySelector("input");
        if (input) {
            input.focus();
            input.select();
        }
    })();
    """
    sidebar_web.eval(js_code)

    # 4. Trigger 'Paste' action after a tiny delay to allow focus to settle
    def trigger_paste():
        # WebAction.Paste is usually enum value 6
        sidebar_web.triggerPageAction(QWebEnginePage.WebAction.Paste)
    
    QTimer.singleShot(50, trigger_paste)

def filter_by_card_deck(browser):
    cids = browser.selectedCards()
    if not cids:
        return
    
    card = mw.col.get_card(cids[0])
    deck_name = mw.col.decks.name(card.did)
    
    # 1. Filter main list (standard method)
    browser.setFilter(f'deck:"{deck_name}"')
    
    # 2. Try Legacy sidebar (for old Anki)
    is_legacy = expand_and_select_legacy(browser, deck_name)
    
    # 3. If not legacy, use the Clipboard+Paste Hack
    if not is_legacy:
        filter_sidebar_modern_paste(browser, deck_name)

def on_context_menu(browser, menu):
    action = menu.addAction("Go to Deck")
    action.triggered.connect(lambda: filter_by_card_deck(browser))

browser_will_show_context_menu.append(on_context_menu)