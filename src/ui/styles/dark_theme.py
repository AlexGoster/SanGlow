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
    background-color: #141414;
    border-right: 1px solid #2a2a2a;
}

QWidget#sidebar QPushButton {
    text-align: left;
    padding: 10px 16px;
    border-radius: 8px;
    margin: 2px 8px;
    font-size: 13px;
    color: #8a8580;
    background: transparent;
}

QWidget#sidebar QPushButton:hover {
    color: #e8734a;
    background-color: #252525;
}

QWidget#sidebar QPushButton:checked {
    color: #e8734a;
    background-color: #2a2220;
}

QPushButton {
    background-color: transparent;
    color: #8a8580;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 13px;
}

QPushButton:hover {
    color: #e8734a;
    background-color: #252525;
}

QPushButton:pressed {
    background-color: #303030;
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
    background-color: #f08060;
}

QPushButton#primaryButton {
    background-color: #e8734a;
    color: #ffffff;
    font-weight: 600;
    padding: 12px 32px;
    border-radius: 24px;
    font-size: 14px;
}

QPushButton#primaryButton:hover {
    background-color: #f08060;
}

QPushButton#primaryButton:pressed {
    background-color: #d06040;
}

QPushButton#ghostButton {
    background: transparent;
    color: #e8734a;
    border: 1px solid #3a3535;
    border-radius: 20px;
    padding: 8px 20px;
    font-size: 12px;
}

QPushButton#ghostButton:hover {
    color: #f08060;
    border-color: #e8734a;
    background-color: rgba(232, 115, 74, 0.08);
}

QPushButton#likeButton {
    background: transparent;
    color: #8a8580;
    border: none;
    font-size: 18px;
    padding: 4px;
}

QPushButton#likeButton:hover {
    color: #e85040;
}

QPushButton#likeButton:checked {
    color: #e85040;
}

QLineEdit {
    background-color: #242424;
    color: #e0d6cc;
    border: 1px solid #3a3535;
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 14px;
    selection-background-color: #e8734a;
}

QLineEdit:focus {
    border-color: #e8734a;
    background-color: #282828;
}

QLineEdit::placeholder {
    color: #5a5550;
}

QTextEdit {
    background-color: #242424;
    color: #e0d6cc;
    border: 1px solid #3a3535;
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
    color: #8a8580;
}

QLabel#accentLabel {
    color: #e8734a;
    font-weight: 600;
}

QLabel#sectionTitle {
    font-size: 18px;
    font-weight: 700;
    color: #ffffff;
}

QLabel#smallLabel {
    font-size: 11px;
    color: #5a5550;
}

QLabel#trackTitle {
    font-size: 13px;
    font-weight: 600;
    color: #e0d6cc;
    background: transparent;
}

QLabel#trackArtist {
    font-size: 11px;
    color: #8a8580;
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
    color: #c0b8b0;
    background: transparent;
}

QLabel#commentTime {
    font-size: 10px;
    color: #5a5550;
    background: transparent;
}

QLabel#likeCount {
    font-size: 11px;
    color: #8a8580;
    background: transparent;
}

QListWidget {
    background-color: transparent;
    border: none;
    outline: none;
    font-size: 13px;
}

QListWidget::item {
    padding: 8px 12px;
    border-radius: 8px;
    margin: 2px 4px;
}

QListWidget::item:selected {
    background-color: #2a2220;
    color: #e8734a;
}

QListWidget::item:hover {
    background-color: #242424;
}

QSlider::groove:horizontal {
    border: none;
    height: 4px;
    background: #3a3535;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #e0d6cc;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}

QSlider::handle:horizontal:hover {
    background: #e8734a;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}

QSlider::sub-page:horizontal {
    background: #e8734a;
    border-radius: 2px;
}

QScrollBar:vertical {
    background-color: transparent;
    width: 6px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #3a3535;
    border-radius: 3px;
    min-height: 40px;
}

QScrollBar::handle:vertical:hover {
    background-color: #e8734a;
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
    color: #8a8580;
    padding: 10px 20px;
    border: none;
    font-size: 13px;
    font-weight: 500;
}

QTabBar::tab:selected {
    color: #e8734a;
    border-bottom: 2px solid #e8734a;
}

QTabBar::tab:hover {
    color: #e0d6cc;
}

QDialog {
    background-color: #1a1a1a;
}

QMessageBox {
    background-color: #242424;
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
}

QMessageBox QPushButton:hover {
    background-color: #f08060;
}

QFrame#card {
    background-color: #242424;
    border-radius: 12px;
    border: 1px solid #2a2a2a;
}

QFrame#card:hover {
    background-color: #2a2a2a;
    border-color: #3a3535;
}

QFrame#playerBar {
    background-color: #141414;
    border-top: 1px solid #2a2a2a;
}

QFrame#commentItem {
    background-color: #242424;
    border-radius: 10px;
    border: 1px solid #2a2a2a;
}

QFrame#waveCard {
    background-color: #242424;
    border-radius: 12px;
    border: 1px solid #2a2a2a;
}

QFrame#waveCard:hover {
    background-color: #2a2a2a;
    border-color: #e8734a;
}

QComboBox {
    background-color: #242424;
    color: #e0d6cc;
    border: 1px solid #3a3535;
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
    background-color: #242424;
    color: #e0d6cc;
    border: 1px solid #3a3535;
    selection-background-color: #e8734a;
    selection-color: #ffffff;
    border-radius: 8px;
}
"""
