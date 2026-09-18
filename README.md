# Convertifull

A seamless Windows context menu extension for converting image, audio, and video files directly from File Explorer.

## Features
* **Right-Click Conversion:** Convert files quickly via the native Windows context menu.
* **Smart Context:** The menu automatically adapts, showing only relevant target formats for the selected file type.
* **Multithreaded Processing:** Converts multiple files simultaneously using a background worker pool.
* **Reliable Multi-file Batching:** Queue system guarantees all selected files are processed without drops or race conditions.
* **Silent Background Execution:** Converts files silently in the background without opening disruptive console windows.
* **Non-Destructive:** Creates converted files in the same directory while keeping original files intact.

## Prerequisites

1. **Python (3.8 or newer) - REQUIRED**
   * Download from the [official Python website](https://www.python.org/downloads/).
   * During installation, check the box that says **"Add Python to PATH"**.

2. **FFmpeg - OPTIONAL (Required ONLY for Video & Audio)**
   * Required only for audio and video conversion.
   * Download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/).
   * Extract to a folder (e.g. `C:\ffmpeg`) and add its `bin` folder to your system `Path`.

## Required Libraries

Convertifull uses the following Python libraries (managed via `requirements.txt`):
* **Pillow:** Image manipulation and raster conversion.
* **svglib:** SVG file parsing.
* **reportlab:** Rendering backend for vector SVG conversion.
* **pillow-heif:** Decoder support for Apple HEIC/HEIF images.

## Installation
1. Download or clone this repository to a permanent folder on your computer.
2. Double-click the **`install.bat`** file.
3. If prompted by User Account Control (UAC), click **Yes** to grant Administrator privileges.
4. The installer will automatically verify Python, install all dependencies from `requirements.txt`, and register the context menu in Windows.

## Usage
1. Open Windows File Explorer.
2. Select one or more files of the same category. *(On Windows 11, click "Show more options" if needed)*.
3. Hover over **Convert**.
4. Select your desired output format.
5. Files will convert silently in the background. Converted files will appear in the same folder.

## Configuration
Settings can be adjusted in `config.json`:
* `max_workers`: Number of simultaneous conversion threads (default: `4`). Set to `0` for automatic core count detection.
* `delete_source`: Set to `true` to delete the original file after conversion (default: `false`).

If you add new target formats or modify extensions, run `install.bat` again to update the context menu.

## Supported Formats Out-of-the-Box
* **Images:** `.jpg`, `.jpeg`, `.png`, `.webp`, `.bmp`, `.tiff`, `.ico`, `.heic`, `.jfif`
* **Vectors:** `.svg` (converts to raster formats)
* **Audio:** `.mp3`, `.wav`, `.ogg`, `.flac`, `.aac`, `.m4a`, `.wma`
* **Video:** `.mp4`, `.avi`, `.mkv`, `.mov`, `.gif`, `.webm`, `.flv`, `.wmv`

## Uninstallation
To remove Convertifull from your Windows context menu, double-click **`uninstall.bat`** and grant Administrator privileges.