# Convertifull

A seamless Windows context menu extension for converting image, audio, and video files directly from File Explorer.

## Features
* **Right-Click Conversion:** Convert files quickly via the native Windows context menu.
* **Smart Context:** The menu automatically adapts, showing only relevant target formats for the selected file type.
* **Multi-file Support:** Select multiple files at once and convert them in a single, organized background batch.
* **Clean Execution:** Processes files without spawning multiple disruptive console windows.
* **Non-Destructive:** Creates a new converted file in the same directory while keeping your original file intact.

## Prerequisites

1. **Python (3.8 or newer) - REQUIRED**
   * Download from the [official Python website](https://www.python.org/downloads/).
   * **Crucial:** During installation, make sure to check the box that says **"Add Python to PATH"**.

2. **FFmpeg - OPTIONAL (Required ONLY for Video & Audio)**
   * If you only want to convert images, you can skip this step.
   * Download the latest essential build from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/).
   * Extract the downloaded archive to a permanent folder (e.g., `C:\ffmpeg`).
   * Add the `bin` folder (e.g., `C:\ffmpeg\bin`) to your Windows **System Environment Variables** (`Path`).

## Installation
1. Download this repository as a `.zip` file and extract it to a permanent folder on your computer.
2. Open Command Prompt (`cmd`) in the extracted folder and install the required processing libraries:
   ```bash
   pip install Pillow svglib reportlab
   ```
3. Double-click the **`install.bat`** file. 
4. If prompted by Windows User Account Control (UAC), click **Yes** to grant Administrator privileges.

## Usage
1. Open Windows File Explorer.
2. Right-click on any supported media file. *(On Windows 11, you may need to click "Show more options" first).*
3. Hover over **Convert**.
4. Select the format you want to convert the file into.
5. A single console window will appear to show the progress. Once done, the window will close automatically, and your new file will be ready next to the original one.

## Configuration
You can easily add or remove supported formats by editing the `config.json` file in a text editor. If you add new target formats, run `install.bat` again to update your context menu.

## Supported Formats Out-of-the-Box
* **Images:** `.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp`, `.tiff`, `.ico`, `.heic`, `.jfif`
* **Vector:** `.svg`
* **Audio:** `.mp3`, `.wav`, `.ogg`, `.flac`, `.aac`, `.m4a`, `.wma`
* **Video:** `.mp4`, `.avi`, `.mkv`, `.mov`, `.gif`, `.webm`, `.flv`, `.wmv`

## Uninstallation
To cleanly remove Convertifull from your Windows context menu, simply double-click the **`uninstall.bat`** file and grant Administrator privileges if prompted.
