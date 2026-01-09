#!/usr/bin/env python3
"""
Project Presentation Generator
-------------------------------
Generates HTML slide presentations from README.md files using an upgraded
template with a 4-section theme selector (Background, Accent, Card, Font).

Usage:
    python generate_presentation.py [path/to/readme.md] [output.html] [config.json]
    
If no arguments provided, looks for README.md in current directory
and outputs to presentation.html

Author: True North Data Strategies LLC
"""

import os
import sys
import re
import json
from datetime import datetime
from pathlib import Path


def parse_readme(readme_path: str) -> dict:
    """
    Parse a README.md file and extract structured content for presentation.
    
    Returns a dictionary with:
        - title: Project name
        - tagline: Short description
        - sections: List of content sections
        - features: List of key features
        - tech_stack: Technology information
        - installation: Setup instructions
        - usage: Usage examples
        - status: Project status/badges
        - contact: Contact information
        - license: License info
    """
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    parsed = {
        'title': '',
        'tagline': '',
        'sections': [],
        'features': [],
        'tech_stack': [],
        'installation': [],
        'usage': [],
        'status': '',
        'contact': {},
        'license': '',
        'raw_sections': {}
    }
    
    # Extract title - first H1
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        parsed['title'] = title_match.group(1).strip()
    
    # Extract tagline - first paragraph after title or blockquote
    tagline_match = re.search(r'^#\s+.+\n+(?:>\s*)?(.+?)(?:\n\n|\n#)', content, re.MULTILINE)
    if tagline_match:
        tagline = tagline_match.group(1).strip()
        # Clean up blockquote markers
        tagline = re.sub(r'^>\s*', '', tagline)
        parsed['tagline'] = tagline
    
    # Split content into sections by H2 headers
    section_pattern = r'##\s+(.+?)\n([\s\S]*?)(?=\n##\s+|\Z)'
    sections = re.findall(section_pattern, content)
    
    for section_title, section_content in sections:
        section_title = section_title.strip()
        section_content = section_content.strip()
        
        # Store raw section content
        parsed['raw_sections'][section_title.lower()] = section_content
        
        # Categorize sections
        title_lower = section_title.lower()
        
        if any(word in title_lower for word in ['feature', 'capability', 'what', 'highlight']):
            parsed['features'] = extract_list_items(section_content)
            
        elif any(word in title_lower for word in ['tech', 'stack', 'built', 'tool', 'technology']):
            parsed['tech_stack'] = extract_list_items(section_content)
            
        elif any(word in title_lower for word in ['install', 'setup', 'getting started', 'quick start']):
            parsed['installation'] = extract_list_items(section_content)
            
        elif any(word in title_lower for word in ['usage', 'example', 'how to', 'demo']):
            parsed['usage'] = extract_code_blocks(section_content)
            
        elif any(word in title_lower for word in ['status', 'roadmap', 'progress']):
            parsed['status'] = section_content
            
        elif any(word in title_lower for word in ['contact', 'author', 'contributor', 'team']):
            parsed['contact'] = extract_contact_info(section_content)
            
        elif any(word in title_lower for word in ['license']):
            parsed['license'] = section_content
        
        # Add to general sections list
        parsed['sections'].append({
            'title': section_title,
            'content': section_content,
            'items': extract_list_items(section_content)
        })
    
    return parsed


def extract_list_items(content: str) -> list:
    """Extract bullet points and numbered items from markdown content."""
    items = []
    
    # Match bullet points (-, *, +) and numbered lists
    pattern = r'^[\s]*[-*+]\s+(.+)$|^[\s]*\d+\.\s+(.+)$'
    matches = re.findall(pattern, content, re.MULTILINE)
    
    for match in matches:
        item = match[0] or match[1]
        if item:
            # Clean up markdown formatting
            item = re.sub(r'\*\*(.+?)\*\*', r'\1', item)  # Bold
            item = re.sub(r'\*(.+?)\*', r'\1', item)      # Italic
            item = re.sub(r'`(.+?)`', r'\1', item)        # Code
            items.append(item.strip())
    
    return items


def extract_code_blocks(content: str) -> list:
    """Extract code blocks from markdown content."""
    blocks = []
    pattern = r'```(\w+)?\n([\s\S]*?)```'
    matches = re.findall(pattern, content)
    
    for lang, code in matches:
        blocks.append({
            'language': lang or 'text',
            'code': code.strip()
        })
    
    return blocks


def extract_contact_info(content: str) -> dict:
    """Extract contact information from content."""
    contact = {}
    
    # Email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', content)
    if email_match:
        contact['email'] = email_match.group(0)
    
    # GitHub
    github_match = re.search(r'github\.com/([\w-]+)', content, re.IGNORECASE)
    if github_match:
        contact['github'] = github_match.group(1)
    
    # Website
    website_match = re.search(r'https?://(?!github\.com)[\w\.-]+\.\w+[/\w\.-]*', content)
    if website_match:
        contact['website'] = website_match.group(0)
    
    # LinkedIn
    linkedin_match = re.search(r'linkedin\.com/in/([\w-]+)', content, re.IGNORECASE)
    if linkedin_match:
        contact['linkedin'] = linkedin_match.group(1)
    
    return contact


def generate_slides(parsed: dict, config: dict = None) -> list:
    """
    Generate slide content from parsed README data.
    
    Returns a list of slide dictionaries with:
        - type: Slide template type
        - title: Slide title
        - content: Slide-specific content
    """
    
    config = config or {}
    slides_config = config.get('slides', {})
    max_items = slides_config.get('max_items_per_slide', 6)
    max_features = slides_config.get('max_features', 9)
    
    slides = []
    
    # Slide 1: Title
    slides.append({
        'type': 'title',
        'title': parsed['title'],
        'tagline': parsed['tagline'] or 'Project Overview',
        'date': config.get('date', datetime.now().strftime('%B %Y'))
    })
    
    # Slide 2: Overview/Problem (if available)
    overview_sections = ['overview', 'about', 'introduction', 'problem', 'motivation']
    for key in overview_sections:
        if key in parsed['raw_sections']:
            content = parsed['raw_sections'][key]
            items = extract_list_items(content)
            # If no list items, split content into sentences
            if not items:
                sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', content) if s.strip()]
                items = sentences[:max_items]
            slides.append({
                'type': 'content',
                'title': key.title(),
                'items': items[:max_items]
            })
            break
    
    # Slide 3: Features
    if parsed['features']:
        slides.append({
            'type': 'features',
            'title': 'Key Features',
            'items': parsed['features'][:max_features]
        })
    
    # Slide 4: Tech Stack
    if parsed['tech_stack']:
        slides.append({
            'type': 'grid',
            'title': 'Tech Stack',
            'items': parsed['tech_stack'][:max_features]
        })
    
    # Slide 5-N: Additional sections
    skip_sections = ['feature', 'tech', 'stack', 'install', 'setup', 'license', 
                     'overview', 'about', 'introduction', 'contact', 'author',
                     'getting started', 'quick start']
    
    for section in parsed['sections']:
        title_lower = section['title'].lower()
        if not any(skip in title_lower for skip in skip_sections):
            if section['items']:
                # Check if this looks like a roadmap section
                if 'roadmap' in title_lower or 'status' in title_lower:
                    slides.append({
                        'type': 'roadmap',
                        'title': section['title'],
                        'content': section['content'],
                        'items': section['items'][:max_items]
                    })
                else:
                    slides.append({
                        'type': 'content',
                        'title': section['title'],
                        'items': section['items'][:max_items]
                    })
    
    # Installation/Setup slide
    if parsed['installation']:
        slides.append({
            'type': 'steps',
            'title': 'Getting Started',
            'items': parsed['installation'][:max_items]
        })
    
    # Closing slide
    slides.append({
        'type': 'closing',
        'title': parsed['title'],
        'tagline': parsed['tagline'] or 'Project Overview',
        'contact': parsed['contact']
    })
    
    return slides


