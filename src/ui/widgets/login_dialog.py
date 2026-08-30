from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QStackedWidget, QWidget, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal

from src.auth.service import AuthService
from src.models.database import get_db_session


class LoginDialog(QDialog):
    login_successful = pyqtSignal(dict)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("SanGlow")
        self.setFixedSize(480, 640)
        self._error_label = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        hero = QFrame()
        hero.setFixedHeight(200)
        hero.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2018, stop:1 #1a1a1a);
                border: none;
            }
        """)
        hero_layout = QVBoxLayout(hero)
        hero_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo = QLabel("SanGlow")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("font-size: 36px; font-weight: 700; color: #e8734a; background: transparent;")
        hero_layout.addWidget(logo)

        tagline = QLabel("Your music. Your sound.")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tagline.setStyleSheet("font-size: 13px; color: #8a8580; background: transparent; margin-top: 4px;")
        hero_layout.addWidget(tagline)
        layout.addWidget(hero)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(48, 24, 48, 24)
        content_layout.setSpacing(14)

        self._stack = QStackedWidget()
        self._stack.addWidget(self._create_login_page())
        self._stack.addWidget(self._create_register_page())
        content_layout.addWidget(self._stack)
        content_layout.addStretch()

        layout.addWidget(content, stretch=1)

    def _create_login_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(12)

        title = QLabel("Welcome back")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        subtitle = QLabel("Sign in to continue listening")
        subtitle.setObjectName("subtitleLabel")
        layout.addWidget(subtitle)
        layout.addSpacing(6)

        self._login_username = QLineEdit()
        self._login_username.setPlaceholderText("Username or email")
        self._login_username.setFixedHeight(46)
        layout.addWidget(self._login_username)

        self._login_password = QLineEdit()
        self._login_password.setPlaceholderText("Password")
        self._login_password.setEchoMode(QLineEdit.EchoMode.Password)
        self._login_password.setFixedHeight(46)
        self._login_password.returnPressed.connect(self._handle_login)
        layout.addWidget(self._login_password)

        layout.addSpacing(4)

        login_btn = QPushButton("Sign In")
        login_btn.setObjectName("primaryButton")
        login_btn.setFixedHeight(46)
        login_btn.clicked.connect(self._handle_login)
        layout.addWidget(login_btn)

        layout.addSpacing(16)

        register_link = QPushButton("Create an account")
        register_link.setObjectName("ghostButton")
        register_link.setFixedHeight(42)
        register_link.clicked.connect(lambda: self._stack.setCurrentIndex(1))
        layout.addWidget(register_link)

        return page

    def _create_register_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)

        title = QLabel("Create account")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        subtitle = QLabel("Start your music journey")
        subtitle.setObjectName("subtitleLabel")
        layout.addWidget(subtitle)
        layout.addSpacing(4)

        self._reg_username = QLineEdit()
        self._reg_username.setPlaceholderText("Username")
        self._reg_username.setFixedHeight(42)
        layout.addWidget(self._reg_username)

        self._reg_email = QLineEdit()
        self._reg_email.setPlaceholderText("Email")
        self._reg_email.setFixedHeight(42)
        layout.addWidget(self._reg_email)

        self._reg_display = QLineEdit()
        self._reg_display.setPlaceholderText("Display name (optional)")
        self._reg_display.setFixedHeight(42)
        layout.addWidget(self._reg_display)

        self._reg_password = QLineEdit()
        self._reg_password.setPlaceholderText("Password")
        self._reg_password.setEchoMode(QLineEdit.EchoMode.Password)
        self._reg_password.setFixedHeight(42)
        layout.addWidget(self._reg_password)

        self._reg_confirm = QLineEdit()
        self._reg_confirm.setPlaceholderText("Confirm password")
        self._reg_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self._reg_confirm.setFixedHeight(42)
        self._reg_confirm.returnPressed.connect(self._handle_register)
        layout.addWidget(self._reg_confirm)

        layout.addSpacing(4)

        register_btn = QPushButton("Create Account")
        register_btn.setObjectName("primaryButton")
        register_btn.setFixedHeight(46)
        register_btn.clicked.connect(self._handle_register)
        layout.addWidget(register_btn)

        layout.addSpacing(12)

        login_link = QPushButton("Already have an account? Sign in")
        login_link.setObjectName("ghostButton")
        login_link.setFixedHeight(42)
        login_link.clicked.connect(lambda: self._stack.setCurrentIndex(0))
        layout.addWidget(login_link)

        return page

    def _handle_login(self) -> None:
        username = self._login_username.text().strip()
        password = self._login_password.text()
        if not username or not password:
            self._show_error("Please fill in all fields")
            return
        with get_db_session() as db:
            result = AuthService(db).login(username, password)
            if result.success and result.user:
                self.login_successful.emit(result.user.to_dict())
                self.accept()
            else:
                self._show_error(result.error or "Invalid credentials")

    def _handle_register(self) -> None:
        username = self._reg_username.text().strip()
        email = self._reg_email.text().strip()
        display_name = self._reg_display.text().strip()
        password = self._reg_password.text()
        confirm = self._reg_confirm.text()
        if not username or not email or not password:
            self._show_error("Please fill in all required fields")
            return
        if password != confirm:
            self._show_error("Passwords do not match")
            return
        with get_db_session() as db:
            result = AuthService(db).register(username, email, password, display_name or None)
            if result.success and result.user:
                self.login_successful.emit(result.user.to_dict())
                self.accept()
            else:
                self._show_error(result.error or "Registration failed")

    def _show_error(self, msg: str) -> None:
        if self._error_label:
            self._error_label.deleteLater()
        self._error_label = QLabel(f"  {msg}")
        self._error_label.setStyleSheet("""
            QLabel {
                background-color: rgba(232, 80, 64, 0.1);
                color: #e85040;
                border: 1px solid rgba(232, 80, 64, 0.2);
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 12px;
            }
        """)
        self._error_label.setFixedHeight(40)
        current_page = self._stack.currentWidget()
        current_page.layout().insertWidget(2, self._error_label)
