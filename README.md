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

## 🗂️ Project Structure

