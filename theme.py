"""
theme.py — Premium minimalist clinical dark QSS stylesheet.
Palette: Deep slate and indigo, matching the Neural Diagnostics UI design.
"""

PALETTE = {
    "bg":             "#0b1326",
    "card":           "#1e293b",
    "surface":        "#2d3449",
    "sidebar":        "#0f172a",
    "accent":         "#c0c1ff",
    "accent_hover":   "#8083ff",
    "accent_pressed": "#494bd6",
    "success":        "#4edea3",
    "success_hover":  "#00a572",
    "danger":         "#ef4444",
    "danger_hover":   "#dc2626",
    "warn":           "#ffb95f",
    "warn_hover":     "#ca8100",
    "text":           "#dae2fd",
    "text2":          "#c7c4d7",
    "text3":          "#908fa0",
    "border":         "#334155",
    "border_focus":   "#c0c1ff",
}

QSS = """
/* ═══════════════════════════════════════════════════════
   BASE
═══════════════════════════════════════════════════════ */
QMainWindow, QDialog {
    background-color: #0b1326;
}

QWidget {
    background-color: transparent;
    color: #dae2fd;
    font-family: 'Inter', 'Outfit', 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
    selection-background-color: #8083ff;
    selection-color: #0b1326;
}

QWidget#appRoot {
    background-color: #0b1326;
}

QWidget#contentArea {
    background-color: #0b1326;
}

/* ═══════════════════════════════════════════════════════
   SIDEBAR
═══════════════════════════════════════════════════════ */
QWidget#sidebar {
    background-color: #0b1326;
    border-right: 1px solid #334155;
}

/* ═══════════════════════════════════════════════════════
   CARDS & FRAMES
═══════════════════════════════════════════════════════ */
QFrame#card {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
}

QWidget#card {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
}

QFrame#innerCard {
    background-color: #2d3449;
    border-radius: 10px;
    border: none;
}

QFrame#separator {
    background-color: #334155;
    max-height: 1px;
    min-height: 1px;
    border: none;
}

QFrame#userCard {
    background-color: #1e293b;
    border-radius: 10px;
    border: 1px solid #334155;
}

/* ═══════════════════════════════════════════════════════
   LABELS
═══════════════════════════════════════════════════════ */
QLabel {
    background: transparent;
    color: #dae2fd;
}

QLabel#brand {
    font-family: 'Outfit', 'Segoe UI';
    font-size: 24px;
    font-weight: 600;
    color: #c0c1ff;
    letter-spacing: -0.01em;
}

QLabel#heading {
    font-family: 'Outfit', 'Segoe UI';
    font-size: 32px;
    font-weight: 600;
    color: #dae2fd;
    letter-spacing: -0.01em;
}

QLabel#subheading {
    font-family: 'Inter', 'Segoe UI';
    font-size: 20px;
    font-weight: 600;
    color: #dae2fd;
}

QLabel#sectionTitle {
    font-family: 'Inter', 'Segoe UI';
    font-size: 16px;
    font-weight: 600;
    color: #dae2fd;
}

QLabel#subtext {
    color: #c7c4d7;
    font-size: 14px;
}

QLabel#muted {
    color: #908fa0;
    font-size: 12px;
    font-weight: 500;
}

QLabel#successLabel {
    color: #4edea3;
    font-weight: 700;
}

QLabel#dangerLabel {
    color: #ef4444;
    font-weight: 700;
}

QLabel#warnLabel {
    color: #ffb95f;
    font-weight: 600;
}

QLabel#warningBadge {
    background-color: rgba(239, 68, 68, 0.1);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
}

QLabel#resultTitle {
    font-family: 'Outfit', 'Segoe UI';
    font-size: 24px;
    font-weight: 600;
}

QLabel#imagePlaceholder {
    background-color: #0b1326;
    border-radius: 12px;
    color: #908fa0;
    font-size: 12px;
    font-family: 'Inter', monospace;
    border: 1px dashed #464554;
}

QLabel#formLabel {
    color: #c7c4d7;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

QLabel#statusLabel {
    color: #c7c4d7;
    font-size: 12px;
    font-weight: 600;
}

/* ═══════════════════════════════════════════════════════
   LINE EDIT / TEXT INPUT
═══════════════════════════════════════════════════════ */
QLineEdit {
    background-color: #0b1326;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 10px 14px;
    color: #dae2fd;
    font-size: 14px;
    selection-background-color: #8083ff;
}

QLineEdit:focus {
    border: 1px solid #c0c1ff;
    background-color: #0b1326;
}

QLineEdit:hover {
    border: 1px solid #464554;
}

QLineEdit[placeholderText] {
    color: #908fa0;
}

/* ═══════════════════════════════════════════════════════
   COMBO BOX
═══════════════════════════════════════════════════════ */
QComboBox {
    background-color: #0b1326;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 10px 14px;
    color: #dae2fd;
    font-size: 14px;
}

QComboBox:focus {
    border: 1px solid #c0c1ff;
}

QComboBox:hover {
    border: 1px solid #464554;
}

QComboBox::drop-down {
    border: none;
    width: 28px;
    subcontrol-origin: padding;
    subcontrol-position: top right;
}

QComboBox::down-arrow {
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #908fa0;
    width: 0;
    height: 0;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    selection-background-color: #8083ff;
    selection-color: #0b1326;
    padding: 4px;
    outline: none;
    color: #dae2fd;
}

QComboBox QAbstractItemView::item {
    padding: 9px 14px;
    border-radius: 4px;
    min-height: 30px;
}

QComboBox QAbstractItemView::item:hover {
    background-color: #2d3449;
}

QComboBox QAbstractItemView::item:selected {
    background-color: #8083ff;
    color: #0b1326;
}

/* ═══════════════════════════════════════════════════════
   PUSH BUTTONS
═══════════════════════════════════════════════════════ */
QPushButton {
    background-color: #2d3449;
    color: #dae2fd;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #334155;
}

QPushButton:pressed {
    background-color: #1e293b;
}

QPushButton:disabled {
    background-color: #1e293b;
    color: #464554;
    border: 1px solid #2d3449;
}

/* Accent (Indigo) */
QPushButton#accentBtn {
    background-color: #c0c1ff;
    color: #0b1326;
    border: none;
}
QPushButton#accentBtn:hover  { background-color: #e1e0ff; }
QPushButton#accentBtn:pressed { background-color: #8083ff; }
QPushButton#accentBtn:disabled { background-color: #2d3449; color: #464554; }

/* Success (Emerald) */
QPushButton#successBtn {
    background-color: #4edea3;
    color: #0b1326;
    border: none;
}
QPushButton#successBtn:hover  { background-color: #6ffbbe; }
QPushButton#successBtn:pressed { background-color: #00a572; }

/* Danger (Red) */
QPushButton#dangerBtn {
    background-color: #ef4444;
    color: #ffffff;
    border: none;
}
QPushButton#dangerBtn:hover  { background-color: #dc2626; }
QPushButton#dangerBtn:pressed { background-color: #b91c1c; }

/* Warn (Amber) */
QPushButton#warnBtn {
    background-color: #ffb95f;
    color: #0b1326;
    border: none;
}
QPushButton#warnBtn:hover  { background-color: #ffddb8; }
QPushButton#warnBtn:pressed { background-color: #ca8100; }

/* Ghost (transparent) */
QPushButton#ghostBtn {
    background-color: transparent;
    color: #c7c4d7;
    border: 1px solid #334155;
}
QPushButton#ghostBtn:hover { background-color: #1e293b; color: #dae2fd; }

/* Sidebar nav buttons */
QPushButton#navBtn {
    background-color: transparent;
    color: #908fa0;
    border-radius: 8px;
    padding: 10px 16px;
    text-align: left;
    font-size: 14px;
    font-weight: 500;
    border: none;
}
QPushButton#navBtn:hover {
    background-color: #1e293b;
    color: #dae2fd;
}

QPushButton#navBtnActive {
    background-color: rgba(192, 193, 255, 0.1);
    color: #c0c1ff;
    border-radius: 8px;
    padding: 10px 16px;
    text-align: left;
    font-size: 14px;
    font-weight: 600;
    border-left: 4px solid #c0c1ff;
}

/* Logout button */
QPushButton#logoutBtn {
    background-color: transparent;
    color: #ef4444;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    text-align: left;
    font-size: 14px;
    font-weight: 500;
}
QPushButton#logoutBtn:hover {
    background-color: rgba(239, 68, 68, 0.1);
}

/* Back button */
QPushButton#backBtn {
    background-color: transparent;
    color: #c7c4d7;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 14px;
    font-weight: 500;
}
QPushButton#backBtn:hover { background-color: rgba(192, 193, 255, 0.05); color: #dae2fd; }

/* ═══════════════════════════════════════════════════════
   PROGRESS BAR
═══════════════════════════════════════════════════════ */
QProgressBar {
    background-color: #171f33;
    border: 1px solid #334155;
    border-radius: 6px;
    height: 12px;
    text-align: center;
    color: transparent;
    font-size: 1px;
}

QProgressBar::chunk {
    background-color: #c0c1ff;
    border-radius: 5px;
}

QProgressBar#successBar::chunk { background-color: #4edea3; }
QProgressBar#dangerBar::chunk  { background-color: #ef4444; }
QProgressBar#warnBar::chunk    { background-color: #ffb95f; }

/* ═══════════════════════════════════════════════════════
   SCROLLBARS (slim, modern)
═══════════════════════════════════════════════════════ */
QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #2d3449;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #908fa0; }
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical { height: 0; background: none; }
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical { background: none; }

QScrollBar:horizontal {
    background: transparent;
    height: 8px;
}
QScrollBar::handle:horizontal {
    background: #2d3449;
    border-radius: 4px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover { background: #908fa0; }
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal { width: 0; background: none; }
QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal { background: none; }

/* ═══════════════════════════════════════════════════════
   SCROLL AREA
═══════════════════════════════════════════════════════ */
QScrollArea {
    border: none;
    background-color: transparent;
}

/* ═══════════════════════════════════════════════════════
   KPI DASHBOARD CARDS
═══════════════════════════════════════════════════════ */
QFrame#kpiCard {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
}

QFrame#kpiCard:hover {
    border-color: #c0c1ff;
}

QLabel#kpiVal {
    font-family: 'Outfit', 'Segoe UI';
    font-size: 32px;
    font-weight: 600;
    color: #dae2fd;
    letter-spacing: -0.01em;
}

QLabel#kpiTitle {
    font-family: 'Inter', monospace;
    font-size: 12px;
    color: #908fa0;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

QLabel#kpiIcon {
    font-size: 24px;
}

/* ═══════════════════════════════════════════════════════
   LIST ITEMS / TABLE ROWS
═══════════════════════════════════════════════════════ */
QFrame#listItemRow {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
}

QFrame#listItemRow:hover {
    background-color: #2d3449;
}

QFrame#listItemRowSelected {
    background-color: rgba(192, 193, 255, 0.05);
    border: 1px solid #c0c1ff;
    border-radius: 8px;
}

QLabel#badge {
    background-color: #2d3449;
    color: #dae2fd;
    border-radius: 4px;
    padding: 2px 6px;
    font-family: 'Inter', monospace;
    font-size: 10px;
    font-weight: 600;
    border: 1px solid #334155;
    text-transform: uppercase;
}

QLabel#badgeAccent {
    background-color: rgba(192, 193, 255, 0.1);
    color: #c0c1ff;
    border-radius: 4px;
    padding: 2px 6px;
    font-family: 'Inter', monospace;
    font-size: 10px;
    font-weight: 600;
    border: 1px solid rgba(192, 193, 255, 0.2);
    text-transform: uppercase;
}

QLabel#badgeSuccess {
    background-color: rgba(78, 222, 163, 0.1);
    color: #4edea3;
    border-radius: 4px;
    padding: 2px 6px;
    font-family: 'Inter', monospace;
    font-size: 10px;
    font-weight: 600;
    border: 1px solid rgba(78, 222, 163, 0.2);
    text-transform: uppercase;
}

/* ═══════════════════════════════════════════════════════
   MESSAGE BOX
═══════════════════════════════════════════════════════ */
QMessageBox {
    background-color: #1e293b;
}
QMessageBox QLabel {
    color: #dae2fd;
    font-size: 14px;
    min-width: 280px;
}
QMessageBox QPushButton {
    background-color: #c0c1ff;
    color: #0b1326;
    border: none;
    border-radius: 8px;
    padding: 8px 22px;
    min-width: 80px;
    font-weight: 600;
}
QMessageBox QPushButton:hover  { background-color: #e1e0ff; }
QMessageBox QPushButton:pressed { background-color: #8083ff; }
"""