def get_template_head(title: str, config: dict = None) -> str:
    """Generate the HTML head section with all CSS and theme selector styles."""
    
    config = config or {}
    theme = config.get('theme', {})
    
    # Default theme values
    primary_gradient = theme.get('primary_gradient', 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)')
    accent_color = theme.get('accent_color', '#ffd700')
    secondary_color = theme.get('secondary_color', '#87ceeb')
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Presentation</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        :root {{
            --primary-gradient: {primary_gradient};
            --bg-solid: #1e3c72;
            --accent-color: {accent_color};
            --accent-dim: #ccac00;
            --secondary-color: {secondary_color};
            --text-color: #ffffff;
            --text-muted: rgba(255, 255, 255, 0.7);
            --card-bg: rgba(255, 255, 255, 0.1);
            --card-border: rgba(255, 255, 255, 0.1);
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--primary-gradient);
            color: var(--text-color);
            overflow: hidden;
        }}

        /* Theme Toggle Button */
        .theme-toggle-btn {{
            position: fixed;
            top: 50%;
            right: 0;
            transform: translateY(-50%);
            z-index: 1001;
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-right: none;
            color: white;
            font-family: 'Space Mono', monospace;
            font-size: 0.65rem;
            padding: 1rem 0.4rem;
            cursor: pointer;
            writing-mode: vertical-rl;
            text-orientation: mixed;
            letter-spacing: 2px;
            text-transform: uppercase;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }}

        .theme-toggle-btn:hover {{
            background: rgba(0, 0, 0, 0.6);
            border-color: var(--accent-color);
        }}

        /* Theme Panel */
        .theme-panel {{
            position: fixed;
            top: 0;
            right: -420px;
            width: 420px;
            height: 100vh;
            background: rgba(0, 0, 0, 0.95);
            border-left: 1px solid rgba(255, 255, 255, 0.1);
            z-index: 1000;
            transition: right 0.3s ease;
            overflow-y: auto;
            padding: 1.5rem;
        }}

        .theme-panel.active {{
            right: 0;
        }}

        .theme-panel-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .theme-panel-title {{
            font-family: 'Space Mono', monospace;
            font-size: 1rem;
            letter-spacing: 2px;
            color: white;
            text-transform: uppercase;
        }}

        .theme-panel-close {{
            background: transparent;
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: rgba(255, 255, 255, 0.6);
            width: 28px;
            height: 28px;
            cursor: pointer;
            font-size: 1rem;
            transition: all 0.3s ease;
        }}

        .theme-panel-close:hover {{
            border-color: var(--accent-color);
            color: var(--accent-color);
        }}

        .theme-section {{
            margin-bottom: 1.5rem;
        }}

        .theme-section-title {{
            font-family: 'Space Mono', monospace;
            font-size: 0.65rem;
            color: rgba(255, 255, 255, 0.5);
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .theme-section-title::after {{
            content: '';
            flex: 1;
            height: 1px;
            background: rgba(255, 255, 255, 0.1);
        }}

        .theme-option {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.6rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 0.35rem;
            cursor: pointer;
            transition: all 0.3s ease;
            border-radius: 4px;
        }}

        .theme-option:hover {{
            border-color: rgba(255, 255, 255, 0.3);
            background: rgba(255, 255, 255, 0.05);
        }}

        .theme-option.active {{
            border-color: var(--accent-color);
            background: rgba(255, 255, 255, 0.08);
        }}

        .theme-swatch {{
            width: 28px;
            height: 28px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            flex-shrink: 0;
            border-radius: 4px;
        }}

        .theme-swatch.gradient {{
            background-size: cover;
        }}

        .theme-info {{
            flex: 1;
        }}

        .theme-name {{
            font-size: 0.8rem;
            font-weight: 600;
            color: white;
            margin-bottom: 0.1rem;
        }}

        .theme-desc {{
            font-family: 'Space Mono', monospace;
            font-size: 0.55rem;
            color: rgba(255, 255, 255, 0.5);
        }}

        .theme-hex {{
            font-family: 'Space Mono', monospace;
            font-size: 0.5rem;
            color: rgba(255, 255, 255, 0.4);
            padding: 0.15rem 0.35rem;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 3px;
        }}

        .current-theme-display {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 1rem;
            margin-bottom: 1.5rem;
            border-radius: 4px;
        }}

        .current-theme-label {{
            font-family: 'Space Mono', monospace;
            font-size: 0.6rem;
            color: rgba(255, 255, 255, 0.5);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 0.75rem;
        }}

        .current-theme-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 0.5rem;
        }}

        .current-theme-item {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .current-theme-item .preview-swatch {{
            width: 16px;
            height: 16px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            flex-shrink: 0;
            border-radius: 3px;
        }}

        .current-theme-item span {{
            font-size: 0.65rem;
            color: rgba(255, 255, 255, 0.7);
        }}

        .reset-btn {{
            width: 100%;
            padding: 0.75rem;
            background: transparent;
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: rgba(255, 255, 255, 0.6);
            font-family: 'Space Mono', monospace;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 1rem;
            border-radius: 4px;
        }}

        .reset-btn:hover {{
            border-color: #C41E3A;
            color: #C41E3A;
            background: rgba(196, 30, 58, 0.1);
        }}

        /* Slide Container */
        .slide-container {{
            width: 100vw;
            height: 100vh;
            position: relative;
        }}

        .slide {{
            position: absolute;
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 60px;
            opacity: 0;
            visibility: hidden;
            transition: all 0.5s ease;
            text-align: center;
        }}

        .slide.active {{
            opacity: 1;
            visibility: visible;
        }}

        .slide h1 {{
            font-size: 4rem;
            margin-bottom: 1rem;
            color: var(--text-color);
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }}

        .slide h2 {{
            font-size: 2.5rem;
            margin-bottom: 2rem;
            color: var(--accent-color);
        }}

        .slide h3 {{
            font-size: 1.8rem;
            margin-bottom: 1rem;
            color: var(--text-color);
        }}

        .slide p {{
            font-size: 1.4rem;
            line-height: 1.6;
            max-width: 800px;
            color: var(--text-color);
        }}

        .slide ul {{
            text-align: left;
            font-size: 1.3rem;
            line-height: 2;
            max-width: 800px;
            list-style-type: none;
        }}

        .slide ul li {{
            margin-bottom: 0.5rem;
            padding-left: 2rem;
            position: relative;
            color: var(--text-color);
        }}

        .slide ul li::before {{
            content: '>';
            position: absolute;
            left: 0;
            color: var(--accent-color);
            font-weight: bold;
        }}

        .slide-counter {{
            position: fixed;
            top: 30px;
            right: 30px;
            background: rgba(0, 0, 0, 0.3);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 1rem;
            backdrop-filter: blur(10px);
            font-family: 'Space Mono', monospace;
            color: var(--text-color);
        }}

        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 2rem;
            margin: 2rem 0;
            max-width: 800px;
        }}

        .stat-card {{
            background: var(--card-bg);
            padding: 2rem;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid var(--card-border);
        }}

        .stat-number {{
            font-size: 3rem;
            font-weight: bold;
            color: var(--accent-color);
            margin-bottom: 0.5rem;
        }}

        .feature-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1.5rem;
            margin: 2rem 0;
            max-width: 1000px;
        }}

        .feature-card {{
            background: var(--card-bg);
            padding: 1.5rem;
            border-radius: 10px;
            backdrop-filter: blur(10px);
            border: 1px solid var(--card-border);
            transition: all 0.3s ease;
        }}

        .feature-card:hover {{
            border-color: var(--accent-color);
            transform: translateY(-2px);
        }}

        .feature-card h4 {{
            color: var(--accent-color);
            margin-bottom: 0.5rem;
        }}

        .feature-card p {{
            color: var(--text-muted);
            font-size: 1rem;
        }}

        .steps-container {{
            display: flex;
            flex-direction: column;
            gap: 1rem;
            max-width: 700px;
            width: 100%;
        }}

        .step-item {{
            display: flex;
            align-items: center;
            gap: 1rem;
            background: var(--card-bg);
            padding: 1rem 1.5rem;
            border-radius: 10px;
            text-align: left;
            border: 1px solid var(--card-border);
            transition: all 0.3s ease;
        }}

        .step-item:hover {{
            border-color: var(--accent-color);
        }}

        .step-item span {{
            color: var(--text-color);
        }}

        .step-number {{
            background: var(--accent-color);
            color: #1e3c72;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            flex-shrink: 0;
        }}

        .contact-info {{
            background: var(--card-bg);
            padding: 2rem;
            border-radius: 15px;
            margin: 2rem 0;
            max-width: 600px;
            backdrop-filter: blur(10px);
            border: 1px solid var(--card-border);
        }}

        .contact-info h3 {{
            color: var(--accent-color);
        }}

        .contact-info p {{
            color: var(--text-color);
        }}

        .contact-info a {{
            color: var(--secondary-color);
            text-decoration: none;
        }}

        .contact-info a:hover {{
            text-decoration: underline;
            color: var(--accent-color);
        }}

        .navigation {{
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 1rem;
            z-index: 100;
        }}

        .nav-btn {{
            background: var(--card-bg);
            border: 2px solid var(--text-color);
            color: var(--text-color);
            padding: 0.8rem 1.5rem;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1rem;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }}

        .nav-btn:hover {{
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
            border-color: var(--accent-color);
        }}

        /* TNDS Badge */
        .tnds-badge {{
            position: fixed;
            bottom: 30px;
            left: 30px;
            font-family: 'Space Mono', monospace;
            font-size: 0.6rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 2px;
            padding: 0.5rem 1rem;
            border: 1px solid var(--card-border);
            backdrop-filter: blur(10px);
            border-radius: 4px;
        }}

        .roadmap-container {{
            display: flex;
            gap: 3rem;
            max-width: 900px;
        }}

        .roadmap-column {{
            flex: 1;
        }}

        .roadmap-column h3 {{
            color: var(--accent-color);
            margin-bottom: 1rem;
            font-size: 1.5rem;
        }}

        .roadmap-column.planned h3 {{
            color: var(--secondary-color);
        }}

        .roadmap-column ul {{
            text-align: left;
        }}

        @media (max-width: 768px) {{
            .slide {{
                padding: 30px;
            }}
            
            .slide h1 {{
                font-size: 2.5rem;
            }}
            
            .slide h2 {{
                font-size: 2rem;
            }}
            
            .feature-grid,
            .stat-grid {{
                grid-template-columns: 1fr;
            }}

            .theme-panel {{
                width: 100%;
                right: -100%;
            }}

            .roadmap-container {{
                flex-direction: column;
                gap: 2rem;
            }}
        }}
    </style>
