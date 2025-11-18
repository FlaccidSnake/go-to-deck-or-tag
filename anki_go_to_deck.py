from aqt import mw
from aqt.gui_hooks import browser_will_show_context_menu
from aqt.qt import (
    QTreeWidgetItemIterator, 
    QApplication, 
    Qt, 
    QKeyEvent, 
    QEvent, 
    QTimer
)

def get_config():
    # Get config for the current add-on package
    addon_package = __name__.split('.')[0]
    config = mw.addonManager.getConfig(addon_package)
    return config if config else {}

def expand_and_select_legacy(browser, deck_name):
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

def simulate_key(widget, key, modifiers=Qt.KeyboardModifier.NoModifier):
    e_press = QKeyEvent(QEvent.Type.KeyPress, key, modifiers)
    e_release = QKeyEvent(QEvent.Type.KeyRelease, key, modifiers)
    QApplication.postEvent(widget, e_press)
    QApplication.postEvent(widget, e_release)

def filter_sidebar_modern_keyboard(browser, deck_name):
    # 1. Copy leaf name to clipboard
    leaf_name = deck_name.split("::")[-1]
    QApplication.clipboard().setText(leaf_name)

    # 2. Focus Sidebar (Ctrl+Shift+F)
    simulate_key(
        browser, 
        Qt.Key.Key_F, 
        Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier
    )

    def step_clear_paste_enter():
        focus_widget = QApplication.focusWidget()
        
        if focus_widget:
            # Select All (Ctrl+A)
            simulate_key(
                focus_widget, 
                Qt.Key.Key_A, 
                Qt.KeyboardModifier.ControlModifier
            )
            
            # Delete (Backspace)
            simulate_key(focus_widget, Qt.Key.Key_Backspace)
            
            # Paste (Ctrl+V)
            simulate_key(
                focus_widget, 
                Qt.Key.Key_V, 
                Qt.KeyboardModifier.ControlModifier
            )
            
            # Enter
            QTimer.singleShot(50, lambda: simulate_key(focus_widget, Qt.Key.Key_Return))

    # Wait for focus to change
    QTimer.singleShot(150, step_clear_paste_enter)

def filter_by_card_deck(browser):
    cids = browser.selectedCards()
    if not cids:
        return
    
    card = mw.col.get_card(cids[0])
    deck_name = mw.col.decks.name(card.did)
    
    # Always apply standard safety filter
    browser.setFilter(f'deck:"{deck_name}"')
    
    # Try Legacy method
    is_legacy = expand_and_select_legacy(browser, deck_name)
    
    if not is_legacy:
        # Check config before running the clipboard hack
        config = get_config()
        if config.get("enable_sidebar_clipboard_hack", False):
            filter_sidebar_modern_keyboard(browser, deck_name)

def on_context_menu(browser, menu):
    action = menu.addAction("Go to Deck")
    action.triggered.connect(lambda: filter_by_card_deck(browser))

browser_will_show_context_menu.append(on_context_menu)