# 🛠️ Utility WebApp

A futuristic, all-in-one web application toolkit giving you the power to process images, documents, and PDFs with a sleek, modern interface.

![Modern UI](https://dummyimage.com/600x400/0f172a/38bdf8?text=Utility+WebApp)

---

## ✨ Features

### 🎨 Modern UI & Experience
- **Dark Futuristic Theme**: Deep blue/black aesthetics with neon accents (#38bdf8).
- **Glassmorphism**: Translucent, frosted-glass cards and panels.
- **Animations**: Smooth, staggered entry animations and interactive hover effects.
- **Ad Integrations**: Dedicated Leaderboard, In-Feed, and Footer ad spaces.

### 🖼️ Image Tools
- **Compression**: Inteligent JPEG/PNG compression to reduce file size.
- **Conversion**: Convert between formats (PNG, JPEG, WEBP, BMP, TIFF, ICO, etc.).
- **Background Remover**: AI-powered background removal with optional solid color replacement.

### 📄 PDF Tools
- **Interactive Signing**: 
    - Drag & drop signature placement.
    - Real-time preview with rotation (0-360°) and scaling.
    - Multi-page support.
- **Compression**: Reduce PDF file size.
- **Editor**: Merge, Split, Rotate, and Extract pages.

### 📝 Document Conversion (High Fidelity)
- **PDF ↔ Word**: 
    - Uses **Microsoft Word Automation** (if installed) for perfect layout preservation.
    - Fallback to optimized multi-core `pdf2docx` processing.
    - Converts DOCX to professional PDFs.

### 📱 QR Generator
- Generate custom QR codes from text or URLs instantly.

---

## 🚀 Installation

### Prerequisites
- Python 3.8+
- [Optional] Microsoft Word (for high-fidelity conversions)

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/utility_web.git
   cd utility_web
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirement.txt
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Access the App**
   Open your browser and navigate to `http://localhost:5000`.

---

## 🛠️ Usage

### File Downloads
Processed files are automatically saved to your system's **temporary directory** to keep the project clean, and strictly downloaded to your browser's default **Downloads** folder.

### PDF Signing
1. Go to **Sign PDF**.
2. Upload a PDF and a Signature Image.
3. Drag the signature to the desired location on the preview.
4. Use the sliders to **Scale** or **Rotate** the signature.
5. Click **Sign & Download**.

### Document Conversion
- The app automatically detects if Microsoft Word is installed.
- **PDF to Word**: Preserves complex layouts, tables, and images.
- **Word to PDF**: Ensures generic formatting and font embedding.

---

## 🧰 Tech Stack

| Component | Technologies |
|-----------|--------------|
| **Backend** | Python, Flask |
| **Frontend** | HTML5, CSS3, Bootstrap 5, JavaScript |
| **PDF Engine** | `reportlab`, `pypdf`, `pdf2docx`, `win32com` |
| **Image Engine** | `Pillow`, `rembg`, `opencv-python` |
| **Server** | Werkzeug (Dev), Gunicorn (Prod) |

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

&copy; A Tiny Company - 2025
