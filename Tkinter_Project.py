import os
import sys
import json
import hashlib
import base64
from datetime import datetime
import logging
from typing import List, Tuple, Dict, Optional, Union

import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk

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
    APP_TITLE = "Graphical Authentication System"
    USER_DATA_DIR = "user_data"
    USER_DATA_FILE = os.path.join(USER_DATA_DIR, "users.json")
    DEFAULT_IMAGE_PATH = os.path.join("assets", "default_image.jpg")
    TOLERANCE_RADIUS = 20  # Pixel radius for click validation
    MAX_POINTS = 5  # Maximum number of points in a pattern
    WINDOW_WIDTH = 600
    WINDOW_HEIGHT = 500
    AUTH_ATTEMPTS_MAX = 3


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


class AuthCanvas(tk.Canvas):
    """Custom canvas for graphical authentication."""
    
    def __init__(self, parent, **kwargs):
        """Initialize the authentication canvas."""
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.configure(bg="white", highlightthickness=1, highlightbackground="gray")
        
        self.image = None
        self.image_tk = None
        self.points = []
        self.point_markers = []
        self.image_path = ""
        
        # Bind click event
        self.bind("<Button-1>", self.on_canvas_click)
    
    def load_image(self, image_path: str) -> bool:
        """
        Load an image into the canvas
        
        Args:
            image_path: Path to the image file
            
        Returns:
            True if image loaded successfully, False otherwise
        """
        try:
            # Clear canvas and points
            self.clear()
            
            # Load and resize image
            self.image_path = image_path
            self.image = Image.open(image_path)
            # Calculate new size to fit in canvas while maintaining aspect ratio
            canvas_width = self.winfo_width() or Config.WINDOW_WIDTH
            canvas_height = self.winfo_height() or Config.WINDOW_HEIGHT
            
            width_ratio = canvas_width / self.image.width
            height_ratio = canvas_height / self.image.height
            ratio = min(width_ratio, height_ratio)
            
            new_width = int(self.image.width * ratio)
            new_height = int(self.image.height * ratio)
            
            self.image = self.image.resize((new_width, new_height), Image.LANCZOS)
            self.image_tk = ImageTk.PhotoImage(self.image)
            
            # Calculate position to center the image
            x_offset = (canvas_width - new_width) // 2
            y_offset = (canvas_height - new_height) // 2
            
            # Add image to canvas
            self.create_image(x_offset, y_offset, anchor=tk.NW, image=self.image_tk)
            
            return True
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            messagebox.showerror("Error", f"Failed to load image: {e}")
            return False
    
    def on_canvas_click(self, event) -> None:
        """Handle click events on the canvas."""
        if len(self.points) >= Config.MAX_POINTS:
            messagebox.showinfo("Information", f"Maximum of {Config.MAX_POINTS} points reached.")
            return
        
        # Add point to list
        self.points.append((event.x, event.y))
        
        # Draw marker on canvas
        marker = self.create_oval(
            event.x - 5, event.y - 5, 
            event.x + 5, event.y + 5, 
            fill="red", outline="black"
        )
        self.point_markers.append(marker)
        
        # Draw line between consecutive points
        if len(self.points) > 1:
            x1, y1 = self.points[-2]
            x2, y2 = self.points[-1]
            line = self.create_line(x1, y1, x2, y2, fill="blue", width=2)
            self.point_markers.append(line)
    
    def clear(self) -> None:
        """Clear all points and markers from the canvas."""
        self.delete("all")
        self.points = []
        self.point_markers = []
    
    def get_points(self) -> List[Tuple[int, int]]:
        """Get the list of selected points."""
        return self.points


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
        self.root.resizable(True, True)
        
        # Initialize components
        self.user_manager = UserManager()
        self.current_username = None
        self.auth_attempts = 0
        
        # Set up UI
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        # Main frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Username entry
        self.username_frame = tk.Frame(self.main_frame)
        self.username_frame.pack(fill=tk.X, pady=5)
        
        self.username_label = tk.Label(self.username_frame, text="Username:")
        self.username_label.pack(side=tk.LEFT, padx=5)
        
        self.username_entry = tk.Entry(self.username_frame, width=20)
        self.username_entry.pack(side=tk.LEFT, padx=5)
        
        # Auth canvas
        self.auth_canvas = AuthCanvas(
            self.main_frame,
            width=Config.WINDOW_WIDTH - 20,
            height=Config.WINDOW_HEIGHT - 150
        )
        self.auth_canvas.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Default image
        if os.path.exists(Config.DEFAULT_IMAGE_PATH):
            self.auth_canvas.load_image(Config.DEFAULT_IMAGE_PATH)
        else:
            logger.warning(f"Default image not found: {Config.DEFAULT_IMAGE_PATH}")
        
        # Buttons frame
        self.buttons_frame = tk.Frame(self.main_frame)
        self.buttons_frame.pack(fill=tk.X, pady=5)
        
        # Create buttons
        self.select_image_btn = tk.Button(
            self.buttons_frame, text="Select Image", command=self.select_image
        )
        self.select_image_btn.pack(side=tk.LEFT, padx=5)
        
        self.register_btn = tk.Button(
            self.buttons_frame, text="Register", command=self.register
        )
        self.register_btn.pack(side=tk.LEFT, padx=5)
        
        self.login_btn = tk.Button(
            self.buttons_frame, text="Login", command=self.login
        )
        self.login_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = tk.Button(
            self.buttons_frame, text="Clear", command=self.auth_canvas.clear
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.quit_btn = tk.Button(
            self.buttons_frame, text="Quit", command=self.root.quit
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
            if self.auth_canvas.load_image(file_path):
                logger.info(f"Image loaded: {file_path}")
    
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
            messagebox.showerror("Error", "Please select at least 3 points.")
            return
        
        if not image_path:
            messagebox.showerror("Error", "Please select an image.")
            return
        
        # Register user
        if self.user_manager.user_exists(username):
            messagebox.showerror("Error", "Username already exists.")
            return
        
        if self.user_manager.register_user(username, points, image_path):
            messagebox.showinfo("Success", "User registered successfully.")
            self.auth_canvas.clear()
        else:
            messagebox.showerror("Error", "Failed to register user.")
    
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
        
        if not points:
            messagebox.showerror("Error", "Please select your authentication points.")
            return
        
        # If this is a new login attempt, load the user's image
        if self.current_username != username:
            self.current_username = username
            self.auth_attempts = 0
            user_image = self.user_manager.get_user_image_path(username)
            self.auth_canvas.load_image(user_image)
            messagebox.showinfo("Login", "Please select your authentication pattern.")
            return
        
        # Authenticate
        self.auth_attempts += 1
        if self.user_manager.authenticate_user(username, points):
            messagebox.showinfo("Success", "Authentication successful!")
            self.current_username = None
            self.auth_attempts = 0
            self.auth_canvas.clear()
            # In a real application, you would proceed to the main application screen here
        else:
            if self.auth_attempts >= Config.AUTH_ATTEMPTS_MAX:
                messagebox.showerror(
                    "Error", 
                    f"Authentication failed. Maximum attempts ({Config.AUTH_ATTEMPTS_MAX}) reached."
                )
                self.current_username = None
                self.auth_attempts = 0
                self.auth_canvas.clear()
            else:
                remaining = Config.AUTH_ATTEMPTS_MAX - self.auth_attempts
                messagebox.showerror(
                    "Error", 
                    f"Authentication failed. {remaining} attempts remaining."
                )
                self.auth_canvas.clear_points()


def main():
    """Main entry point for the application."""
    # Create directories if they don't exist
    os.makedirs(Config.USER_DATA_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(Config.DEFAULT_IMAGE_PATH), exist_ok=True)
    
    # Create default image if it doesn't exist
    if not os.path.exists(Config.DEFAULT_IMAGE_PATH):
        try:
            # Create a simple default image
            img = Image.new('RGB', (400, 300), color='white')
            img.save(Config.DEFAULT_IMAGE_PATH)
            logger.info(f"Created default image: {Config.DEFAULT_IMAGE_PATH}")
        except Exception as e:
            logger.error(f"Failed to create default image: {e}")
    
    # Start the application
    root = tk.Tk()
    app = GraphicalAuthenticationApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()