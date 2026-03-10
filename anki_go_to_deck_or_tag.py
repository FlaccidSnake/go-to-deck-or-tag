from aqt import mw
from aqt.gui_hooks import browser_will_show_context_menu
from . import config_dialog
from aqt.qt import *

def get_config():
    addon_package = __name__.split('.')[0]
    config = mw.addonManager.getConfig(addon_package)
    return config if config else {}

def expand_and_select_legacy(browser, item_name):
    try:
        tree = browser.form.searchTree
    except AttributeError:
        return False
    
    iterator = QTreeWidgetItemIterator(tree)
    while iterator.value():
        item = iterator.value()
        if item.text(0) == item_name:
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

def filter_sidebar_modern_keyboard(browser, item_name):
    leaf_name = item_name.split("::")[-1]
    QApplication.clipboard().setText(leaf_name)
    
    simulate_key(
        browser, 
        Qt.Key.Key_F, 
        Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier
    )
    
    def step_clear_paste_enter():
        focus_widget = QApplication.focusWidget()
        
        if focus_widget:
            simulate_key(focus_widget, Qt.Key.Key_A, Qt.KeyboardModifier.ControlModifier)
            simulate_key(focus_widget, Qt.Key.Key_Backspace)
            simulate_key(focus_widget, Qt.Key.Key_V, Qt.KeyboardModifier.ControlModifier)
            QTimer.singleShot(50, lambda: simulate_key(focus_widget, Qt.Key.Key_Return))
    
    QTimer.singleShot(150, step_clear_paste_enter)

# --- FLOW LAYOUT CLASS ---

class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self.item_list = []
    
    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)
    
    def addItem(self, item):
        self.item_list.append(item)
    
    def count(self):
        return len(self.item_list)
    
    def itemAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list[index]
        return None
    
    def takeAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list.pop(index)
        return None
    
    def expandingDirections(self):
        return Qt.Orientation(0)
    
    def hasHeightForWidth(self):
        return True
    
    def heightForWidth(self, width):
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height
    
    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, False)
    
    def sizeHint(self):
        return self.minimumSize()
    
    def minimumSize(self):
        size = QSize()
        for item in self.item_list:
            size = size.expandedTo(item.minimumSize())
        margin = self.contentsMargins()
        size += QSize(margin.left() + margin.right(), margin.top() + margin.bottom())
        return size
    
    def _do_layout(self, rect, test_only):
        left, top, right, bottom = self.getContentsMargins()
        effective_rect = rect.adjusted(left, top, -right, -bottom)
        x = effective_rect.x()
        y = effective_rect.y()
        line_height = 0
        
        for item in self.item_list:
            widget = item.widget()
            space_x = self.spacing()
            space_y = self.spacing()
            
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > effective_rect.right() and line_height > 0:
                x = effective_rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0
            
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        
        return y + line_height - rect.y() + bottom

# --- DECK SELECTION DIALOG ---

