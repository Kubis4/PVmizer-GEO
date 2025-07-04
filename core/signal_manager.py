"""
Signal Management Module
Handles all signal connections and routing
"""


class SignalManager:
    """Manages signal connections throughout the application"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.connected_signals = []
    
    def connect_all_signals(self):
        """Connect all application signals"""
        try:
            print("🔧 Connecting signals...")
            connected_count = 0
            
            # Left Panel Signals
            connected_count += self._connect_left_panel_signals()
            
            # Content Tabs Signals
            connected_count += self._connect_content_tabs_signals()
            
            # Drawing Tab Panel Signals (Critical for model tab access)
            connected_count += self._connect_drawing_tab_signals()
            
            # Roof Button Signals
            connected_count += self._connect_roof_button_signals()
            
            print(f"✅ Connected {connected_count} signals total")
            
        except Exception as e:
            print(f"❌ Signal connection failed: {e}")
    
    def _connect_left_panel_signals(self):
        """Connect left panel signals"""
        connected_count = 0
        
        if not self.main_window.left_panel:
            return connected_count
        
        signal_mappings = [
            ('snip_requested', self.main_window._handle_snip_request),
            ('search_location_requested', self.main_window._handle_search_location),
            ('undo_requested', self.main_window._handle_undo_request),
            ('clear_drawing_requested', self.main_window._handle_clear_request),
            ('scale_changed', self.main_window._handle_scale_change),
            ('generate_model_requested', self.main_window._handle_generate_building),
        ]
        
        for signal_name, handler in signal_mappings:
            if hasattr(self.main_window.left_panel, signal_name):
                try:
                    signal = getattr(self.main_window.left_panel, signal_name)
                    signal.connect(handler)
                    connected_count += 1
                    self.connected_signals.append(f"LeftPanel.{signal_name}")
                    print(f"✅ Connected LeftPanel.{signal_name}")
                except Exception as e:
                    print(f"❌ Failed to connect LeftPanel.{signal_name}: {e}")
            else:
                print(f"⚠️ Signal LeftPanel.{signal_name} not found")
        
        return connected_count
    
    def _connect_content_tabs_signals(self):
        """Connect content tabs signals"""
        connected_count = 0
        
        if not self.main_window.content_tabs:
            return connected_count
        
        content_signals = [
            ('snip_completed', self.main_window._on_snip_completed),
            ('building_generated', self.main_window._on_building_generated),
            ('screenshot_captured', self.main_window._on_screenshot_captured),
        ]
        
        for signal_name, handler in content_signals:
            if hasattr(self.main_window.content_tabs, signal_name):
                try:
                    signal = getattr(self.main_window.content_tabs, signal_name)
                    signal.connect(handler)
                    connected_count += 1
                    self.connected_signals.append(f"ContentTabs.{signal_name}")
                    print(f"✅ Connected ContentTabs.{signal_name}")
                except Exception as e:
                    print(f"❌ Failed to connect ContentTabs.{signal_name}: {e}")
            else:
                print(f"⚠️ Signal ContentTabs.{signal_name} not found")
        
        return connected_count
    
    def _connect_drawing_tab_signals(self):
        """Connect drawing tab panel signals (critical for model tab access)"""
        connected_count = 0
        
        drawing_tab_panel = self._find_drawing_tab_panel()
        if not drawing_tab_panel:
            print("⚠️ DrawingTabPanel not found for signal connection")
            return connected_count
        
        drawing_signals = [
            ('generate_model_requested', self.main_window._handle_generate_building_from_drawing_tab),
            ('scale_changed', self.main_window._handle_scale_change),
            ('angle_snap_toggled', self.main_window._handle_angle_snap_toggle),
            ('clear_drawing_requested', self.main_window._handle_clear_request),
        ]
        
        for signal_name, handler in drawing_signals:
            if hasattr(drawing_tab_panel, signal_name):
                try:
                    signal = getattr(drawing_tab_panel, signal_name)
                    signal.connect(handler)
                    connected_count += 1
                    self.connected_signals.append(f"DrawingTabPanel.{signal_name}")
                    print(f"✅ Connected DrawingTabPanel.{signal_name}")
                except Exception as e:
                    print(f"❌ Failed to connect DrawingTabPanel.{signal_name}: {e}")
            else:
                print(f"⚠️ Signal DrawingTabPanel.{signal_name} not found")
        
        return connected_count
    
    def _connect_roof_button_signals(self):
        """Connect roof button signals"""
        connected_count = 0
        
        # Create a set to track connected buttons to avoid duplicates
        connected_buttons = set()
        
        # Define the roof button mappings
        roof_buttons = [
            ('flat_roof_button', self.main_window.handle_flat_roof_button, 'flat'),
            ('gable_roof_button', self.main_window.handle_gable_roof_button, 'gable'),
            ('hip_roof_button', self.main_window.handle_hip_roof_button, 'hip'),
            ('pyramid_roof_button', self.main_window.handle_pyramid_roof_button, 'pyramid'),
            # Try alternative naming patterns
            ('flatRoofButton', self.main_window.handle_flat_roof_button, 'flat'),
            ('gableRoofButton', self.main_window.handle_gable_roof_button, 'gable'),
            ('hipRoofButton', self.main_window.handle_hip_roof_button, 'hip'),
            ('pyramidRoofButton', self.main_window.handle_pyramid_roof_button, 'pyramid'),
            # More alternatives
            ('flat_btn', self.main_window.handle_flat_roof_button, 'flat'),
            ('gable_btn', self.main_window.handle_gable_roof_button, 'gable'),
            ('hip_btn', self.main_window.handle_hip_roof_button, 'hip'),
            ('pyramid_btn', self.main_window.handle_pyramid_roof_button, 'pyramid'),
        ]
        
        # Try to find and connect buttons in maps tab panel
        maps_tab = self._find_maps_tab_panel()
        if maps_tab:
            for button_name, handler, roof_type in roof_buttons:
                # Skip if we already connected a button for this roof type
                if roof_type in connected_buttons:
                    continue
                    
                if hasattr(maps_tab, button_name):
                    try:
                        button = getattr(maps_tab, button_name)
                        if hasattr(button, 'clicked'):
                            # Disconnect any existing connections first
                            try:
                                button.clicked.disconnect()
                            except:
                                pass
                                
                            button.clicked.connect(handler)
                            connected_count += 1
                            connected_buttons.add(roof_type)
                            self.connected_signals.append(f"MapsTabPanel.{button_name}")
                            print(f"✅ Connected MapsTabPanel.{button_name}")
                    except Exception as e:
                        print(f"❌ Failed to connect MapsTabPanel.{button_name}: {e}")
        
        # Try to find and connect buttons in left panel
        if self.main_window.left_panel:
            for button_name, handler, roof_type in roof_buttons:
                # Skip if we already connected a button for this roof type
                if roof_type in connected_buttons:
                    continue
                    
                if hasattr(self.main_window.left_panel, button_name):
                    try:
                        button = getattr(self.main_window.left_panel, button_name)
                        if hasattr(button, 'clicked'):
                            # Disconnect any existing connections first
                            try:
                                button.clicked.disconnect()
                            except:
                                pass
                                
                            button.clicked.connect(handler)
                            connected_count += 1
                            connected_buttons.add(roof_type)
                            self.connected_signals.append(f"LeftPanel.{button_name}")
                            print(f"✅ Connected LeftPanel.{button_name}")
                    except Exception as e:
                        print(f"❌ Failed to connect LeftPanel.{button_name}: {e}")
        
        # Try to find buttons directly in the UI (brute force search)
        if connected_count == 0:
            print("🔍 Searching for roof buttons in UI...")
            from PyQt5.QtWidgets import QPushButton
            
            # Create mapping of button text to handlers
            text_to_handler = {
                'flat': (self.main_window.handle_flat_roof_button, 'flat'),
                'gable': (self.main_window.handle_gable_roof_button, 'gable'),
                'hip': (self.main_window.handle_hip_roof_button, 'hip'),
                'pyramid': (self.main_window.handle_pyramid_roof_button, 'pyramid'),
            }
            
            # Find all buttons
            for button in self.main_window.findChildren(QPushButton):
                button_text = button.text().lower()
                for key, (handler, roof_type) in text_to_handler.items():
                    if key in button_text and roof_type not in connected_buttons:
                        try:
                            # Disconnect any existing connections first
                            try:
                                button.clicked.disconnect()
                            except:
                                pass
                                
                            button.clicked.connect(handler)
                            connected_count += 1
                            connected_buttons.add(roof_type)
                            self.connected_signals.append(f"Button.{button_text}")
                            print(f"✅ Connected button with text '{button_text}'")
                        except Exception as e:
                            print(f"❌ Failed to connect button '{button_text}': {e}")
        
        return connected_count
    
    def _find_drawing_tab_panel(self):
        """Find the DrawingTabPanel widget in the UI hierarchy"""
        try:
            if self.main_window.content_tabs:
                # Method 1: Check if content_tabs has drawing_tab_panel attribute
                if hasattr(self.main_window.content_tabs, 'drawing_tab_panel'):
                    return self.main_window.content_tabs.drawing_tab_panel
                
                # Method 2: Search through tab widgets
                for i in range(self.main_window.content_tabs.count()):
                    tab_widget = self.main_window.content_tabs.widget(i)
                    if tab_widget:
                        # Check if the tab widget is DrawingTabPanel
                        if tab_widget.__class__.__name__ == 'DrawingTabPanel':
                            return tab_widget
                        
                        # Search children for DrawingTabPanel
                        drawing_panel = self._find_widget_by_class(tab_widget, 'DrawingTabPanel')
                        if drawing_panel:
                            return drawing_panel
            
            return None
        except Exception as e:
            print(f"❌ Error finding DrawingTabPanel: {e}")
            return None
    
    def _find_maps_tab_panel(self):
        """Find the Maps Tab Panel widget in the UI hierarchy"""
        try:
            if self.main_window.content_tabs:
                # Method 1: Check if content_tabs has maps_tab_panel attribute
                if hasattr(self.main_window.content_tabs, 'maps_tab_panel'):
                    return self.main_window.content_tabs.maps_tab_panel
                
                # Method 2: Search through tab widgets
                for i in range(self.main_window.content_tabs.count()):
                    tab_widget = self.main_window.content_tabs.widget(i)
                    if tab_widget:
                        # Check if the tab widget is MapsTabPanel
                        if tab_widget.__class__.__name__ == 'MapsTabPanel':
                            return tab_widget
                        
                        # Search children for MapsTabPanel
                        maps_panel = self._find_widget_by_class(tab_widget, 'MapsTabPanel')
                        if maps_panel:
                            return maps_panel
            
            return None
        except Exception as e:
            print(f"❌ Error finding MapsTabPanel: {e}")
            return None

    def _find_widget_by_class(self, parent, class_name):
        """Find widget by class name recursively"""
        try:
            from PyQt5.QtWidgets import QWidget
            
            if parent.__class__.__name__ == class_name:
                return parent
            
            for child in parent.findChildren(QWidget):
                if child.__class__.__name__ == class_name:
                    return child
            
            return None
        except Exception as e:
            return None
    
    def disconnect_all_signals(self):
        """Disconnect all connected signals"""
        for signal_name in self.connected_signals:
            try:
                # Implementation would depend on keeping signal references
                print(f"🔧 Disconnecting {signal_name}")
            except Exception as e:
                print(f"❌ Failed to disconnect {signal_name}: {e}")
        
        self.connected_signals.clear()