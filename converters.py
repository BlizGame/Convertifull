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
        clean_ext = target_ext.split('_')[0]
        return f"{base}.{clean_ext}"


class ImageConverter(BaseConverter):
    def convert(self, input_path: str, target_ext: str) -> None:
        out_path = self.get_output_path(input_path, target_ext)
        with Image.open(input_path) as img:
            if img.mode in ("RGBA", "P", "LA", "L"):
                if target_ext.lower() in ("jpg", "jpeg", "bmp"):
                    img = img.convert("RGB")
                elif target_ext.lower() in ("png", "webp"):
                    img = img.convert("RGBA")
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

        if target_ext.lower() == "gif_hq":
            vf = "split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse"
            cmd = ["ffmpeg", "-y", "-i", input_path, "-vf", vf, out_path]
        elif target_ext.lower() == "gif_low":
            # Снижение FPS до 12 и ограничение ширины до 480px для веса
            vf = "fps=12,scale=480:-1:flags=lanczos"
            cmd = ["ffmpeg", "-y", "-i", input_path, "-vf", vf, out_path]
        else:
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


class GifConverter(BaseConverter):
    def convert(self, input_path: str, target_ext: str) -> None:
        image_targets = ["jpg", "jpeg", "png", "webp", "bmp", "tiff", "ico"]
        clean_target = target_ext.split('_')[0].lower()
        if clean_target in image_targets:
            ImageConverter().convert(input_path, target_ext)
        else:
            FFmpegConverter().convert(input_path, target_ext)


class ConverterFactory:
    @staticmethod
    def get_converter(file_ext: str, config: dict) -> BaseConverter:
        ext = file_ext.lower()
        if ext in config.get("image", {}).get("extensions", []):
            return ImageConverter()
        if ext in config.get("vector", {}).get("extensions", []):
            return SvgConverter()
        if ext in config.get("gif", {}).get("extensions", []):
            return GifConverter()
        if ext in config.get("audio", {}).get("extensions", []) or \
                ext in config.get("video", {}).get("extensions", []):
            return FFmpegConverter()
        raise ValueError(f"Unsupported extension: {ext}")