</head>
<body>'''


def get_theme_panel() -> str:
    """Generate the theme selector panel HTML."""
    return '''
    <!-- Theme Toggle Button -->
    <button class="theme-toggle-btn" onclick="toggleThemePanel()">Themes</button>

    <!-- Theme Selector Panel -->
    <div class="theme-panel" id="themePanel">
        <div class="theme-panel-header">
            <h2 class="theme-panel-title">Theme Selector</h2>
            <button class="theme-panel-close" onclick="toggleThemePanel()">&times;</button>
        </div>

        <div class="current-theme-display">
            <div class="current-theme-label">Current Theme</div>
            <div class="current-theme-grid">
                <div class="current-theme-item">
                    <div class="preview-swatch" id="previewBg" style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);"></div>
                    <span id="currentBgName">Navy Gradient</span>
                </div>
                <div class="current-theme-item">
                    <div class="preview-swatch" id="previewAccent" style="background: #ffd700;"></div>
                    <span id="currentAccentName">Gold</span>
                </div>
                <div class="current-theme-item">
                    <div class="preview-swatch" id="previewCard" style="background: rgba(255, 255, 255, 0.1);"></div>
                    <span id="currentCardName">Glass Light</span>
                </div>
                <div class="current-theme-item">
                    <div class="preview-swatch" id="previewFont" style="background: #ffffff;"></div>
                    <span id="currentFontName">White</span>
                </div>
            </div>
        </div>

        <!-- Background Options -->
        <div class="theme-section">
            <div class="theme-section-title">Background</div>
            
            <div class="theme-option active" data-type="bg" onclick="setBackground('navy-gradient', 'Navy Gradient', 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)')">
                <div class="theme-swatch gradient" style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);"></div>
                <div class="theme-info">
                    <div class="theme-name">Navy Gradient</div>
                    <div class="theme-desc">Professional, trustworthy</div>
                </div>
            </div>

            <div class="theme-option" data-type="bg" onclick="setBackground('charcoal-gradient', 'Charcoal Gradient', 'linear-gradient(135deg, #232526 0%, #414345 100%)')">
                <div class="theme-swatch gradient" style="background: linear-gradient(135deg, #232526 0%, #414345 100%);"></div>
                <div class="theme-info">
                    <div class="theme-name">Charcoal Gradient</div>
                    <div class="theme-desc">Dark, sophisticated</div>
                </div>
            </div>

            <div class="theme-option" data-type="bg" onclick="setBackground('midnight-gradient', 'Midnight', 'linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%)')">
                <div class="theme-swatch gradient" style="background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);"></div>
                <div class="theme-info">
                    <div class="theme-name">Midnight</div>
                    <div class="theme-desc">Deep purple night</div>
                </div>
            </div>

            <div class="theme-option" data-type="bg" onclick="setBackground('forest-gradient', 'Forest', 'linear-gradient(135deg, #134e5e 0%, #71b280 100%)')">
                <div class="theme-swatch gradient" style="background: linear-gradient(135deg, #134e5e 0%, #71b280 100%);"></div>
                <div class="theme-info">
                    <div class="theme-name">Forest</div>
                    <div class="theme-desc">Nature, growth</div>
                </div>
            </div>

            <div class="theme-option" data-type="bg" onclick="setBackground('olive-gradient', 'Olive Drab', 'linear-gradient(135deg, #3c4219 0%, #556B2F 100%)')">
                <div class="theme-swatch gradient" style="background: linear-gradient(135deg, #3c4219 0%, #556B2F 100%);"></div>
                <div class="theme-info">
                    <div class="theme-name">Olive Drab</div>
                    <div class="theme-desc">Military, tactical</div>
                </div>
            </div>

            <div class="theme-option" data-type="bg" onclick="setBackground('steel-gradient', 'Steel', 'linear-gradient(135deg, #2c3e50 0%, #4a6fa5 100%)')">
                <div class="theme-swatch gradient" style="background: linear-gradient(135deg, #2c3e50 0%, #4a6fa5 100%);"></div>
                <div class="theme-info">
                    <div class="theme-name">Steel</div>
                    <div class="theme-desc">Industrial strength</div>
                </div>
            </div>

            <div class="theme-option" data-type="bg" onclick="setBackground('ember-gradient', 'Ember', 'linear-gradient(135deg, #3d1c00 0%, #8B4513 100%)')">
                <div class="theme-swatch gradient" style="background: linear-gradient(135deg, #3d1c00 0%, #8B4513 100%);"></div>
                <div class="theme-info">
                    <div class="theme-name">Ember</div>
                    <div class="theme-desc">Warm, grounded</div>
                </div>
            </div>

            <div class="theme-option" data-type="bg" onclick="setBackground('black-solid', 'Pure Black', '#0D0D0D')">
                <div class="theme-swatch" style="background: #0D0D0D;"></div>
                <div class="theme-info">
                    <div class="theme-name">Pure Black</div>
                    <div class="theme-desc">Maximum contrast</div>
                </div>
            </div>

            <div class="theme-option" data-type="bg" onclick="setBackground('dark-gray-solid', 'Dark Gray', '#1A1A1A')">
                <div class="theme-swatch" style="background: #1A1A1A;"></div>
                <div class="theme-info">
                    <div class="theme-name">Dark Gray</div>
                    <div class="theme-desc">Soft black</div>
                </div>
            </div>

            <div class="theme-option" data-type="bg" onclick="setBackground('cream-solid', 'Cream', '#F5F0EB')">
                <div class="theme-swatch" style="background: #F5F0EB; border-color: #999;"></div>
                <div class="theme-info">
                    <div class="theme-name">Cream</div>
                    <div class="theme-desc">Warm light mode</div>
                </div>
            </div>

            <div class="theme-option" data-type="bg" onclick="setBackground('white-solid', 'Pure White', '#FFFFFF')">
                <div class="theme-swatch" style="background: #FFFFFF; border-color: #999;"></div>
                <div class="theme-info">
                    <div class="theme-name">Pure White</div>
                    <div class="theme-desc">Clean light mode</div>
                </div>
            </div>
        </div>

        <!-- Accent Color Options -->
        <div class="theme-section">
            <div class="theme-section-title">Accent Color</div>

            <div class="theme-option active" data-type="accent" onclick="setAccent('gold', 'Gold', '#ffd700', '#ccac00', '#87ceeb')">
                <div class="theme-swatch" style="background: #ffd700;"></div>
                <div class="theme-info">
                    <div class="theme-name">Gold</div>
                    <div class="theme-desc">Premium, professional</div>
                </div>
                <div class="theme-hex">#FFD700</div>
            </div>

            <div class="theme-option" data-type="accent" onclick="setAccent('concrete-gray', 'Concrete Gray', '#8A8A8A', '#6E6E6E', '#B8B8B8')">
                <div class="theme-swatch" style="background: #8A8A8A;"></div>
                <div class="theme-info">
                    <div class="theme-name">Concrete Gray</div>
                    <div class="theme-desc">Industrial, utilitarian</div>
                </div>
                <div class="theme-hex">#8A8A8A</div>
            </div>

            <div class="theme-option" data-type="accent" onclick="setAccent('burnt-orange', 'Burnt Orange', '#D4652F', '#A84F25', '#E8A87C')">
                <div class="theme-swatch" style="background: #D4652F;"></div>
                <div class="theme-info">
                    <div class="theme-name">Burnt Orange</div>
                    <div class="theme-desc">Earthy, grounded</div>
                </div>
                <div class="theme-hex">#D4652F</div>
            </div>

            <div class="theme-option" data-type="accent" onclick="setAccent('steel-blue', 'Steel Blue', '#4A6FA5', '#3A5A87', '#7A9FD5')">
                <div class="theme-swatch" style="background: #4A6FA5;"></div>
                <div class="theme-info">
                    <div class="theme-name">Steel Blue</div>
                    <div class="theme-desc">Quiet strength</div>
                </div>
                <div class="theme-hex">#4A6FA5</div>
            </div>

            <div class="theme-option" data-type="accent" onclick="setAccent('desert-sand', 'Desert Sand', '#C9A66B', '#A68A56', '#E5D4B8')">
                <div class="theme-swatch" style="background: #C9A66B;"></div>
                <div class="theme-info">
                    <div class="theme-name">Desert Sand</div>
                    <div class="theme-desc">Workwear, rugged</div>
                </div>
                <div class="theme-hex">#C9A66B</div>
            </div>

            <div class="theme-option" data-type="accent" onclick="setAccent('forest-green', 'Forest Green', '#4A5D3A', '#3B4A2E', '#7A8D6A')">
                <div class="theme-swatch" style="background: #4A5D3A;"></div>
                <div class="theme-info">
                    <div class="theme-name">Forest Green</div>
                    <div class="theme-desc">Survival, endurance</div>
                </div>
                <div class="theme-hex">#4A5D3A</div>
            </div>

            <div class="theme-option" data-type="accent" onclick="setAccent('army-green', 'Army Green', '#4B5320', '#3C4219', '#7B8350')">
                <div class="theme-swatch" style="background: #4B5320;"></div>
                <div class="theme-info">
                    <div class="theme-name">Army Green</div>
                    <div class="theme-desc">Classic olive drab</div>
                </div>
                <div class="theme-hex">#4B5320</div>
            </div>

            <div class="theme-option" data-type="accent" onclick="setAccent('navy', 'Navy', '#1E3A5F', '#182E4C', '#4E6A8F')">
                <div class="theme-swatch" style="background: #1E3A5F;"></div>
                <div class="theme-info">
                    <div class="theme-name">Navy</div>
                    <div class="theme-desc">Classic navy</div>
                </div>
                <div class="theme-hex">#1E3A5F</div>
            </div>

            <div class="theme-option" data-type="accent" onclick="setAccent('red', 'Blood Red', '#C41E3A', '#9A1830', '#E44E68')">
                <div class="theme-swatch" style="background: #C41E3A;"></div>
                <div class="theme-info">
                    <div class="theme-name">Blood Red</div>
                    <div class="theme-desc">Survival, grit</div>
                </div>
                <div class="theme-hex">#C41E3A</div>
            </div>

            <div class="theme-option" data-type="accent" onclick="setAccent('cyan', 'Cyan', '#00CED1', '#00A5A8', '#5EEAED')">
                <div class="theme-swatch" style="background: #00CED1;"></div>
                <div class="theme-info">
                    <div class="theme-name">Cyan</div>
                    <div class="theme-desc">Tech, modern</div>
                </div>
                <div class="theme-hex">#00CED1</div>
            </div>

            <div class="theme-option" data-type="accent" onclick="setAccent('pure-white', 'Pure White', '#FAFAFA', '#E5E5E5', '#FFFFFF')">
                <div class="theme-swatch" style="background: #FAFAFA; border-color: #666;"></div>
                <div class="theme-info">
                    <div class="theme-name">Pure White</div>
                    <div class="theme-desc">Clean, minimal</div>
                </div>
                <div class="theme-hex">#FAFAFA</div>
            </div>
        </div>

        <!-- Card Color Options -->
        <div class="theme-section">
            <div class="theme-section-title">Card Style</div>

            <div class="theme-option active" data-type="card" onclick="setCard('glass-light', 'Glass Light', 'rgba(255, 255, 255, 0.1)', 'rgba(255, 255, 255, 0.1)')">
                <div class="theme-swatch" style="background: rgba(255, 255, 255, 0.1); border-color: rgba(255,255,255,0.3);"></div>
                <div class="theme-info">
                    <div class="theme-name">Glass Light</div>
                    <div class="theme-desc">Subtle transparency</div>
                </div>
            </div>

            <div class="theme-option" data-type="card" onclick="setCard('glass-medium', 'Glass Medium', 'rgba(255, 255, 255, 0.15)', 'rgba(255, 255, 255, 0.2)')">
                <div class="theme-swatch" style="background: rgba(255, 255, 255, 0.15); border-color: rgba(255,255,255,0.3);"></div>
                <div class="theme-info">
                    <div class="theme-name">Glass Medium</div>
                    <div class="theme-desc">More visible</div>
                </div>
            </div>

            <div class="theme-option" data-type="card" onclick="setCard('glass-dark', 'Glass Dark', 'rgba(0, 0, 0, 0.2)', 'rgba(0, 0, 0, 0.3)')">
                <div class="theme-swatch" style="background: rgba(0, 0, 0, 0.3);"></div>
                <div class="theme-info">
                    <div class="theme-name">Glass Dark</div>
                    <div class="theme-desc">Dark overlay</div>
                </div>
            </div>

            <div class="theme-option" data-type="card" onclick="setCard('glass-heavy', 'Glass Heavy', 'rgba(0, 0, 0, 0.4)', 'rgba(0, 0, 0, 0.5)')">
                <div class="theme-swatch" style="background: rgba(0, 0, 0, 0.5);"></div>
                <div class="theme-info">
                    <div class="theme-name">Glass Heavy</div>
                    <div class="theme-desc">Strong contrast</div>
                </div>
            </div>

            <div class="theme-option" data-type="card" onclick="setCard('solid-dark', 'Solid Dark', '#1A1A1A', '#333333')">
                <div class="theme-swatch" style="background: #1A1A1A;"></div>
                <div class="theme-info">
                    <div class="theme-name">Solid Dark</div>
                    <div class="theme-desc">No transparency</div>
                </div>
            </div>

            <div class="theme-option" data-type="card" onclick="setCard('solid-charcoal', 'Solid Charcoal', '#2D2D2D', '#404040')">
                <div class="theme-swatch" style="background: #2D2D2D;"></div>
                <div class="theme-info">
                    <div class="theme-name">Solid Charcoal</div>
                    <div class="theme-desc">Medium dark</div>
                </div>
            </div>

            <div class="theme-option" data-type="card" onclick="setCard('solid-white', 'Solid White', '#FFFFFF', '#E5E5E5')">
                <div class="theme-swatch" style="background: #FFFFFF; border-color: #999;"></div>
                <div class="theme-info">
                    <div class="theme-name">Solid White</div>
                    <div class="theme-desc">For light backgrounds</div>
                </div>
            </div>

            <div class="theme-option" data-type="card" onclick="setCard('solid-cream', 'Solid Cream', '#F5F0EB', '#E5E0DB')">
                <div class="theme-swatch" style="background: #F5F0EB; border-color: #999;"></div>
                <div class="theme-info">
                    <div class="theme-name">Solid Cream</div>
                    <div class="theme-desc">Warm white</div>
                </div>
            </div>
        </div>

        <!-- Font Color Options -->
        <div class="theme-section">
            <div class="theme-section-title">Font Color</div>

            <div class="theme-option active" data-type="font" onclick="setFont('white', 'White', '#FFFFFF', 'rgba(255, 255, 255, 0.7)')">
                <div class="theme-swatch" style="background: #FFFFFF; border-color: #666;"></div>
                <div class="theme-info">
                    <div class="theme-name">White</div>
                    <div class="theme-desc">For dark backgrounds</div>
                </div>
            </div>

            <div class="theme-option" data-type="font" onclick="setFont('off-white', 'Off White', '#F5F5F5', 'rgba(245, 245, 245, 0.7)')">
                <div class="theme-swatch" style="background: #F5F5F5; border-color: #666;"></div>
                <div class="theme-info">
                    <div class="theme-name">Off White</div>
                    <div class="theme-desc">Softer white</div>
                </div>
            </div>

            <div class="theme-option" data-type="font" onclick="setFont('cream', 'Cream', '#F5F0EB', 'rgba(245, 240, 235, 0.7)')">
                <div class="theme-swatch" style="background: #F5F0EB; border-color: #666;"></div>
                <div class="theme-info">
                    <div class="theme-name">Cream</div>
                    <div class="theme-desc">Warm tone</div>
                </div>
            </div>

            <div class="theme-option" data-type="font" onclick="setFont('light-gray', 'Light Gray', '#CCCCCC', 'rgba(204, 204, 204, 0.7)')">
                <div class="theme-swatch" style="background: #CCCCCC; border-color: #666;"></div>
                <div class="theme-info">
                    <div class="theme-name">Light Gray</div>
                    <div class="theme-desc">Subdued</div>
                </div>
            </div>

            <div class="theme-option" data-type="font" onclick="setFont('black', 'Black', '#0D0D0D', 'rgba(13, 13, 13, 0.6)')">
                <div class="theme-swatch" style="background: #0D0D0D;"></div>
                <div class="theme-info">
                    <div class="theme-name">Black</div>
                    <div class="theme-desc">For light backgrounds</div>
                </div>
            </div>

            <div class="theme-option" data-type="font" onclick="setFont('dark-gray', 'Dark Gray', '#333333', 'rgba(51, 51, 51, 0.6)')">
                <div class="theme-swatch" style="background: #333333;"></div>
                <div class="theme-info">
                    <div class="theme-name">Dark Gray</div>
                    <div class="theme-desc">Softer black</div>
                </div>
            </div>

            <div class="theme-option" data-type="font" onclick="setFont('charcoal', 'Charcoal', '#36454F', 'rgba(54, 69, 79, 0.6)')">
                <div class="theme-swatch" style="background: #36454F;"></div>
                <div class="theme-info">
                    <div class="theme-name">Charcoal</div>
                    <div class="theme-desc">Blue undertone</div>
                </div>
            </div>

            <div class="theme-option" data-type="font" onclick="setFont('navy', 'Navy', '#1E3A5F', 'rgba(30, 58, 95, 0.6)')">
                <div class="theme-swatch" style="background: #1E3A5F;"></div>
                <div class="theme-info">
                    <div class="theme-name">Navy</div>
                    <div class="theme-desc">Deep blue</div>
                </div>
            </div>
        </div>

        <button class="reset-btn" onclick="resetThemes()">Reset to Defaults</button>
    </div>
