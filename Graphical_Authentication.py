import os
import sys
import json
import hashlib
import base64
from datetime import datetime
import logging
from typing import List, Tuple, Dict, Optional, Union
import math

import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageOps, ImageEnhance

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("graphical_auth.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("GraphicalAuth")

class Config:
    """Configuration settings for the application."""
    APP_TITLE = "Secure Graphical Authentication"
    USER_DATA_DIR = "user_data"
    USER_DATA_FILE = os.path.join(USER_DATA_DIR, "users.json")
    ASSETS_DIR = "assets"
    DEFAULT_IMAGE_PATH = os.path.join(ASSETS_DIR, "default_image.jpg")
    ICON_PATH = os.path.join(ASSETS_DIR, "icon.png")
    TOLERANCE_RADIUS = 20  # Pixel radius for click validation
    MAX_POINTS = 5  # Maximum number of points in a pattern
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    AUTH_ATTEMPTS_MAX = 3
    
    # UI Colors
    PRIMARY_COLOR = "#3498db"  # Blue
    SECONDARY_COLOR = "#2ecc71"  # Green
    ACCENT_COLOR = "#e74c3c"  # Red
    BG_COLOR = "#f5f5f5"  # Light Gray
    TEXT_COLOR = "#2c3e50"  # Dark Blue/Gray
    
    # UI Fonts
    TITLE_FONT = ("Helvetica", 16, "bold")
    HEADER_FONT = ("Helvetica", 14, "bold")
    NORMAL_FONT = ("Helvetica", 11)
    BUTTON_FONT = ("Helvetica", 10, "bold")


class ThemeManager:
    """Manages the application theme and styling."""
    
    @staticmethod
    def setup_theme(root):
        """
        Set up the application theme
        
        Args:
            root: The tkinter root window
        """
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')  # Use the 'clam' theme as base
        
        # Configure button style
        style.configure(
            'TButton',
            font=Config.BUTTON_FONT,
            background=Config.PRIMARY_COLOR,
            foreground='white',
            padding=(10, 5),
            borderwidth=0
        )
        style.map(
            'TButton',
            background=[('active', Config.PRIMARY_COLOR), ('pressed', '#2980b9')],
            foreground=[('active', 'white'), ('pressed', 'white')]
        )
        
        # Configure accent button style
        style.configure(
            'Accent.TButton',
            font=Config.BUTTON_FONT,
            background=Config.SECONDARY_COLOR,
            foreground='white',
            padding=(10, 5),
            borderwidth=0
        )
        style.map(
            'Accent.TButton',
            background=[('active', Config.SECONDARY_COLOR), ('pressed', '#27ae60')],
            foreground=[('active', 'white'), ('pressed', 'white')]
        )
        
        # Configure danger button style
        style.configure(
            'Danger.TButton',
            font=Config.BUTTON_FONT,
            background=Config.ACCENT_COLOR,
            foreground='white',
            padding=(10, 5),
            borderwidth=0
        )
        style.map(
            'Danger.TButton',
            background=[('active', Config.ACCENT_COLOR), ('pressed', '#c0392b')],
            foreground=[('active', 'white'), ('pressed', 'white')]
        )
        
        # Configure entry style
        style.configure(
            'TEntry',
            font=Config.NORMAL_FONT,
            padding=(5, 5)
        )
        
        # Configure label style
        style.configure(
            'TLabel',
            font=Config.NORMAL_FONT,
            background=Config.BG_COLOR,
            foreground=Config.TEXT_COLOR
        )
        
        # Configure frame style
        style.configure(
            'TFrame',
            background=Config.BG_COLOR
        )
        
        # Configure header label style
        style.configure(
            'Header.TLabel',
            font=Config.HEADER_FONT,
            background=Config.BG_COLOR,
            foreground=Config.TEXT_COLOR
        )
        
        # Configure title label style
        style.configure(
            'Title.TLabel',
            font=Config.TITLE_FONT,
            background=Config.BG_COLOR,
            foreground=Config.TEXT_COLOR
        )


class SecurityUtils:
    """Utilities for security operations."""
    
    @staticmethod
    def hash_points(points: List[Tuple[int, int]], salt: str = None) -> str:
        """
        Hash the pattern points with an optional salt
        
        Args:
            points: List of (x, y) coordinates
            salt: Optional salt for the hash
            
        Returns:
            String hash of the points
        """
        if salt is None:
            salt = SecurityUtils.generate_salt()
        
        # Convert points to string and add salt
        points_str = json.dumps(points) + salt
        # Create hash
        hash_obj = hashlib.sha256(points_str.encode())
        return hash_obj.hexdigest()
    
    @staticmethod
    def generate_salt() -> str:
        """Generate a random salt."""
        return base64.b64encode(os.urandom(16)).decode('utf-8')
    
    @staticmethod
    def validate_points(stored_points: List[Tuple[int, int]], 
                      input_points: List[Tuple[int, int]], 
                      tolerance: int = Config.TOLERANCE_RADIUS) -> bool:
        """
        Validate if input points match stored points within tolerance
        
        Args:
            stored_points: The reference points to validate against
            input_points: The points to validate
            tolerance: Radius in pixels to consider a match
            
        Returns:
            True if patterns match, False otherwise
        """
        if len(stored_points) != len(input_points):
            return False
        
        for i, stored_point in enumerate(stored_points):
            input_point = input_points[i]
            # Calculate Euclidean distance
            distance = ((stored_point[0] - input_point[0]) ** 2 + 
                        (stored_point[1] - input_point[1]) ** 2) ** 0.5
            if distance > tolerance:
                return False
        
        return True


class UserManager:
    """Manages user data and authentication."""
    
    def __init__(self, data_file: str = Config.USER_DATA_FILE):
        """
        Initialize the user manager
        
        Args:
            data_file: Path to user data file
        """
        self.data_file = data_file
        self.users_data = self._load_users_data()
        
    def _load_users_data(self) -> Dict:
        """Load user data from file or create default."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading user data: {e}")
                return {"users": {}}
        else:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            return {"users": {}}
    
    def _save_users_data(self) -> None:
        """Save user data to file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.users_data, f, indent=2)
        except IOError as e:
            logger.error(f"Error saving user data: {e}")
            messagebox.showerror("Error", "Failed to save user data.")
    
    def user_exists(self, username: str) -> bool:
        """Check if a user exists."""
        return username in self.users_data["users"]
    
    def register_user(self, username: str, points: List[Tuple[int, int]], 
                     image_path: str) -> bool:
        """
        Register a new user
        
        Args:
            username: User's username
            points: Points selected by user for authentication
            image_path: Path to the authentication image
            
        Returns:
            True if registration successful, False otherwise
        """
        if self.user_exists(username):
            logger.warning(f"User {username} already exists.")
            return False
        
        # Create salt and hash points
        salt = SecurityUtils.generate_salt()
        hashed_points = SecurityUtils.hash_points(points, salt)
        
        # Store user data
        self.users_data["users"][username] = {
            "hashed_points": hashed_points,
            "salt": salt,
            "image_path": image_path,
            "original_points": points,  # In a real system, we wouldn't store the original points
            "created_at": datetime.now().isoformat(),
            "last_login": None
        }
        
        self._save_users_data()
        logger.info(f"User {username} registered successfully.")
        return True
    
    def authenticate_user(self, username: str, input_points: List[Tuple[int, int]]) -> bool:
        """
        Authenticate a user
        
        Args:
            username: User's username
            input_points: Points selected by user for authentication
            
        Returns:
            True if authentication successful, False otherwise
        """
        if not self.user_exists(username):
            logger.warning(f"Authentication attempt for non-existent user: {username}")
            return False
        
        user_data = self.users_data["users"][username]
        result = SecurityUtils.validate_points(
            user_data["original_points"], 
            input_points
        )
        
        if result:
            # Update last login time
            self.users_data["users"][username]["last_login"] = datetime.now().isoformat()
            self._save_users_data()
            logger.info(f"User {username} authenticated successfully.")
        else:
            logger.warning(f"Authentication failed for user {username}.")
        
        return result
    
    def get_user_image_path(self, username: str) -> str:
        """Get the image path for a user."""
        if not self.user_exists(username):
            return Config.DEFAULT_IMAGE_PATH
        
        return self.users_data["users"][username]["image_path"]


