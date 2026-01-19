from aqt.qt import *
from aqt import mw
from aqt.utils import tooltip

class BrowserNavConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        addon_package = __name__.split('.')[0]
        self.config = mw.addonManager.getConfig(addon_package) or {}
        
        self.setWindowTitle("Browser Navigation Configuration")
        self.setMinimumWidth(450)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("<b>Browser Navigation Settings</b>")
        title_label.setStyleSheet("font-size: 14pt;")
        layout.addWidget(title_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Sidebar clipboard hack checkbox
        self.clipboard_cb = QCheckBox("Enable sidebar clipboard hack (for modern Anki)")
        self.clipboard_cb.setChecked(self.config.get("enable_sidebar_clipboard_hack", False))
        self.clipboard_cb.setToolTip(
            "Uses keyboard shortcuts to navigate the sidebar when the legacy tree view is not available.\n"
            "This is a workaround for newer Anki versions."
        )
        layout.addWidget(self.clipboard_cb)
        
        # Abbreviate tags checkbox
        self.abbreviate_cb = QCheckBox("Abbreviate long hierarchical tags")
        self.abbreviate_cb.setChecked(self.config.get("abbreviate_tags", False))
        self.abbreviate_cb.setToolTip(
            "Shortens tags like 'parent::middle::child' to 'parent::(...):child'\n"
            "in the tag selection dialog for better readability."
        )
        layout.addWidget(self.abbreviate_cb)
        
        # Info text
        info_label = QLabel(
            "<i>These settings control how the 'Go to Deck' and 'Go to Tag' context menu items work.</i>"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray;")
        layout.addWidget(info_label)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_config)
        save_button.setDefault(True)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.resize(450, 250)
    
    def save_config(self):
        """Save configuration"""
        addon_package = __name__.split('.')[0]
        
        self.config["enable_sidebar_clipboard_hack"] = self.clipboard_cb.isChecked()
        self.config["abbreviate_tags"] = self.abbreviate_cb.isChecked()
        
        mw.addonManager.writeConfig(addon_package, self.config)
        
        tooltip("Configuration saved! Changes will apply to new dialogs.")
        self.accept()

def show_config_dialog():
    """Show the configuration dialog"""
    dialog = BrowserNavConfigDialog(mw)
    dialog.exec()
