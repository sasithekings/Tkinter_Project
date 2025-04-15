# 🔐 Graphical Authentication System

A beginner-friendly **Graphical Password Authentication System** built using Python and Tkinter. Instead of typing passwords, users **click on specific points** in an image to log in—just like a **pattern lock** using images.

---

## 🚀 Features

- Click-based graphical password system
- Secure login with hashing and salting (SHA-256)
- User-friendly GUI with Tkinter
- Image-based authentication with visual feedback
- Stores user data securely in a JSON file
- Includes login attempt limits and logging

---

## 🧠 How It Works

### 🔐 Registration Flow

1. User inputs a unique username.
2. Selects a password image.
3. Clicks 3–5 points on the image (the "password").
4. Points are stored with:
   - SHA-256 hash of the pattern + salt
   - Image path
   - Salt (randomized per user)

### 🔓 Login Flow

1. User enters their username.
2. The same image is loaded.
3. User clicks on the image to reproduce the pattern.
4. System checks if the click pattern matches within a ±20 pixel tolerance.

---

## 🛡️ Security Highlights

- Uses **SHA-256 hashing** with a unique salt per user.
- Compares click locations with defined **tolerance** to avoid false rejections.
- Limits login attempts to prevent brute-force attacks.
- All events are logged to `graphical_auth.log`.

---




---

## 🛠️ Requirements

- Python 3.x
- Tkinter (usually comes with Python)
- Pillow (`pip install pillow`)

---

## 📚 Learnings

- GUI development with Tkinter
- Secure password hashing using SHA-256 with salt
- Image handling with Pillow
- JSON data storage and logging
- Pattern-based authentication logic

---

## 📈 Future Improvements

- Add user image selection from gallery
- Enhance UI/UX with animations
- Store user data in an encrypted database
- Support mobile/touch-based systems

---

## ✅ Usage

1. Run `main.py`
2. Choose an image and register with a username
3. Click 3–5 points on the image to register your pattern
4. Login by entering your username and repeating the pattern

---

## 📄 License

MIT License – feel free to use, modify, and share!

---

Made with ❤️ for learning purposes!