class AnimatedCanvas(tk.Canvas):
    """Custom canvas with animation capabilities."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        
        # Animation properties
        self.animations = []
        self.is_animating = False
    
    def animate_point(self, x, y, color="#3498db", radius_start=5, radius_end=20, 
                     duration=500, callback=None):
        """
        Animate a point with a ripple effect
        
        Args:
            x: X coordinate
            y: Y coordinate
            color: Point color
            radius_start: Starting radius
            radius_end: Ending radius
            duration: Animation duration in milliseconds
            callback: Function to call when animation completes
        """
        start_time = datetime.now().timestamp() * 1000
        end_time = start_time + duration
        
        # Create initial circle
        circle_id = self.create_oval(
            x - radius_start, y - radius_start,
            x + radius_start, y + radius_start,
            outline=color, width=2, fill=""
        )
        
        animation = {
            "id": circle_id,
            "type": "ripple",
            "x": x,
            "y": y,
            "color": color,
            "radius_start": radius_start,
            "radius_end": radius_end,
            "start_time": start_time,
            "end_time": end_time,
            "callback": callback
        }
        
        self.animations.append(animation)
        
        if not self.is_animating:
            self.is_animating = True
            self._animate()
    
    def _animate(self):
        """Handle animation updates."""
        if not self.animations:
            self.is_animating = False
            return
        
        current_time = datetime.now().timestamp() * 1000
        completed_animations = []
        
        for anim in self.animations:
            progress = min(1.0, (current_time - anim["start_time"]) / 
                         (anim["end_time"] - anim["start_time"]))
            
            if anim["type"] == "ripple":
                radius = anim["radius_start"] + (anim["radius_end"] - anim["radius_start"]) * progress
                opacity = int(255 * (1 - progress))
                color = anim["color"]
                
                # Update circle
                self.coords(
                    anim["id"],
                    anim["x"] - radius, anim["y"] - radius,
                    anim["x"] + radius, anim["y"] + radius
                )
                
                # Update opacity
                if progress < 1.0:
                    alpha = format(opacity, '02x')
                    if len(color) == 7:  # #RRGGBB format
                        color_with_alpha = color + alpha
                    else:
                        color_with_alpha = color
                    self.itemconfig(anim["id"], outline=color_with_alpha)
            
            if progress >= 1.0:
                completed_animations.append(anim)
                self.delete(anim["id"])
                if anim["callback"]:
                    anim["callback"]()
        
        # Remove completed animations
        for anim in completed_animations:
            self.animations.remove(anim)
        
        # Continue animation loop
        if self.animations:
            self.after(16, self._animate)  # ~60fps
        else:
            self.is_animating = False


class AuthCanvas(AnimatedCanvas):
    """Custom canvas for graphical authentication."""
    
    def __init__(self, parent, **kwargs):
        """Initialize the authentication canvas."""
        super().__init__(parent, **kwargs)
        self.configure(bg="white", highlightthickness=1, highlightbackground="gray")
        
        self.image = None
        self.image_tk = None
        self.points = []
        self.point_markers = []
        self.image_path = ""
        self.image_item = None
        
        # Visual properties
        self.point_color = Config.PRIMARY_COLOR
        self.line_color = Config.SECONDARY_COLOR
        self.point_size = 6
        self.line_width = 2
        
        # Bind click event
        self.bind("<Button-1>", self.on_canvas_click)
        
        # Bind resize event
        self.bind("<Configure>", self.on_resize)
    
    def on_resize(self, event=None):
        """Handle canvas resize events."""
        if self.image_path and self.winfo_width() > 1 and self.winfo_height() > 1:
            self._reload_image()
    
    def _reload_image(self):
        """Reload and resize the current image."""
        if not self.image_path or not os.path.exists(self.image_path):
            return False
        
        try:
            # Save current points
            current_points = self.points.copy()
            
            # Clear canvas
            self.delete("all")
            self.point_markers = []
            
            # Load and resize image
            self.image = Image.open(self.image_path)
            
            # Calculate new size to fit in canvas while maintaining aspect ratio
            canvas_width = self.winfo_width()
            canvas_height = self.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = Config.WINDOW_WIDTH
                canvas_height = Config.WINDOW_HEIGHT
            
            width_ratio = canvas_width / self.image.width
            height_ratio = canvas_height / self.image.height
            ratio = min(width_ratio, height_ratio)
            
            new_width = int(self.image.width * ratio)
            new_height = int(self.image.height * ratio)
            
            self.image = self.image.resize((new_width, new_height), Image.LANCZOS)
            
            # Apply subtle enhancements
            enhancer = ImageEnhance.Contrast(self.image)
            self.image = enhancer.enhance(1.05)
            
            enhancer = ImageEnhance.Sharpness(self.image)
            self.image = enhancer.enhance(1.1)
            
            self.image_tk = ImageTk.PhotoImage(self.image)
            
            # Calculate position to center the image
            x_offset = (canvas_width - new_width) // 2
            y_offset = (canvas_height - new_height) // 2
            
            # Add image to canvas
            self.image_item = self.create_image(x_offset, y_offset, anchor=tk.NW, image=self.image_tk)
            
            # Restore points if any
            self.points = []
            for point in current_points:
                self.add_point(point[0], point[1], animate=False)
            
            return True
        except Exception as e:
            logger.error(f"Error reloading image: {e}")
            return False
    
    def load_image(self, image_path: str) -> bool:
        """
        Load an image into the canvas
        
        Args:
            image_path: Path to the image file
            
        Returns:
            True if image loaded successfully, False otherwise
        """
        if not os.path.exists(image_path):
            logger.error(f"Image path does not exist: {image_path}")
            return False
            
        try:
            # Clear canvas and points
            self.clear()
            
            # Store image path
            self.image_path = image_path
            
            # Load the image
            return self._reload_image()
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            messagebox.showerror("Error", f"Failed to load image: {e}")
            return False
    
    def on_canvas_click(self, event) -> None:
        """Handle click events on the canvas."""
        if len(self.points) >= Config.MAX_POINTS:
            messagebox.showinfo("Information", f"Maximum of {Config.MAX_POINTS} points reached.")
            return
        
        self.add_point(event.x, event.y, animate=True)
    
    def add_point(self, x, y, animate=True) -> None:
        """
        Add a point to the pattern
        
        Args:
            x: X coordinate
            y: Y coordinate
            animate: Whether to animate the addition
        """
        # Add point to list
        self.points.append((x, y))
        
        # Draw marker on canvas
        if animate:
            # Create the permanent point marker
            marker = self.create_oval(
                x - self.point_size, y - self.point_size,
                x + self.point_size, y + self.point_size,
                fill=self.point_color, outline="black", width=1
            )
            self.point_markers.append(marker)
            
            # Add sequence number
            text = self.create_text(
                x, y, text=str(len(self.points)),
                fill="white", font=("Helvetica", 9, "bold")
            )
            self.point_markers.append(text)
            
            # Draw line between consecutive points
            if len(self.points) > 1:
                x1, y1 = self.points[-2]
                x2, y2 = self.points[-1]
                line = self.create_line(
                    x1, y1, x2, y2,
                    fill=self.line_color, width=self.line_width, 
                    arrow=tk.LAST, arrowshape=(10, 12, 6)
                )
                self.point_markers.append(line)
            
            # Animate the point addition
            self.animate_point(
                x, y, color=self.point_color,
                radius_start=self.point_size, radius_end=30, 
                duration=500
            )
        else:
            # Create the permanent point marker without animation
            marker = self.create_oval(
                x - self.point_size, y - self.point_size,
                x + self.point_size, y + self.point_size,
                fill=self.point_color, outline="black", width=1
            )
            self.point_markers.append(marker)
            
            # Add sequence number
            text = self.create_text(
                x, y, text=str(len(self.points)),
                fill="white", font=("Helvetica", 9, "bold")
            )
            self.point_markers.append(text)
            
            # Draw line between consecutive points
            if len(self.points) > 1:
                x1, y1 = self.points[-2]
                x2, y2 = self.points[-1]
                line = self.create_line(
                    x1, y1, x2, y2,
                    fill=self.line_color, width=self.line_width, 
                    arrow=tk.LAST, arrowshape=(10, 12, 6)
                )
                self.point_markers.append(line)
    
    def clear(self) -> None:
        """Clear all points and markers from the canvas."""
        self.delete("all")
        self.points = []
        self.point_markers = []
        self.image_item = None
        
        # Reload the image if available
        if self.image_path:
            self._reload_image()
    
    def clear_points(self) -> None:
        """Clear only the points, keeping the image."""
        # Remove point markers
        for marker in self.point_markers:
            self.delete(marker)
        
        self.points = []
        self.point_markers = []
    
    def get_points(self) -> List[Tuple[int, int]]:
        """Get the list of selected points."""
        return self.points


class StatusBar(ttk.Frame):
    """Status bar for displaying application status."""
    
    def __init__(self, parent):
        """Initialize the status bar."""
        super().__init__(parent)
        self.configure(padding=(5, 2))
        
        # Status label
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_label = ttk.Label(self, textvariable=self.status_var)
        self.status_label.pack(side=tk.LEFT)
        
        # Version label
        version = "v1.0.0"
        self.version_label = ttk.Label(self, text=version)
        self.version_label.pack(side=tk.RIGHT)
    
    def set_status(self, text: str) -> None:
        """Set the status text."""
        self.status_var.set(text)


class ToolTip:
    """Create a tooltip for a given widget."""
    
    def __init__(self, widget, text):
        """Initialize the tooltip."""
        self.widget = widget
        self.text = text
        self.tooltip = None
        
        # Bind events
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        """Show the tooltip."""
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # Create tooltip window
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(
            self.tooltip, text=self.text, background="#ffffe0", 
            relief="solid", borderwidth=1, padding=(5, 2)
        )
        label.pack()
    
    def hide_tooltip(self, event=None):
        """Hide the tooltip."""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class GraphicalAuthenticationApp:
    """Main application class for the graphical authentication system."""
    
    def __init__(self, root):
        """
        Initialize the application
        
        Args:
            root: The tkinter root window
        """
        self.root = root
        self.root.title(Config.APP_TITLE)
        self.root.geometry(f"{Config.WINDOW_WIDTH}x{Config.WINDOW_HEIGHT}")
        self.root.minsize(600, 450)
        self.root.configure(bg=Config.BG_COLOR)
        
        # Set application icon if available
        if os.path.exists(Config.ICON_PATH):
            icon = tk.PhotoImage(file=Config.ICON_PATH)
            self.root.iconphoto(True, icon)
        
        # Set up theme
        ThemeManager.setup_theme(self.root)
        
        # Initialize components
        self.user_manager = UserManager()
        self.current_username = None
        self.auth_attempts = 0
        
        # Set up UI
        self._setup_ui()
        
        # Create default assets if needed
        self._create_default_assets()
        
        # Load default image
        if os.path.exists(Config.DEFAULT_IMAGE_PATH):
            self.auth_canvas.load_image(Config.DEFAULT_IMAGE_PATH)
    
    def _create_default_assets(self) -> None:
        """Create default assets if they don't exist."""
        # Create assets directory if it doesn't exist
        os.makedirs(Config.ASSETS_DIR, exist_ok=True)
        os.makedirs(Config.USER_DATA_DIR, exist_ok=True)
        
        # Create default image if it doesn't exist
        if not os.path.exists(Config.DEFAULT_IMAGE_PATH):
            try:
                # Create a nice default image with gradient background
                width, height = 400, 300
                image = Image.new('RGB', (width, height), color=(245, 245, 245))
                draw = ImageDraw.Draw(image)
                
                # Create a gradient background
                for y in range(height):
                    r = int(52 + (y / height) * (41 - 52))
                    g = int(152 + (y / height) * (128 - 152))
                    b = int(219 + (y / height) * (185 - 219))
                    for x in range(width):
                        draw.point((x, y), fill=(r, g, b))
                
                # Add a grid pattern
                for x in range(0, width, 20):
                    for y in range(0, height, 20):
                        draw.rectangle((x, y, x+1, y+1), fill=(255, 255, 255, 128))
                
                # Add a subtle blur
                image = image.filter(ImageFilter.GaussianBlur(radius=1))
                
                # Save the image
                image.save(Config.DEFAULT_IMAGE_PATH)
                logger.info(f"Created default image: {Config.DEFAULT_IMAGE_PATH}")
            except Exception as e:
                logger.error(f"Failed to create default image: {e}")
                
        # Create icon if it doesn't exist
        if not os.path.exists(Config.ICON_PATH):
            try:
                # Create a simple icon
                size = 64
                icon = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
                draw = ImageDraw.Draw(icon)
                
                # Draw a shield shape
                padding = 4
                draw.polygon([
                    (size//2, padding),  # Top
                    (size - padding, size//3),  # Right
                    (size//2, size - padding),  # Bottom
                    (padding, size//3)  # Left
                ], fill=Config.PRIMARY_COLOR)
                
                # Draw lock symbol
                lock_size = size//2
                lock_x = (size - lock_size)//2
                lock_y = (size - lock_size)//2 + 5
                
                # Lock body
                draw.rectangle(
                    (lock_x, lock_y + lock_size//3, 
                     lock_x + lock_size, lock_y + lock_size),
                    fill="#ffffff"
                )
                
                # Lock shackle
                shackle_width = lock_size//3
                draw.rectangle(
                    (lock_x + (lock_size - shackle_width)//2, lock_y,
                     lock_x + (lock_size + shackle_width)//2, lock_y + lock_size//2),
                    fill="#ffffff"
                )
                
                # Add points pattern suggestion
                point_radius = 2
                points = [
                    (lock_x + lock_size//4, lock_y + lock_size//1.5),
                    (lock_x + lock_size//2, lock_y + lock_size//2),
                    (lock_x + lock_size//1.5, lock_y + lock_size//1.8)
                ]
                
                for point in points:
                    draw.ellipse(
                        (point[0] - point_radius, point[1] - point_radius,
                         point[0] + point_radius, point[1] + point_radius),
                        fill=Config.SECONDARY_COLOR
                    )
                
                # Connect points with lines
                for i in range(len(points) - 1):
                    draw.line(
                        [points[i], points[i+1]], 
                        fill=Config.SECONDARY_COLOR, width=1
                    )
                
                # Save the icon
                icon.save(Config.ICON_PATH)
                logger.info(f"Created application icon: {Config.ICON_PATH}")
            except Exception as e:
                logger.error(f"Failed to create application icon: {e}")
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        # Main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title frame
        self.title_frame = ttk.Frame(self.main_frame)
        self.title_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.title_label = ttk.Label(
            self.title_frame, text=Config.APP_TITLE, style="Title.TLabel"
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Username frame
        self.username_frame = ttk.Frame(self.main_frame)
        self.username_frame.pack(fill=tk.X, pady=5)
        # Username entry section
        self.username_label = ttk.Label(self.username_frame, text="Username:")
        self.username_label.pack(side=tk.LEFT, padx=5)
        
        self.username_entry = ttk.Entry(self.username_frame, width=20, font=Config.NORMAL_FONT)
        self.username_entry.pack(side=tk.LEFT, padx=5)
        
        # User action buttons
        self.login_btn = ttk.Button(
            self.username_frame, text="Login",
            command=self.login, style="Accent.TButton"
        )
        self.login_btn.pack(side=tk.RIGHT, padx=5)
        
        self.register_btn = ttk.Button(
            self.username_frame, text="Register",
            command=self.register
        )
        self.register_btn.pack(side=tk.RIGHT, padx=5)
        
        # Instructions frame
        self.instructions_frame = ttk.Frame(self.main_frame)
        self.instructions_frame.pack(fill=tk.X, pady=5)
        
        self.instructions_label = ttk.Label(
            self.instructions_frame,
            text="Select points on the image to create your authentication pattern.",
            wraplength=Config.WINDOW_WIDTH - 40
        )
        self.instructions_label.pack(side=tk.LEFT, padx=5)
        
        # Canvas frame with border
        self.canvas_frame = ttk.Frame(self.main_frame, borderwidth=2, relief=tk.GROOVE)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Auth canvas
        self.auth_canvas = AuthCanvas(
            self.canvas_frame,
            width=Config.WINDOW_WIDTH - 40,
            height=Config.WINDOW_HEIGHT - 200,
            bg="white"
        )
        self.auth_canvas.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Action buttons frame
        self.buttons_frame = ttk.Frame(self.main_frame)
        self.buttons_frame.pack(fill=tk.X, pady=5)
        
        # Create buttons
        self.select_image_btn = ttk.Button(
            self.buttons_frame, text="Select Image",
            command=self.select_image
        )
        self.select_image_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(
            self.buttons_frame, text="Clear Pattern",
            command=self.auth_canvas.clear_points
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Add tooltips
        ToolTip(self.register_btn, "Create a new account")
        ToolTip(self.login_btn, "Login with existing credentials")
        ToolTip(self.select_image_btn, "Choose a different authentication image")
        ToolTip(self.clear_btn, "Clear the current pattern")
        
        # Status bar
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Help button
        self.help_btn = ttk.Button(
            self.buttons_frame, text="Help",
            command=self.show_help
        )
        self.help_btn.pack(side=tk.RIGHT, padx=5)
        
        self.quit_btn = ttk.Button(
            self.buttons_frame, text="Quit",
            command=self.root.quit, style="Danger.TButton"
        )
        self.quit_btn.pack(side=tk.RIGHT, padx=5)
    
    def select_image(self) -> None:
        """Let the user select an image for authentication."""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.status_bar.set_status("Loading image...")
            if self.auth_canvas.load_image(file_path):
                logger.info(f"Image loaded: {file_path}")
                self.status_bar.set_status("Image loaded successfully")
            else:
                self.status_bar.set_status("Failed to load image")
    
    def register(self) -> None:
        """Register a new user."""
        username = self.username_entry.get().strip()
        points = self.auth_canvas.get_points()
        image_path = self.auth_canvas.image_path
        
        # Validate inputs
        if not username:
            messagebox.showerror("Error", "Please enter a username.")
            return
        
        if len(points) < 3:
            messagebox.showerror("Error", "Please select at least 3 points for security.")
            return
        
        if not image_path:
            messagebox.showerror("Error", "Please select an image.")
            return
        
        # Register user
        if self.user_manager.user_exists(username):
            messagebox.showerror("Error", "Username already exists. Please choose another.")
            return
        
        self.status_bar.set_status(f"Registering user {username}...")
        
        if self.user_manager.register_user(username, points, image_path):
            messagebox.showinfo("Success", "User registered successfully!")
            self.auth_canvas.clear_points()
            self.status_bar.set_status(f"User {username} registered successfully")
            
            # Show authentication success animation
            self._show_success_animation()
        else:
            messagebox.showerror("Error", "Failed to register user.")
            self.status_bar.set_status("Registration failed")
    
    def login(self) -> None:
        """Authenticate a user."""
        username = self.username_entry.get().strip()
        points = self.auth_canvas.get_points()
        
        # Validate inputs
        if not username:
            messagebox.showerror("Error", "Please enter a username.")
            return
        
        if not self.user_manager.user_exists(username):
            messagebox.showerror("Error", "User does not exist.")
            return
        
        # If this is a new login attempt, load the user's image
        if self.current_username != username:
            self.current_username = username
            self.auth_attempts = 0
            user_image = self.user_manager.get_user_image_path(username)
            
            self.status_bar.set_status(f"Loading {username}'s authentication image...")
            
            if not self.auth_canvas.load_image(user_image):
                messagebox.showerror("Error", "Failed to load user's image.")
                self.status_bar.set_status("Failed to load image")
                return
                
            messagebox.showinfo("Login", "Please recreate your authentication pattern.")
            self.instructions_label.config(
                text="Recreate your authentication pattern by selecting points in the correct order."
            )
            self.status_bar.set_status(f"Ready for authentication")
            return
        
        if not points:
            messagebox.showerror("Error", "Please select your authentication points.")
            return
        
        # Authenticate
        self.auth_attempts += 1
        self.status_bar.set_status(f"Authenticating {username}...")
        
        if self.user_manager.authenticate_user(username, points):
            messagebox.showinfo("Success", "Authentication successful!")
            self.current_username = None
            self.auth_attempts = 0
            self.auth_canvas.clear_points()
            self.instructions_label.config(
                text="Select points on the image to create your authentication pattern."
            )
            self.status_bar.set_status("Authentication successful")
            
            # Show authentication success animation
            self._show_success_animation()
            
            # In a real app, you would transition to the main application screen here
            # For demo purposes, we'll just reset the UI
            self.username_entry.delete(0, tk.END)
        else:
            if self.auth_attempts >= Config.AUTH_ATTEMPTS_MAX:
                messagebox.showerror(
                    "Error", 
                    f"Authentication failed. Maximum attempts ({Config.AUTH_ATTEMPTS_MAX}) reached."
                )
                self.current_username = None
                self.auth_attempts = 0
                self.auth_canvas.clear()
                self.instructions_label.config(
                    text="Select points on the image to create your authentication pattern."
                )
                self.status_bar.set_status("Authentication failed - max attempts reached")
            else:
                remaining = Config.AUTH_ATTEMPTS_MAX - self.auth_attempts
                messagebox.showerror(
                    "Error", 
                    f"Authentication failed. {remaining} attempts remaining."
                )
                self.auth_canvas.clear_points()
                self.status_bar.set_status(f"Authentication failed - {remaining} attempts remaining")
    
    def _show_success_animation(self) -> None:
        """Show a success animation on the canvas."""
        # Get canvas center
        canvas_width = self.auth_canvas.winfo_width()
        canvas_height = self.auth_canvas.winfo_height()
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        # Create a checkmark animation
        check_color = Config.SECONDARY_COLOR
        
        # Start with a circle
        self.auth_canvas.animate_point(
            center_x, center_y,
            color=check_color,
            radius_start=5,
            radius_end=50,
            duration=1000
        )
    
    def show_help(self) -> None:
        """Show help information."""
        help_text = """
        Graphical Authentication System Help
        
        This system allows you to authenticate using a pattern of points on an image instead of a traditional password.
        
        To register:
        1. Enter a username
        2. Click "Select Image" to choose your authentication image
        3. Click on the image to create a pattern (3-5 points recommended)
        4. Click "Register" to create your account
        
        To login:
        1. Enter your username
        2. Click "Login" to load your authentication image
        3. Recreate your pattern by clicking the same points in the same order
        4. Click "Login" again to authenticate
        
        Tips:
        - Choose distinctive points that you can easily remember
        - The order of points matters
        - Select points that are far apart for better security
        """
        
        # Create help dialog
        help_dialog = tk.Toplevel(self.root)
        help_dialog.title("Help")
        help_dialog.geometry("500x400")
        help_dialog.resizable(False, False)
        help_dialog.transient(self.root)
        help_dialog.grab_set()
        
        # Add help text
        text_widget = tk.Text(help_dialog, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(text_widget, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        # Add close button
        button_frame = ttk.Frame(help_dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        close_button = ttk.Button(
            button_frame,
            text="Close",
            command=help_dialog.destroy
        )
        close_button.pack(side=tk.RIGHT)
        
        # Center dialog on parent
        help_dialog.update_idletasks()
        width = help_dialog.winfo_width()
        height = help_dialog.winfo_height()
        x = self.root.winfo_x() + (self.root.winfo_width() - width) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - height) // 2
        help_dialog.geometry(f"{width}x{height}+{x}+{y}")


def main():
    """Main entry point for the application."""
    try:
        # Set up root window
        root = tk.Tk()
        
        # Create splash screen
        splash_width = 400
        splash_height = 300
        splash = tk.Toplevel(root)
        splash.title("")
        splash.geometry(f"{splash_width}x{splash_height}")
        splash.overrideredirect(True)  # Remove window decorations
        
        # Center splash screen
        x = (root.winfo_screenwidth() - splash_width) // 2
        y = (root.winfo_screenheight() - splash_height) // 2
        splash.geometry(f"{splash_width}x{splash_height}+{x}+{y}")
        
        # Create splash content
        splash_frame = tk.Frame(splash, bg="#3498db")
        splash_frame.pack(fill=tk.BOTH, expand=True)
        
        app_title = tk.Label(
            splash_frame, text=Config.APP_TITLE,
            font=("Helvetica", 18, "bold"),
            fg="white", bg="#3498db"
        )
        app_title.pack(pady=(80, 10))
        
        app_subtitle = tk.Label(
            splash_frame, text="Secure Authentication System",
            font=("Helvetica", 12),
            fg="white", bg="#3498db"
        )
        app_subtitle.pack(pady=5)
        
        loading_frame = tk.Frame(splash_frame, bg="#3498db")
        loading_frame.pack(pady=20)
        
        loading_bar = ttk.Progressbar(
            loading_frame, orient="horizontal",
            length=300, mode="determinate"
        )
        loading_bar.pack(side=tk.TOP, pady=10)
        
        loading_text = tk.Label(
            loading_frame, text="Loading...",
            font=("Helvetica", 10),
            fg="white", bg="#3498db"
        )
        loading_text.pack(side=tk.TOP)
        
        # Hide the main window
        root.withdraw()
        
        # Simulate loading
        def simulate_progress():
            for i in range(101):
                loading_bar["value"] = i
                if i == 0:
                    loading_text.config(text="Initializing application...")
                elif i == 33:
                    loading_text.config(text="Loading resources...")
                elif i == 66:
                    loading_text.config(text="Starting application...")
                elif i == 100:
                    loading_text.config(text="Complete!")
                splash.update()
                root.after(20)  # Delay in milliseconds
            
            # Close splash and show main window after loading
            splash.destroy()
            root.deiconify()
            
            # Initialize application
            app = GraphicalAuthenticationApp(root)
        
        # Start the loading simulation
        root.after(100, simulate_progress)
        
        # Start the application
        root.mainloop()
    
    except Exception as e:
        logger.critical(f"Application crashed: {e}", exc_info=True)
        if 'root' in locals() and root.winfo_exists():
            messagebox.showerror("Critical Error", f"The application encountered a critical error: {e}")


if __name__ == "__main__":
    main()