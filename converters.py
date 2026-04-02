import os
import subprocess
from abc import ABC, abstractmethod
from PIL import Image
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM


class BaseConverter(ABC):
    @abstractmethod
    def convert(self, input_path: str, target_ext: str) -> None:
        pass

    def get_output_path(self, input_path: str, target_ext: str) -> str:
        base, _ = os.path.splitext(input_path)
        return f"{base}.{target_ext}"


class ImageConverter(BaseConverter):
    def convert(self, input_path: str, target_ext: str) -> None:
        out_path = self.get_output_path(input_path, target_ext)
        with Image.open(input_path) as img:
            if img.mode in ("RGBA", "P") and target_ext.lower() in ("jpg", "jpeg", "bmp"):
                img = img.convert("RGB")
            img.save(out_path)


class SvgConverter(BaseConverter):
    def convert(self, input_path: str, target_ext: str) -> None:
        out_path = self.get_output_path(input_path, target_ext)
        drawing = svg2rlg(input_path)
        img = renderPM.drawToPIL(drawing)
        if img.mode in ("RGBA", "P") and target_ext.lower() in ("jpg", "jpeg", "bmp"):
            img = img.convert("RGB")
        img.save(out_path)


class FFmpegConverter(BaseConverter):
    def convert(self, input_path: str, target_ext: str) -> None:
        out_path = self.get_output_path(input_path, target_ext)
        cmd = ["ffmpeg", "-y", "-i", input_path, out_path]

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            startupinfo=startupinfo,
            check=True
        )


class ConverterFactory:
    @staticmethod
    def get_converter(file_ext: str, config: dict) -> BaseConverter:
        ext = file_ext.lower()
        if ext in config.get("image", {}).get("extensions", []):
            return ImageConverter()
        if ext in config.get("vector", {}).get("extensions", []):
            return SvgConverter()
        if ext in config.get("audio", {}).get("extensions", []) or \
                ext in config.get("video", {}).get("extensions", []):
            return FFmpegConverter()
        raise ValueError(f"Unsupported extension: {ext}")