'''


def get_template_scripts() -> str:
    """Generate the JavaScript for theme switching and slide navigation."""
    return '''
    <script>
        // Theme state
        let currentBg = 'navy-gradient';
        let currentAccent = 'gold';
        let currentCard = 'glass-light';
        let currentFont = 'white';

        function toggleThemePanel() {
            const panel = document.getElementById('themePanel');
            panel.classList.toggle('active');
        }

        function setBackground(bgId, bgName, bgValue) {
            currentBg = bgId;
            document.body.style.background = bgValue;
            document.getElementById('currentBgName').textContent = bgName;
            document.getElementById('previewBg').style.background = bgValue;
            document.querySelectorAll('.theme-option[data-type="bg"]').forEach(opt => opt.classList.remove('active'));
            event.currentTarget.classList.add('active');
            localStorage.setItem('presentation_bg', JSON.stringify({ id: bgId, name: bgName, value: bgValue }));
        }

        function setAccent(accentId, accentName, accent, accentDim, secondary) {
            currentAccent = accentId;
            document.documentElement.style.setProperty('--accent-color', accent);
            document.documentElement.style.setProperty('--accent-dim', accentDim);
            document.documentElement.style.setProperty('--secondary-color', secondary);
            document.getElementById('currentAccentName').textContent = accentName;
            document.getElementById('previewAccent').style.background = accent;
            document.querySelectorAll('.theme-option[data-type="accent"]').forEach(opt => opt.classList.remove('active'));
            event.currentTarget.classList.add('active');
            localStorage.setItem('presentation_accent', JSON.stringify({ id: accentId, name: accentName, accent: accent, accentDim: accentDim, secondary: secondary }));
        }

        function setCard(cardId, cardName, cardBg, cardBorder) {
            currentCard = cardId;
            document.documentElement.style.setProperty('--card-bg', cardBg);
            document.documentElement.style.setProperty('--card-border', cardBorder);
            document.getElementById('currentCardName').textContent = cardName;
            document.getElementById('previewCard').style.background = cardBg;
            document.querySelectorAll('.theme-option[data-type="card"]').forEach(opt => opt.classList.remove('active'));
            event.currentTarget.classList.add('active');
            localStorage.setItem('presentation_card', JSON.stringify({ id: cardId, name: cardName, bg: cardBg, border: cardBorder }));
        }

        function setFont(fontId, fontName, fontColor, fontMuted) {
            currentFont = fontId;
            document.documentElement.style.setProperty('--text-color', fontColor);
            document.documentElement.style.setProperty('--text-muted', fontMuted);
            document.getElementById('currentFontName').textContent = fontName;
            document.getElementById('previewFont').style.background = fontColor;
            document.querySelectorAll('.theme-option[data-type="font"]').forEach(opt => opt.classList.remove('active'));
            event.currentTarget.classList.add('active');
            localStorage.setItem('presentation_font', JSON.stringify({ id: fontId, name: fontName, color: fontColor, muted: fontMuted }));
        }

        function resetThemes() {
            localStorage.removeItem('presentation_bg');
            localStorage.removeItem('presentation_accent');
            localStorage.removeItem('presentation_card');
            localStorage.removeItem('presentation_font');
            
            document.body.style.background = 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)';
            document.documentElement.style.setProperty('--accent-color', '#ffd700');
            document.documentElement.style.setProperty('--accent-dim', '#ccac00');
            document.documentElement.style.setProperty('--secondary-color', '#87ceeb');
            document.documentElement.style.setProperty('--card-bg', 'rgba(255, 255, 255, 0.1)');
            document.documentElement.style.setProperty('--card-border', 'rgba(255, 255, 255, 0.1)');
            document.documentElement.style.setProperty('--text-color', '#ffffff');
            document.documentElement.style.setProperty('--text-muted', 'rgba(255, 255, 255, 0.7)');
            
            document.getElementById('currentBgName').textContent = 'Navy Gradient';
            document.getElementById('currentAccentName').textContent = 'Gold';
            document.getElementById('currentCardName').textContent = 'Glass Light';
            document.getElementById('currentFontName').textContent = 'White';
            document.getElementById('previewBg').style.background = 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)';
            document.getElementById('previewAccent').style.background = '#ffd700';
            document.getElementById('previewCard').style.background = 'rgba(255, 255, 255, 0.1)';
            document.getElementById('previewFont').style.background = '#ffffff';
            
            document.querySelectorAll('.theme-option').forEach(opt => opt.classList.remove('active'));
            document.querySelectorAll('.theme-option[data-type="bg"]')[0].classList.add('active');
            document.querySelectorAll('.theme-option[data-type="accent"]')[0].classList.add('active');
            document.querySelectorAll('.theme-option[data-type="card"]')[0].classList.add('active');
            document.querySelectorAll('.theme-option[data-type="font"]')[0].classList.add('active');
        }

        function loadSavedThemes() {
            const savedBg = localStorage.getItem('presentation_bg');
            const savedAccent = localStorage.getItem('presentation_accent');
            const savedCard = localStorage.getItem('presentation_card');
            const savedFont = localStorage.getItem('presentation_font');
            
            if (savedBg) {
                const bg = JSON.parse(savedBg);
                document.body.style.background = bg.value;
                document.getElementById('currentBgName').textContent = bg.name;
                document.getElementById('previewBg').style.background = bg.value;
            }
            
            if (savedAccent) {
                const accent = JSON.parse(savedAccent);
                document.documentElement.style.setProperty('--accent-color', accent.accent);
                document.documentElement.style.setProperty('--accent-dim', accent.accentDim);
                document.documentElement.style.setProperty('--secondary-color', accent.secondary);
                document.getElementById('currentAccentName').textContent = accent.name;
                document.getElementById('previewAccent').style.background = accent.accent;
            }
            
            if (savedCard) {
                const card = JSON.parse(savedCard);
                document.documentElement.style.setProperty('--card-bg', card.bg);
                document.documentElement.style.setProperty('--card-border', card.border);
                document.getElementById('currentCardName').textContent = card.name;
                document.getElementById('previewCard').style.background = card.bg;
            }
            
            if (savedFont) {
                const font = JSON.parse(savedFont);
                document.documentElement.style.setProperty('--text-color', font.color);
                document.documentElement.style.setProperty('--text-muted', font.muted);
                document.getElementById('currentFontName').textContent = font.name;
                document.getElementById('previewFont').style.background = font.color;
            }
        }

        // Slide navigation
        let currentSlide = 0;
        const slides = document.querySelectorAll('.slide');
        const totalSlides = slides.length;

        document.getElementById('total-slides').textContent = totalSlides;

        function showSlide(n) {
            slides[currentSlide].classList.remove('active');
            currentSlide = (n + totalSlides) % totalSlides;
            slides[currentSlide].classList.add('active');
            document.getElementById('current-slide').textContent = currentSlide + 1;
        }

        function nextSlide() {
            showSlide(currentSlide + 1);
        }

        function previousSlide() {
            showSlide(currentSlide - 1);
        }

        // Keyboard navigation
        document.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowRight' || e.key === ' ') {
                nextSlide();
            } else if (e.key === 'ArrowLeft') {
                previousSlide();
            } else if (e.key === 'Escape') {
                const panel = document.getElementById('themePanel');
                if (panel.classList.contains('active')) {
                    panel.classList.remove('active');
                }
            }
        });

        // Touch/swipe navigation for mobile
        let startX = 0;
        let endX = 0;

        document.addEventListener('touchstart', function(e) {
            startX = e.changedTouches[0].screenX;
        });

        document.addEventListener('touchend', function(e) {
            endX = e.changedTouches[0].screenX;
            handleSwipe();
        });

        function handleSwipe() {
            const threshold = 50;
            if (startX - endX > threshold) {
                nextSlide();
            } else if (endX - startX > threshold) {
                previousSlide();
            }
        }

        // Initialize
        loadSavedThemes();
    </script>
