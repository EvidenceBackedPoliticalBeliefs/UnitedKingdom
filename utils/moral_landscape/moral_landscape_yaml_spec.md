# YAML Specification for Moral Landscape Generator

## Overview

This specification defines a YAML syntax for creating moral landscapes more easily. The YAML format separates data (coordinates and labels) from code, making it simpler to create and modify landscapes.

## Design Principles

1. **Simplicity**: Focus on coordinates and labels only, as requested
2. **Clarity**: Human-readable structure that mirrors the conceptual model
3. **Flexibility**: Support for manual label positioning
4. **Static Rendering**: Enable generation of static images with specified viewpoint

---

## YAML Schema

### Top-Level Structure

```yaml
# Landscape metadata
landscape:
  title: "My Moral Landscape"
  resolution: 150
  x_range: [-5, 5]
  y_range: [-5, 5]
  noise_level: 0.2
  
  # Axis labels
  axes:
    xlabel: "Action Dimension 1"
    ylabel: "Action Dimension 2"
    zlabel: "Moral Value"
  
  # Visual styling
  style:
    colormap: "RdYlGn"
    figsize: [14, 10]

# Peaks in the landscape (moral highs)
peaks:
  - coords: [2, 2, 6]
    label: "Altruism"
    type: "peak"  # optional, defaults to "peak"
    label_offset: [1.5, 1.5, 2.5]  # optional manual positioning
  
  - coords: [-2, -2, 5]
    label: "Creative\nExpression"
  
  - coords: [0, 3, 4]
    label: "Education"
    label_offset: [0, 0, 0.8]

# Troughs in the landscape (moral lows)
troughs:
  - coords: [-3, 2, 4]
    label: "Harm"
    type: "trough"  # optional, defaults to "trough"
    label_offset: [0, 0, -0.8]
  
  - coords: [3, -2, 3]
    label: "Deception"

# Moral actions - arrows between points (optional)
moral_actions:
  - source: "Altruism"
    target: "Education"
    label: "Learn to help better"
    color: "green"
    linewidth: 2.0
    linestyle: "-"
  
  - source: "Deception"
    target: "Harm"
    label: "Escalation"
    z_index: 1
    color: "red"
    linewidth: 2.5
    linestyle: "--"
    alpha: 0.8

# Static image rendering configuration (optional)
render:
  output_file: "my_landscape.png"
  dpi: 300
  view:
    elevation: 25  # viewing angle elevation in degrees
    azimuth: 45    # viewing angle azimuth in degrees
```
![my_landscape.png](../images/my_landscape.png)


---

## Detailed Schema Components

### 1. Landscape Configuration

```yaml
landscape:
  title: string              # Title displayed on the plot
  resolution: integer        # Grid resolution (default: 100)
  x_range: [float, float]   # X-axis range (default: [-5, 5])
  y_range: [float, float]   # Y-axis range (default: [-5, 5])
  noise_level: float        # Random variation amount (default: 0.1)
  
  axes:
    xlabel: string          # X-axis label
    ylabel: string          # Y-axis label
    zlabel: string          # Z-axis label
  
  style:
    colormap: string        # Matplotlib colormap name
    figsize: [int, int]    # Figure size [width, height] in inches
```

### 2. Peaks (Moral Highs)

Each peak is a point of high moral value in the landscape.

```yaml
peaks:
  - coords: [x, y, height]      # Required: [x, y, z] coordinates
    label: string                # Required: Label text (supports \n for newlines)
    type: "peak"                 # Optional: Explicit type (default: "peak")
    label_offset: [dx, dy, dz]  # Optional: Relative offset from point coordinates
```

**Coordinates Explained:**
- `x`: Position on the X-axis
- `y`: Position on the Y-axis
- `height`: The "moral value" height (Z-axis). Higher = better wellbeing

**Label Offset:**
- If not specified, auto-calculated as a relative offset `[+1.5, +1.5, +2.5]` from the point
- If specified, the offset is **added to the point coordinates** to determine final label position
  - Example: Point at `[2, 2, 6]` with `label_offset: [1, 1, 3]` → Label at `[3, 3, 9]`
  - Common pattern: `[0, 0, 0.8]` places label slightly above the point in Z

### 3. Troughs (Moral Lows)

Each trough is a point of low moral value in the landscape.

```yaml
troughs:
  - coords: [x, y, depth]       # Required: [x, y, z] coordinates
    label: string                # Required: Label text
    type: "trough"               # Optional: Explicit type (default: "trough")
    label_offset: [dx, dy, dz]  # Optional: Manual label position
```

