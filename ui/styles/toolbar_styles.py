#!/usr/bin/env python3
"""
Toolbar Styles - CSS styling for enhanced toolbar components with flat buttons
"""

class ToolbarStyles:
    """Centralized styling for toolbar components with theme support"""
    
    @staticmethod
    def get_toolbar_style(dark_theme=False):
        """Get main toolbar styling"""
        if dark_theme:
            return """
                QToolBar {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 #34495e, stop: 1 #2c3e50);
                    border: none;
                    border-bottom: 1px solid #3498db;
                    spacing: 5px;
                    padding: 2px;
                    min-height: 50px;
                }
                
                QToolBar::separator {
                    background-color: #3498db;
                    width: 1px;
                    margin: 6px 4px;
                }
                
                QToolBar::handle {
                    background-color: #3498db;
                    width: 6px;
                    margin: 4px;
                }
            """
        else:
            return """
                QToolBar {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 #ffffff, stop: 1 #f8f9fa);
                    border: none;
                    border-bottom: 1px solid #3498db;
                    spacing: 5px;
                    padding: 2px;
                    min-height: 50px;
                }
                
                QToolBar::separator {
                    background-color: #3498db;
                    width: 1px;
                    margin: 6px 4px;
                }
                
                QToolBar::handle {
                    background-color: #3498db;
                    width: 6px;
                    margin: 4px;
                }
            """
    
    @staticmethod
    def get_button_style(dark_theme=False):
        """Get standard button styling with hover effects"""
        if dark_theme:
            return """
                QToolButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px;
                    text-align: left;
                    min-width: 90px;
                    min-height: 30px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 13px;
                    font-weight: bold;
                }
                
                QToolButton:hover {
                    background-color: #2980b9;
                }
                
                QToolButton:pressed {
                    background-color: #21618c;
                }
                
                QToolButton:disabled {
                    background-color: #7f8c8d;
                    color: #bdc3c7;
                }
            """
        else:
            return """
                QToolButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px;
                    text-align: left;
                    min-width: 90px;
                    min-height: 30px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 13px;
                    font-weight: bold;
                }
                
                QToolButton:hover {
                    background-color: #2980b9;
                }
                
                QToolButton:pressed {
                    background-color: #21618c;
                }
                
                QToolButton:disabled {
                    background-color: #bdc3c7;
                    color: #7f8c8d;
                }
            """
    
    @staticmethod
    def get_dropdown_button_style(dark_theme=False):
        """Get dropdown button styling with menu indicators"""
        if dark_theme:
            return """
                QToolButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px;
                    padding-right: 20px;
                    text-align: left;
                    min-width: 90px;
                    min-height: 30px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 13px;
                    font-weight: bold;
                }
                
                QToolButton:hover {
                    background-color: #2980b9;
                }
                
                QToolButton:pressed {
                    background-color: #21618c;
                }
                
                QToolButton::menu-indicator {
                    image: none;
                    width: 0px;
                }
                
                QToolButton::menu-arrow {
                    image: none;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 5px solid white;
                    margin-right: 6px;
                    margin-top: 2px;
                }
                
                QToolButton:disabled {
                    background-color: #7f8c8d;
                    color: #bdc3c7;
                }
                
                QToolButton:disabled::menu-arrow {
                    border-top-color: #bdc3c7;
                }
            """
        else:
            return """
                QToolButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px;
                    padding-right: 20px;
                    text-align: left;
                    min-width: 90px;
                    min-height: 30px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 13px;
                    font-weight: bold;
                }
                
                QToolButton:hover {
                    background-color: #2980b9;
                }
                
                QToolButton:pressed {
                    background-color: #21618c;
                }
                
                QToolButton::menu-indicator {
                    image: none;
                    width: 0px;
                }
                
                QToolButton::menu-arrow {
                    image: none;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 5px solid white;
                    margin-right: 6px;
                    margin-top: 2px;
                }
                
                QToolButton:disabled {
                    background-color: #bdc3c7;
                    color: #7f8c8d;
                }
                
                QToolButton:disabled::menu-arrow {
                    border-top-color: #7f8c8d;
                }
            """
    
    @staticmethod
    def get_exit_button_style(dark_theme=False):
        """Get special styling for the exit button"""
        return """
            QToolButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                text-align: left;
                min-width: 90px;
                min-height: 30px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                font-weight: bold;
            }
            
            QToolButton:hover {
                background-color: #c0392b;
            }
            
            QToolButton:pressed {
                background-color: #a93226;
            }
        """
    
    @staticmethod
    def get_project_frame_style(dark_theme=False):
        """Get styling for single-container project display"""
        if dark_theme:
            return """
                QFrame {
                    background-color: #343A40;
                    color: #3498db;
                    border: 1px solid #3498db;
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-size: 13px;
                    font-weight: bold;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                
                QFrame:hover {
                    border-color: #2980b9;
                    background-color: #2B3035;
                }
                
                QFrame QLabel {
                    background-color: transparent;
                    color: #3498db;
                    border: none;
                    padding: 0;
                    margin: 0;
                }
            """
        else:
            return """
                QFrame {
                    background-color: #FFFFFF;
                    color: #3498db;
                    border: 1px solid #3498db;
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-size: 13px;
                    font-weight: bold;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                
                QFrame:hover {
                    border-color: #2980b9;
                    background-color: #F8F9FA;
                }
                
                QFrame QLabel {
                    background-color: transparent;
                    color: #3498db;
                    border: none;
                    padding: 0;
                    margin: 0;
                }
            """
    
    @staticmethod
    def get_menu_style(dark_theme=False):
        """Get styling for dropdown menus"""
        if dark_theme:
            return """
                QMenu {
                    background-color: #343A40;
                    color: #E0E0E0;
                    border: 1px solid #3498db;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 12px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                
                QMenu::item {
                    background-color: transparent;
                    padding: 8px 16px;
                    border-radius: 2px;
                    margin: 2px 0px;
                    min-width: 150px;
                }
                
                QMenu::item:selected {
                    background-color: #3498db;
                    color: white;
                }
                
                QMenu::item:pressed {
                    background-color: #2980b9;
                }
                
                QMenu::item:disabled {
                    color: #6C757D;
                    background-color: transparent;
                }
                
                QMenu::separator {
                    height: 1px;
                    background-color: #3498db;
                    margin: 5px 10px;
                }
                
                QMenu::icon {
                    padding-left: 8px;
                }
            """
        else:
            return """
                QMenu {
                    background-color: #FFFFFF;
                    color: #333333;
                    border: 1px solid #3498db;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 12px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                
                QMenu::item {
                    background-color: transparent;
                    padding: 8px 16px;
                    border-radius: 2px;
                    margin: 2px 0px;
                    min-width: 150px;
                }
                
                QMenu::item:selected {
                    background-color: #3498db;
                    color: white;
                }
                
                QMenu::item:pressed {
                    background-color: #2980b9;
                }
                
                QMenu::item:disabled {
                    color: #BDBDBD;
                    background-color: transparent;
                }
                
                QMenu::separator {
                    height: 1px;
                    background-color: #3498db;
                    margin: 5px 10px;
                }
                
                QMenu::icon {
                    padding-left: 8px;
                }
            """
    
    @staticmethod
    def get_action_style(dark_theme=False):
        """Get styling for toolbar actions (non-button items)"""
        if dark_theme:
            return """
                QAction {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    margin: 2px;
                    font-weight: bold;
                    font-size: 12px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                
                QAction:hover {
                    background-color: #2980b9;
                }
            """
        else:
            return """
                QAction {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    margin: 2px;
                    font-weight: bold;
                    font-size: 12px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                
                QAction:hover {
                    background-color: #2980b9;
                }
            """
    
    @staticmethod
    def get_message_box_style(dark_theme=False):
        """Get styling for message boxes"""
        if dark_theme:
            return """
                QMessageBox {
                    background-color: #343A40;
                    color: #E0E0E0;
                    border: 1px solid #3498db;
                    border-radius: 4px;
                }
                
                QMessageBox QLabel {
                    color: #E0E0E0;
                    font-size: 13px;
                    padding: 10px;
                }
                
                QMessageBox QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    min-width: 80px;
                    font-weight: bold;
                }
                
                QMessageBox QPushButton:hover {
                    background-color: #2980b9;
                }
                
                QMessageBox QPushButton:pressed {
                    background-color: #21618c;
                }
            """
        else:
            return """
                QMessageBox {
                    background-color: #FFFFFF;
                    color: #333333;
                    border: 1px solid #3498db;
                    border-radius: 4px;
                }
                
                QMessageBox QLabel {
                    color: #333333;
                    font-size: 13px;
                    padding: 10px;
                }
                
                QMessageBox QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    min-width: 80px;
                    font-weight: bold;
                }
                
                QMessageBox QPushButton:hover {
                    background-color: #2980b9;
                }
                
                QMessageBox QPushButton:pressed {
                    background-color: #21618c;
                }
            """
        
    @staticmethod
    def get_dialog_style(dark_theme=False):
        """Get styling for custom dialogs with consistent dark theme support"""
        # Define colors based on theme
        if dark_theme:
            bg_color = "#2c3e50"
            text_color = "#ecf0f1"
            border_color = "#34495e"
        else:
            bg_color = "#ffffff"
            text_color = "#2c3e50"
            border_color = "#bdc3c7"
        
        # Main dialog style
        dialog_style = f"""
            QDialog {{
                background-color: {bg_color}; 
                color: {text_color};
                border: 2px solid {border_color};
                border-radius: 8px;
            }}
            QLabel {{
                color: {text_color};
                background-color: transparent;
                font-size: 13px;
            }}
            QPushButton {{
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                min-width: 80px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #2980b9;
            }}
            QPushButton:pressed {{
                background-color: #21618c;
            }}
            QScrollArea {{
                border: 1px solid {border_color};
                background-color: {bg_color};
            }}
            QWidget#container {{
                background-color: {bg_color};
                color: {text_color};
            }}
        """
        
        return dialog_style, bg_color, text_color
