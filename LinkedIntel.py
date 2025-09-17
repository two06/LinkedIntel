#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LinkedIntel - LinkedIn Profile Extraction The Lazy Way
Author: @two06
Description: Automatically extracts and analyzes LinkedIn profile data from HTTP responses
"""

from burp import IBurpExtender, IHttpListener, ITab, IContextMenuFactory
from java.awt import BorderLayout, GridBagLayout, GridBagConstraints, Insets, FlowLayout
from java.awt.event import ActionListener
from javax.swing import JPanel, JScrollPane, JTextArea, JButton, JLabel, JCheckBox, JTextField
from javax.swing import JTable, JFrame, JFileChooser, JSplitPane, JTabbedPane, JMenuItem
from javax.swing.table import DefaultTableModel
from java.io import File
import json
import re
import csv
import os
from datetime import datetime

class BurpExtender(IBurpExtender, IHttpListener, ITab, IContextMenuFactory):
    
    def __init__(self):
        self.profiles = []
        self.auto_extract = True
        self.save_to_file = False
        self.output_directory = ""
        self.debug_enabled = False
        
    def registerExtenderCallbacks(self, callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        
        # Set extension name
        callbacks.setExtensionName("LinkedIntel")
        
        # Register HTTP listener
        callbacks.registerHttpListener(self)
        
        # Register context menu factory
        callbacks.registerContextMenuFactory(self)
        
        # Create the GUI
        self._create_gui()
        
        # Add the custom tab to Burp's UI
        callbacks.addSuiteTab(self)
        
        # Print banner
        self._print_banner()
        
        print("[LinkedIntel] Extension loaded successfully!")
        
    def _print_banner(self):
        banner = """
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                      ║
║    ██▓     ██▓ ███▄    █  ██ ▄█▀▓█████ ▓█████▄  ██▓ ███▄    █ ▄▄▄█████▓▓█████  ██▓   ║    
║   ▓██▒    ▓██▒ ██ ▀█   █  ██▄█▒ ▓█   ▀ ▒██▀ ██▌▓██▒ ██ ▀█   █ ▓  ██▒ ▓▒▓█   ▀ ▓██▒   ║    
║   ▒██▒    ▒██▒▓██  ▀█ ██▒▓███▄░ ▒███   ░██   █▌▒██▒▓██  ▀█ ██▒▒ ▓██░ ▒░▒███   ▒██▒   ║    
║   ░██░    ░██░▓██▒  ▐▌██▒▓██ █▄ ▒▓█  ▄ ░▓█▄   ▌░██░▓██▒  ▐▌██▒░ ▓██▓ ░ ▒▓█  ▄ ░██░   ║    
║   ░██░    ░██░▒██░   ▓██░▒██▒ █▄░▒████▒░▒████▓ ░██░▒██░   ▓██░  ▒██▒ ░ ░▒████▒░██░   ║    
║   ░▓      ░▓  ░ ▒░   ▒ ▒ ▒ ▒▒ ▓▒░░ ▒░ ░ ▒▒▓  ▒ ░▓  ░ ▒░   ▒ ▒   ▒ ░░   ░░ ▒░ ░░▓     ║    
║    ▒ ░     ▒ ░░ ░░   ░ ▒░░ ░▒ ▒░ ░ ░  ░ ░ ▒  ▒  ▒ ░░ ░░   ░ ▒░    ░     ░ ░  ░ ▒ ░   ║    
║    ▒ ░     ▒ ░   ░   ░ ░ ░ ░░ ░    ░    ░ ░  ░  ▒ ░   ░   ░ ░   ░         ░    ▒ ░   ║    
║    ░       ░           ░ ░  ░      ░  ░   ░     ░           ░               ░  ░ ░   ║      
║                                         ░                                            ║
║                                                                                      ║
║            ⚡⚡⚡ LinkedIn Profile Extraction The Lazy Way ⚡⚡⚡                 ║
║                                   by @two06                                          ║
║                                                                                      ║
║                                                                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        
    def _create_gui(self):
        # Main panel
        self._main_panel = JPanel(BorderLayout())
        
        # Create tabbed pane
        self._tabbed_pane = JTabbedPane()
        
        # Profiles tab
        self._profiles_tab = self._create_profiles_tab()
        self._tabbed_pane.addTab("Extracted Profiles", self._profiles_tab)
        
        # Settings tab
        self._settings_tab = self._create_settings_tab()
        self._tabbed_pane.addTab("Settings", self._settings_tab)
        
        # About tab
        self._about_tab = self._create_about_tab()
        self._tabbed_pane.addTab("About", self._about_tab)
        
        self._main_panel.add(self._tabbed_pane, BorderLayout.CENTER)
        
    def _create_profiles_tab(self):
        panel = JPanel(BorderLayout())
        
        # Control panel
        control_panel = JPanel(FlowLayout(FlowLayout.LEFT))
        
        # Clear button
        clear_button = JButton("Clear All", actionPerformed=self._clear_profiles)
        control_panel.add(clear_button)
        
        # Export button
        export_button = JButton("Export to CSV", actionPerformed=self._export_profiles)
        control_panel.add(export_button)
        
        # Stats label
        self._stats_label = JLabel("Profiles extracted: 0")
        control_panel.add(self._stats_label)
        
        panel.add(control_panel, BorderLayout.NORTH)
        
        # Create table for profiles
        self._table_model = DefaultTableModel()
        self._table_model.setColumnIdentifiers(["Name", "Position", "Location", "Profile URL", "Badge", "Timestamp"])
        
        self._profiles_table = JTable(self._table_model)
        self._profiles_table.setAutoResizeMode(JTable.AUTO_RESIZE_ALL_COLUMNS)
        
        # Add table to scroll pane
        scroll_pane = JScrollPane(self._profiles_table)
        panel.add(scroll_pane, BorderLayout.CENTER)
        
        return panel
        
    def _create_settings_tab(self):
        panel = JPanel(GridBagLayout())
        gbc = GridBagConstraints()
        gbc.insets = Insets(5, 5, 5, 5)
        gbc.anchor = GridBagConstraints.WEST
        
        # Auto-extract checkbox
        gbc.gridx = 0
        gbc.gridy = 0
        panel.add(JLabel("Auto-extract profiles:"), gbc)
        
        gbc.gridx = 1
        self._auto_extract_checkbox = JCheckBox("", self.auto_extract)
        panel.add(self._auto_extract_checkbox, gbc)
        
        # Auto-save checkbox
        gbc.gridx = 0
        gbc.gridy = 1
        panel.add(JLabel("Auto-save to file:"), gbc)
        
        gbc.gridx = 1
        self._auto_save_checkbox = JCheckBox("", self.save_to_file)
        panel.add(self._auto_save_checkbox, gbc)
        
        # Debug checkbox
        gbc.gridx = 0
        gbc.gridy = 3
        panel.add(JLabel("Enable debug logging:"), gbc)
        
        gbc.gridx = 1
        gbc.fill = GridBagConstraints.NONE
        self._debug_checkbox = JCheckBox("", self.debug_enabled)
        panel.add(self._debug_checkbox, gbc)
        
        # Output directory
        gbc.gridx = 0
        gbc.gridy = 4
        panel.add(JLabel("Output directory:"), gbc)
        
        gbc.gridx = 1
        gbc.fill = GridBagConstraints.HORIZONTAL
        self._output_dir_field = JTextField(20)
        panel.add(self._output_dir_field, gbc)
        
        gbc.gridx = 2
        gbc.fill = GridBagConstraints.NONE
        browse_button = JButton("Browse", actionPerformed=self._browse_directory)
        panel.add(browse_button, gbc)
        
        return panel
        
    def _create_about_tab(self):
        panel = JPanel(BorderLayout())
        
        about_text = """
LinkedIntel - LinkedIn Profile Extractor

A Burp Suite extension for red team operators and security researchers to automatically 
extract and analyze LinkedIn profile data from HTTP responses during reconnaissance activities.

Features:
• Automatic profile extraction from LinkedIn API responses
• Real-time monitoring of LinkedIn traffic
• CSV export functionality  
• Configurable auto-save options
• Clean, organized profile data presentation

Usage:
1. Enable the extension in Burp Suite
2. Configure settings in the Settings tab
3. Browse LinkedIn or use other tools to generate traffic
4. View extracted profiles in the Profiles tab
5. Export data as needed for further analysis

Author: @two06
        """
        
        text_area = JTextArea(about_text)
        text_area.setEditable(False)
        text_area.setLineWrap(True)
        text_area.setWrapStyleWord(True)
        
        scroll_pane = JScrollPane(text_area)
        panel.add(scroll_pane, BorderLayout.CENTER)
        
        return panel
        
    def _debug_log(self, message):
        """Log debug messages only if debug is enabled"""
        if self._debug_checkbox.isSelected():
            print(message)
            
    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
        # Only process responses
        if messageIsRequest:
            return
            
        # Check if auto-extract is enabled
        if not self._auto_extract_checkbox.isSelected():
            return
            
        # Get the response
        response = messageInfo.getResponse()
        if not response:
            return
            
        # Get the request URL for debugging
        request = messageInfo.getRequest()
        request_str = self._helpers.bytesToString(request)
        
        # Convert response to string
        response_str = self._helpers.bytesToString(response)
        
        # Debug: Check for LinkedIn URLs
        if "linkedin.com" in request_str.lower():
            self._debug_log("[LinkedIntel] DEBUG: LinkedIn request detected")
            self._debug_log("[LinkedIntel] DEBUG: Request URL contains: " + request_str.split('\n')[0])
            
        # Check for various LinkedIn API patterns
        is_linkedin_api = False
        if "/voyager/api/graphql" in request_str:
            self._debug_log("[LinkedIntel] DEBUG: GraphQL API detected")
            is_linkedin_api = True
        elif "/voyager/api/search" in request_str:
            self._debug_log("[LinkedIntel] DEBUG: Search API detected")
            is_linkedin_api = True
        elif "linkedin.com" in request_str and "api" in request_str:
            self._debug_log("[LinkedIntel] DEBUG: General LinkedIn API detected")
            is_linkedin_api = True
            
        if not is_linkedin_api:
            return
            
        # Debug: Check response content
        if "included" in response_str:
            self._debug_log("[LinkedIntel] DEBUG: Response contains 'included' array")
        if "EntityResultViewModel" in response_str:
            self._debug_log("[LinkedIntel] DEBUG: Response contains EntityResultViewModel")
            
        # Extract profiles from the response
        profiles = self._extract_profiles_from_response(response_str)
        
        if profiles:
            print("[LinkedIntel] SUCCESS: Found {} profiles".format(len(profiles)))
            # Add to our collection
            for profile in profiles:
                profile['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.profiles.append(profile)
                
                # Add to table
                self._table_model.addRow([
                    profile.get('name', 'N/A'),
                    profile.get('position', 'N/A'),
                    profile.get('location', 'N/A'),
                    profile.get('profile_url', 'N/A'),
                    profile.get('badge', 'N/A'),
                    profile.get('timestamp', 'N/A')
                ])
            
            # Update stats
            self._stats_label.setText("Profiles extracted: " + str(len(self.profiles)))
            
            # Auto-save if enabled
            if self._auto_save_checkbox.isSelected():
                self._auto_save_profiles()
                
            print("[LinkedIntel] Extracted {} new profiles".format(len(profiles)))
        else:
            self._debug_log("[LinkedIntel] DEBUG: No profiles found in response")
            
    def _extract_profiles_from_response(self, response_text):
        """Extract profile information from LinkedIn response"""
        profiles = []
        
        # Find JSON start
        json_start = response_text.find('{')
        if json_start == -1:
            self._debug_log("[LinkedIntel] DEBUG: No JSON found in response")
            return profiles
            
        try:
            # Parse JSON
            json_data = json.loads(response_text[json_start:])
            self._debug_log("[LinkedIntel] DEBUG: JSON parsed successfully")
            
            # Check for different possible structures
            included_items = json_data.get('included', [])
            if not included_items:
                # Try alternative structures
                data_items = json_data.get('data', {})
                if isinstance(data_items, dict):
                    # Look for searchDashClustersByAll or similar
                    search_results = data_items.get('searchDashClustersByAll', {})
                    if search_results:
                        elements = search_results.get('elements', [])
                        for element in elements:
                            items = element.get('items', [])
                            included_items.extend(items)
                            
                # Try looking for elements directly
                if not included_items:
                    elements = json_data.get('elements', [])
                    included_items.extend(elements)
                    
            self._debug_log("[LinkedIntel] DEBUG: Found {} items to process".format(len(included_items)))
            
            # Extract profiles from included array
            for item in included_items:
                if not isinstance(item, dict):
                    continue
                    
                # Look for different profile indicators
                item_type = item.get('$type', '')
                if any(indicator in item_type for indicator in ['EntityResultViewModel', 'ProfileViewModel', 'Person', 'SearchHit']):
                    self._debug_log("[LinkedIntel] DEBUG: Found potential profile item: " + item_type)
                    profile_data = self._extract_profile_data(item)
                    if profile_data and profile_data.get('name'):
                        profiles.append(profile_data)
                        self._debug_log("[LinkedIntel] DEBUG: Extracted profile: " + profile_data.get('name', 'Unknown'))
                        
        except Exception as e:
            print("[LinkedIntel] ERROR: Error parsing JSON: " + str(e))
            # Try to save problematic response for debugging
            try:
                with open('/tmp/linkedintel_debug.json', 'w') as f:
                    f.write(response_text[json_start:json_start+1000])  # First 1000 chars
            except:
                pass
                
        return profiles
        
    def _extract_profile_data(self, item):
        """Extract profile data from a single item"""
        profile_data = {}
        
        # Extract name - try multiple possible fields
        name = None
        if 'title' in item and isinstance(item['title'], dict) and 'text' in item['title']:
            name = item['title']['text']
        elif 'headline' in item and isinstance(item['headline'], dict):
            name = item['headline'].get('text', '')
        elif 'name' in item:
            if isinstance(item['name'], dict):
                name = item['name'].get('text', item['name'].get('value', ''))
            else:
                name = str(item['name'])
        elif 'fullName' in item:
            name = item['fullName']
            
        if name and name != "LinkedIn Member" and len(name.strip()) > 0:
            profile_data['name'] = name.strip()
        else:
            return None  # Skip if no valid name
        
        # Extract position - try multiple fields
        if 'primarySubtitle' in item and isinstance(item['primarySubtitle'], dict) and 'text' in item['primarySubtitle']:
            profile_data['position'] = item['primarySubtitle']['text']
        elif 'headline' in item and isinstance(item['headline'], dict) and 'text' in item['headline']:
            profile_data['position'] = item['headline']['text']
        elif 'occupation' in item:
            profile_data['position'] = item['occupation']
            
        # Extract location
        if 'secondarySubtitle' in item and isinstance(item['secondarySubtitle'], dict) and 'text' in item['secondarySubtitle']:
            profile_data['location'] = item['secondarySubtitle']['text']
        elif 'location' in item:
            if isinstance(item['location'], dict):
                profile_data['location'] = item['location'].get('name', item['location'].get('text', ''))
            else:
                profile_data['location'] = str(item['location'])
        
        # Extract profile URL
        if 'navigationUrl' in item:
            profile_data['profile_url'] = item['navigationUrl']
        elif 'url' in item:
            profile_data['profile_url'] = item['url']
        elif 'publicIdentifier' in item:
            profile_data['profile_url'] = "https://linkedin.com/in/" + item['publicIdentifier']
            
        # Extract badge info
        if 'badgeIcon' in item and item['badgeIcon'] and 'accessibilityText' in item['badgeIcon']:
            profile_data['badge'] = item['badgeIcon']['accessibilityText']
        elif 'premium' in item and item['premium']:
            profile_data['badge'] = 'Premium'
            
        # Extract summary
        if 'summary' in item and item['summary'] and 'text' in item['summary']:
            profile_data['summary'] = item['summary']['text']
        elif 'snippet' in item:
            profile_data['summary'] = item['snippet']
            
        # Extract tracking ID
        if 'trackingId' in item:
            profile_data['tracking_id'] = item['trackingId']
        elif 'id' in item:
            profile_data['tracking_id'] = item['id']
            
        return profile_data
        
    def _clear_profiles(self, event):
        """Clear all extracted profiles"""
        self.profiles = []
        self._table_model.setRowCount(0)
        self._stats_label.setText("Profiles extracted: 0")
        print("[LinkedIntel] Cleared all profiles")
        
    def _export_profiles(self, event):
        """Export profiles to CSV"""
        if not self.profiles:
            print("[LinkedIntel] No profiles to export")
            return
            
        # File chooser
        file_chooser = JFileChooser()
        file_chooser.setSelectedFile(File("linkedin_profiles_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv"))
        
        if file_chooser.showSaveDialog(None) == JFileChooser.APPROVE_OPTION:
            file_path = file_chooser.getSelectedFile().getAbsolutePath()
            self._save_profiles_to_file(file_path)
            
    def _save_profiles_to_file(self, file_path):
        """Save profiles to CSV file - Jython compatible"""
        try:
            # Open file for writing
            with open(file_path, 'wb') as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                writer.writerow(["Name", "Position", "Location", "Profile URL", "Badge", "Summary", "Timestamp"])

                # Write each profile
                for profile in self.profiles:
                    row = [
                        profile.get('name', ''),
                        profile.get('position', ''),
                        profile.get('location', ''),
                        profile.get('profile_url', ''),
                        profile.get('badge', ''),
                        profile.get('summary', ''),
                        profile.get('timestamp', '')
                    ]
                    writer.writerow([s.encode('utf-8') for s in row])
                    
            print("[LinkedIntel] Exported {} profiles to {}".format(len(self.profiles), file_path))
            
        except Exception as e:
            print("[LinkedIntel] Error saving file: " + str(e))
            
    def _auto_save_profiles(self):
        """Auto-save profiles if directory is set"""
        output_dir = self._output_dir_field.getText()
        if output_dir:
            file_path = os.path.join(output_dir, "linkedin_profiles_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv")
            self._save_profiles_to_file(file_path)
            
    def _browse_directory(self, event):
        """Browse for output directory"""
        file_chooser = JFileChooser()
        file_chooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY)
        
        if file_chooser.showOpenDialog(None) == JFileChooser.APPROVE_OPTION:
            self._output_dir_field.setText(file_chooser.getSelectedFile().getAbsolutePath())
            
    def getTabCaption(self):
        return "LinkedIntel"
        
    def getUiComponent(self):
        return self._main_panel
        
    def createMenuItems(self, invocation):
        """Create context menu items"""
        menu_items = []
        
        # Only show menu for responses
        if invocation.getInvocationContext() == invocation.CONTEXT_MESSAGE_VIEWER_RESPONSE:
            menu_item = JMenuItem("Extract LinkedIn Profiles", actionPerformed=lambda x: self._extract_from_context(invocation))
            menu_items.append(menu_item)
            
        return menu_items
        
    def _extract_from_context(self, invocation):
        """Extract profiles from context menu"""
        messages = invocation.getSelectedMessages()
        if not messages:
            return
            
        for message in messages:
            response = message.getResponse()
            if response:
                response_str = self._helpers.bytesToString(response)
                profiles = self._extract_profiles_from_response(response_str)
                
                if profiles:
                    for profile in profiles:
                        profile['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        self.profiles.append(profile)
                        
                        self._table_model.addRow([
                            profile.get('name', 'N/A'),
                            profile.get('position', 'N/A'),
                            profile.get('location', 'N/A'),
                            profile.get('profile_url', 'N/A'),
                            profile.get('badge', 'N/A'),
                            profile.get('timestamp', 'N/A')
                        ])
                    
                    self._stats_label.setText("Profiles extracted: " + str(len(self.profiles)))
                    print("[LinkedIntel] Manually extracted {} profiles".format(len(profiles)))