**Coordinates Explained:**
- `x`: Position on the X-axis
- `y`: Position on the Y-axis
- `depth`: The "moral value" depth (Z-axis). This value represents the magnitude of the trough

**Label Offset:**
- If not specified, auto-calculated as `[x+1.5, y+1.5, z-2.5]`
- Negative Z offset for troughs places label below the point

### 4. Moral Actions (Transition Arrows)

Moral actions represent arrows between points on the landscape, showing transitions, pathways, or relationships between moral states.

```yaml
moral_actions:
  - source: string               # Required: Label of source point (peak, trough, or neutral)
    target: string               # Required: Label of target point (peak, trough, or neutral)
    label: string                # Required: Description of the action/transition
    z_index: integer             # Optional: Rendering order (higher = in front)
    color: string                # Optional: Line color (e.g., 'red', '#FF0000', 'darkblue')
    linewidth: number            # Optional: Line thickness (positive number)
    linestyle: string            # Optional: Line style ('-', '--', '-.', ':', 'solid', 'dashed', 'dashdot', 'dotted')
    alpha: number                # Optional: Transparency (0.0 to 1.0, where 1.0 is fully opaque)
```

**Field Descriptions:**
- `source`: Must match the `label` field of an existing peak, trough, or neutral point
- `target`: Must match the `label` field of an existing peak, trough, or neutral point
- `label`: Text displayed on the arrow (supports \n for newlines)
- `z_index`: Optional rendering order (default: 0). Higher values appear in front.
- `color`: Optional line color. Accepts matplotlib color names, hex codes, or RGB tuples. Default: `darkblue`
- `linewidth`: Optional line thickness. Must be positive. Default: varies by implementation
- `linestyle`: Optional line pattern. Accepts short forms (`-`, `--`, `-.`, `:`) or long forms (`solid`, `dashed`, `dashdot`, `dotted`). Default: `--` (dashed)
- `alpha`: Optional transparency level. 0.0 = fully transparent, 1.0 = fully opaque. Default: 1.0

**Default Visual Style:**
- Color: Dark blue (`darkblue`)
- Line style: Dashed (`--`)
- Arrow style: Large prominent arrowhead
- Label background: Light yellow with blue border
- Label font: Italic, smaller than outcome labels

**Style Customization Examples:**

```yaml
# Emphasize a critical action with bold red line
moral_actions:
  - source: "Deception"
    target: "Harm"
    label: "Escalation"
    color: "red"
    linewidth: 3.0
    linestyle: "-"
    alpha: 0.8

# Subtle suggestion with light, dotted line
  - source: "Education"
    target: "Altruism"
    label: "Inspired to help"
    color: "lightblue"
    linewidth: 1.0
    linestyle: ":"
    alpha: 0.5

# Custom colored pathway
  - source: "Altruism"
    target: "Burnout"
    label: "Overextension"
    color: "#FFA500"  # Orange
    linewidth: 2.0
    linestyle: "-."
```

**Common Use Cases:**
- Decision pathways between moral states
- Consequences of actions (e.g., "Altruism" → "Burnout")
- Recommended or discouraged transitions
- Causal relationships between moral positions
- Different action types with distinct visual styles

### 5. Render Configuration (Static Images)

```yaml
render:
  output_file: string    # Required: Output filename (e.g., "landscape.png")
  dpi: integer          # Optional: Resolution in dots per inch (default: 300)
  view:
    elevation: float    # Required: Elevation angle in degrees (0-90)
    azimuth: float      # Required: Azimuth angle in degrees (0-360)
```
![string](../images/string)


**View Angles:**
- `elevation`: Vertical viewing angle (0 = looking from side, 90 = looking from top)
- `azimuth`: Horizontal rotation angle (0 = front, 90 = right side, etc.)

---

## Label Positioning Options

Labels are positioned using **relative offsets** from the point coordinates.

### How Label Offset Works

The `label_offset` values are **added to** the point coordinates:

```yaml
peaks:
  - coords: [2, 2, 6]
    label: "Altruism"
    label_offset: [1.5, 1.5, 2.5]  # Offset from point: final = [3.5, 3.5, 8.5]
```

**Final label position = [2 + 1.5, 2 + 1.5, 6 + 2.5] = [3.5, 3.5, 8.5]**

### Common Patterns

