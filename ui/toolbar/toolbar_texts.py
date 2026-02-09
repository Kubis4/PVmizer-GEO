#!/usr/bin/env python3
"""
Toolbar Text Content - All dialog text content separated for maintainability
PVmizer GEO - Enhanced Building Designer
"""

class ToolbarTexts:
    """Centralized text content for toolbar dialogs and messages"""
    
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