</body>
</html>'''


def render_slide(slide: dict, is_first: bool = False) -> str:
    """Render a single slide to HTML."""
    
    active_class = ' active' if is_first else ''
    slide_type = slide.get('type', 'content')
    
    if slide_type == 'title':
        return f'''
        <!-- Slide: Title -->
        <div class="slide{active_class}">
            <h1>{slide['title']}</h1>
            <p style="font-size: 1.8rem; margin-bottom: 2rem;">{slide['tagline']}</p>
            <p style="margin-top: 3rem; font-size: 1.2rem;">{slide.get('date', '')}</p>
        </div>'''
    
    elif slide_type == 'features':
        items = slide.get('items', [])
        cards_html = ''
        for item in items[:9]:
            # Try to extract title and description
            match = re.match(r'^([^-:]+?)\s*[-:]\s*(.+)$', item)
            if match:
                title = match.group(1).strip()
                desc = match.group(2).strip()
            else:
                title = item
                desc = ''
            
            if len(title) > 50:
                title = title[:47] + '...'
            
            cards_html += f'''
                <div class="feature-card">
                    <h4>{title}</h4>
                    <p style="font-size: 1rem;">{desc}</p>
                </div>'''
        
        return f'''
        <!-- Slide: Features -->
        <div class="slide{active_class}">
            <h2>{slide['title']}</h2>
            <div class="feature-grid">
                {cards_html}
            </div>
        </div>'''
    
    elif slide_type == 'grid':
        items = slide.get('items', [])
        cards_html = ''
        for item in items[:9]:
            cards_html += f'''
                <div class="feature-card">
                    <p>{item}</p>
                </div>'''
        
        return f'''
        <!-- Slide: Grid -->
        <div class="slide{active_class}">
            <h2>{slide['title']}</h2>
            <div class="feature-grid">
                {cards_html}
            </div>
        </div>'''
    
    elif slide_type == 'steps':
        items = slide.get('items', [])
        steps_html = ''
        for i, item in enumerate(items[:6], 1):
            steps_html += f'''
                <div class="step-item">
                    <div class="step-number">{i}</div>
                    <span>{item}</span>
                </div>'''
        
        return f'''
        <!-- Slide: Steps -->
        <div class="slide{active_class}">
            <h2>{slide['title']}</h2>
            <div class="steps-container">
                {steps_html}
            </div>
        </div>'''
    
    elif slide_type == 'roadmap':
        items = slide.get('items', [])
        # Try to split into completed and planned
        completed = []
        planned = []
        
        for item in items:
            item_lower = item.lower()
            if any(word in item_lower for word in ['done', 'completed', 'finished', '✓', '✔']):
                completed.append(item)
            else:
                planned.append(item)
        
        # If no clear separation, put first half in completed
        if not completed and not planned:
            mid = len(items) // 2
            completed = items[:mid] if mid > 0 else items[:2]
            planned = items[mid:] if mid > 0 else items[2:]
        
        completed_html = ''.join(f'<li>{item}</li>' for item in completed[:4])
        planned_html = ''.join(f'<li>{item}</li>' for item in planned[:4])
        
        return f'''
        <!-- Slide: Roadmap -->
        <div class="slide{active_class}">
            <h2>{slide['title']}</h2>
            <div class="roadmap-container">
                <div class="roadmap-column">
                    <h3>Completed</h3>
                    <ul>{completed_html}</ul>
                </div>
                <div class="roadmap-column planned">
                    <h3>Planned</h3>
                    <ul>{planned_html}</ul>
                </div>
            </div>
        </div>'''
    
    elif slide_type == 'closing':
        contact = slide.get('contact', {})
        contact_html = ''
        
        if contact:
            contact_items = []
            if contact.get('email'):
                contact_items.append(f'<p><strong>Email:</strong> <a href="mailto:{contact["email"]}">{contact["email"]}</a></p>')
            if contact.get('github'):
                contact_items.append(f'<p><strong>GitHub:</strong> <a href="https://github.com/{contact["github"]}" target="_blank">github.com/{contact["github"]}</a></p>')
            if contact.get('website'):
                contact_items.append(f'<p><strong>Website:</strong> <a href="{contact["website"]}" target="_blank">{contact["website"]}</a></p>')
            if contact.get('linkedin'):
                contact_items.append(f'<p><strong>LinkedIn:</strong> <a href="https://linkedin.com/in/{contact["linkedin"]}" target="_blank">linkedin.com/in/{contact["linkedin"]}</a></p>')
            
            if contact_items:
                contact_html = f'''
            <div class="contact-info">
                <h3>Contact</h3>
                {"".join(contact_items)}
            </div>'''
        
        return f'''
        <!-- Slide: Closing -->
        <div class="slide{active_class}">
            <h1>{slide['title']}</h1>
            <p style="font-size: 1.5rem;">{slide.get('tagline', '')}</p>
            {contact_html}
            <p style="margin-top: 2rem; font-size: 1.2rem;">Thank you!</p>
        </div>'''
    
    else:  # Default content slide
        items = slide.get('items', [])
        items_html = ''
        if items:
            items_html = '<ul>' + ''.join(f'<li>{item}</li>' for item in items) + '</ul>'
        
        return f'''
        <!-- Slide: Content -->
        <div class="slide{active_class}">
            <h2>{slide['title']}</h2>
            {items_html}
        </div>'''


def render_html(slides: list, config: dict = None) -> str:
    """Render the complete HTML presentation."""
    
    config = config or {}
    company = config.get('company', {})
    company_name = company.get('name', 'True North Data Strategies LLC')
    
    title = slides[0]['title'] if slides else 'Presentation'
    
    # Render all slides
    html_slides = []
    for i, slide in enumerate(slides):
        html_slides.append(render_slide(slide, is_first=(i == 0)))
    
    # Build complete HTML
    html = get_template_head(title, config)
    html += get_theme_panel()
    html += f'''
    <div class="slide-container">
        <div class="slide-counter">
            <span id="current-slide">1</span> / <span id="total-slides">{len(slides)}</span>
        </div>

        {"".join(html_slides)}

        <div class="navigation">
            <button class="nav-btn" onclick="previousSlide()">&#8592; Previous</button>
            <button class="nav-btn" onclick="nextSlide()">Next &#8594;</button>
        </div>

        <div class="tnds-badge">{company_name}</div>
    </div>
