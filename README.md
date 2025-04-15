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

### 1. **User Interface (UI):**
- Made using Python's built-in GUI toolkit: **Tkinter**
- Displays an image on a canvas where users can click to register or login

### 2. **User Registration:**
- Enter a username
- Select **3 to 5 points** on the image (click pattern)
- Saves:
  - Clicked points
  - A **secure hash** of the pattern with a random salt
  - Image path

### 3. **User Login:**
- Enter the same username
- Recreate the click pattern (within a ±20 pixel tolerance)
- If matched, login is successful; else up to **3 attempts** allowed

### 4. **Security Measures:**
- Uses **SHA-256 hashing** with random **salt**
- Pattern comparison done with point tolerance to allow slight deviation
- Stores data in `users.json` and logs activity in `graphical_auth.log`

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


