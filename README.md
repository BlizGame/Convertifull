# Convertifull

A seamless Windows context menu extension for converting image, audio, and video files directly from File Explorer. 

## Features
- **Right-Click Conversion:** Convert files via the Windows context menu.
- **Smart Menus:** Only shows target formats relevant to the selected file type.
- **Multi-file Support:** Select multiple files and convert them in a single batch process.
- **Background Execution:** Converts files silently without spawning multiple console windows.

## Prerequisites
Before installing Convertifull, ensure you have the following installed on your system:
1. **Python 3.8+**: [Download Python](https://www.python.org/downloads/) (Check "Add Python to PATH" during installation).
2. **FFmpeg**: Required for audio and video conversion.
   - Download the latest essential build from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/).
   - Extract the archive.
   - Add the `bin` folder path to your Windows **System Environment Variables** (`Path`).

## Installation
1. Download or clone this repository to a permanent location on your drive.
2. Open Command Prompt (cmd) in the project folder and install the required Python library:
   
   ```bash
   pip install Pillow
   ```
4. Open Command Prompt as Administrator.
5. Navigate to your project folder using the cd command (e.g., cd C:\path\to\Convertifull).
6. Run the installation script:
   
   ```
   python main.py --install
   ```

## Usage
1. Open Windows File Explorer.
2. Right-click on any supported media file. (On Windows 11, you may need to click "Show more options" first).
3. Hover over Convert.
4. Select the format you want to convert the file into.
5. A single console window will appear to show the progress. Once done, the window will close automatically, and your new file will be ready next to the original one.

## Configuration
You can easily add or remove supported formats by editing the config.json file in a text editor. If you add new target formats, re-run the installation command to update your context menu.

## Uninstallation
To cleanly remove Convertifull from your Windows context menu:

1. Open Command Prompt as Administrator.
2. Navigate to the folder containing the script.
3. Run the following command:
   
  ```
  python main.py --uninstall
  ```
