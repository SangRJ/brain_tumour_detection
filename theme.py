"""
theme.py — Light/Gray Clinical Theme.
"""

QSS = """
/* ═══════════════════════════════════════════════════════
   BASE
═══════════════════════════════════════════════════════ */
QMainWindow, QDialog {
    background-color: #fafafa;
}

QWidget {
    font-family: 'Inter', 'Outfit', 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
    color: #0f172a;
}

/* Base application wrapper */
QWidget#appRoot {
    background-color: #fafafa;
}

QWidget#contentArea {
    background-color: #fafafa;
}

/* Sidebar */
QWidget#sidebar {
    background-color: #ffffff;
    border-right: 1px solid #e2e8f0;
}

/* ═══════════════════════════════════════════════════════
   CARDS & FRAMES
═══════════════════════════════════════════════════════ */
QFrame#card, QWidget#card, QFrame#innerCard, QFrame#userCard, QFrame#kpiCard {
    background-color: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
}

QFrame#listItemRow {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
}
QFrame#listItemRow:hover {
    background-color: #f8fafc;
    border: 1px solid #cbd5e1;
}

QFrame#separator {
    background-color: #e2e8f0;
    max-height: 1px;
    min-height: 1px;
    border: none;
}

/* ═══════════════════════════════════════════════════════
   LABELS
═══════════════════════════════════════════════════════ */
QLabel {
    background: transparent;
    color: #0f172a;
}

QLabel#brand {
    font-family: 'Outfit', 'Segoe UI';
    font-size: 24px;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.01em;
}

QLabel#heading {
    font-family: 'Outfit', 'Segoe UI';
    font-size: 32px;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.01em;
}

QLabel#subheading, QLabel#sectionTitle {
    font-family: 'Inter', 'Segoe UI';
    font-size: 16px;
    font-weight: 600;
    color: #0f172a;
}

QLabel#subtext {
    color: #64748b;
    font-size: 14px;
}

QLabel#muted, QLabel#formLabel, QLabel#kpiTitle {
    color: #64748b;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

QLabel#warningBadge {
    background-color: #fee2e2;
    color: #b91c1c;
    border: 1px solid #fca5a5;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
}

/* ═══════════════════════════════════════════════════════
   LINE EDIT / COMBO BOX / TABLE
═══════════════════════════════════════════════════════ */
QLineEdit, QComboBox {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 10px 14px;
    color: #0f172a;
    font-size: 14px;
    selection-background-color: #e2e8f0;
    selection-color: #0f172a;
}

QLineEdit:focus, QComboBox:focus {
    border: 1px solid #0f172a;
}

QLineEdit:hover, QComboBox:hover {
    border: 1px solid #94a3b8;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    color: #0f172a;
    selection-background-color: #f1f5f9;
    selection-color: #0f172a;
}
QComboBox QAbstractItemView::item:hover {
    background-color: #f8fafc;
}

/* ═══════════════════════════════════════════════════════
   PUSH BUTTONS
═══════════════════════════════════════════════════════ */
/* Primary Buttons (Black background, White text) */
QPushButton {
    background-color: #000000;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #333333;
}

QPushButton:pressed {
    background-color: #555555;
}

QPushButton:disabled {
    background-color: #e2e8f0;
    color: #94a3b8;
    border: none;
}

/* Sidebar nav buttons */
QWidget#sidebar QPushButton#navBtn {
    background-color: transparent;
    color: #64748b;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: left;
    font-size: 14px;
    font-weight: 600;
    border: none;
}
QWidget#sidebar QPushButton#navBtn:hover {
    background-color: #f8fafc;
    color: #0f172a;
}

QWidget#sidebar QPushButton#navBtnActive {
    background-color: #e2e8f0;
    color: #0f172a;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: left;
    font-size: 14px;
    font-weight: 700;
    border-left: 4px solid #0f172a;
}

QWidget#sidebar QPushButton#logoutBtn {
    background-color: transparent;
    color: #0f172a;
    border: none;
    border-radius: 8px;
    padding: 12px 16px;
    text-align: left;
    font-size: 14px;
    font-weight: bold;
}
QWidget#sidebar QPushButton#logoutBtn:hover {
    background-color: #f1f5f9;
}

/* Secondary / Ghost buttons */
QPushButton#ghostBtn {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    padding: 6px 12px;
}
QPushButton#ghostBtn:hover { background-color: #f8fafc; border-color: #94a3b8; }

/* ═══════════════════════════════════════════════════════
   PROGRESS BAR & SCROLLBARS
═══════════════════════════════════════════════════════ */
QProgressBar {
    background-color: #e2e8f0;
    border: none;
    border-radius: 6px;
    height: 12px;
    text-align: center;
    color: transparent;
}
QProgressBar::chunk { background-color: #0f172a; border-radius: 6px; }

QScrollBar:vertical { background: transparent; width: 8px; margin: 0; }
QScrollBar::handle:vertical { background: #cbd5e1; border-radius: 4px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: #94a3b8; }
QScrollBar:horizontal { background: transparent; height: 8px; }
QScrollBar::handle:horizontal { background: #cbd5e1; border-radius: 4px; min-width: 30px; }

QScrollArea, QScrollArea > QWidget > QWidget { border: none; background-color: transparent; }
QAbstractScrollArea::viewport { background-color: transparent; }

/* ═══════════════════════════════════════════════════════
   TABLE / BADGES
═══════════════════════════════════════════════════════ */
QLabel#badge {
    background-color: #f1f5f9;
    color: #475569;
    border-radius: 6px;
    padding: 4px 8px;
    font-family: 'Inter', monospace;
    font-size: 11px;
    font-weight: 600;
    border: 1px solid #cbd5e1;
}

QLabel#badgeAccent {
    background-color: #eff6ff;
    color: #1d4ed8;
    border-radius: 6px;
    padding: 4px 8px;
    font-family: 'Inter', monospace;
    font-size: 11px;
    font-weight: 600;
    border: 1px solid #bfdbfe;
}

QLabel#badgeSuccess {
    background-color: #f0fdf4;
    color: #15803d;
    border-radius: 6px;
    padding: 4px 8px;
    font-family: 'Inter', monospace;
    font-size: 11px;
    font-weight: 600;
    border: 1px solid #bbf7d0;
}

/* ═══════════════════════════════════════════════════════
   MESSAGE BOX
═══════════════════════════════════════════════════════ */
QMessageBox {
    background-color: #ffffff;
}
QMessageBox QLabel {
    color: #0f172a;
    font-size: 14px;
    min-width: 550px;
    padding-right: 20px;
}
QMessageBox QPushButton {
    background-color: #000000;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 8px 22px;
    min-width: 80px;
    font-weight: bold;
}
QMessageBox QPushButton:hover  { background-color: #333333; }
QMessageBox QPushButton:pressed { background-color: #555555; }
"""
