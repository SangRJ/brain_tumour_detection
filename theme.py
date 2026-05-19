"""
theme.py — Premium dark QSS stylesheet for Brain Tumour Diagnostics.
Palette: Slate/Indigo dark theme matching the original CTk design.
"""

PALETTE = {
    "bg":             "#020617",
    "card":           "#1e293b",
    "surface":        "#334155",
    "sidebar":        "#0f172a",
    "accent":         "#6366f1",
    "accent_hover":   "#4f46e5",
    "accent_pressed": "#4338ca",
    "success":        "#10b981",
    "success_hover":  "#059669",
    "danger":         "#ef4444",
    "danger_hover":   "#dc2626",
    "warn":           "#f59e0b",
    "warn_hover":     "#d97706",
    "text":           "#f8fafc",
    "text2":          "#94a3b8",
    "text3":          "#64748b",
    "border":         "#334155",
    "border_focus":   "#6366f1",
}

QSS = """
/* ═══════════════════════════════════════════════════════
   BASE
═══════════════════════════════════════════════════════ */
QMainWindow, QDialog {
    background-color: #020617;
}

QWidget {
    background-color: transparent;
    color: #f8fafc;
    font-family: 'Segoe UI', 'SF Pro Display', 'Inter', 'Helvetica Neue', Arial, sans-serif;
    font-size: 14px;
    selection-background-color: #6366f1;
    selection-color: #f8fafc;
}

QWidget#appRoot {
    background-color: #020617;
}

QWidget#contentArea {
    background-color: #020617;
}

/* ═══════════════════════════════════════════════════════
   SIDEBAR
═══════════════════════════════════════════════════════ */
QWidget#sidebar {
    background-color: #0f172a;
    border-right: 1px solid #334155;
}

/* ═══════════════════════════════════════════════════════
   CARDS & FRAMES
═══════════════════════════════════════════════════════ */
QFrame#card {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 14px;
}

QWidget#card {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 14px;
}

QFrame#innerCard {
    background-color: #334155;
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
    color: #f8fafc;
}

QLabel#brand {
    font-size: 20px;
    font-weight: 700;
    color: #f8fafc;
    letter-spacing: 0.5px;
}

QLabel#heading {
    font-size: 24px;
    font-weight: 700;
    color: #f8fafc;
}

QLabel#subheading {
    font-size: 17px;
    font-weight: 600;
    color: #f8fafc;
}

QLabel#sectionTitle {
    font-size: 15px;
    font-weight: 600;
    color: #f8fafc;
}

QLabel#subtext {
    color: #94a3b8;
    font-size: 13px;
}

QLabel#muted {
    color: #64748b;
    font-size: 12px;
}

QLabel#successLabel {
    color: #10b981;
    font-weight: 700;
}

QLabel#dangerLabel {
    color: #ef4444;
    font-weight: 700;
}

QLabel#warnLabel {
    color: #f59e0b;
    font-weight: 600;
}

QLabel#warningBadge {
    background-color: #7f1d1d;
    color: #fca5a5;
    border-radius: 6px;
    padding: 5px 12px;
    font-size: 11px;
    font-weight: 700;
}

QLabel#resultTitle {
    font-size: 20px;
    font-weight: 700;
}

QLabel#imagePlaceholder {
    background-color: #1e293b;
    border-radius: 10px;
    color: #94a3b8;
    font-size: 13px;
    border: 1px dashed #334155;
}

QLabel#formLabel {
    color: #94a3b8;
    font-size: 13px;
    font-weight: 600;
}

QLabel#statusLabel {
    color: #94a3b8;
    font-size: 12px;
    font-weight: 600;
}

/* ═══════════════════════════════════════════════════════
   LINE EDIT / TEXT INPUT
═══════════════════════════════════════════════════════ */
QLineEdit {
    background-color: #0f172a;
    border: 1.5px solid #334155;
    border-radius: 8px;
    padding: 11px 14px;
    color: #f8fafc;
    font-size: 14px;
    selection-background-color: #6366f1;
}

QLineEdit:focus {
    border: 1.5px solid #6366f1;
    background-color: #0f172a;
}

QLineEdit:hover {
    border: 1.5px solid #475569;
}

QLineEdit[placeholderText] {
    color: #64748b;
}

/* ═══════════════════════════════════════════════════════
   COMBO BOX
═══════════════════════════════════════════════════════ */
QComboBox {
    background-color: #0f172a;
    border: 1.5px solid #334155;
    border-radius: 8px;
    padding: 11px 14px;
    color: #f8fafc;
    font-size: 14px;
}

QComboBox:focus {
    border: 1.5px solid #6366f1;
}

QComboBox:hover {
    border: 1.5px solid #475569;
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
    border-top: 6px solid #94a3b8;
    width: 0;
    height: 0;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    selection-background-color: #6366f1;
    selection-color: #f8fafc;
    padding: 4px;
    outline: none;
    color: #f8fafc;
}

QComboBox QAbstractItemView::item {
    padding: 9px 14px;
    border-radius: 4px;
    min-height: 30px;
}

QComboBox QAbstractItemView::item:hover {
    background-color: #334155;
}

QComboBox QAbstractItemView::item:selected {
    background-color: #6366f1;
}

/* ═══════════════════════════════════════════════════════
   PUSH BUTTONS
═══════════════════════════════════════════════════════ */
QPushButton {
    background-color: #334155;
    color: #f8fafc;
    border: none;
    border-radius: 8px;
    padding: 11px 20px;
    font-size: 14px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #475569;
}

QPushButton:pressed {
    background-color: #1e293b;
}

QPushButton:disabled {
    background-color: #1e293b;
    color: #475569;
}

/* Accent (Indigo) */
QPushButton#accentBtn {
    background-color: #6366f1;
    color: #ffffff;
}
QPushButton#accentBtn:hover  { background-color: #4f46e5; }
QPushButton#accentBtn:pressed { background-color: #4338ca; }
QPushButton#accentBtn:disabled { background-color: #312e81; color: #818cf8; }

/* Success (Emerald) */
QPushButton#successBtn {
    background-color: #10b981;
    color: #ffffff;
}
QPushButton#successBtn:hover  { background-color: #059669; }
QPushButton#successBtn:pressed { background-color: #047857; }

/* Danger (Red) */
QPushButton#dangerBtn {
    background-color: #ef4444;
    color: #ffffff;
}
QPushButton#dangerBtn:hover  { background-color: #dc2626; }
QPushButton#dangerBtn:pressed { background-color: #b91c1c; }

/* Warn (Amber) */
QPushButton#warnBtn {
    background-color: #f59e0b;
    color: #0f172a;
}
QPushButton#warnBtn:hover  { background-color: #d97706; }
QPushButton#warnBtn:pressed { background-color: #b45309; }

/* Ghost (transparent) */
QPushButton#ghostBtn {
    background-color: transparent;
    color: #94a3b8;
    border: 1px solid #334155;
}
QPushButton#ghostBtn:hover { background-color: #1e293b; color: #f8fafc; }

/* Sidebar nav buttons */
QPushButton#navBtn {
    background-color: transparent;
    color: #94a3b8;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: left;
    font-size: 14px;
    font-weight: 600;
}
QPushButton#navBtn:hover {
    background-color: #1e293b;
    color: #f8fafc;
}

QPushButton#navBtnActive {
    background-color: #1e293b;
    color: #f8fafc;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: left;
    font-size: 14px;
    font-weight: 600;
    border-left: 3px solid #6366f1;
}

/* Logout button */
QPushButton#logoutBtn {
    background-color: transparent;
    color: #ef4444;
    border: none;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: left;
    font-size: 14px;
    font-weight: 600;
}
QPushButton#logoutBtn:hover {
    background-color: #7f1d1d;
    color: #fca5a5;
}

/* Back button */
QPushButton#backBtn {
    background-color: transparent;
    color: #94a3b8;
    border: none;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    font-weight: 600;
}
QPushButton#backBtn:hover { color: #f8fafc; background-color: #1e293b; }

/* ═══════════════════════════════════════════════════════
   PROGRESS BAR
═══════════════════════════════════════════════════════ */
QProgressBar {
    background-color: #334155;
    border: none;
    border-radius: 6px;
    height: 12px;
    text-align: center;
    color: transparent;
    font-size: 1px;
}

QProgressBar::chunk {
    background-color: #6366f1;
    border-radius: 6px;
}

QProgressBar#successBar::chunk { background-color: #10b981; }
QProgressBar#dangerBar::chunk  { background-color: #ef4444; }
QProgressBar#warnBar::chunk    { background-color: #f59e0b; }

/* ═══════════════════════════════════════════════════════
   SCROLLBARS (slim, modern)
═══════════════════════════════════════════════════════ */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #334155;
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #475569; }
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical { height: 0; background: none; }
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical { background: none; }

QScrollBar:horizontal {
    background: transparent;
    height: 6px;
}
QScrollBar::handle:horizontal {
    background: #334155;
    border-radius: 3px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover { background: #475569; }
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
    border-color: #6366f1;
    background-color: #243147;
}

QLabel#kpiVal {
    font-size: 22px;
    font-weight: bold;
    color: #f8fafc;
}

QLabel#kpiTitle {
    font-size: 11px;
    color: #94a3b8;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

QLabel#kpiIcon {
    font-size: 24px;
}

/* ═══════════════════════════════════════════════════════
   LIST ITEMS / TABLE ROWS
═══════════════════════════════════════════════════════ */
QFrame#listItemRow {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 8px;
}

QFrame#listItemRow:hover {
    border-color: #6366f1;
    background-color: #1e293b;
}

QFrame#listItemRowSelected {
    background-color: #1e293b;
    border: 1.5px solid #6366f1;
    border-radius: 8px;
}

QLabel#badge {
    background-color: #334155;
    color: #e2e8f0;
    border-radius: 4px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: 600;
}

QLabel#badgeAccent {
    background-color: #312e81;
    color: #c7d2fe;
    border-radius: 4px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: 600;
}

QLabel#badgeSuccess {
    background-color: #064e3b;
    color: #a7f3d0;
    border-radius: 4px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: 600;
}

/* ═══════════════════════════════════════════════════════
   MESSAGE BOX
═══════════════════════════════════════════════════════ */
QMessageBox {
    background-color: #1e293b;
}
QMessageBox QLabel {
    color: #f8fafc;
    font-size: 14px;
    min-width: 280px;
}
QMessageBox QPushButton {
    background-color: #6366f1;
    color: #ffffff;
    border: none;
    border-radius: 6px;
    padding: 8px 22px;
    min-width: 80px;
    font-weight: 600;
}
QMessageBox QPushButton:hover  { background-color: #4f46e5; }
QMessageBox QPushButton:pressed { background-color: #4338ca; }
"""
