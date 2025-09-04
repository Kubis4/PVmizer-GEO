#!/usr/bin/env python3
"""
core/connection_helper.py - Enhanced connection helper with better plotter integration
"""
from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from PyQt5.QtWidgets import QMessageBox

class ConnectionHelper(QObject):
    """Enhanced helper class to establish and maintain connections between components"""
    
    # Signals
    connection_established = pyqtSignal(object)  # Emitted when connection is established
    connection_lost = pyqtSignal()  # Emitted when connection is lost
    plotter_connected = pyqtSignal(object)  # Emitted when plotter is connected
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        
        # Connection state
        self.connection_timer = QTimer()
        self.connection_timer.timeout.connect(self._check_connections)
        self.connection_timer.start(1500)  # Check every 1.5 seconds
        
        # State tracking
        self.last_roof = None
        self.last_plotter = None
        self.connections_established = False
        self.connection_attempts = 0
        self.max_attempts = 15
        
        # Component references
        self.modifications_tab = None
        self.current_roof = None
        self.current_plotter = None
    
    def _check_connections(self):
        """Enhanced connection checking with better error handling"""
        try:
            # Find current components
            current_roof = self._find_current_roof()
            current_plotter = self._find_plotter()
            modifications_tab = self._find_modifications_tab()
            
            # Track changes
            roof_changed = current_roof != self.last_roof
            plotter_changed = current_plotter != self.last_plotter
            
            # Handle roof changes
            if roof_changed:
                if current_roof:
                    self.current_roof = current_roof
                    self.last_roof = current_roof
                    self._establish_roof_connections(current_roof, modifications_tab)
                    self.connection_established.emit(current_roof)
                else:
                    if self.last_roof:
                        self.connection_lost.emit()
                    self.current_roof = None
                    self.last_roof = None
                    self.connections_established = False
            
            # Handle plotter changes
            if plotter_changed:
                if current_plotter:
                    self.current_plotter = current_plotter
                    self.last_plotter = current_plotter
                    self._ensure_plotter_roof_connection(current_roof, current_plotter)
                    self.plotter_connected.emit(current_plotter)
                else:
                    self.current_plotter = None
                    self.last_plotter = None
            
            # Update modifications tab reference
            if modifications_tab != self.modifications_tab:
                self.modifications_tab = modifications_tab
            
            # Reset connection attempts on success
            if current_roof and modifications_tab:
                self.connection_attempts = 0
            else:
                self.connection_attempts += 1
        
        except Exception as e:
            self.connection_attempts += 1
    
    def _find_current_roof(self):
        """Enhanced roof finding with multiple fallback methods"""
        try:
            # Method 1: Through roof generation manager
            if hasattr(self.main_window, 'roof_generation_manager'):
                manager = self.main_window.roof_generation_manager
                if hasattr(manager, 'current_roof') and manager.current_roof:
                    return manager.current_roof
            
            # Method 2: Through model tab
            model_tab = self._find_model_tab()
            if model_tab:
                if hasattr(model_tab, 'current_roof') and model_tab.current_roof:
                    return model_tab.current_roof
                
                # Check for roof in various attributes
                for attr_name in ['roof', 'active_roof', 'building_roof']:
                    if hasattr(model_tab, attr_name):
                        roof = getattr(model_tab, attr_name)
                        if roof and hasattr(roof, 'plotter'):
                            return roof
            
            # Method 3: Through content tabs
            if hasattr(self.main_window, 'content_tabs'):
                for i in range(self.main_window.content_tabs.count()):
                    tab = self.main_window.content_tabs.widget(i)
                    if hasattr(tab, 'current_roof') and tab.current_roof:
                        return tab.current_roof
            
            # Method 4: Search through main window attributes
            for attr_name in dir(self.main_window):
                if 'roof' in attr_name.lower():
                    attr = getattr(self.main_window, attr_name)
                    if attr and hasattr(attr, '__class__') and 'roof' in attr.__class__.__name__.lower():
                        return attr
            
            return None
            
        except Exception as e:
            return None
    
    def _find_plotter(self):
        """Enhanced plotter finding with comprehensive search"""
        try:
            # Method 1: Through model tab
            model_tab = self._find_model_tab()
            if model_tab:
                plotter_attrs = ['plotter', 'pv_widget', 'vtk_widget', 'pyvista_widget', 'render_widget']
                for attr in plotter_attrs:
                    if hasattr(model_tab, attr):
                        plotter = getattr(model_tab, attr)
                        if plotter and self._validate_plotter(plotter):
                            return plotter
            
            # Method 2: Through PyVista integration
            if hasattr(self.main_window, 'pyvista_integration'):
                integration = self.main_window.pyvista_integration
                if hasattr(integration, 'plotter') and integration.plotter:
                    if self._validate_plotter(integration.plotter):
                        return integration.plotter
            
            # Method 3: Through content tabs
            if hasattr(self.main_window, 'content_tabs'):
                for i in range(self.main_window.content_tabs.count()):
                    tab = self.main_window.content_tabs.widget(i)
                    plotter_attrs = ['plotter', 'pv_widget', 'vtk_widget', 'pyvista_widget']
                    for attr in plotter_attrs:
                        if hasattr(tab, attr):
                            plotter = getattr(tab, attr)
                            if plotter and self._validate_plotter(plotter):
                                return plotter
            
            # Method 4: Search through main window
            for attr_name in dir(self.main_window):
                if 'plotter' in attr_name.lower() or 'pyvista' in attr_name.lower():
                    attr = getattr(self.main_window, attr_name)
                    if attr and self._validate_plotter(attr):
                        return attr
            
            return None
            
        except Exception as e:
            return None
    
    def _validate_plotter(self, plotter):
        """Validate that the plotter is a valid PyVista plotter"""
        try:
            return (plotter and 
                   hasattr(plotter, 'add_mesh') and 
                   hasattr(plotter, 'render') and
                   hasattr(plotter, 'clear'))
        except:
            return False
    
    def _find_model_tab(self):
        """Find the 3D model tab"""
        try:
            if hasattr(self.main_window, 'content_tabs'):
                tab_count = self.main_window.content_tabs.count()
                for i in range(tab_count):
                    tab_text = self.main_window.content_tabs.tabText(i).lower()
                    if any(keyword in tab_text for keyword in ['model', '3d', 'roof', 'building']):
                        return self.main_window.content_tabs.widget(i)
            return None
        except Exception as e:
            return None
    
    def _find_modifications_tab(self):
        """Enhanced modifications tab finding"""
        try:
            # Method 1: Direct reference if stored
            if self.modifications_tab and hasattr(self.modifications_tab, 'solar_panel_config_changed'):
                return self.modifications_tab
            
            # Method 2: Through left panel
            if hasattr(self.main_window, 'left_panel'):
                left_panel = self.main_window.left_panel
                
                # Direct access
                if hasattr(left_panel, 'modifications_tab'):
                    tab = left_panel.modifications_tab
                    if hasattr(tab, 'solar_panel_config_changed'):
                        return tab
                
                # Through tabs widget
                if hasattr(left_panel, 'tabs'):
                    for i in range(left_panel.tabs.count()):
                        tab = left_panel.tabs.widget(i)
                        if hasattr(tab, 'solar_panel_config_changed'):
                            return tab
                
                # Search through attributes
                for attr_name in dir(left_panel):
                    if 'modification' in attr_name.lower():
                        attr = getattr(left_panel, attr_name)
                        if hasattr(attr, 'solar_panel_config_changed'):
                            return attr
            
            # Method 3: Search through main window
            for attr_name in dir(self.main_window):
                attr = getattr(self.main_window, attr_name)
                if (hasattr(attr, 'solar_panel_config_changed') and 
                    hasattr(attr, 'obstacle_placement_requested')):
                    return attr
            
            return None
            
        except Exception as e:
            return None
    
    def _establish_roof_connections(self, roof, modifications_tab):
        """Establish all connections for the roof"""
        try:
            if not roof or not modifications_tab:
                return False
            
            # Ensure plotter connection
            plotter = self._find_plotter()
            if plotter:
                self._ensure_plotter_roof_connection(roof, plotter)
            
            # Connect solar panel signals
            self._connect_solar_panel_signals(modifications_tab, roof)
            
            # Connect obstacle signals
            self._connect_obstacle_signals(modifications_tab, roof)
            
            # Connect environment signals
            self._connect_environment_signals(modifications_tab, roof)
            
            self.connections_established = True
            return True
            
        except Exception as e:
            return False
    
    def _ensure_plotter_roof_connection(self, roof, plotter):
        """Ensure roof has plotter connection"""
        try:
            if not roof or not plotter:
                return False
            
            if not hasattr(roof, 'plotter') or roof.plotter != plotter:
                roof.plotter = plotter
            
            # Additional plotter setup if needed
            if hasattr(roof, 'setup_plotter'):
                roof.setup_plotter(plotter)
                
            return True
            
        except Exception as e:
            return False
    
    def _connect_solar_panel_signals(self, modifications_tab, roof):
        """Connect solar panel signals with enhanced error handling"""
        try:
            if not hasattr(modifications_tab, 'solar_panel_config_changed'):
                return False
            
            # Disconnect existing connections
            try:
                modifications_tab.solar_panel_config_changed.disconnect()
            except:
                pass
            
            # Create enhanced handler
            def handle_solar_config(config):
                try:
                    return self._handle_solar_panel_config(config, roof)
                except Exception as e:
                    return False
            
            # Connect signal
            modifications_tab.solar_panel_config_changed.connect(handle_solar_config)
            return True
            
        except Exception as e:
            return False
    
    def _connect_obstacle_signals(self, modifications_tab, roof):
        """Connect obstacle signals with enhanced error handling"""
        try:
            if not hasattr(modifications_tab, 'obstacle_placement_requested'):
                return False
            
            # Disconnect existing connections
            try:
                modifications_tab.obstacle_placement_requested.disconnect()
            except:
                pass
            
            # Create enhanced handler
            def handle_obstacle_placement(obstacle_type, dimensions):
                try:
                    return self._handle_obstacle_placement(obstacle_type, dimensions, roof)
                except Exception as e:
                    return False
            
            # Connect signal
            modifications_tab.obstacle_placement_requested.connect(handle_obstacle_placement)
            return True
            
        except Exception as e:
            return False
    
    def _connect_environment_signals(self, modifications_tab, roof):
        """Connect environment signals with enhanced error handling"""
        try:
            if not hasattr(modifications_tab, 'environment_action_requested'):
                return False
            
            # Disconnect existing connections
            try:
                modifications_tab.environment_action_requested.disconnect()
            except:
                pass
            
            # Create enhanced handler
            def handle_environment_action(action_type, parameters):
                try:
                    return self._handle_environment_action(action_type, parameters, roof)
                except Exception as e:
                    return False
            
            # Connect signal
            modifications_tab.environment_action_requested.connect(handle_environment_action)
            return True
            
        except Exception as e:
            return False
    
    # ==================== ENHANCED SIGNAL HANDLERS ====================
    
    def _handle_solar_panel_config(self, config, roof):
        """Enhanced solar panel configuration handler"""
        try:
            # Method 1: Solar panel handler
            if hasattr(roof, 'solar_panel_handler') and roof.solar_panel_handler:
                handler = roof.solar_panel_handler
                
                # Update handler properties
                for key, value in config.items():
                    if hasattr(handler, key):
                        setattr(handler, key, value)
                
                # Update config method
                if hasattr(handler, 'update_config'):
                    handler.update_config(config)
                
                # Generate panels
                if hasattr(handler, 'generate_panels'):
                    result = handler.generate_panels()
                
                # Trigger render
                self._trigger_render(roof)
                
                return True
            
            # Method 2: Direct roof methods
            elif hasattr(roof, 'add_solar_panels'):
                result = roof.add_solar_panels(config)
                self._trigger_render(roof)
                return result
            
            elif hasattr(roof, 'update_panel_config'):
                result = roof.update_panel_config(config)
                self._trigger_render(roof)
                return result
            
            # Method 3: Set properties directly
            else:
                for key, value in config.items():
                    if hasattr(roof, key):
                        setattr(roof, key, value)
                
                self._trigger_render(roof)
                return True
                
        except Exception as e:
            return False
    
    def _handle_obstacle_placement(self, obstacle_type, dimensions, roof):
        """Enhanced obstacle placement handler"""
        try:
            # Method 1: Direct add_obstacle
            if hasattr(roof, 'add_obstacle'):
                result = roof.add_obstacle(obstacle_type, dimensions)
                if result:
                    self._trigger_render(roof)
                    return True
            
            # Method 2: Set properties for placement mode
            placed = False
            if hasattr(roof, 'selected_obstacle_type'):
                roof.selected_obstacle_type = obstacle_type
                placed = True
            
            if hasattr(roof, 'obstacle_dimensions'):
                roof.obstacle_dimensions = dimensions
                placed = True
            
            # Method 3: Activate placement mode
            if hasattr(roof, 'add_attachment_points'):
                roof.add_attachment_points()
                placed = True
            
            if hasattr(roof, 'enable_obstacle_placement'):
                roof.enable_obstacle_placement(obstacle_type, dimensions)
                placed = True
            
            if placed:
                self._trigger_render(roof)
                return True
            else:
                return False
            
        except Exception as e:
            return False
    
    def _handle_environment_action(self, action_type, parameters, roof):
        """Enhanced environment action handler"""
        try:
            # Method 1: Direct environment handler
            if hasattr(roof, 'handle_environment_action'):
                result = roof.handle_environment_action(action_type, parameters)
                if result:
                    self._trigger_render(roof)
                    return result
            
            # Method 2: Specific action handlers
            result = False
            
            if action_type == 'add_tree':
                result = self._handle_add_tree(roof, parameters)
            elif action_type == 'add_multiple_trees':
                result = self._handle_add_multiple_trees(roof, parameters)
            elif action_type == 'add_pole':
                result = self._handle_add_pole(roof, parameters)
            elif action_type == 'clear_all_environment':
                result = self._handle_clear_environment(roof)
            elif action_type == 'auto_populate_scene':
                result = self._handle_auto_populate(roof, parameters)
            elif action_type == 'toggle_attachment_points':
                result = self._handle_toggle_attachment_points(roof)
            else:
                return False
            
            if result:
                self._trigger_render(roof)
            
            return result
                
        except Exception as e:
            return False
    
    def _handle_add_tree(self, roof, parameters):
        """Handle add tree action"""
        try:
            tree_type = parameters.get('tree_type', 'deciduous')
            
            # Set tree type if available
            if hasattr(roof, 'tree_type_index'):
                if tree_type == 'pine':
                    roof.tree_type_index = 1
                elif tree_type == 'oak':
                    roof.tree_type_index = 2
                else:
                    roof.tree_type_index = 0
            
            # Add tree
            if hasattr(roof, 'add_environment_obstacle_at_point'):
                result = roof.add_environment_obstacle_at_point('tree')
                return result
            
            return False
            
        except Exception as e:
            return False
    
    def _handle_add_multiple_trees(self, roof, parameters):
        """Handle add multiple trees action"""
        try:
            count = parameters.get('count', 5)
            tree_types = ['deciduous', 'pine', 'oak']
            success_count = 0
            
            for i in range(count):
                # Cycle through tree types
                tree_type_index = i % len(tree_types)
                if hasattr(roof, 'tree_type_index'):
                    roof.tree_type_index = tree_type_index
                
                if hasattr(roof, 'add_environment_obstacle_at_point'):
                    if roof.add_environment_obstacle_at_point('tree'):
                        success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            return False
    
    def _handle_add_pole(self, roof, parameters):
        """Handle add pole action"""
        try:
            if hasattr(roof, 'add_environment_obstacle_at_point'):
                result = roof.add_environment_obstacle_at_point('pole')
                return result
            return False
            
        except Exception as e:
            return False
    
    def _handle_clear_environment(self, roof):
        """Handle clear environment action"""
        try:
            if hasattr(roof, 'clear_environment_obstacles'):
                roof.clear_environment_obstacles()
                return True
            return False
            
        except Exception as e:
            return False
    
    def _handle_auto_populate(self, roof, parameters):
        """Handle auto populate scene action"""
        try:
            success_count = 0
            
            # Add deciduous trees
            if hasattr(roof, 'tree_type_index'):
                roof.tree_type_index = 0
            for _ in range(3):
                if hasattr(roof, 'add_environment_obstacle_at_point'):
                    if roof.add_environment_obstacle_at_point('tree'):
                        success_count += 1
            
            # Add pine trees
            if hasattr(roof, 'tree_type_index'):
                roof.tree_type_index = 1
            for _ in range(2):
                if hasattr(roof, 'add_environment_obstacle_at_point'):
                    if roof.add_environment_obstacle_at_point('tree'):
                        success_count += 1
            
            # Add oak tree
            if hasattr(roof, 'tree_type_index'):
                roof.tree_type_index = 2
            if hasattr(roof, 'add_environment_obstacle_at_point'):
                if roof.add_environment_obstacle_at_point('tree'):
                    success_count += 1
            
            # Add poles
            for _ in range(2):
                if hasattr(roof, 'add_environment_obstacle_at_point'):
                    roof.add_environment_obstacle_at_point('pole')
            
            return True
            
        except Exception as e:
            return False
    
    def _handle_toggle_attachment_points(self, roof):
        """Handle toggle attachment points action"""
        try:
            if hasattr(roof, 'hide_environment_attachment_points'):
                try:
                    roof.hide_environment_attachment_points()
                    return True
                except:
                    if hasattr(roof, 'show_environment_attachment_points'):
                        roof.show_environment_attachment_points()
                        return True
            return False
            
        except Exception as e:
            return False
    
    def _trigger_render(self, roof):
        """Enhanced render triggering"""
        try:
            # Method 1: Through roof's plotter
            if hasattr(roof, 'plotter') and roof.plotter:
                plotter = roof.plotter
                if hasattr(plotter, 'render'):
                    QTimer.singleShot(50, plotter.render)
                    return True
            
            # Method 2: Through current plotter
            if self.current_plotter and hasattr(self.current_plotter, 'render'):
                QTimer.singleShot(50, self.current_plotter.render)
                return True
            
            # Method 3: Force render through roof
            if hasattr(roof, 'render'):
                QTimer.singleShot(50, roof.render)
                return True
            
            return False
            
        except Exception as e:
            return False
    
    # ==================== PUBLIC METHODS ====================
    
    def force_reconnect(self):
        """Force reconnection of all components"""
        try:
            # Reset state
            self.connection_attempts = 0
            self.connections_established = False
            self.last_roof = None
            self.last_plotter = None
            
            # Clear references
            self.current_roof = None
            self.current_plotter = None
            self.modifications_tab = None
            
            # Trigger immediate connection check
            self._check_connections()
            
            return True
            
        except Exception as e:
            return False
    
    def test_all_connections(self):
        """Test all connections and return detailed status"""
        try:
            results = []
            
            # Test current roof
            current_roof = self._find_current_roof()
            if current_roof:
                results.append(f"✅ Current roof: {current_roof.__class__.__name__}")
                
                # Test roof capabilities
                capabilities = []
                if hasattr(current_roof, 'solar_panel_handler'):
                    capabilities.append("solar")
                if hasattr(current_roof, 'add_obstacle'):
                    capabilities.append("obstacles")
                if hasattr(current_roof, 'handle_environment_action'):
                    capabilities.append("environment")
                if hasattr(current_roof, 'plotter'):
                    capabilities.append("plotter")
                
                if capabilities:
                    results.append(f"  ✅ Capabilities: {', '.join(capabilities)}")
                else:
                    results.append("  ⚠️ No recognized capabilities")
                
            else:
                results.append("❌ Current roof: Not found")
            
            # Test plotter
            current_plotter = self._find_plotter()
            if current_plotter:
                results.append("✅ Plotter: Found and validated")
            else:
                results.append("❌ Plotter: Not found")
            
            # Test modifications tab
            modifications_tab = self._find_modifications_tab()
            if modifications_tab:
                results.append("✅ Modifications tab: Found")
                
                # Test signals
                signals = []
                if hasattr(modifications_tab, 'solar_panel_config_changed'):
                    signals.append("solar")
                if hasattr(modifications_tab, 'obstacle_placement_requested'):
                    signals.append("obstacles")
                if hasattr(modifications_tab, 'environment_action_requested'):
                    signals.append("environment")
                
                if signals:
                    results.append(f"  ✅ Signals: {', '.join(signals)}")
                else:
                    results.append("  ❌ No signals found")
            else:
                results.append("❌ Modifications tab: Not found")
            
            # Connection status
            if self.connections_established:
                results.append("✅ Connection status: Established")
            else:
                results.append("⚠️ Connection status: Not established")
            
            # Connection attempts
            results.append(f"📊 Connection attempts: {self.connection_attempts}/{self.max_attempts}")
            
            return results
            
        except Exception as e:
            return [f"❌ Error testing connections: {e}"]
    
    def show_connection_status(self):
        """Show detailed connection status in message box"""
        try:
            results = self.test_all_connections()
            
            # Count success/failure
            success_count = len([r for r in results if r.startswith("✅")])
            total_count = len([r for r in results if r.startswith(("✅", "❌"))])
            
            if total_count > 0:
                success_rate = (success_count / total_count) * 100
                if success_rate >= 80:
                    status = "EXCELLENT"
                elif success_rate >= 60:
                    status = "GOOD"
                elif success_rate >= 40:
                    status = "FAIR"
                else:
                    status = "NEEDS ATTENTION"
            else:
                status = "UNKNOWN"
            
            message = f"Connection Status: {status} ({success_count}/{total_count})\n\n" + "\n".join(results)
            
            if status in ["EXCELLENT", "GOOD"]:
                QMessageBox.information(self.main_window, "Connection Status", message)
            elif status == "FAIR":
                QMessageBox.warning(self.main_window, "Connection Status", message)
            else:
                QMessageBox.critical(self.main_window, "Connection Status", message)
            
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Error checking connection status: {e}")
    
    def get_connection_info(self):
        """Get connection information as dictionary"""
        try:
            return {
                'current_roof': self.current_roof.__class__.__name__ if self.current_roof else None,
                'current_plotter': type(self.current_plotter).__name__ if self.current_plotter else None,
                'modifications_tab': type(self.modifications_tab).__name__ if self.modifications_tab else None,
                'connections_established': self.connections_established,
                'connection_attempts': self.connection_attempts,
                'max_attempts': self.max_attempts
            }
        except Exception as e:
            return {'error': str(e)}
    
    def cleanup(self):
        """Enhanced cleanup"""
        try:
            # Stop timer
            if self.connection_timer:
                self.connection_timer.stop()
                self.connection_timer = None
            
            # Clear references
            self.last_roof = None
            self.last_plotter = None
            self.current_roof = None
            self.current_plotter = None
            self.modifications_tab = None
            self.connections_established = False
            
        except Exception as e:
            pass

