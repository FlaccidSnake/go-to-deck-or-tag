# Anki Go-to-Deck Context Menu

A lightweight Anki add-on that adds a "Go to Deck" option to the browser's context menu, allowing you to instantly filter the view to the specific deck of a selected card.

[![Version](https://img.shields.io/badge/version-v1.2.0-blue)](https://github.com/yourusername/anki-go-to-deck) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Anki](https://img.shields.io/badge/Anki-2.1%2B-lightgrey)](https://apps.ankiweb.net/)

This utility solves a common navigation friction in the Anki Browser. Instead of manually searching for a deck name or scrolling through the sidebar, you can right-click any card and instantly isolate its home deck.

## Table of Contents

- [Anki Go-to-Deck Context Menu](#anki-go-to-deck-context-menu)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
    - [`enable_sidebar_clipboard_hack`](#enable_sidebar_clipboard_hack)
  - [Usage](#usage)
  - [Compatibility Notes](#compatibility-notes)
  - [Kardenwort Ecosystem](#kardenwort-ecosystem)
  - [License](#license)

## Features

-   **Context Menu Integration**: Adds a convenient "Go to Deck" option when right-clicking a card in the Browser.
-   **Instant Filtering**: Automatically applies a `deck:"Name"` filter to the search bar.
-   **Hybrid Behavior**:
    -   **Legacy Anki (Qt5)**: Automatically expands the sidebar tree and highlights the specific deck folder.
    -   **Modern Anki (2.1.50+ / Qt6)**: Applies the search filter by default. Optionally, it can visually expand the sidebar using an advanced input simulation method (see [Configuration](#configuration)).

[Back to Top](#table-of-contents)

## Prerequisites

-   **Anki Desktop**: Works on both legacy (2.1.x) and modern (23.x/24.x) versions.
-   **OS**: Windows, macOS, or Linux.

## Installation

**Step 1: Open the Add-ons Folder**
1.  Open Anki.
2.  Go to **Tools** -> **Add-ons** -> **View Files**.
3.  This opens the `addons21` folder on your computer.

**Step 2: Create the Folder Structure**
Inside `addons21`, create a new folder named `AnkiGoToDeck` (or any name you prefer, but avoid spaces).

**Step 3: Copy Files**
Copy the following three files from this repository into your newly created `AnkiGoToDeck` folder:
1.  `__init__.py`
2.  `anki_go_to_deck.py`
3.  `config.json`

**Final Structure:**
```
addons21/
└── AnkiGoToDeck/
    ├── __init__.py
    ├── anki_go_to_deck.py
    └── config.json
```

**Step 4: Restart Anki**
Restart the application for the add-on to load.

[Back to Top](#table-of-contents)

## Configuration

This add-on includes a `config.json` file to control advanced behavior for modern versions of Anki.

```json
{
    "enable_sidebar_clipboard_hack": false
}
```

### `enable_sidebar_clipboard_hack`
-   **Default:** `false`
-   **Description:** In modern Anki (2.1.50+), the sidebar is a web component that cannot be controlled via standard API calls. 
    -   **If `false`**: The add-on will simply filter the card list (`deck:"Name"`). The sidebar tree will not change visually.
    -   **If `true`**: The add-on will use a workaround to force the sidebar to expand to the correct deck.
    
**⚠️ Important Note for the "True" setting:**
To achieve this on modern Anki, the script copies the deck name to your **system clipboard** and simulates a keyboard sequence (`Ctrl+Shift+F` -> `Ctrl+A` -> `Delete` -> `Ctrl+V` -> `Enter`). Enable this only if you are comfortable with the add-on briefly using your clipboard when you click "Go to Deck".

[Back to Top](#table-of-contents)

## Usage

1.  Open the **Browser** in Anki.
2.  **Right-click** on any card in the list.
3.  Select **Go to Deck** from the context menu.
4.  The browser will immediately filter the list to show only cards from that deck.

[Back to Top](#table-of-contents)

## Compatibility Notes

**Sidebar Highlighting**
-   **Legacy Versions**: On older versions of Anki where the sidebar is a standard Qt Widget, this add-on will visually expand the tree and select the deck item automatically (ignoring `config.json`).
-   **Modern Versions (2.1.50+)**: Visual sidebar highlighting is disabled by default due to technical restrictions. It can be enabled by setting `"enable_sidebar_clipboard_hack": true` in the configuration file.

[Back to Top](#table-of-contents)


## Kardenwort Ecosystem

This project is part of the **[Kardenwort](https://github.com/kardenwort)** environment, designed to create a focused and efficient learning ecosystem.

[Back to Top](#table-of-contents)

## License

[MIT](./LICENSE)

[Back to Top](#table-of-contents)
