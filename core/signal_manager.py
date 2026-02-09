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
            
            # Content Tabs Signals
            connected_count += self._connect_content_tabs_signals()
            
            # Left Panel Signals
            connected_count += self._connect_left_panel_signals()
            
            # Roof Button Signals
            connected_count += self._connect_roof_button_signals()
            
            print(f"✅ Connected {connected_count} signals total")
            
        except Exception as e:
            print(f"❌ Signal connection failed: {e}")
    
    def _connect_content_tabs_signals(self):
        """Connect content tabs signals"""
        connected_count = 0
        
        if not self.main_window.content_tabs:
            return connected_count
        
        # Only building_generated signal is needed
        content_signals = [
            ('building_generated', self.main_window._on_building_generated),
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
    
    def _connect_left_panel_signals(self):
        """Connect left panel signals (solar and animation only)"""
        connected_count = 0
        
        if not self.main_window.left_panel:
            return connected_count
        
        # Only solar and animation signals are needed
        signal_mappings = [
            ('solar_parameter_changed', self.main_window._handle_solar_parameter_changed),
            ('animation_toggled', self.main_window._handle_animation_toggled),
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
        
        return connected_count
    
    def _connect_roof_button_signals(self):
        """Connect roof button signals from MapsTabPanel"""
        connected_count = 0
        
        # Find MapsTabPanel
        maps_tab = self._find_maps_tab_panel()
        if not maps_tab:
            print("⚠️ MapsTabPanel not found for roof button connections")
            return connected_count
        
        # Check if MapsTabPanel has roof_buttons dictionary
        if hasattr(maps_tab, 'roof_buttons'):
            roof_handlers = {
                'Gable': self.main_window.handle_gable_roof_button,
                'Hip': self.main_window.handle_hip_roof_button,
                'Flat': self.main_window.handle_flat_roof_button,
                'Pyramid': self.main_window.handle_pyramid_roof_button,
            }
            
            for roof_type, handler in roof_handlers.items():
                if roof_type in maps_tab.roof_buttons:
                    try:
                        button = maps_tab.roof_buttons[roof_type]
                        # Disconnect any existing connections
                        try:
                            button.clicked.disconnect()
                        except:
                            pass
                        
                        button.clicked.connect(handler)
                        connected_count += 1
                        self.connected_signals.append(f"MapsTabPanel.{roof_type}Button")
                        print(f"✅ Connected {roof_type} roof button")
                    except Exception as e:
                        print(f"❌ Failed to connect {roof_type} roof button: {e}")
        else:
            print("⚠️ MapsTabPanel.roof_buttons not found")
        
        return connected_count
    
    def _find_maps_tab_panel(self):
        """Find the MapsTabPanel widget in the UI hierarchy"""
        try:
            # Check in left panel first (since MapsTabPanel is now in left panel)
            if self.main_window.left_panel:
                if hasattr(self.main_window.left_panel, 'maps_tab_widget'):
                    return self.main_window.left_panel.maps_tab_widget
                
                if hasattr(self.main_window.left_panel, 'maps_tab'):
                    return self.main_window.left_panel.maps_tab
            
            # Fallback: Search in content tabs
            if self.main_window.content_tabs:
                for i in range(self.main_window.content_tabs.count()):
                    tab_widget = self.main_window.content_tabs.widget(i)
                    if tab_widget and tab_widget.__class__.__name__ == 'MapsTabPanel':
                        return tab_widget
            
            # Last resort: Search all children
            from PyQt5.QtWidgets import QWidget
            for child in self.main_window.findChildren(QWidget):
                if child.__class__.__name__ == 'MapsTabPanel':
                    return child
            
            return None
        except Exception as e:
            print(f"❌ Error finding MapsTabPanel: {e}")
            return None
    
    def disconnect_all_signals(self):
        """Disconnect all connected signals"""
        for signal_name in self.connected_signals:
            try:
                print(f"🔧 Disconnecting {signal_name}")
            except Exception as e:
                print(f"❌ Failed to disconnect {signal_name}: {e}")
        
        self.connected_signals.clear()