```yaml
# Place label directly above point (common for peaks)
label_offset: [0, 0, 2.0]  # Only Z offset

# Place label directly below point (common for troughs)
label_offset: [0, 0, -2.0]  # Negative Z offset

# Small offset for slight adjustment
label_offset: [0, 0, 0.8]  # Just above the point

# Diagonal offset to avoid overlap
label_offset: [2, 2, 1.5]  # Move label to upper-right
```

---

## Complete Example YAML Files

### Example 1: Utilitarian Landscape

```yaml
landscape:
  title: "Utilitarian Moral Landscape"
  resolution: 150
  x_range: [-5, 5]
  y_range: [-5, 5]
  noise_level: 0.15
  
  axes:
    xlabel: "Personal Actions →"
    ylabel: "Social Impact →"
    zlabel: "Total Wellbeing"
  
  style:
    colormap: "RdYlGn"
    figsize: [12, 9]

peaks:
  - coords: [2, 2, 6]
    label: "Altruism\nPeak"
    label_offset: [0, 0, 0.8]
  
  - coords: [-2, -2, 5]
    label: "Creative\nExpression"
    label_offset: [0, 0, 0.8]
  
  - coords: [0, 3, 4]
    label: "Education"
    label_offset: [0, 0, 0.6]

troughs:
  - coords: [-3, 2, 4]
    label: "Harm"
    label_offset: [0, 0, -0.8]
  
  - coords: [3, -2, 3]
    label: "Deception"
    label_offset: [0, 0, -0.6]

render:
  output_file: "utilitarian_landscape.png"
  dpi: 300
  view:
    elevation: 25
    azimuth: 45
```
![utilitarian_landscape.png](../images/utilitarian_landscape.png)


### Example 2: Civil War Moral Landscape

```yaml
landscape:
  title: "Moral Landscape: Human Wellbeing Across Civil War Era Scenarios"
  resolution: 150
  x_range: [-5, 5]
  y_range: [-5, 5]
  noise_level: 0.2
  
  axes:
    xlabel: "Theoretical Dimension 1 (all possible states)"
    ylabel: "Theoretical Dimension 2 (all possible states)"
    zlabel: "Total Human Wellbeing"
  
  style:
    colormap: "RdYlGn"
    figsize: [14, 10]

peaks:
  - coords: [-2, 3, 9]
    label: "Peaceful Abolition\n(No War)"
  
  - coords: [0, 2.5, 7]
    label: "Gradual Abolition\n(Compensated)"
  
  - coords: [2, 2, 6.5]
    label: "Civil War →\nAbolition"

troughs:
  - coords: [0, -3.5, 9]
    label: "Slavery\nContinues"
  
  - coords: [3, -2, 5]
    label: "Prolonged\nCivil War"
  
  - coords: [-3, -2, 4.5]
    label: "Failed\nReconstruction"

render:
  output_file: "civil_war_landscape.png"
  dpi: 300
  view:
    elevation: 25
    azimuth: 45
```
![civil_war_landscape.png](../images/civil_war_landscape.png)


### Example 3: Minimal Configuration

For simple use cases with defaults:

```yaml
landscape:
  title: "Simple Landscape"

peaks:
  - coords: [0, 0, 5]
    label: "Peak"

troughs:
  - coords: [2, 2, 3]
    label: "Trough"

render:
  output_file: "simple.png"
  view:
    elevation: 25
    azimuth: 45
```
![simple.png](../images/simple.png)


---

## Implementation Notes

### Default Values

When fields are omitted, use these defaults:

```python
DEFAULTS = {
    'landscape': {
        'resolution': 100,
        'x_range': [-5, 5],
        'y_range': [-5, 5],
        'noise_level': 0.1,
        'axes': {
            'xlabel': 'Action Dimension 1',
            'ylabel': 'Action Dimension 2',
            'zlabel': 'Moral Value'
        },
        'style': {
            'colormap': 'viridis',
            'figsize': [12, 9]
        }
    },
    'render': {
        'dpi': 300,
        'view': {
            'elevation': 25,
            'azimuth': 45
        }
    }
}
```

### Label Offset Behavior

The implementation uses **relative offsets** - the offset is added to point coordinates:

```python
if 'label_offset' in peak:
    # Calculate absolute position by adding offset to point coordinates
    label_position = (
        coords[0] + peak['label_offset'][0],
        coords[1] + peak['label_offset'][1],
        coords[2] + peak['label_offset'][2]
    )
else:
    # Auto-calculate with default offset
    label_position = None  # Let the generator use its default offset
```

This approach makes it intuitive to position labels relative to their points, which is more natural when manually positioning labels to avoid overlaps or improve readability.

### Static Rendering

