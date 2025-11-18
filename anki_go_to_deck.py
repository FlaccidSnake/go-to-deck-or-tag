import json
from aqt import mw
from aqt.gui_hooks import browser_will_show_context_menu
from aqt.qt import QTreeWidgetItemIterator

def expand_and_select_legacy(browser, deck_name):
    """Legacy support for Anki < 2.1.50 (Qt Sidebar)"""
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

def filter_sidebar_modern(browser, deck_name):
    """Modern support for Anki 2.1.50+ (Svelte/Web Sidebar)"""
    try:
        sidebar_web = browser.sidebar.web
    except AttributeError:
        return

    # Get the last part of the deck name (e.g. "SubDeck" from "Parent::SubDeck")
    leaf_name = deck_name.split("::")[-1]
    safe_name = json.dumps(leaf_name)

    # JS: Find the first input, focus it (like Ctrl+Shift+F), and type
    js_code = f"""
    (function() {{
        // 1. Find the input. In the sidebar, the filter is usually the very first input.
        var input = document.querySelector("input[type='text']") || document.querySelector("input");
        
        if (input) {{
            // 2. Focus it (Simulate Ctrl+Shift+F)
            input.focus();
            
            // 3. Set the value
            input.value = {safe_name};
            
            // 4. Trigger events so Svelte 'reacts' to the change
            input.dispatchEvent(new Event('input', {{ bubbles: true }}));
            input.dispatchEvent(new Event('change', {{ bubbles: true }}));
        }}
    }})();
    """
    
    sidebar_web.eval(js_code)

def filter_by_card_deck(browser):
    cids = browser.selectedCards()
    if not cids:
        return
    
    card = mw.col.get_card(cids[0])
    deck_name = mw.col.decks.name(card.did)
    
    # 1. Filter main browser list
    browser.setFilter(f'deck:"{deck_name}"')
    
    # 2. Try Legacy Qt Method
    is_legacy = expand_and_select_legacy(browser, deck_name)
    
    # 3. If not legacy, try Modern Sidebar Search
    if not is_legacy:
        filter_sidebar_modern(browser, deck_name)

def on_context_menu(browser, menu):
    action = menu.addAction("Go to Deck")
    action.triggered.connect(lambda: filter_by_card_deck(browser))

browser_will_show_context_menu.append(on_context_menu)