'''
    html += get_template_scripts()
    
    return html


def main():
    """Main entry point for the presentation generator."""
    
    # Parse command line arguments
    readme_path = 'README.md'
    output_path = 'presentation.html'
    config_path = None
    
    args = sys.argv[1:]
    
    if len(args) >= 1:
        readme_path = args[0]
    if len(args) >= 2:
        output_path = args[1]
    if len(args) >= 3:
        config_path = args[2]
    
    # Check if README exists
    if not os.path.exists(readme_path):
        print(f"Error: README file not found: {readme_path}")
        print("\nUsage: python generate_presentation.py [README.md] [output.html] [config.json]")
        sys.exit(1)
    
    # Load config if provided
    config = {}
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"Loaded config: {config_path}")
    
    print(f"Parsing README: {readme_path}")
    parsed = parse_readme(readme_path)
    
    print(f"Generating slides for: {parsed['title']}")
    slides = generate_slides(parsed, config)
    
    print(f"Rendering {len(slides)} slides to HTML...")
    html = render_html(slides, config)
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\nPresentation saved to: {output_path}")
    print(f"Open in a browser to view your presentation!")
    print(f"\nFeatures included:")
    print(f"  - 4-section theme selector (Background, Accent, Card, Font)")
    print(f"  - 11 background options (gradients + solids)")
    print(f"  - 11 accent colors")
    print(f"  - 8 card styles")
    print(f"  - 8 font colors")
    print(f"  - Theme persistence via localStorage")
    print(f"  - Keyboard navigation (arrows, space, ESC)")
    print(f"  - Touch/swipe support for mobile")


if __name__ == '__main__':
    main()
