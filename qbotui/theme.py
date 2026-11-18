"""QBot Platform control-center stylesheet using Fayetteville State University colors.

Official FSU Blue is Pantone 293 C / #0067B1 (see uncfsu.edu brand color codes).
Background uses deepened FSU blue; accents use white and athletic gold.
"""

from __future__ import annotations

# Fayetteville State University brand-aligned palette
FSU_BLUE = "#0067B1"
FSU_BLUE_DEEP = "#002B5C"
FSU_BLUE_MID = "#003F7F"
FSU_BLUE_CARD = "#0A3A6E"
FSU_BLUE_PANEL = "#062E5A"
FSU_GOLD = "#F2C75C"
FSU_GOLD_HOVER = "#FFD76A"
FSU_WHITE = "#FFFFFF"
FSU_SLATE = "#B0B7BC"

CONTROL_CENTER_QSS = f"""
QWidget {{
    background-color: {FSU_BLUE_DEEP};
    color: {FSU_WHITE};
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}}

QMainWindow, QDialog {{
    background-color: {FSU_BLUE_DEEP};
}}

QLabel#appTitle {{
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 1px;
    color: {FSU_WHITE};
}}

QLabel#appSubtitle {{
    font-size: 11px;
    color: {FSU_SLATE};
    letter-spacing: 1.5px;
}}

QLabel#sectionTitle {{
    font-size: 11px;
    font-weight: 700;
    color: {FSU_GOLD};
    letter-spacing: 1.2px;
}}

QLabel#mutedLabel {{
    color: {FSU_SLATE};
    font-size: 12px;
}}

QLabel#ipHostLabel, QLabel#deviceAddressLabel, QLabel#statusNote {{
    color: #D7E6F5;
}}

QLabel#liveBadge {{
    background-color: #0E4A2C;
    color: #7CFFB2;
    border: 1px solid #218C53;
    border-radius: 8px;
    padding: 2px 8px;
    font-size: 10px;
    font-weight: 700;
}}

QLabel#systemReadyPill {{
    background-color: #0E4A2C;
    color: #7CFFB2;
    border: 1px solid #218C53;
    border-radius: 10px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 700;
}}

QLabel#networkStatusLabel {{
    color: {FSU_SLATE};
    font-size: 11px;
    letter-spacing: 0.8px;
}}

QFrame#card {{
    background-color: {FSU_BLUE_CARD};
    border: 1px solid #1F6FB5;
    border-radius: 14px;
}}

QFrame#viewerCard {{
    background-color: {FSU_BLUE_PANEL};
    border: 1px solid #1F6FB5;
    border-radius: 12px;
}}

QFrame#consoleCard {{
    background-color: #001F45;
    border: 1px solid #1F6FB5;
    border-radius: 12px;
}}

QComboBox, QLineEdit {{
    background-color: #001F45;
    border: 1px solid #2E7CC4;
    border-radius: 8px;
    padding: 8px 10px;
    color: {FSU_WHITE};
    min-height: 20px;
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox QAbstractItemView {{
    background-color: {FSU_BLUE_CARD};
    border: 1px solid #2E7CC4;
    selection-background-color: {FSU_BLUE};
    color: {FSU_WHITE};
}}

QPushButton {{
    background-color: {FSU_BLUE_MID};
    border: 1px solid #2E7CC4;
    border-radius: 8px;
    padding: 8px 14px;
    color: {FSU_WHITE};
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: {FSU_BLUE};
}}

QPushButton:disabled {{
    color: #7A93B0;
    background-color: #163A63;
}}

QPushButton#primaryButton, QPushButton#startListenersButton, QPushButton#confirmAddressButton,
QPushButton#executeTaskButton, QPushButton#startQbotButton {{
    background-color: {FSU_GOLD};
    border: 1px solid {FSU_GOLD_HOVER};
    color: {FSU_BLUE_DEEP};
}}

QPushButton#primaryButton:hover, QPushButton#startListenersButton:hover,
QPushButton#confirmAddressButton:hover, QPushButton#executeTaskButton:hover,
QPushButton#startQbotButton:hover {{
    background-color: {FSU_GOLD_HOVER};
}}

QPushButton#dangerButton, QPushButton#disconnectButton, QPushButton#emergencyDisconnectButton {{
    background-color: #8B1E1E;
    border: 1px solid #A52A2A;
    color: {FSU_WHITE};
}}

QPushButton#dangerButton:hover, QPushButton#disconnectButton:hover,
QPushButton#emergencyDisconnectButton:hover {{
    background-color: #A52A2A;
}}

QPlainTextEdit#consoleOutput {{
    background-color: #001633;
    border: none;
    color: {FSU_GOLD};
    font-family: "Cascadia Mono", "Consolas", "Courier New", monospace;
    font-size: 12px;
    padding: 8px;
}}

QScrollBar:vertical {{
    background: {FSU_BLUE_DEEP};
    width: 10px;
    margin: 0;
}}

QScrollBar::handle:vertical {{
    background: #2E7CC4;
    border-radius: 4px;
    min-height: 24px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
"""
