"""
3D Moral Landscape Generator

A tool for creating 3D visualizations of moral landscapes for philosophical discussions.
Allows labeling of peaks (moral highs) and troughs (moral lows).
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from typing import List, Tuple, Optional


class MoralLandscape:
    """Generate and visualize 3D moral landscapes."""
    
    def __init__(self, resolution: int = 100):
        """
        Initialize the moral landscape generator.
        
        Args:
            resolution: Grid resolution for the landscape (higher = smoother)
        """
        self.resolution = resolution
        self.fig = None
        self.ax = None
        self.surface = None
        
    def generate_landscape(
        self,
        x_range: Tuple[float, float] = (-5, 5),
        y_range: Tuple[float, float] = (-5, 5),
        peaks: Optional[List[Tuple[float, float, float]]] = None,
        troughs: Optional[List[Tuple[float, float, float]]] = None,
        neutrals: Optional[List[Tuple[float, float, float]]] = None,
        noise_level: float = 0.0
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate a moral landscape with specified peaks, troughs, and neutral points.
        
        Args:
            x_range: Range for x-axis (e.g., different ethical dimensions)
            y_range: Range for y-axis (e.g., different scenarios)
            peaks: List of (x, y, height) tuples for moral peaks
            troughs: List of (x, y, depth) tuples for moral troughs
            neutrals: List of (x, y, height) tuples for neutral moral points
            noise_level: Amount of random variation to add
            
        Returns:
            Tuple of (X, Y, Z) arrays for plotting
        """
        # Create grid
        x = np.linspace(x_range[0], x_range[1], self.resolution)
        y = np.linspace(y_range[0], y_range[1], self.resolution)
        X, Y = np.meshgrid(x, y)
        
        # Initialize with base level
        Z = np.zeros_like(X)
        
        # Add peaks (Gaussian hills)
        if peaks is None:
            peaks = [(0, 0, 5)]  # Default peak at center
            
        for peak_x, peak_y, height in peaks:
            Z += height * np.exp(-((X - peak_x)**2 + (Y - peak_y)**2) / 2)
        
        # Add troughs (inverted Gaussians)
        if troughs is None:
            troughs = []
            
        for trough_x, trough_y, depth in troughs:
            Z -= depth * np.exp(-((X - trough_x)**2 + (Y - trough_y)**2) / 2)
        
        # Add neutral points (flat plateaus at given height)
        if neutrals is None:
            neutrals = []
            
        for neutral_x, neutral_y, height in neutrals:
            # Create a flatter Gaussian for neutral points
            Z += height * np.exp(-((X - neutral_x)**2 + (Y - neutral_y)**2) / 4)
        
        # Add some noise for realism
        if noise_level > 0:
            Z += noise_level * np.random.randn(*Z.shape)
        
        return X, Y, Z
    
    def plot_landscape(
        self,
        X: np.ndarray,
        Y: np.ndarray,
        Z: np.ndarray,
        title: str = "Moral Landscape",
        xlabel: str = "",
        ylabel: str = "",
        zlabel: str = "Relative Moral Value",
        colormap: str = "RdYlGn",
        figsize: Tuple[int, int] = (12, 9)
    ):
        """
        Create a 3D plot of the moral landscape.
        
        Args:
            X, Y, Z: Meshgrid arrays from generate_landscape
            title: Plot title
            xlabel, ylabel, zlabel: Axis labels
            colormap: Matplotlib colormap name
            figsize: Figure size in inches
        """
        self.fig = plt.figure(figsize=figsize)
        self.ax = self.fig.add_subplot(111, projection='3d', computed_zorder=False)
        
        # Plot surface
        self.surface = self.ax.plot_surface(
            X, Y, Z,
            cmap=colormap,
            alpha=0.8,
            edgecolor='none',
            antialiased=True,
            zorder=0  # Surface at base layer, labels can be above or below
        )
        
        # Labels and title
        
        self.ax.set_xlabel(xlabel, fontsize=10)
        self.ax.set_ylabel(ylabel, fontsize=10)
        self.ax.set_zlabel(zlabel, fontsize=10)
        self.ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Better viewing angle
        self.ax.view_init(elev=25, azim=45)
        
    def add_label(
        self,
        x: float,
        y: float,
        z: float,
        label: str,
        label_type: str = 'peak',
        label_position: Tuple[float, float, float] = None,
        z_index: Optional[int] = None,
        fontsize: int = 11
    ):
        """
        Add a text label with an arrow pointing to a specific point on the landscape.
        
        Args:
            x, y, z: Coordinates of the point to label
            label: Text to display
            label_type: 'peak', 'trough', or 'neutral' (affects color)
            label_position: Where to place the label text (if None, auto-calculated)
            z_index: Z-order for label rendering (higher values appear in front)
            fontsize: Font size for the label text (default: 11)
        """
        if self.ax is None:
            raise ValueError("Must call plot_landscape first")
        
        # Color based on type
        if label_type == 'peak':
            color = 'darkgreen'
            marker_color = 'lime'
        elif label_type == 'trough':
            color = 'darkred'
            marker_color = 'red'
        else:  # neutral
            color = 'darkorange'
            marker_color = 'yellow'
        
        # Calculate z-order for rendering
        # Base zorders: surface=0, markers=10, arrows=12, text=15
        # z_index multiplier allows fine control
        marker_zorder = 10 if z_index is None else 10 + (z_index * 5)
        text_zorder = 15 if z_index is None else 15 + (z_index * 5)
        arrow_zorder = 12 if z_index is None else 12 + (z_index * 5)
        
        # Add marker at the point
        self.ax.scatter([x], [y], [z], color=marker_color, s=150, marker='*',
                       edgecolors='black', linewidths=2, zorder=marker_zorder)
        
        # Auto-calculate label position if not provided
        if label_position is None:
            # Place label above peaks, below troughs, and to the side for neutrals
            if label_type == 'peak':
                label_position = (x, y, z + 2.5)
            elif label_type == 'trough':
                label_position = (x, y, z - 2.5)
            else:  # neutral
                label_position = (x + 1.5, y, z + 1.0)
        
        # Add text label with arrow
        self.ax.text(
            label_position[0],
            label_position[1],
            label_position[2],
            label,
            fontsize=fontsize,
            fontweight='bold',
            color='black',
            ha='center',
            va='center',
            bbox=dict(boxstyle='round,pad=0.6', facecolor='white',
                     edgecolor=color, linewidth=2.5, alpha=0.95),
            zorder=text_zorder
        )
        
        # Draw arrow from label to point
        from matplotlib.patches import FancyArrowPatch
        from mpl_toolkits.mplot3d import proj3d
        
        class Arrow3D(FancyArrowPatch):
            def __init__(self, xs, ys, zs, *args, **kwargs):
                super().__init__((0,0), (0,0), *args, **kwargs)
                self._verts3d = xs, ys, zs

            def do_3d_projection(self, renderer=None):
                xs3d, ys3d, zs3d = self._verts3d
                xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, self.axes.M)
                self.set_positions((xs[0],ys[0]),(xs[1],ys[1]))
                return np.min(zs)
        
        arrow = Arrow3D(
            [label_position[0], x],
            [label_position[1], y],
            [label_position[2], z],
            mutation_scale=20,
            lw=2,
            arrowstyle='-|>',
            color=color,
            zorder=arrow_zorder
        )
        self.ax.add_artist(arrow)
    
    def add_action_arrow(
        self,
        source_coords: Tuple[float, float, float],
        target_coords: Tuple[float, float, float],
        label: str,
        z_index: Optional[int] = None,
        color: Optional[str] = None,
        linewidth: Optional[float] = None,
        linestyle: Optional[str] = None,
        alpha: Optional[float] = None,
        fontsize: int = 10
    ):
        """
        Add an action arrow between two points on the landscape.
        
        Args:
            source_coords: (x, y, z) coordinates of the starting point
            target_coords: (x, y, z) coordinates of the ending point
            label: Text to display for this action
            z_index: Z-order for rendering (higher values appear in front)
            color: Line color (default: 'darkblue')
            linewidth: Line thickness (default: 2)
            linestyle: Line style (default: '--')
            alpha: Transparency level 0.0-1.0 (default: 1.0)
            fontsize: Font size for the label text (default: 10)
        """
        if self.ax is None:
            raise ValueError("Must call plot_landscape first")
        
        # Apply defaults for style parameters
        color = color if color is not None else 'darkblue'
        linewidth = linewidth if linewidth is not None else 2
        linestyle = linestyle if linestyle is not None else '--'
        alpha = alpha if alpha is not None else 1.0
        
        # Calculate z-order for rendering
        # Actions use a different base z-order to distinguish from labels
        arrow_zorder = 20 if z_index is None else 20 + (z_index * 5)
        text_zorder = 22 if z_index is None else 22 + (z_index * 5)
        
        # Draw arrow from source to target
        from matplotlib.patches import FancyArrowPatch
        from mpl_toolkits.mplot3d import proj3d
        
        class Arrow3D(FancyArrowPatch):
            def __init__(self, xs, ys, zs, *args, **kwargs):
                super().__init__((0,0), (0,0), *args, **kwargs)
                self._verts3d = xs, ys, zs

            def do_3d_projection(self, renderer=None):
                xs3d, ys3d, zs3d = self._verts3d
                xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, self.axes.M)
                self.set_positions((xs[0],ys[0]),(xs[1],ys[1]))
                return np.min(zs)
        
        # Action arrows with customizable styling
        arrow = Arrow3D(
            [source_coords[0], target_coords[0]],
            [source_coords[1], target_coords[1]],
            [source_coords[2], target_coords[2]],
            mutation_scale=25,
            lw=linewidth,
            arrowstyle='-|>',
            color=color,
            linestyle=linestyle,
            alpha=alpha,
            zorder=arrow_zorder
        )
        self.ax.add_artist(arrow)
        
        # Add label at midpoint of arrow
        mid_x = (source_coords[0] + target_coords[0]) / 2
        mid_y = (source_coords[1] + target_coords[1]) / 2
        mid_z = (source_coords[2] + target_coords[2]) / 2
        
        # Offset label slightly above the midpoint
        label_pos = (mid_x, mid_y, mid_z + 0.5)
        
        self.ax.text(
            label_pos[0],
            label_pos[1],
            label_pos[2],
            label,
            fontsize=fontsize,
            fontstyle='italic',
            color=color,
            ha='center',
            va='center',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow',
                     edgecolor=color, linewidth=2, alpha=alpha),
            zorder=text_zorder
        )
    
    def show(self):
        """Display the plot."""
        plt.tight_layout()
        plt.show()
    
    def save(self, filename: str, dpi: int = 300):
        """
        Save the plot to a file.
        
        Args:
            filename: Output filename
            dpi: Resolution in dots per inch
        """
        if self.fig is None:
            raise ValueError("Must create a plot first")
        plt.savefig(filename, dpi=dpi, bbox_inches='tight')
        print(f"Saved landscape to {filename}")


if __name__ == "__main__":
    print("3D Moral Landscape Generator")
    print("=" * 50)
    print("\nAvailable examples:")
    print("1. Utilitarian moral landscape")
    print("2. Virtue ethics landscape")
    print("3. Custom landscape")
    print("\nGenerating example landscapes...\n")
    
    # Run examples
    try:
        print("Creating utilitarian landscape...")
        example_utilitarian_landscape()
        
        print("\nCreating virtue ethics landscape...")
        example_virtue_ethics_landscape()
        
        print("\nCreating custom landscape...")
        example_custom_landscape()
        
        print("\n✓ All landscapes generated successfully!")
        print("You can now modify the code to create your own landscapes.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
