from __future__ import annotations

import logging

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QStackedWidget, QWidget, QFrame,
    QScrollArea,
)
from PyQt6.QtCore import Qt, pyqtSignal

from src.auth.service import AuthService
from src.models.database import get_db_session
from src.utils.captcha import MathCaptcha

logger = logging.getLogger(__name__)


class LoginDialog(QDialog):
    login_successful = pyqtSignal(dict)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("SanGlow")
        self.setFixedSize(480, 720)
        self._error_label = None
        self._captcha = MathCaptcha()
        self._pending_user = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        hero = QFrame()
        hero.setFixedHeight(180)
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
        content_layout.setContentsMargins(48, 20, 48, 20)
        content_layout.setSpacing(10)

        self._stack = QStackedWidget()
        self._stack.addWidget(self._create_login_page())
        self._stack.addWidget(self._create_register_page())
        self._stack.addWidget(self._create_verify_page())
        content_layout.addWidget(self._stack)
        content_layout.addStretch()

        layout.addWidget(content, stretch=1)

    def _create_login_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)

        title = QLabel("Welcome back")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        subtitle = QLabel("Sign in to continue listening")
        subtitle.setObjectName("subtitleLabel")
        layout.addWidget(subtitle)
        layout.addSpacing(4)

        self._login_username = QLineEdit()
        self._login_username.setPlaceholderText("Username or email")
        self._login_username.setFixedHeight(44)
        layout.addWidget(self._login_username)

        self._login_password = QLineEdit()
        self._login_password.setPlaceholderText("Password")
        self._login_password.setEchoMode(QLineEdit.EchoMode.Password)
        self._login_password.setFixedHeight(44)
        self._login_password.returnPressed.connect(self._handle_login)
        layout.addWidget(self._login_password)

        layout.addSpacing(4)

        login_btn = QPushButton("Sign In")
        login_btn.setObjectName("primaryButton")
        login_btn.setFixedHeight(44)
        login_btn.clicked.connect(self._handle_login)
        layout.addWidget(login_btn)

        layout.addSpacing(12)

        register_link = QPushButton("Create an account")
        register_link.setObjectName("ghostButton")
        register_link.setFixedHeight(40)
        register_link.clicked.connect(lambda: self._stack.setCurrentIndex(1))
        layout.addWidget(register_link)

        return page

    def _create_register_page(self) -> QWidget:
        page = QWidget()
        outer_layout = QVBoxLayout(page)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setSpacing(8)

        title = QLabel("Create account")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        subtitle = QLabel("Start your music journey")
        subtitle.setObjectName("subtitleLabel")
        layout.addWidget(subtitle)
        layout.addSpacing(2)

        self._reg_username = QLineEdit()
        self._reg_username.setPlaceholderText("Username")
        self._reg_username.setFixedHeight(40)
        layout.addWidget(self._reg_username)

        self._reg_email = QLineEdit()
        self._reg_email.setPlaceholderText("Email")
        self._reg_email.setFixedHeight(40)
        layout.addWidget(self._reg_email)

        self._reg_display = QLineEdit()
        self._reg_display.setPlaceholderText("Display name (optional)")
        self._reg_display.setFixedHeight(40)
        layout.addWidget(self._reg_display)

        self._reg_password = QLineEdit()
        self._reg_password.setPlaceholderText("Password")
        self._reg_password.setEchoMode(QLineEdit.EchoMode.Password)
        self._reg_password.setFixedHeight(40)
        layout.addWidget(self._reg_password)

        self._reg_confirm = QLineEdit()
        self._reg_confirm.setPlaceholderText("Confirm password")
        self._reg_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self._reg_confirm.setFixedHeight(40)
        layout.addWidget(self._reg_confirm)

        captcha_frame = QFrame()
        captcha_frame.setStyleSheet("QFrame { background: #252525; border-radius: 8px; padding: 8px; }")
        captcha_layout = QVBoxLayout(captcha_frame)
        captcha_layout.setContentsMargins(12, 8, 12, 8)
        captcha_layout.setSpacing(6)

        self._captcha_label = QLabel(self._captcha.question)
        self._captcha_label.setStyleSheet("color: #e0d6cc; font-size: 14px; font-weight: 600; background: transparent;")
        captcha_layout.addWidget(self._captcha_label)

        self._captcha_input = QLineEdit()
        self._captcha_input.setPlaceholderText("Your answer")
        self._captcha_input.setFixedHeight(36)
        captcha_layout.addWidget(self._captcha_input)
        layout.addWidget(captcha_frame)

        layout.addSpacing(2)

        register_btn = QPushButton("Create Account")
        register_btn.setObjectName("primaryButton")
        register_btn.setFixedHeight(44)
        register_btn.clicked.connect(self._handle_register)
        layout.addWidget(register_btn)

        layout.addSpacing(8)

        login_link = QPushButton("Already have an account? Sign in")
        login_link.setObjectName("ghostButton")
        login_link.setFixedHeight(40)
        login_link.clicked.connect(lambda: self._stack.setCurrentIndex(0))
        layout.addWidget(login_link)

        layout.addStretch()

        scroll.setWidget(inner)
        outer_layout.addWidget(scroll)

        return page

    def _create_verify_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)

        title = QLabel("Verify your email")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)

        subtitle = QLabel("We sent a 6-digit code to your email")
        subtitle.setObjectName("subtitleLabel")
        layout.addWidget(subtitle)
        layout.addSpacing(4)

        self._verify_code = QLineEdit()
        self._verify_code.setPlaceholderText("Enter verification code")
        self._verify_code.setFixedHeight(44)
        self._verify_code.setMaxLength(6)
        self._verify_code.returnPressed.connect(self._handle_verify)
        layout.addWidget(self._verify_code)

        layout.addSpacing(4)

        verify_btn = QPushButton("Verify Email")
        verify_btn.setObjectName("primaryButton")
        verify_btn.setFixedHeight(44)
        verify_btn.clicked.connect(self._handle_verify)
        layout.addWidget(verify_btn)

        layout.addSpacing(8)

        resend_link = QPushButton("Resend code")
        resend_link.setObjectName("ghostButton")
        resend_link.setFixedHeight(36)
        resend_link.clicked.connect(self._handle_resend)
        layout.addWidget(resend_link)

        back_link = QPushButton("Back to login")
        back_link.setObjectName("ghostButton")
        back_link.setFixedHeight(36)
        back_link.clicked.connect(lambda: self._stack.setCurrentIndex(0))
        layout.addWidget(back_link)

        return page

    def _handle_login(self) -> None:
        username = self._login_username.text().strip()
        password = self._login_password.text()
        if not username or not password:
            self._show_error("Please fill in all fields")
            return
        logger.info("Login attempt for: %s", username)
        with get_db_session() as db:
            result = AuthService(db).login(username, password)
            if result.success and result.user:
                logger.info("Login successful for: %s", username)
                self.login_successful.emit(result.user.to_dict())
                self.accept()
            elif result.requires_verification:
                self._pending_user = username
                self._stack.setCurrentIndex(2)
                self._show_error_on_page(2, "Please verify your email first")
            else:
                logger.warning("Login failed for: %s - %s", username, result.error)
                self._show_error(result.error or "Invalid credentials")

    def _handle_register(self) -> None:
        username = self._reg_username.text().strip()
        email = self._reg_email.text().strip()
        display_name = self._reg_display.text().strip()
        password = self._reg_password.text()
        confirm = self._reg_confirm.text()
        captcha_answer = self._captcha_input.text().strip()

        if not username or not email or not password:
            self._show_error("Please fill in all required fields")
            return
        if password != confirm:
            self._show_error("Passwords do not match")
            return
        if not self._captcha.check(captcha_answer):
            self._show_error("Incorrect captcha answer")
            self._captcha = MathCaptcha()
            self._captcha_label.setText(self._captcha.question)
            self._captcha_input.clear()
            return

        with get_db_session() as db:
            existing = AuthService(db).check_existing(username, email)
            if existing:
                logger.warning("Registration blocked: %s", existing)
                self._show_error(existing)
                self._captcha = MathCaptcha()
                self._captcha_label.setText(self._captcha.question)
                self._captcha_input.clear()
                return
            result = AuthService(db).register(username, email, password, display_name or None)
            if result.success and result.requires_verification:
                logger.info("Registration successful, verification needed for: %s", username)
                self._pending_user = username
                self._stack.setCurrentIndex(2)
                if result.verification_code:
                    self._show_error_on_page(2, f"Email not configured. Your code: {result.verification_code}")
            elif result.success and result.user:
                logger.info("Registration successful (auto-verified) for: %s", username)
                self.login_successful.emit(result.user.to_dict())
                self.accept()
            else:
                logger.warning("Registration failed for: %s - %s", username, result.error)
                self._show_error(result.error or "Registration failed")
                self._captcha = MathCaptcha()
                self._captcha_label.setText(self._captcha.question)
                self._captcha_input.clear()

    def _handle_verify(self) -> None:
        code = self._verify_code.text().strip()
        if not code or not self._pending_user:
            return
        with get_db_session() as db:
            result = AuthService(db).verify_email(self._pending_user, code)
            if result.success and result.user:
                self.login_successful.emit(result.user.to_dict())
                self.accept()
            else:
                self._show_error_on_page(2, result.error or "Verification failed")

    def _handle_resend(self) -> None:
        if not self._pending_user:
            return
        with get_db_session() as db:
            result = AuthService(db).resend_verification(self._pending_user)
        if result.success and result.access_token:
            self.login_successful.emit(result.user.to_dict())
            self.accept()
        else:
            code_msg = f" (code: {result.verification_code})" if result.verification_code else ""
            self._show_error_on_page(2, f"New code sent to your email{code_msg}")

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
        self._error_label.setWordWrap(True)
        current_page = self._stack.currentWidget()
        current_page.layout().insertWidget(2, self._error_label)

    def _show_error_on_page(self, page_index: int, msg: str) -> None:
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
        self._error_label.setWordWrap(True)
        page = self._stack.widget(page_index)
        page.layout().insertWidget(2, self._error_label)
