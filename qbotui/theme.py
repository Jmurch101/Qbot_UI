"""QBot Platform stylesheet — dark navy / cyan mock with FSU blue base."""

from __future__ import annotations

# Near-black page with navy cards and light-blue borders (mock-aligned).
BG = "#050B14"
CARD = "#0B1F38"
PANEL = "#0A2748"
BORDER = "#3A86FF"
BORDER_SOFT = "#1F6FB5"
CYAN = "#5EC8FF"
GREEN = "#3DFF8A"
GREEN_DIM = "#1B5E3A"
WHITE = "#FFFFFF"
MUTED = "#9BB0C7"
GOLD = "#F2C75C"  # retained accent for compatibility
FSU_BLUE = "#0067B1"
FSU_BLUE_DEEP = BG
FSU_BLUE_MID = "#0E3A6E"
FSU_BLUE_CARD = CARD
FSU_BLUE_PANEL = PANEL
FSU_GOLD = GOLD
FSU_GOLD_HOVER = "#FFD76A"
FSU_WHITE = WHITE
FSU_SLATE = MUTED

CONTROL_CENTER_QSS = f"""
QWidget {{
    background-color: {BG};
    color: {WHITE};
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}}

QMainWindow, QDialog {{
    background-color: {BG};
}}

QFrame#initHero {{
    background-color: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #061428, stop:0.45 #0A2A52, stop:1 #061428
    );
    border: 1px solid {BORDER_SOFT};
    border-radius: 16px;
}}

QLabel#heroTitle {{
    font-size: 36px;
    font-weight: 800;
    letter-spacing: 2px;
    color: {WHITE};
}}

QLabel#heroSubtitle {{
    font-size: 12px;
    letter-spacing: 2px;
    color: {CYAN};
}}

QLabel#initPill {{
    background-color: {GREEN_DIM};
    color: {GREEN};
    border: 1px solid {GREEN};
    border-radius: 14px;
    padding: 6px 14px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
}}

QLabel#appTitle, QLabel#platformPageTitle {{
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 1.4px;
    color: {WHITE};
}}

QLabel#appSubtitle {{
    font-size: 11px;
    color: {MUTED};
    letter-spacing: 1.5px;
}}

QLabel#sectionTitle {{
    font-size: 12px;
    font-weight: 700;
    color: {WHITE};
    letter-spacing: 1.4px;
}}

QLabel#mutedLabel {{
    color: {MUTED};
    font-size: 12px;
}}

QLabel#platformInfoLine {{
    color: {WHITE};
    font-size: 13px;
}}

QLabel#ipHostLabel, QLabel#deviceAddressLabel, QLabel#statusNote {{
    color: #D7E6F5;
}}

QLabel#checklistLabel {{
    color: {WHITE};
    font-size: 14px;
}}

QLabel#checklistMark {{
    color: {BORDER};
    font-size: 16px;
}}

QLabel#checklistMarkDone {{
    color: {CYAN};
    font-size: 16px;
}}

QLabel#liveBadge {{
    background-color: {GREEN_DIM};
    color: {GREEN};
    border: 1px solid {GREEN};
    border-radius: 8px;
    padding: 2px 8px;
    font-size: 10px;
    font-weight: 700;
}}

QLabel#sshKeyBadge, QLabel#verifiedBadge {{
    background-color: {GREEN_DIM};
    color: {GREEN};
    border: 1px solid {GREEN};
    border-radius: 10px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 700;
}}

QLabel#unverifiedBadge {{
    background-color: #2A2030;
    color: #FFB4B4;
    border: 1px solid #8B4A4A;
    border-radius: 10px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 700;
}}

QLabel#systemReadyPill {{
    background-color: {GREEN_DIM};
    color: {GREEN};
    border: 1px solid {GREEN};
    border-radius: 10px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 700;
}}

QLabel#networkStatusLabel {{
    color: {MUTED};
    font-size: 11px;
    letter-spacing: 0.8px;
}}

QLabel#metricValue, QLabel#metricValueCompact {{
    font-size: 18px;
    font-weight: 700;
    color: {WHITE};
}}

QLabel#liveDot {{
    color: {GREEN};
    font-size: 14px;
}}

QLabel#idleDot {{
    color: {MUTED};
    font-size: 14px;
}}

QLabel#liveText {{
    color: {GREEN};
    font-weight: 700;
    letter-spacing: 1px;
}}

QProgressBar#batteryBar {{
    background-color: #001F45;
    border: 1px solid {BORDER_SOFT};
    border-radius: 5px;
}}

QProgressBar#batteryBar::chunk {{
    background-color: {CYAN};
    border-radius: 4px;
}}

QFrame#card {{
    background-color: {CARD};
    border: 1px solid {BORDER};
    border-radius: 14px;
}}

QFrame#cardFlat, QFrame#consoleCardFlat {{
    background-color: transparent;
    border: none;
}}

QWidget#viewerCard {{
    background-color: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 12px;
}}

QFrame#consoleCard {{
    background-color: #06101C;
    border: 1px solid {BORDER_SOFT};
    border-radius: 12px;
}}

QComboBox, QLineEdit {{
    background-color: #06101C;
    border: 1px solid {BORDER_SOFT};
    border-radius: 8px;
    padding: 8px 10px;
    color: {WHITE};
    min-height: 20px;
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox QAbstractItemView {{
    background-color: {CARD};
    border: 1px solid {BORDER};
    selection-background-color: {FSU_BLUE};
    color: {WHITE};
}}

QPushButton {{
    background-color: {FSU_BLUE_MID};
    border: 1px solid {BORDER_SOFT};
    border-radius: 10px;
    padding: 8px 14px;
    color: {WHITE};
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: {FSU_BLUE};
}}

QPushButton:disabled {{
    color: #7A93B0;
    background-color: #163A63;
}}

QPushButton#startListenersButton, QPushButton#verifySshButton,
QPushButton#primaryButton, QPushButton#confirmAddressButton,
QPushButton#executeTaskButton, QPushButton#startQbotButton {{
    background-color: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #1A6FE0, stop:1 #3A9BFF
    );
    border: 1px solid {CYAN};
    color: {WHITE};
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 1px;
}}

QPushButton#startListenersButton:hover, QPushButton#verifySshButton:hover,
QPushButton#primaryButton:hover, QPushButton#confirmAddressButton:hover,
QPushButton#executeTaskButton:hover, QPushButton#startQbotButton:hover {{
    background-color: #4AA8FF;
}}

QPushButton#openPlatformButton, QPushButton#backInitButton,
QPushButton#windowModeButton, QPushButton#refreshAddressesButton {{
    background-color: #0A1A2E;
    border: 1px solid {BORDER_SOFT};
    color: {WHITE};
}}

QPushButton#openPlatformButton {{
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.8px;
}}

QPushButton#dangerButton, QPushButton#disconnectButton,
QPushButton#emergencyDisconnectButton {{
    background-color: #8B1E1E;
    border: 1px solid #A52A2A;
    color: {WHITE};
    font-size: 15px;
    font-weight: 700;
}}

QPushButton#dangerButton:hover, QPushButton#disconnectButton:hover,
QPushButton#emergencyDisconnectButton:hover {{
    background-color: #A52A2A;
}}

QPlainTextEdit#consoleOutput {{
    background-color: #040A12;
    border: 1px solid #12263F;
    border-radius: 8px;
    color: {GREEN};
    font-family: "Cascadia Mono", "Consolas", "Courier New", monospace;
    font-size: 12px;
    padding: 10px;
}}

QScrollBar:vertical {{
    background: {BG};
    width: 10px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: {BORDER_SOFT};
    border-radius: 4px;
    min-height: 24px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
"""
