from aqt import mw
from aqt.gui_hooks import browser_will_show_context_menu
from aqt.utils import tooltip
from aqt.qt import QTreeWidgetItemIterator

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

def filter_by_card_deck(browser):
    cids = browser.selectedCards()
    if not cids:
        return
    
    card = mw.col.get_card(cids[0])
    deck_name = mw.col.decks.name(card.did)
    
    browser.setFilter(f'deck:"{deck_name}"')
    
    success_legacy = expand_and_select_legacy(browser, deck_name)
    
    if not success_legacy:
        tooltip(f"Deck:\n{deck_name}")

def on_context_menu(browser, menu):
    action = menu.addAction("Go to Deck")
    action.triggered.connect(lambda: filter_by_card_deck(browser))

browser_will_show_context_menu.append(on_context_menu)