class DeckSelectionDialog(QDialog):
    def __init__(self, decks, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Decks")
        
        addon_package = __name__.split('.')[0]
        self.config = mw.addonManager.getConfig(addon_package) or {}
        self.abbreviate = self.config.get("abbreviate_decks", False)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Top bar
        top_bar = QHBoxLayout()
        
        self.select_all_cb = QCheckBox("Select All")
        self.select_all_cb.setChecked(True)
        self.select_all_cb.stateChanged.connect(self.toggle_all)
        top_bar.addWidget(self.select_all_cb)
        
        top_bar.addSpacing(20)
        
        self.abbreviate_cb = QCheckBox("Abbreviate decks")
        self.abbreviate_cb.setChecked(self.abbreviate)
        self.abbreviate_cb.stateChanged.connect(self.on_abbreviate_changed)
        top_bar.addWidget(self.abbreviate_cb)
        
        top_bar.addStretch()
        layout.addLayout(top_bar)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        scroll_widget = QWidget()
        self.flow_layout = FlowLayout()
        self.flow_layout.setContentsMargins(0, 0, 0, 0)
        scroll_widget.setLayout(self.flow_layout)
        
        self.deck_checkboxes = []
        for deck in sorted(decks):
            cb = QCheckBox(self._get_display_deck(deck))
            cb.setProperty("full_deck", deck)
            cb.setChecked(True)
            cb.stateChanged.connect(self.update_select_all_state)
            cb.setToolTip(deck)
            self.deck_checkboxes.append(cb)
            self.flow_layout.addWidget(cb)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)
        
        self.setLayout(layout)
        self.resize(400, 300)
    
    def toggle_all(self, state):
        checked = state == Qt.CheckState.Checked.value
        for cb in self.deck_checkboxes:
            cb.setChecked(checked)
    
    def on_abbreviate_changed(self, state):
        self.abbreviate = (state == Qt.CheckState.Checked.value)
        
        addon_package = __name__.split('.')[0]
        self.config['abbreviate_decks'] = self.abbreviate
        mw.addonManager.writeConfig(addon_package, self.config)
        
        for cb in self.deck_checkboxes:
            full_deck = cb.property("full_deck")
            cb.setText(self._get_display_deck(full_deck))
    
    def _get_display_deck(self, deck: str) -> str:
        if not self.abbreviate:
            return deck
        if "::" not in deck:
            return deck
        parts = deck.split("::")
        if len(parts) <= 2:
            return deck
        return f"{parts[0]}::(...)::{parts[-1]}"
    
    def update_select_all_state(self):
        all_checked = all(cb.isChecked() for cb in self.deck_checkboxes)
        none_checked = not any(cb.isChecked() for cb in self.deck_checkboxes)
        
        self.select_all_cb.blockSignals(True)
        if all_checked:
            self.select_all_cb.setChecked(True)
        elif none_checked:
            self.select_all_cb.setChecked(False)
        else:
            self.select_all_cb.setCheckState(Qt.CheckState.PartiallyChecked)
        self.select_all_cb.blockSignals(False)
    
    def get_selected_decks(self):
        return [cb.property("full_deck") for cb in self.deck_checkboxes if cb.isChecked()]

# --- TAG SELECTION DIALOG ---

class TagSelectionDialog(QDialog):
    def __init__(self, tags, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Tags")
        self.selected_tags = []
        
        addon_package = __name__.split('.')[0]
        self.config = mw.addonManager.getConfig(addon_package) or {}
        self.abbreviate = self.config.get("abbreviate_tags", False)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        top_bar = QHBoxLayout()
        
        self.select_all_cb = QCheckBox("Select All")
        self.select_all_cb.setChecked(True)
        self.select_all_cb.stateChanged.connect(self.toggle_all)
        top_bar.addWidget(self.select_all_cb)
        
        top_bar.addSpacing(20)
        
        self.abbreviate_cb = QCheckBox("Abbreviate tags")
        self.abbreviate_cb.setChecked(self.abbreviate)
        self.abbreviate_cb.stateChanged.connect(self.on_abbreviate_changed)
        top_bar.addWidget(self.abbreviate_cb)
        
        top_bar.addStretch()
        layout.addLayout(top_bar)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        scroll_widget = QWidget()
        self.flow_layout = FlowLayout()
        self.flow_layout.setContentsMargins(0, 0, 0, 0)
        scroll_widget.setLayout(self.flow_layout)
        
        self.tag_checkboxes = []
        for tag in sorted(tags):
            cb = QCheckBox(self._get_display_tag(tag))
            cb.setProperty("full_tag", tag)
            cb.setChecked(True)
            cb.stateChanged.connect(self.update_select_all_state)
            cb.setToolTip(tag)
            self.tag_checkboxes.append(cb)
            self.flow_layout.addWidget(cb)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)
        
        self.setLayout(layout)
        self.resize(400, 300)
    
    def toggle_all(self, state):
        checked = state == Qt.CheckState.Checked.value
        for cb in self.tag_checkboxes:
            cb.setChecked(checked)
    
    def on_abbreviate_changed(self, state):
        self.abbreviate = (state == Qt.CheckState.Checked.value)
        
        addon_package = __name__.split('.')[0]
        self.config['abbreviate_tags'] = self.abbreviate
        mw.addonManager.writeConfig(addon_package, self.config)
        
        for cb in self.tag_checkboxes:
            full_tag = cb.property("full_tag")
            cb.setText(self._get_display_tag(full_tag))
    
    def _get_display_tag(self, tag: str) -> str:
        if not self.abbreviate:
            return tag
        if "::" not in tag:
            return tag
        parts = tag.split("::")
        if len(parts) <= 2:
            return tag
        return f"{parts[0]}::(...)::{parts[-1]}"
    
    def update_select_all_state(self):
        all_checked = all(cb.isChecked() for cb in self.tag_checkboxes)
        none_checked = not any(cb.isChecked() for cb in self.tag_checkboxes)
        
        self.select_all_cb.blockSignals(True)
        if all_checked:
            self.select_all_cb.setChecked(True)
        elif none_checked:
            self.select_all_cb.setChecked(False)
        else:
            self.select_all_cb.setCheckState(Qt.CheckState.PartiallyChecked)
        self.select_all_cb.blockSignals(False)
    
    def get_selected_tags(self):
        return [cb.property("full_tag") for cb in self.tag_checkboxes if cb.isChecked()]

