```markdown
# OPEN IMAGE COMPRESSOR

**A fast, multi-core Image Compressor with a clean and user-friendly GUI**

Developed by **Shahzaib Rasool** from Pakistan  
📧 Email: srzaibi@gmail.com

---
<img width="786" height="714" alt="Screenshot" src="https://github.com/user-attachments/assets/de326036-f066-4be5-89de-64c0b93d9e53" />

## ✨ Features

- Select **multiple images** or an entire **folder**
- Two resize modes:
  - **Percentage** (with smooth slider 10% – 200%)
  - **Max Width / Max Height** (keeps aspect ratio)
- Compression Quality slider (0% = maximum compression → 100% = best quality)
- Save options:
  - Create a `Compressed` folder (recommended)
  - Overwrite original files
- **Multi-core processing** – uses all available CPU cores for maximum speed
- Real-time progress bar + status updates
- "Open Folder" button after compression completes
- Supports: `JPG`, `JPEG`, `PNG`, `WEBP`, `BMP`, `TIFF`

---

## 🖼️ Preview

> *(You can add screenshots here later)*

---

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/open-image-compressor.git
cd open-image-compressor
```

### 2. Install dependencies
```bash
pip install Pillow
```

> Requires **Python 3.8+**

---

## 💻 How to Use

1. Run the application:
```bash
python image_compressor.py
```

2. Click **Select Images** or **Select Folder**
3. Choose your preferred resize mode and quality
4. Select save option (`Compressed` folder or overwrite)
5. Click **Start Compression**
6. After completion, click **Open Folder** to view the results

---

## ⚙️ Technical Details

| Feature              | Implementation                          |
|----------------------|-----------------------------------------|
| GUI Framework        | `tkinter` (built-in)                    |
| Image Processing     | `Pillow (PIL)`                          |
| Multi-core Speed     | `concurrent.futures.ProcessPoolExecutor`|
| Supported Platforms  | Windows, macOS, Linux                   |

---

## 📄 License

This project is open source and available under the **MIT License**.

```
MIT License

Copyright (c) 2025 Shahzaib Rasool

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!  
Feel free to fork the repository and submit a pull request.

---

## 👨‍💻 Developer

**Shahzaib Rasool**  
Pakistan  
📧 srzaibi@gmail.com

---

⭐ If you find this project useful, please give it a star on GitHub!
```