# ==================== INTEGRATION FUNCTION ====================

def setup_connection_helper(main_window):
    """Set up enhanced connection helper for the main window"""
    try:
        # Create connection helper
        connection_helper = ConnectionHelper(main_window)
        
        # Store reference in main window
        main_window.connection_helper = connection_helper
        
        # Add utility methods to main window
        def test_connections():
            return connection_helper.test_all_connections()
        
        def show_connection_status():
            connection_helper.show_connection_status()
        
        def force_reconnect():
            return connection_helper.force_reconnect()
        
        def get_connection_info():
            return connection_helper.get_connection_info()
        
        # Bind methods to main window
        main_window.test_connections = test_connections
        main_window.show_connection_status = show_connection_status
        main_window.force_reconnect = force_reconnect
        main_window.get_connection_info = get_connection_info
        
        return connection_helper
        
    except Exception as e:
        return None

# ==================== USAGE EXAMPLE ====================

def example_usage(main_window):
    """Example of how to use the enhanced connection helper"""
    try:
        # Setup connection helper
        helper = setup_connection_helper(main_window)
        
        if helper:
            # Test connections
            results = main_window.test_connections()
            
            # Get connection info
            info = main_window.get_connection_info()
            
            # Show status dialog
            main_window.show_connection_status()
            
            return True
        
        return False
        
    except Exception as e:
        return False
