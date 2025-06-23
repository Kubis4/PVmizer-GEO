#!/usr/bin/env python3
"""
Toolbar Text Content - All dialog text content separated for maintainability
PVmizer GEO - Enhanced Building Designer
"""

class ToolbarTexts:
    """Centralized text content for toolbar dialogs and messages"""
    
    @staticmethod
    def get_help_text():
        """Comprehensive help dialog text"""
        return """<h3>🌍 PVmizer GEO - Comprehensive Help</h3>

<p><b>🚀 Getting Started Guide:</b></p>
<ol>
<li><b>📁 Create Project:</b> Use 'Project → New Project' to set up comprehensive energy data</li>
<li><b>🗺️ Navigate:</b> Use Google Maps to find your building location</li>
<li><b>📸 Capture:</b> Take high-quality screenshot of the building</li>
<li><b>✏️ Draw:</b> Click points to draw the building boundary</li>
<li><b>🏗️ Generate:</b> Create detailed 3D model and review results</li>
<li><b>💾 Save & Export:</b> Save your project and export in multiple formats</li>
</ol>

<p><b>📁 Project Management:</b></p>
<ul>
<li><b>New Project (Ctrl+N):</b> Create project with energy and financial data</li>
<li><b>Load Project (Ctrl+O):</b> Open existing .pvgeo project files</li>
<li><b>Save Project (Ctrl+S):</b> Save to current location</li>
<li><b>Save As (Ctrl+Shift+S):</b> Save with new name</li>
<li><b>Edit Project:</b> Modify project information</li>
<li><b>Project Info:</b> View detailed project summary</li>
</ul>

<p><b>🖱️ Drawing Controls:</b></p>
<ul>
<li><b>Left-click:</b> Place points to draw outline</li>
<li><b>Middle-click + drag:</b> Pan around the image</li>
<li><b>Right-click:</b> Finish current drawing</li>
<li><b>ESC:</b> Cancel current operation</li>
<li><b>Scroll wheel:</b> Zoom in/out</li>
</ul>

<p><b>⚙️ Settings & Features:</b></p>
<ul>
<li><b>🌓 Theme Toggle:</b> Switch between light and dark themes</li>
<li><b>📏 Scale Setting:</b> Set real-world measurements</li>
<li><b>📐 Snap Modes:</b> Align to angles and grids</li>
<li><b>🏠 Roof Types:</b> Flat, Gable, Hip, Pyramid options</li>
</ul>

<p><b>⌨️ Keyboard Shortcuts:</b></p>
<ul>
<li><b>Ctrl+N:</b> New Project</li>
<li><b>Ctrl+O:</b> Load Project</li>
<li><b>Ctrl+S:</b> Save Project</li>
<li><b>Ctrl+Q:</b> Exit Application</li>
<li><b>F1:</b> Show Help</li>
<li><b>ESC:</b> Cancel Operation</li>
</ul>"""
    
    @staticmethod
    def get_about_text(theme, enhanced_mode, project_active):
        """About dialog text with dynamic content"""
        return f"""<h3>🌍 PVmizer GEO</h3>
<p><b>Version:</b> 2.0.0 Enhanced</p>
<p><b>Theme:</b> {theme}</p>
<p><b>Mode:</b> {'Enhanced' if enhanced_mode else 'Standard'}</p>
<p><b>Project Active:</b> {'Yes' if project_active else 'No'}</p>

<p><b>🌟 Professional Geospatial Design Tool</b></p>
<p>Advanced software for designing solar installations from satellite imagery with comprehensive project management.</p>

<p><b>🎯 Key Features:</b></p>
<ul>
<li>🗺️ Google Maps satellite integration</li>
<li>📁 Complete project management system</li>
<li>✏️ Interactive drawing tools</li>
<li>🏗️ Real-time 3D model generation</li>
<li>📏 Accurate scale measurements</li>
<li>🎨 Multiple roof types</li>
<li>💾 Export capabilities</li>
<li>🌓 Theme support</li>
<li>📊 Energy analysis</li>
<li>💰 Financial calculations</li>
</ul>

<p><b>🚀 Workflow:</b></p>
<ol>
<li>📁 Create comprehensive project</li>
<li>🗺️ Navigate to building location</li>
<li>📸 Capture building screenshot</li>
<li>✏️ Draw precise outline</li>
<li>🏗️ Generate 3D model</li>
<li>📊 Review analysis</li>
<li>💾 Export results</li>
</ol>

<p><i>Professional solar panel design and energy analysis tool.</i></p>"""
    
    @staticmethod
    def get_preferences_text(projects_dir):
        """Preferences dialog text"""
        return f"""<h3>⚙️ PVmizer GEO Preferences</h3>

<p><b>🎨 Available Settings:</b></p>
<ul>
<li><b>🌓 Theme Toggle:</b> Switch between light and dark themes</li>
<li><b>⚡ Enhanced Mode:</b> Enable advanced features</li>
<li><b>🎨 Canvas Type:</b> Choose rendering implementation</li>
<li><b>📁 Project Management:</b> Comprehensive workflows</li>
<li><b>🔧 Auto-save:</b> Automatic project backup</li>
</ul>

<p><b>🚀 Performance Options:</b></p>
<ul>
<li><b>VTK Rendering:</b> Hardware-accelerated graphics</li>
<li><b>High DPI Support:</b> Optimal display scaling</li>
<li><b>Memory Management:</b> Optimized for large projects</li>
</ul>

<p><b>💾 File Management:</b></p>
<ul>
<li><b>Project Directory:</b> {projects_dir}</li>
<li><b>Auto-save:</b> On project creation/update</li>
<li><b>Export Formats:</b> Multiple output options</li>
</ul>

<p><i>Detailed preferences dialog will be implemented in a future update.</i></p>"""
    
    @staticmethod
    def get_export_info_text(export_type):
        """Export information texts"""
        texts = {
            "data": """Project data export feature will be implemented.

This will include:
• Energy calculations
• Financial projections
• Technical specifications
• Performance metrics""",
            
            "model": """3D model export feature will be implemented.

Supported formats:
• OBJ
• STL
• PLY
• VTK""",
            
            "report": """Project report export feature will be implemented.

Report will include:
• Executive summary
• Technical analysis
• Financial projections
• Visual renderings
• Performance predictions"""
        }
        return texts.get(export_type, "Export feature not implemented yet.")
    
    @staticmethod
    def get_feature_unavailable_text(feature):
        """Feature unavailable texts"""
        texts = {
            "canvas": """Canvas type switching is not yet implemented.

Available options:
• Standard Canvas
• Enhanced Canvas
• WebGL Canvas""",
            
            "enhanced_mode": """Enhanced mode toggle is not yet implemented.

Enhanced mode features:
• Advanced calculations
• Extended export options
• Professional tools""",
            
            "wizard": """Project wizard is not available. Please check that ui/project_wizard.py is properly installed.

Project management features are disabled until this is resolved."""
        }
        return texts.get(feature, "Feature is not available.")
    
    @staticmethod
    def format_project_info(project_data):
        """Format project data into HTML for display"""
        if not project_data:
            return "<p>No project data available.</p>"
        
        # Extract project info sections
        basic = project_data.get('basic_info', {})
        location = project_data.get('location_info', {})
        energy = project_data.get('energy_info', {})
        technical = project_data.get('technical_info', {})
        
        # Calculate energy metrics
        annual_cost = energy.get('annual_consumption_kwh', 0) * energy.get('electricity_rate_per_kwh', 0)
        monthly_cost = annual_cost / 12
        
        # Format project info with icons and energy data
        html = f"""
        <div style="padding: 10px; line-height: 1.5;">
            <h3 style="margin-bottom: 15px;">{basic.get('project_name', 'Untitled Project')}</h3>
            
            <h4 style="color: #2ecc71;">📝 Description</h4>
            <p>{basic.get('description', 'No description provided.')}</p>
            
            <h4 style="color: #3498db;">📋 Project Details</h4>
            <ul>
                <li><b>Client:</b> {basic.get('client_name', 'N/A')}</li>
                <li><b>Type:</b> {basic.get('project_type', 'N/A')}</li>
                <li><b>Location:</b> {location.get('address', 'N/A')}</li>
                <li><b>City:</b> {location.get('city', 'N/A')} {location.get('zip_code', '')}</li>
            </ul>
            
            <h4 style="color: #e74c3c;">⚡ Energy Profile</h4>
            <ul>
                <li><b>Annual Consumption:</b> {energy.get('annual_consumption_kwh', 0):,.0f} kWh/year</li>
                <li><b>Monthly Average:</b> {energy.get('monthly_consumption_kwh', 0):,.0f} kWh/month</li>
                <li><b>Electricity Rate:</b> {energy.get('electricity_rate_per_kwh', 0):.4f} €/kWh</li>
                <li><b>Current Annual Cost:</b> {annual_cost:,.2f} €</li>
                <li><b>Current Monthly Cost:</b> {monthly_cost:,.2f} €</li>
            </ul>
            
            <h4 style="color: #9b59b6;">🔧 Technical Details</h4>
            <ul>
                <li><b>Roof Material:</b> {technical.get('roof_material', 'N/A')}</li>
                <li><b>Roof Age:</b> {technical.get('roof_age_years', 0)} years</li>
                <li><b>Roof Condition:</b> {technical.get('roof_condition', 'N/A')}</li>
                <li><b>Shading Issues:</b> {'Yes' if technical.get('has_shading', False) else 'No'}</li>
                <li><b>Grid Connected:</b> {'Yes' if technical.get('grid_connected', True) else 'No'}</li>
            </ul>
        </div>
        """
        
        return html