When [`render`](moral_landscape_yaml_spec.md:121) section is present:
1. Generate the landscape
2. Set the view using [`ax.view_init()`](../utils/moral_landscape/moral_landscape_generator.py:123)
3. Save to file without showing interactive plot
4. Do NOT call `plt.show()`

---

## File Naming Convention

Suggested convention for YAML landscape files:

```
<name>_landscape.yaml
```

Examples:
- `utilitarian_landscape.yaml`
- `civil_war_landscape.yaml`
- `homeless_help_landscape.yaml`
- `virtue_ethics_landscape.yaml`

---

## Benefits of This Design

1. **Separation of Concerns**: Data (YAML) separate from logic (Python)
2. **Easy to Edit**: Non-programmers can create landscapes
3. **Version Control Friendly**: YAML diffs are readable
4. **Reusable**: Same landscape with different views/renders
5. **Type Safety**: Schema can be validated with tools like `pydantic`
6. **Documentation**: YAML serves as self-documenting configuration

---

## Alternative Coordinate Format

For those who prefer explicit naming:

```yaml
peaks:
  - x: 2
    y: 2
    z: 6
    label: "Altruism"
    label_x: 3.5
    label_y: 3.5
    label_z: 8.5
```

However, the array format `coords: [x, y, z]` is more concise and recommended.

---

## Multi-View Static Rendering

For generating multiple views from the same landscape:

```yaml
render:
  - output_file: "landscape_front.png"
    dpi: 300
    view:
      elevation: 25
      azimuth: 45
  
  - output_file: "landscape_top.png"
    dpi: 300
    view:
      elevation: 90
      azimuth: 0
  
  - output_file: "landscape_side.png"
    dpi: 300
    view:
      elevation: 0
      azimuth: 90
```

This allows batch generation of multiple viewpoints from a single YAML file.

---

## Validation Schema (JSON Schema Format)

For automated validation, a JSON Schema representation:

```json
{
  "type": "object",
  "required": ["landscape"],
  "properties": {
    "landscape": {
      "type": "object",
      "properties": {
        "title": {"type": "string"},
        "resolution": {"type": "integer", "minimum": 10},
        "x_range": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2},
        "y_range": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2},
        "noise_level": {"type": "number", "minimum": 0},
        "axes": {
          "type": "object",
          "properties": {
            "xlabel": {"type": "string"},
            "ylabel": {"type": "string"},
            "zlabel": {"type": "string"}
          }
        },
        "style": {
          "type": "object",
          "properties": {
            "colormap": {"type": "string"},
            "figsize": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2}
          }
        }
      }
    },
    "peaks": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["coords", "label"],
        "properties": {
          "coords": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
          "label": {"type": "string"},
          "type": {"type": "string", "enum": ["peak"]},
          "label_offset": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3}
        }
      }
    },
    "troughs": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["coords", "label"],
        "properties": {
          "coords": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3},
          "label": {"type": "string"},
          "type": {"type": "string", "enum": ["trough"]},
          "label_offset": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3}
        }
      }
    },
    "render": {
      "oneOf": [
        {
          "type": "object",
          "required": ["output_file", "view"],
          "properties": {
            "output_file": {"type": "string"},
            "dpi": {"type": "integer", "minimum": 72},
            "view": {
              "type": "object",
              "required": ["elevation", "azimuth"],
              "properties": {
                "elevation": {"type": "number", "minimum": 0, "maximum": 90},
                "azimuth": {"type": "number", "minimum": 0, "maximum": 360}
              }
            }
          }
        },
        {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["output_file", "view"],
            "properties": {
              "output_file": {"type": "string"},
              "dpi": {"type": "integer", "minimum": 72},
              "view": {
                "type": "object",
                "required": ["elevation", "azimuth"],
                "properties": {
                  "elevation": {"type": "number", "minimum": 0, "maximum": 90},
                  "azimuth": {"type": "number", "minimum": 0, "maximum": 360}
                }
              }
            }
          }
        }
      ]
    }
  }
}
```

---

## Summary

This YAML specification provides:

✅ **Coordinates and labels only** - Clean, focused data structure  
✅ **Manual label positioning** - Via `label_offset` field  
✅ **Static image rendering** - Via `render` section with viewpoint angles  
✅ **Simplicity** - Intuitive structure matching domain concepts  
✅ **Flexibility** - Optional fields with sensible defaults  
✅ **Extensibility** - Easy to add new features without breaking existing files

The design prioritizes ease of use while maintaining the full power of the underlying visualization system.
