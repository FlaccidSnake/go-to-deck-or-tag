from aqt import mw
from aqt.gui_hooks import browser_will_show_context_menu

def filter_by_card_deck(browser):
    cids = browser.selectedCards()
    if not cids:
        return
    
    card = mw.col.get_card(cids[0])
    deck_name = mw.col.decks.name(card.did)
    
    browser.search(f'deck:"{deck_name}"')

def on_context_menu(browser, menu):
    action = menu.addAction("Go to Deck")
    action.triggered.connect(lambda: filter_by_card_deck(browser))

browser_will_show_context_menu.append(on_context_menu)