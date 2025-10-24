# 📷🔗 Image & QR WebApp

A lightweight, user-friendly web application built with **Flask** that allows users to **compress images** and **generate QR codes** directly from their browser. Ideal for developers, designers, and everyday users looking to optimize image sizes or create quick QR links.

---

## 🚀 Features

- ✅ **Image Compression**
  - Upload JPEG or PNG images
  - Choose compression level
  - Download optimized image instantly

- ✅ **QR Code Generator**
  - Input any text or URL
  - Generate QR code as PNG or SVG
  - Download and share easily

- ✅ **Web Interface**
  - Clean, responsive UI using HTML/CSS
  - Simple navigation between tools
  - Upload and download support

---

## 🧰 Tech Stack

| Layer         | Tools/Libraries Used                      |
|--------------|--------------------------------------------|
| Backend       | Flask, Pillow, OpenCV, qrcode             |
| Frontend      | HTML, CSS (Bootstrap optional)            |
| QR Generation | `qrcode`, `segno`                         |
| Image Tools   | `Pillow`, `opencv-python`, `tinify` (optional) |
| Deployment    | Gunicorn, Docker (optional), Heroku/Vercel |

---

## 📁 Project Structure

```
image_qr_webapp/
│
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── routes.py             # URL routes and logic
│   ├── image_tools.py        # Image compression functions
│   ├── qr_tools.py           # QR generation functions
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── compress.html
│       └── qr.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── uploads/              # Uploaded and processed files
│
├── requirements.txt
├── config.py
├── run.py
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/image_qr_webapp.git
cd image_qr_webapp
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
python run.py
```

Visit `http://127.0.0.1:5000` in your browser.

---

## 🧪 Usage

- Navigate to `/compress` to upload and compress images.
- Navigate to `/qr` to generate QR codes from text or URLs.
- Download results directly from the interface.

---

## 🛠️ Configuration

Edit `config.py` to set:
- Upload folder path
- Allowed file types
- Compression quality
- QR output format

---