# --- FILTER FUNCTIONS ---

def filter_by_card_deck(browser):
    cids = browser.selectedCards()
    if not cids:
        return

    # Collect decks from ALL selected cards
    all_decks = set()
    for cid in cids:
        card = mw.col.get_card(cid)
        deck_name = mw.col.decks.name(card.did)
        all_decks.add(deck_name)

    decks = list(all_decks)

    if len(decks) > 1:
        dialog = DeckSelectionDialog(decks, browser)
        if dialog.exec():
            selected_decks = dialog.get_selected_decks()
            if not selected_decks:
                return

            if len(selected_decks) == 1:
                deck_filter = f'deck:"{selected_decks[0]}"'
                sidebar_deck = selected_decks[0]
            else:
                deck_filter = " OR ".join([f'deck:"{d}"' for d in selected_decks])
                sidebar_deck = selected_decks[0]
        else:
            return
    else:
        deck_filter = f'deck:"{decks[0]}"'
        sidebar_deck = decks[0]

    browser.setFilter(deck_filter)

    is_legacy = expand_and_select_legacy(browser, sidebar_deck)

    if not is_legacy:
        config = get_config()
        if config.get("enable_sidebar_clipboard_hack", False):
            filter_sidebar_modern_keyboard(browser, sidebar_deck)

def filter_by_card_tag(browser):
    cids = browser.selectedCards()
    if not cids:
        return
    
    # Collect tags from ALL selected cards
    all_tags = set()
    for cid in cids:
        card = mw.col.get_card(cid)
        note = mw.col.get_note(card.nid)
        all_tags.update(note.tags)
    
    tags = list(all_tags)
    
    if not tags:
        return
    
    if len(tags) > 1:
        dialog = TagSelectionDialog(tags, browser)
        if dialog.exec():
            selected_tags = dialog.get_selected_tags()
            if not selected_tags:
                return
            
            if len(selected_tags) == 1:
                tag_filter = f'tag:"{selected_tags[0]}"'
                sidebar_tag = selected_tags[0]
            else:
                tag_filter = " OR ".join([f'tag:"{tag}"' for tag in selected_tags])
                sidebar_tag = selected_tags[0]
        else:
            return
    else:
        tag_filter = f'tag:"{tags[0]}"'
        sidebar_tag = tags[0]
    
    browser.setFilter(tag_filter)
    
    is_legacy = expand_and_select_legacy(browser, sidebar_tag)
    
    if not is_legacy:
        config = get_config()
        if config.get("enable_sidebar_clipboard_hack", False):
            filter_sidebar_modern_keyboard(browser, sidebar_tag)

def on_context_menu(browser, menu):
    action_deck = menu.addAction("Go to Deck")
    action_deck.triggered.connect(lambda: filter_by_card_deck(browser))
    
    action_tag = menu.addAction("Go to Tag")
    action_tag.triggered.connect(lambda: filter_by_card_tag(browser))

browser_will_show_context_menu.append(on_context_menu)

addon_package = __name__.split('.')[0]
mw.addonManager.setConfigAction(addon_package, config_dialog.show_config_dialog)
