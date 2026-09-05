SANGLOW_DARK = """
* {
    background-color: #1a1a1a;
    color: #e0d6cc;
    font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #1a1a1a;
}

QWidget#sidebar {
    background-color: #1a1a1a;
}

QWidget#sidebar QPushButton {
    text-align: left;
    padding: 10px 16px;
    border-radius: 8px;
    margin: 2px 8px;
    font-size: 14px;
    font-weight: 600;
    color: #a09888;
    background: transparent;
}

QWidget#sidebar QPushButton:hover {
    color: #e0d6cc;
    background-color: #252525;
}

QWidget#sidebar QPushButton:checked {
    color: #ffffff;
    background-color: #e8734a;
}

QPushButton {
    background-color: transparent;
    color: #a09888;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 13px;
}

QPushButton:hover {
    color: #e0d6cc;
    background-color: #252525;
}

QPushButton:pressed {
    background-color: #333333;
}

QPushButton#playButton {
    background-color: #e8734a;
    color: #ffffff;
    border-radius: 50%;
    font-size: 16px;
    font-weight: bold;
    padding: 10px;
    min-width: 42px;
    min-height: 42px;
    max-width: 42px;
    max-height: 42px;
}

QPushButton#playButton:hover {
    background-color: #f28150;
}

QPushButton#primaryButton {
    background-color: #e8734a;
    color: #ffffff;
    font-weight: 700;
    padding: 12px 32px;
    border-radius: 24px;
    font-size: 14px;
}

QPushButton#primaryButton:hover {
    background-color: #f28150;
}

QPushButton#primaryButton:pressed {
    background-color: #d4633a;
}

QPushButton#ghostButton {
    background: transparent;
    color: #e0d6cc;
    border: 1px solid #555555;
    border-radius: 20px;
    padding: 8px 20px;
    font-size: 12px;
}

QPushButton#ghostButton:hover {
    border-color: #e8734a;
    background-color: rgba(232, 115, 74, 0.08);
}

QPushButton#likeButton {
    background: transparent;
    color: #a09888;
    border: none;
    font-size: 18px;
    padding: 4px;
}

QPushButton#likeButton:hover {
    color: #e8734a;
}

QPushButton#likeButton:checked {
    color: #e8734a;
}

QLineEdit {
    background-color: #252525;
    color: #e0d6cc;
    border: 2px solid transparent;
    border-radius: 24px;
    padding: 12px 20px;
    font-size: 14px;
    selection-background-color: #e8734a;
}

QLineEdit:focus {
    border-color: #e8734a;
    background-color: #2a2a2a;
}

QLineEdit::placeholder {
    color: #666666;
}

QTextEdit {
    background-color: #252525;
    color: #e0d6cc;
    border: 1px solid #3a3a3a;
    border-radius: 10px;
    padding: 10px;
    font-size: 13px;
}

QTextEdit:focus {
    border-color: #e8734a;
}

QLabel#titleLabel {
    font-size: 28px;
    font-weight: 700;
    color: #ffffff;
}

QLabel#subtitleLabel {
    font-size: 14px;
    color: #a09888;
}

QLabel#accentLabel {
    color: #e8734a;
    font-weight: 600;
}

QLabel#sectionTitle {
    font-size: 22px;
    font-weight: 700;
    color: #ffffff;
}

QLabel#smallLabel {
    font-size: 11px;
    color: #666666;
}

QLabel#trackTitle {
    font-size: 14px;
    font-weight: 600;
    color: #ffffff;
    background: transparent;
}

QLabel#trackArtist {
    font-size: 12px;
    color: #a09888;
    background: transparent;
}

QLabel#commentUser {
    font-size: 12px;
    font-weight: 600;
    color: #e8734a;
    background: transparent;
}

QLabel#commentText {
    font-size: 12px;
    color: #e0d6cc;
    background: transparent;
}

QLabel#commentTime {
    font-size: 10px;
    color: #666666;
    background: transparent;
}

QLabel#likeCount {
    font-size: 11px;
    color: #a09888;
    background: transparent;
}

QListWidget {
    background-color: transparent;
    border: none;
    outline: none;
    font-size: 14px;
}

QListWidget::item {
    padding: 8px 12px;
    border-radius: 8px;
    margin: 2px 4px;
    color: #a09888;
}

QListWidget::item:selected {
    background-color: #333333;
    color: #ffffff;
}

QListWidget::item:hover {
    background-color: #252525;
    color: #ffffff;
}

QSlider::groove:horizontal {
    border: none;
    height: 4px;
    background: #444444;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #ffffff;
    width: 12px;
    height: 12px;
    margin: -4px 0;
    border-radius: 6px;
}

QSlider::handle:horizontal:hover {
    background: #ffffff;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}

QSlider::sub-page:horizontal {
    background: #a09888;
    border-radius: 2px;
}

QSlider:hover::sub-page:horizontal {
    background: #e8734a;
}

QScrollBar:vertical {
    background-color: transparent;
    width: 8px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: rgba(224, 214, 204, 0.12);
    border-radius: 4px;
    min-height: 40px;
}

QScrollBar::handle:vertical:hover {
    background-color: rgba(224, 214, 204, 0.25);
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: none;
}

QTabWidget::pane {
    border: none;
    background-color: #1a1a1a;
}

QTabBar::tab {
    background: transparent;
    color: #a09888;
    padding: 10px 24px;
    border: none;
    font-size: 14px;
    font-weight: 600;
    border-bottom: 3px solid transparent;
}

QTabBar::tab:selected {
    color: #ffffff;
    border-bottom-color: #e8734a;
}

QTabBar::tab:hover {
    color: #ffffff;
}

QDialog {
    background-color: #1e1e1e;
}

QMessageBox {
    background-color: #252525;
}

QMessageBox QLabel {
    color: #e0d6cc;
}

QMessageBox QPushButton {
    background-color: #e8734a;
    color: #ffffff;
    border-radius: 6px;
    padding: 6px 20px;
    min-width: 80px;
    font-weight: 600;
}

QMessageBox QPushButton:hover {
    background-color: #f28150;
}

QFrame#card {
    background-color: #222222;
    border-radius: 12px;
    border: none;
}

QFrame#card:hover {
    background-color: #2a2a2a;
}

QFrame#playerBar {
    background-color: #161616;
    border-top: 1px solid #2a2a2a;
}

QFrame#commentItem {
    background-color: #222222;
    border-radius: 10px;
    border: 1px solid #2a2a2a;
}

QFrame#waveCard {
    background-color: #222222;
    border-radius: 12px;
    border: none;
}

QFrame#waveCard:hover {
    background-color: #2a2a2a;
}

QComboBox {
    background-color: #252525;
    color: #e0d6cc;
    border: 1px solid #3a3a3a;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 12px;
}

QComboBox:hover {
    border-color: #e8734a;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #252525;
    color: #e0d6cc;
    border: 1px solid #3a3a3a;
    selection-background-color: #e8734a;
    selection-color: #ffffff;
    border-radius: 8px;
}

QCheckBox {
    color: #e0d6cc;
    font-size: 13px;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid #555555;
    background: #252525;
}

QCheckBox::indicator:checked {
    background: #e8734a;
    border-color: #e8734a;
}

QMenu {
    background-color: #252525;
    color: #e0d6cc;
    border: 1px solid #3a3a3a;
    border-radius: 8px;
    padding: 4px;
}

QMenu::item {
    padding: 8px 24px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #3a3a3a;
    color: #ffffff;
}

QMenu::separator {
    height: 1px;
    background: #3a3a3a;
    margin: 4px 8px;
}

QToolTip {
    background-color: #252525;
    color: #ffffff;
    border: 1px solid #e8734a;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
}
"""
