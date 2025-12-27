"""
Process all .md files to generate moral landscape images from YAML blocks.

This script:
1. Finds all YAML blocks in markdown files
2. Generates moral landscape images using the YAML configuration
3. Inserts markdown image tags after the YAML block (outside hidden divs)
4. Uses the output_file as a unique identifier to avoid duplicate image tags
"""

import os
import re
import sys
import argparse
import threading
from pathlib import Path
from typing import List, Tuple, Optional, Set
import yaml
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk

# Add the moral landscape generator to the path
sys.path.insert(0, str(Path(__file__).parent / 'utils' / 'moral_landscape'))

from moral_landscape_generator import MoralLandscape


class MoralLandscapeProcessor:
    """Process markdown files to generate and embed moral landscape images."""
    
    def __init__(self, images_dir: str = "images"):
        """
        Initialize the processor.
        
        Args:
            images_dir: Directory where images will be saved
        """
        self.images_dir = Path(images_dir)
        self.images_dir.mkdir(exist_ok=True)
        
    def find_markdown_files(self, root_dir: str = ".") -> List[Path]:
        """
        Find all .md files in the directory tree.
        
        Args:
            root_dir: Root directory to search
            
        Returns:
            List of Path objects for .md files
        """
        root = Path(root_dir)
        md_files = []
        
        for md_file in root.rglob("*.md"):
            # Skip files in node_modules, .git, etc.
            if not any(part.startswith('.') or part == 'node_modules' 
                      for part in md_file.parts):
                md_files.append(md_file)

        return md_files
    
    def extract_yaml_blocks(self, content: str) -> List[Tuple[str, int, int, Optional[int], Optional[int]]]:
        """
        Extract YAML blocks from markdown content.
        
        Returns:
            List of tuples: (yaml_content, start_pos, end_pos, details_start_pos, details_end_pos)
            details_start_pos: position of <details> tag if exists, else None
            details_end_pos: position after </details> if exists, else None
        """
        blocks = []
        
        # Find all code blocks with yaml
        yaml_pattern = r'```yaml moralgraph\s*\n(.*?)\n```'
        
        for match in re.finditer(yaml_pattern, content, re.DOTALL):
            yaml_content = match.group(1)
            start_pos = match.start()
            end_pos = match.end()
            
            details_start_pos = None
            details_end_pos = None
            
            # Look backwards to find <details> tag (within ~200 chars)
            search_start = max(0, start_pos - 200)
            before_yaml = content[search_start:start_pos]
            
            # Find the last <details> before the yaml block
            details_match = None
            for dm in re.finditer(r'<details[^>]*>', before_yaml):
                details_match = dm
            
            if details_match:
                # Position in the full content
                details_start_pos = search_start + details_match.start()
                
                # Look forward to find </details> after the yaml block
                after_yaml = content[end_pos:]
                closing_details = re.search(r'</details>', after_yaml)
                if closing_details:
                    # Position of the character right after </details>
                    details_end_pos = end_pos + closing_details.end()
            
            blocks.append((yaml_content, start_pos, end_pos, details_start_pos, details_end_pos))
        
        return blocks
    
    def parse_yaml_config(self, yaml_content: str) -> Optional[dict]:
        """
        Parse YAML content and check if it's a valid landscape configuration.
        
        Args:
            yaml_content: YAML string
            
        Returns:
            Parsed config dict or None if invalid
            
        Raises:
            ValueError: If YAML doesn't match the required schema
        """
        try:
            config = yaml.safe_load(yaml_content)
            
            # Check if it has the required structure for a moral landscape
            if not isinstance(config, dict):
                return None
            
            # Must have 'render' with 'output_file' to be processable
            if 'render' not in config or 'output_file' not in config.get('render', {}):
                return None
            
            # Validate against schema
            self._validate_schema(config)
            
            return config
        except yaml.YAMLError:
            return None
    
    def _validate_schema(self, config: dict) -> None:
        """
        Validate YAML configuration against the schema.
        
        Args:
            config: Parsed YAML configuration
            
        Raises:
            ValueError: If configuration doesn't match schema
        """
        errors = []
        
        # Validate landscape section
        if 'landscape' in config:
            landscape = config['landscape']
            if not isinstance(landscape, dict):
                errors.append("'landscape' must be an object")
            else:
                # Validate resolution
                if 'resolution' in landscape and not isinstance(landscape['resolution'], int):
                    errors.append("'landscape.resolution' must be an integer")
                if 'resolution' in landscape and landscape['resolution'] < 10:
                    errors.append("'landscape.resolution' must be at least 10")
                
                # Validate ranges
                for range_key in ['x_range', 'y_range']:
                    if range_key in landscape:
                        range_val = landscape[range_key]
                        if not isinstance(range_val, list) or len(range_val) != 2:
                            errors.append(f"'landscape.{range_key}' must be an array with exactly 2 numbers")
                        elif not all(isinstance(x, (int, float)) for x in range_val):
                            errors.append(f"'landscape.{range_key}' must contain only numbers")
                
                # Validate noise_level
                if 'noise_level' in landscape:
                    if not isinstance(landscape['noise_level'], (int, float)):
                        errors.append("'landscape.noise_level' must be a number")
                    elif landscape['noise_level'] < 0:
                        errors.append("'landscape.noise_level' must be non-negative")
                
                # Validate axes
                if 'axes' in landscape:
                    if not isinstance(landscape['axes'], dict):
                        errors.append("'landscape.axes' must be an object")
                    else:
                        for axis in ['xlabel', 'ylabel', 'zlabel']:
                            if axis in landscape['axes'] and not isinstance(landscape['axes'][axis], str):
                                errors.append(f"'landscape.axes.{axis}' must be a string")
                
                # Validate style
                if 'style' in landscape:
                    if not isinstance(landscape['style'], dict):
                        errors.append("'landscape.style' must be an object")
                    else:
                        if 'colormap' in landscape['style'] and not isinstance(landscape['style']['colormap'], str):
                            errors.append("'landscape.style.colormap' must be a string")
                        if 'figsize' in landscape['style']:
                            figsize = landscape['style']['figsize']
                            if not isinstance(figsize, list) or len(figsize) != 2:
                                errors.append("'landscape.style.figsize' must be an array with exactly 2 integers")
                            elif not all(isinstance(x, int) for x in figsize):
                                errors.append("'landscape.style.figsize' must contain only integers")
        
        # Validate peaks
        if 'peaks' in config:
            if not isinstance(config['peaks'], list):
                errors.append("'peaks' must be an array")
            else:
                for i, peak in enumerate(config['peaks']):
                    if not isinstance(peak, dict):
                        errors.append(f"peaks[{i}] must be an object")
                        continue
                    
                    # Required fields
                    if 'coords' not in peak:
                        errors.append(f"peaks[{i}] is missing required field 'coords'")
                    else:
                        coords = peak['coords']
                        if not isinstance(coords, list) or len(coords) != 3:
                            errors.append(f"peaks[{i}].coords must be an array with exactly 3 numbers")
                        elif not all(isinstance(x, (int, float)) for x in coords):
                            errors.append(f"peaks[{i}].coords must contain only numbers")
                    
                    if 'label' not in peak:
                        errors.append(f"peaks[{i}] is missing required field 'label'")
                    elif not isinstance(peak['label'], str):
                        errors.append(f"peaks[{i}].label must be a string")
                    
                    # Optional fields
                    if 'type' in peak and peak['type'] not in [None, 'peak']:
                        errors.append(f"peaks[{i}].type must be 'peak' if specified")
                    
                    if 'label_offset' in peak:
                        offset = peak['label_offset']
                        if not isinstance(offset, list) or len(offset) != 3:
                            errors.append(f"peaks[{i}].label_offset must be an array with exactly 3 numbers")
                        elif not all(isinstance(x, (int, float)) for x in offset):
                            errors.append(f"peaks[{i}].label_offset must contain only numbers")
                    
                    if 'z_index' in peak:
                        if not isinstance(peak['z_index'], int):
                            errors.append(f"peaks[{i}].z_index must be an integer")
        
        # Validate troughs
        if 'troughs' in config:
            if not isinstance(config['troughs'], list):
                errors.append("'troughs' must be an array")
            else:
                for i, trough in enumerate(config['troughs']):
                    if not isinstance(trough, dict):
                        errors.append(f"troughs[{i}] must be an object")
                        continue
                    
                    # Required fields
                    if 'coords' not in trough:
                        errors.append(f"troughs[{i}] is missing required field 'coords'")
                    else:
                        coords = trough['coords']
                        if not isinstance(coords, list) or len(coords) != 3:
                            errors.append(f"troughs[{i}].coords must be an array with exactly 3 numbers")
                        elif not all(isinstance(x, (int, float)) for x in coords):
                            errors.append(f"troughs[{i}].coords must contain only numbers")
                    
                    if 'label' not in trough:
                        errors.append(f"troughs[{i}] is missing required field 'label'")
                    elif not isinstance(trough['label'], str):
                        errors.append(f"troughs[{i}].label must be a string")
                    
                    # Optional fields
                    if 'type' in trough and trough['type'] not in [None, 'trough']:
                        errors.append(f"troughs[{i}].type must be 'trough' if specified")
                    
                    if 'label_offset' in trough:
                        offset = trough['label_offset']
                        if not isinstance(offset, list) or len(offset) != 3:
                            errors.append(f"troughs[{i}].label_offset must be an array with exactly 3 numbers")
                        elif not all(isinstance(x, (int, float)) for x in offset):
                            errors.append(f"troughs[{i}].label_offset must contain only numbers")
                    
                    if 'z_index' in trough:
                        if not isinstance(trough['z_index'], int):
                            errors.append(f"troughs[{i}].z_index must be an integer")
        
        # Validate neutrals
        if 'neutrals' in config:
            if not isinstance(config['neutrals'], list):
                errors.append("'neutrals' must be an array")
            else:
                for i, neutral in enumerate(config['neutrals']):
                    if not isinstance(neutral, dict):
                        errors.append(f"neutrals[{i}] must be an object")
                        continue
                    
                    # Required fields
                    if 'coords' not in neutral:
                        errors.append(f"neutrals[{i}] is missing required field 'coords'")
                    else:
                        coords = neutral['coords']
                        if not isinstance(coords, list) or len(coords) != 3:
                            errors.append(f"neutrals[{i}].coords must be an array with exactly 3 numbers")
                        elif not all(isinstance(x, (int, float)) for x in coords):
                            errors.append(f"neutrals[{i}].coords must contain only numbers")
                    
                    if 'label' not in neutral:
                        errors.append(f"neutrals[{i}] is missing required field 'label'")
                    elif not isinstance(neutral['label'], str):
                        errors.append(f"neutrals[{i}].label must be a string")
                    
                    # Optional fields
                    if 'type' in neutral and neutral['type'] not in [None, 'neutral']:
                        errors.append(f"neutrals[{i}].type must be 'neutral' if specified")
                    
                    if 'label_offset' in neutral:
                        offset = neutral['label_offset']
                        if not isinstance(offset, list) or len(offset) != 3:
                            errors.append(f"neutrals[{i}].label_offset must be an array with exactly 3 numbers")
                        elif not all(isinstance(x, (int, float)) for x in offset):
                            errors.append(f"neutrals[{i}].label_offset must contain only numbers")
                    
                    if 'z_index' in neutral:
                        if not isinstance(neutral['z_index'], int):
                            errors.append(f"neutrals[{i}].z_index must be an integer")
        
        # Validate moral_actions
        if 'moral_actions' in config:
            if not isinstance(config['moral_actions'], list):
                errors.append("'moral_actions' must be an array")
            else:
                for i, action in enumerate(config['moral_actions']):
                    if not isinstance(action, dict):
                        errors.append(f"moral_actions[{i}] must be an object")
                        continue
                    
                    # Required fields
                    if 'source' not in action:
                        errors.append(f"moral_actions[{i}] is missing required field 'source'")
                    elif not isinstance(action['source'], str):
                        errors.append(f"moral_actions[{i}].source must be a string")
                    
                    if 'target' not in action:
                        errors.append(f"moral_actions[{i}] is missing required field 'target'")
                    elif not isinstance(action['target'], str):
                        errors.append(f"moral_actions[{i}].target must be a string")
                    
                    if 'label' not in action:
                        errors.append(f"moral_actions[{i}] is missing required field 'label'")
                    elif not isinstance(action['label'], str):
                        errors.append(f"moral_actions[{i}].label must be a string")
                    
                    # Optional z_index
                    if 'z_index' in action:
                        if not isinstance(action['z_index'], int):
                            errors.append(f"moral_actions[{i}].z_index must be an integer")
                    
                    # Optional style attributes
                    if 'color' in action and not isinstance(action['color'], str):
                        errors.append(f"moral_actions[{i}].color must be a string")
                    
                    if 'linewidth' in action:
                        if not isinstance(action['linewidth'], (int, float)):
                            errors.append(f"moral_actions[{i}].linewidth must be a number")
                        elif action['linewidth'] <= 0:
                            errors.append(f"moral_actions[{i}].linewidth must be positive")
                    
                    if 'linestyle' in action:
                        valid_linestyles = ['-', '--', '-.', ':', 'solid', 'dashed', 'dashdot', 'dotted']
                        if not isinstance(action['linestyle'], str):
                            errors.append(f"moral_actions[{i}].linestyle must be a string")
                        elif action['linestyle'] not in valid_linestyles:
                            errors.append(f"moral_actions[{i}].linestyle must be one of {valid_linestyles}")
                    
                    if 'alpha' in action:
                        if not isinstance(action['alpha'], (int, float)):
                            errors.append(f"moral_actions[{i}].alpha must be a number")
                        elif not (0 <= action['alpha'] <= 1):
                            errors.append(f"moral_actions[{i}].alpha must be between 0 and 1")
        
        # Validate render section
        if 'render' in config:
            render = config['render']
            if not isinstance(render, dict):
                errors.append("'render' must be an object")
            else:
                # Required fields
                if 'output_file' not in render:
                    errors.append("'render' is missing required field 'output_file'")
                elif not isinstance(render['output_file'], str):
                    errors.append("'render.output_file' must be a string")
                
                # Optional dpi
                if 'dpi' in render:
                    dpi = render['dpi']
                    # Accept int, float, or string that can be converted
                    try:
                        if isinstance(dpi, bool):
                            errors.append(f"'render.dpi' must be an integer (got boolean: {dpi})")
                        else:
                            dpi_val = int(dpi)
                            if dpi_val < 72:
                                errors.append(f"'render.dpi' must be at least 72 (got {dpi_val})")
                    except (ValueError, TypeError) as e:
                        errors.append(f"'render.dpi' must be an integer (got {type(dpi).__name__}: {dpi!r})")
                
                # Validate view section
                if 'view' not in render:
                    errors.append("'render' is missing required field 'view'")
                elif not isinstance(render['view'], dict):
                    errors.append("'render.view' must be an object")
                else:
                    view = render['view']
                    
                    # Required elevation
                    if 'elevation' not in view:
                        errors.append("'render.view' is missing required field 'elevation'")
                    else:
                        elevation = view['elevation']
                        # Accept int, float, or string that can be converted
                        try:
                            if isinstance(elevation, bool):
                                errors.append(f"'render.view.elevation' must be a number (got boolean: {elevation})")
                            else:
                                elev_val = float(elevation)
                                if not (0 <= elev_val <= 90):
                                    errors.append(f"'render.view.elevation' must be between 0 and 90 (got {elev_val})")
                        except (ValueError, TypeError) as e:
                            errors.append(f"'render.view.elevation' must be a number (got {type(elevation).__name__}: {elevation!r})")
                    
                    # Required azimuth
                    if 'azimuth' not in view:
                        errors.append("'render.view' is missing required field 'azimuth'")
                    else:
                        azimuth = view['azimuth']
                        # Accept int, float, or string that can be converted
                        try:
                            if isinstance(azimuth, bool):
                                errors.append(f"'render.view.azimuth' must be a number (got boolean: {azimuth})")
                            else:
                                azim_val = float(azimuth)
                                if not (0 <= azim_val <= 360):
                                    errors.append(f"'render.view.azimuth' must be between 0 and 360 (got {azim_val})")
                        except (ValueError, TypeError) as e:
                            errors.append(f"'render.view.azimuth' must be a number (got {type(azimuth).__name__}: {azimuth!r})")
        
        # Raise error if any validation errors occurred
        if errors:
            error_msg = "YAML schema validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
            raise ValueError(error_msg)
    
    def generate_landscape_image(self, config: dict) -> Optional[str]:
        """
        Generate a moral landscape image from YAML configuration.
        
        Args:
            config: Parsed YAML configuration
            
        Returns:
            Path to generated image or None if generation failed
        """
        try:
            # Extract configuration with defaults
            landscape_config = config.get('landscape', {})
            peaks_config = config.get('peaks', [])
            troughs_config = config.get('troughs', [])
            neutrals_config = config.get('neutrals', [])
            render_config = config.get('render', {})
            
            # Create landscape generator
            resolution = landscape_config.get('resolution', 100)
            landscape = MoralLandscape(resolution=resolution)
            
            # Prepare peaks, troughs, and neutrals
            peaks = [(p['coords'][0], p['coords'][1], p['coords'][2])
                    for p in peaks_config]
            troughs = [(t['coords'][0], t['coords'][1], t['coords'][2])
                      for t in troughs_config]
            neutrals = [(n['coords'][0], n['coords'][1], n['coords'][2])
                       for n in neutrals_config]
            
            # Generate landscape
            x_range = landscape_config.get('x_range', [-5, 5])
            y_range = landscape_config.get('y_range', [-5, 5])
            noise_level = landscape_config.get('noise_level', 0.1)
            
            X, Y, Z = landscape.generate_landscape(
                x_range=tuple(x_range),
                y_range=tuple(y_range),
                peaks=peaks if peaks else None,
                troughs=troughs if troughs else None,
                neutrals=neutrals if neutrals else None,
                noise_level=noise_level
            )
            
            # Plot configuration
            title = landscape_config.get('title', 'Moral Landscape')
            axes = landscape_config.get('axes', {})
            xlabel = axes.get('xlabel', 'Action Dimension 1')
            ylabel = axes.get('ylabel', 'Action Dimension 2')
            zlabel = axes.get('zlabel', 'Moral Value')
            
            style = landscape_config.get('style', {})
            colormap = style.get('colormap', 'viridis')
            figsize = tuple(style.get('figsize', [12, 9]))
            
            landscape.plot_landscape(
                X, Y, Z,
                title=title,
                xlabel=xlabel,
                ylabel=ylabel,
                zlabel=zlabel,
                colormap=colormap,
                figsize=figsize
            )
            
            # Add labels for peaks
            for peak in peaks_config:
                coords = peak['coords']
                label = peak['label']
                label_offset = peak.get('label_offset')
                z_index = peak.get('z_index')
                
                if label_offset:
                    # label_offset is treated as relative offset from the point
                    label_position = (
                        coords[0] + label_offset[0],
                        coords[1] + label_offset[1],
                        coords[2] + label_offset[2]
                    )
                else:
                    label_position = None
                
                landscape.add_label(
                    coords[0], coords[1], coords[2],
                    label,
                    label_type='peak',
                    label_position=label_position,
                    z_index=z_index
                )
            
            # Add labels for troughs
            for trough in troughs_config:
                coords = trough['coords']
                label = trough['label']
                label_offset = trough.get('label_offset')
                z_index = trough.get('z_index')
                
                # For troughs, the z-coordinate should be negative to represent the low point
                trough_z = -coords[2]
                
                if label_offset:
                    # label_offset is treated as relative offset from the point
                    label_position = (
                        coords[0] + label_offset[0],
                        coords[1] + label_offset[1],
                        trough_z + label_offset[2]
                    )
                else:
                    label_position = None
                
                landscape.add_label(
                    coords[0], coords[1], trough_z,
                    label,
                    label_type='trough',
                    label_position=label_position,
                    z_index=z_index
                )
            
            # Add labels for neutrals
            for neutral in neutrals_config:
                coords = neutral['coords']
                label = neutral['label']
                label_offset = neutral.get('label_offset')
                z_index = neutral.get('z_index')
                
                if label_offset:
                    # label_offset is treated as relative offset from the point
                    label_position = (
                        coords[0] + label_offset[0],
                        coords[1] + label_offset[1],
                        coords[2] + label_offset[2]
                    )
                else:
                    label_position = None
                
                landscape.add_label(
                    coords[0], coords[1], coords[2],
                    label,
                    label_type='neutral',
                    label_position=label_position,
                    z_index=z_index
                )
            
            # Process moral actions (arrows between points)
            moral_actions_config = config.get('moral_actions', [])
            if moral_actions_config:
                # Build a lookup dictionary for point labels to their coordinates
                point_lookup = {}
                
                # Add peaks to lookup
                for peak in peaks_config:
                    label = peak['label']
                    coords = peak['coords']
                    point_lookup[label] = (coords[0], coords[1], coords[2])
                
                # Add troughs to lookup (with negated z)
                for trough in troughs_config:
                    label = trough['label']
                    coords = trough['coords']
                    point_lookup[label] = (coords[0], coords[1], -coords[2])
                
                # Add neutrals to lookup
                for neutral in neutrals_config:
                    label = neutral['label']
                    coords = neutral['coords']
                    point_lookup[label] = (coords[0], coords[1], coords[2])
                
                # Draw action arrows
                for action in moral_actions_config:
                    source_label = action['source']
                    target_label = action['target']
                    action_label = action['label']
                    z_index = action.get('z_index')
                    
                    # Extract optional style attributes
                    color = action.get('color')
                    linewidth = action.get('linewidth')
                    linestyle = action.get('linestyle')
                    alpha = action.get('alpha')
                    
                    # Look up coordinates
                    if source_label not in point_lookup:
                        print(f"Warning: Source point '{source_label}' not found for action '{action_label}'")
                        continue
                    
                    if target_label not in point_lookup:
                        print(f"Warning: Target point '{target_label}' not found for action '{action_label}'")
                        continue
                    
                    source_coords = point_lookup[source_label]
                    target_coords = point_lookup[target_label]
                    
                    landscape.add_action_arrow(
                        source_coords,
                        target_coords,
                        action_label,
                        z_index=z_index,
                        color=color,
                        linewidth=linewidth,
                        linestyle=linestyle,
                        alpha=alpha
                    )
            
            # Set view angle
            view = render_config.get('view', {})
            elevation = view.get('elevation', 25)
            azimuth = view.get('azimuth', 45)
            
            # Ensure elevation and azimuth are numeric
            if isinstance(elevation, str):
                try:
                    elevation = float(elevation)
                except ValueError:
                    elevation = 25
            
            if isinstance(azimuth, str):
                try:
                    azimuth = float(azimuth)
                except ValueError:
                    azimuth = 45
            
            landscape.ax.view_init(elev=elevation, azim=azimuth)
            
            # Save image
            output_file = render_config['output_file']
            output_path = self.images_dir / output_file
            dpi = render_config.get('dpi', 300)
            
            # Ensure dpi is an integer
            if isinstance(dpi, (list, tuple)):
                dpi = dpi[0] if dpi else 300
            
            # Handle string values (from documentation/spec files)
            if isinstance(dpi, str):
                try:
                    dpi = int(dpi)
                except ValueError:
                    dpi = 300  # Use default if string is not a valid number
            else:
                dpi = int(dpi)
            
            landscape.save(str(output_path), dpi=dpi)
            
            return str(output_path)
        
        except Exception as e:
            print(f"Error generating landscape: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def create_image_tag(self, image_path: str, alt_text: str) -> str:
        """
        Create a markdown image tag.
        
        Args:
            image_path: Path to the image (relative to markdown file)
            alt_text: Alt text for the image
            
        Returns:
            Markdown image tag
        """
        # Use just the filename for the alt text identifier
        return f"\n![{alt_text}]({image_path})\n"
    
    def process_file(self, file_path: Path) -> bool:
        """
        Process a single markdown file.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            True if file was modified, False otherwise
        """
        print(f"\nProcessing {file_path}...")
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Extract YAML blocks
        yaml_blocks = self.extract_yaml_blocks(content)
        
        if not yaml_blocks:
            print(f"  No YAML blocks found")
            return False
        
        print(f"  Found {len(yaml_blocks)} YAML block(s)")
        
        # Process blocks in reverse order to maintain positions
        modified = False
        for block_idx, (yaml_content, start_pos, end_pos, details_start_pos, details_end_pos) in enumerate(reversed(yaml_blocks)):
            # Parse YAML
            try:
                config = self.parse_yaml_config(yaml_content)
            except ValueError as e:
                # Calculate line number where the YAML block starts
                lines_before = content[:start_pos].count('\n')
                print(f"  ✗ YAML validation error in block at line {lines_before + 1}:")
                print(f"    File: {file_path}")
                for line in str(e).split('\n'):
                    print(f"    {line}")
                continue
            
            if not config:
                print(f"  Skipping invalid YAML block at position {start_pos}")
                continue
            
            output_file = config['render']['output_file']
            print(f"  Processing landscape: {output_file}")
            
            # Check if image tag already exists
            # Use the output_file as a unique identifier
            image_tag_pattern = rf'!\[{re.escape(output_file)}\]'
            
            # Determine search range for existing tag
            # If inside <details>, look before details_start_pos
            # Otherwise, look after end_pos
            if details_start_pos is not None:
                # Look for tag before the <details> block (within 500 chars)
                search_start = max(0, details_start_pos - 500)
                search_region = content[search_start:details_start_pos]
            else:
                # Look for tag after the yaml block
                search_region = content[end_pos:end_pos + 500]
            
            if re.search(image_tag_pattern, search_region):
                print(f"  Image tag already exists for {output_file}, regenerating image...")
                # Regenerate the image but don't add a new tag
                image_path = self.generate_landscape_image(config)
                if image_path:
                    print(f"  ✓ Regenerated: {image_path}")
                continue
            
            # Generate the image
            image_path = self.generate_landscape_image(config)
            
            if not image_path:
                print(f"  Failed to generate image for {output_file}")
                continue
            
            # Create relative path from markdown file to image
            rel_path = os.path.relpath(image_path, file_path.parent)
            rel_path = rel_path.replace('\\', '/')  # Use forward slashes for markdown
            
            # Create image tag using output_file as alt text (identifier)
            image_tag = self.create_image_tag(rel_path, output_file)
            
            # Determine where to insert the image tag
            if details_start_pos is not None:
                # Insert BEFORE the <details> tag
                insert_pos = details_start_pos
            else:
                # Insert AFTER the yaml block (legacy format)
                insert_pos = end_pos
            
            # Insert the image tag
            content = content[:insert_pos] + image_tag + content[insert_pos:]
            modified = True
            
            print(f"  ✓ Generated: {image_path}")
            print(f"  ✓ Added image tag at position {insert_pos}")
        
        # Write back if modified
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ File updated")
            return True
        
        return False
    
    def cleanup_orphaned_images(self, referenced_images: Set[str]) -> int:
        """
        Delete images in the images directory that are not referenced by any markdown file.
        
        Args:
            referenced_images: Set of image filenames that are referenced
            
        Returns:
            Number of images deleted
        """
        if not self.images_dir.exists():
            return 0
        
        deleted_count = 0
        
        # Get all PNG files in the images directory
        for image_file in self.images_dir.glob("*.png"):
            filename = image_file.name
            
            if filename not in referenced_images:
                print(f"  Deleting orphaned image: {filename}")
                image_file.unlink()
                deleted_count += 1
        
        return deleted_count
    
    def process_all(self, root_dir: str = ".") -> None:
        """
        Process all markdown files in the directory tree.
        
        Args:
            root_dir: Root directory to search
        """
        md_files = self.find_markdown_files(root_dir)
        
        if not md_files:
            print("No markdown files found")
            return
        
        print(f"Found {len(md_files)} markdown file(s)")
        
        modified_count = 0
        referenced_images: Set[str] = set()
        
        for md_file in md_files:
            # Track referenced images from this file
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            yaml_blocks = self.extract_yaml_blocks(content)
            for yaml_content, start_pos, *_ in yaml_blocks:
                try:
                    config = self.parse_yaml_config(yaml_content)
                    if config and 'render' in config and 'output_file' in config['render']:
                        referenced_images.add(config['render']['output_file'])
                except ValueError as e:
                    # Skip YAML blocks with validation errors (likely spec/documentation files)
                    lines_before = content[:start_pos].count('\n')
                    print(f"\n  Skipping YAML block in {md_file} at line {lines_before + 1}:")
                    print(f"    Reason: Contains type placeholders (documentation/spec file)")
                    continue
            
            # Process the file
            if self.process_file(md_file):
                modified_count += 1
        
        # Cleanup orphaned images
        print(f"\n{'='*50}")
        print("Checking for orphaned images...")
        deleted_count = self.cleanup_orphaned_images(referenced_images)
        
        if deleted_count > 0:
            print(f"Deleted {deleted_count} orphaned image(s)")
        else:
            print("No orphaned images found")
        
        print(f"\n{'='*50}")
        print(f"Processing complete!")
        print(f"Modified {modified_count} file(s)")
        print(f"{'='*50}")


class MoralLandscapeEditor:
    """Interactive editor for YAML moral landscape configurations."""
    
    def __init__(self, processor: MoralLandscapeProcessor):
        """
        Initialize the editor.
        
        Args:
            processor: MoralLandscapeProcessor instance for reusing functionality
        """
        self.processor = processor
        self.root = tk.Tk()
        self.root.title("Moral Landscape Editor")
        self.root.geometry("1400x800")
        
        self.current_file: Optional[Path] = None
        self.current_content: str = ""
        self.yaml_blocks: List[Tuple[str, int, int, Optional[int], Optional[int]]] = []
        self.current_block_index: int = -1
        self.debounce_timer: Optional[threading.Timer] = None
        self.preview_image_path: Optional[str] = None
        
        self._setup_ui()
        self._setup_close_handler()
        
    def _setup_ui(self):
        """Set up the user interface."""
        # Top toolbar
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Select Markdown File",
                   command=self._select_file).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(toolbar, text="YAML Block:").pack(side=tk.LEFT, padx=5)
        
        self.block_selector = ttk.Combobox(toolbar, state='readonly', width=50)
        self.block_selector.pack(side=tk.LEFT, padx=5)
        self.block_selector.bind('<<ComboboxSelected>>', self._on_block_selected)
        
        ttk.Button(toolbar, text="Save to Markdown",
                   command=self._save_to_markdown).pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(toolbar, text="No file selected")
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Main content area
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left pane - YAML editor
        left_frame = ttk.LabelFrame(content_frame, text="YAML Editor")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.yaml_editor = scrolledtext.ScrolledText(
            left_frame,
            wrap=tk.NONE,
            font=('Consolas', 10),
            undo=True,
            maxundo=-1
        )
        self.yaml_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.yaml_editor.bind('<<Modified>>', self._on_yaml_modified)
        
        # Right pane - Preview
        right_frame = ttk.LabelFrame(content_frame, text="Preview")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # Preview canvas with scrollbars
        preview_container = ttk.Frame(right_frame)
        preview_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        v_scrollbar = ttk.Scrollbar(preview_container, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scrollbar = ttk.Scrollbar(preview_container, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.preview_canvas = tk.Canvas(
            preview_container,
            bg='white',
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        self.preview_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        v_scrollbar.config(command=self.preview_canvas.yview)
        h_scrollbar.config(command=self.preview_canvas.xview)
        
        self.preview_label = ttk.Label(right_frame, text="No preview available")
        
    def _select_file(self):
        """Open file dialog to select a markdown file."""
        file_path = filedialog.askopenfilename(
            title="Select Markdown File",
            initialdir=".",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        self.current_file = Path(file_path)
        self._load_file()
        
    def _load_file(self):
        """Load the selected markdown file and extract YAML blocks."""
        if not self.current_file:
            return
        
        try:
            with open(self.current_file, 'r', encoding='utf-8') as f:
                self.current_content = f.read()
            
            self.yaml_blocks = self.processor.extract_yaml_blocks(self.current_content)
            
            if not self.yaml_blocks:
                messagebox.showwarning("No YAML Blocks",
                                      "No YAML blocks found in the selected file.")
                self.status_label.config(text="No YAML blocks found")
                return
            
            # Populate the dropdown
            block_options = []
            for i, (yaml_content, start_pos, *_) in enumerate(self.yaml_blocks):
                config = self.processor.parse_yaml_config(yaml_content)
                if config:
                    output_file = config.get('render', {}).get('output_file', f'Block {i+1}')
                    title = config.get('landscape', {}).get('title', '')
                    label = f"{i+1}: {output_file}"
                    if title:
                        label += f" - {title}"
                    block_options.append(label)
                else:
                    block_options.append(f"{i+1}: Invalid YAML at position {start_pos}")
            
            self.block_selector['values'] = block_options
            
            if block_options:
                self.block_selector.current(0)
                self._on_block_selected(None)
            
            self.status_label.config(
                text=f"Loaded: {self.current_file.name} ({len(self.yaml_blocks)} blocks)"
            )
            
        except Exception as e:
            messagebox.showerror("Error Loading File", str(e))
            
    def _on_block_selected(self, event):
        """Handle YAML block selection from dropdown."""
        selected_index = self.block_selector.current()
        
        if selected_index < 0 or selected_index >= len(self.yaml_blocks):
            return
        
        self.current_block_index = selected_index
        yaml_content = self.yaml_blocks[selected_index][0]
        
        # Update editor
        self.yaml_editor.delete('1.0', tk.END)
        self.yaml_editor.insert('1.0', yaml_content)
        self.yaml_editor.edit_reset()  # Reset undo stack
        
        # Generate initial preview
        self._update_preview()
        
    def _on_yaml_modified(self, event):
        """Handle YAML editor modifications with debouncing."""
        if not self.yaml_editor.edit_modified():
            return
        
        self.yaml_editor.edit_modified(False)
        
        # Cancel previous timer
        if self.debounce_timer:
            self.debounce_timer.cancel()
        
        # Start new timer (debounce for 1 second)
        self.debounce_timer = threading.Timer(1.0, self._update_preview)
        self.debounce_timer.start()
        
    def _update_preview(self):
        """Generate and display preview of the current YAML configuration."""
        yaml_content = self.yaml_editor.get('1.0', tk.END).strip()
        
        if not yaml_content:
            return
        
        # Parse YAML
        config = self.processor.parse_yaml_config(yaml_content)
        
        if not config:
            # Clear preview and show error
            self.root.after(0, lambda: self._show_preview_error("Invalid YAML configuration"))
            return
        
        # Generate preview image
        try:
            image_path = self.processor.generate_landscape_image(config)
            
            if image_path:
                self.preview_image_path = image_path
                self.root.after(0, lambda: self._display_preview(image_path))
            else:
                self.root.after(0, lambda: self._show_preview_error("Failed to generate image"))
                
        except Exception as e:
            self.root.after(0, lambda: self._show_preview_error(f"Error: {str(e)}"))
            
    def _display_preview(self, image_path: str):
        """Display the preview image on the canvas."""
        try:
            # Load image
            img = Image.open(image_path)
            
            # Resize if too large (keep aspect ratio)
            max_width = 800
            max_height = 600
            
            width, height = img.size
            ratio = min(max_width / width, max_height / height)
            
            if ratio < 1:
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Update canvas
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            self.preview_canvas.image = photo  # Keep reference
            
            # Update scroll region
            self.preview_canvas.config(scrollregion=self.preview_canvas.bbox("all"))
            
        except Exception as e:
            self._show_preview_error(f"Error displaying image: {str(e)}")
            
    def _show_preview_error(self, message: str):
        """Show error message in preview area."""
        self.preview_canvas.delete("all")
        self.preview_canvas.create_text(
            200, 100,
            text=message,
            fill='red',
            font=('Arial', 12)
        )
        
    def _save_to_markdown(self):
        """Save the edited YAML back to the markdown file."""
        if self.current_block_index < 0 or not self.current_file:
            messagebox.showwarning("No Selection", "Please select a YAML block to save.")
            return
        
        yaml_content = self.yaml_editor.get('1.0', tk.END).strip()
        
        # Validate YAML
        config = self.processor.parse_yaml_config(yaml_content)
        if not config:
            if not messagebox.askyesno("Invalid YAML",
                                       "The YAML appears to be invalid. Save anyway?"):
                return
        
        try:
            # Get the block positions
            _, start_pos, end_pos, details_start, details_end = self.yaml_blocks[self.current_block_index]
            
            # Find the actual YAML content positions (within the ```yaml markers)
            yaml_pattern = r'```yaml moralgraph\s*\n(.*?)\n```'
            match = re.search(yaml_pattern, self.current_content[start_pos:end_pos], re.DOTALL)
            
            if not match:
                messagebox.showerror("Error", "Could not find YAML block in file.")
                return
            
            # Calculate positions in original content
            yaml_start = start_pos + match.start(1)
            yaml_end = start_pos + match.end(1)
            
            # Replace the YAML content
            new_content = (
                self.current_content[:yaml_start] +
                yaml_content +
                self.current_content[yaml_end:]
            )
            
            # Write back to file
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # Reload the file to update positions
            self._load_file()
            
            messagebox.showinfo("Success", "YAML block saved to markdown file.")
            
        except Exception as e:
            messagebox.showerror("Error Saving", str(e))
            
    def _setup_close_handler(self):
        """Set up handler for window close event."""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _on_closing(self):
        """Handle window close event - cleanup and exit."""
        # Cancel any pending debounce timer
        if self.debounce_timer:
            self.debounce_timer.cancel()
            self.debounce_timer = None
        
        # Destroy the window
        self.root.destroy()
        
        # Exit the process
        sys.exit(0)
    
    def run(self):
        """Start the editor UI."""
        self.root.mainloop()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Process markdown files to generate moral landscape images."
    )
    parser.add_argument(
        '--editor',
        action='store_true',
        help='Launch interactive editor UI for editing YAML blocks'
    )
    
    args = parser.parse_args()
    
    processor = MoralLandscapeProcessor(images_dir="images")
    
    if args.editor:
        # Launch editor UI
        editor = MoralLandscapeEditor(processor)
        editor.run()
    else:
        # Run batch processing
        processor.process_all(".")


if __name__ == "__main__":
    main()
