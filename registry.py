import os
import sys
import winreg
import json


class RegistryManager:
    def __init__(self, config_path: str):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.python_exe = sys.executable.replace("python.exe", "pythonw.exe")
        self.script_path = os.path.abspath("main.py")
        self.app_key_name = "PyConverter"

    def _delete_key_tree(self, root, subkey):
        try:
            with winreg.OpenKey(root, subkey, 0, winreg.KEY_ALL_ACCESS) as key:
                info = winreg.QueryInfoKey(key)
                for _ in range(info[0]):
                    sub = winreg.EnumKey(key, 0)
                    self._delete_key_tree(root, rf"{subkey}\{sub}")
            winreg.DeleteKey(root, subkey)
        except OSError:
            pass

    def uninstall(self):
        self._delete_key_tree(winreg.HKEY_CLASSES_ROOT, rf"*\shell\{self.app_key_name}")
        for category, data in self.config.items():
            if category == "settings": continue
            self._delete_key_tree(winreg.HKEY_CLASSES_ROOT,
                                  rf"SystemFileAssociations\{category}\shell\{self.app_key_name}")
            for ext in data.get("extensions", []):
                self._delete_key_tree(winreg.HKEY_CLASSES_ROOT,
                                      rf"SystemFileAssociations\{ext}\shell\{self.app_key_name}")

    def install(self):
        self.uninstall()
        try:
            for category, data in self.config.items():
                if category == "settings": continue
                targets = data.get("targets", [])
                for ext in data.get("extensions", []):
                    clean_ext = ext.lstrip('.').lower()
                    valid_targets = [t for t in targets if t.lower() != clean_ext]
                    if not valid_targets: continue

                    base_path = rf"SystemFileAssociations\{ext}\shell\{self.app_key_name}"
                    with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, base_path) as key:
                        winreg.SetValueEx(key, "MUIVerb", 0, winreg.REG_SZ, "Convert")
                        winreg.SetValueEx(key, "SubCommands", 0, winreg.REG_SZ, "")
                        self._register_targets(rf"{base_path}\shell", valid_targets)
        except PermissionError:
            sys.exit(1)

    def _register_targets(self, parent_path: str, targets: list):
        # Группируем GIF таргеты
        gif_variants = [t for t in targets if t.startswith("gif")]
        other_targets = [t for t in targets if not t.startswith("gif")]

        # Регистрация обычных таргетов
        for target in sorted(other_targets):
            self._create_verb(parent_path, target, f"To {target.upper()}")

        # Регистрация каскадного меню для GIF
        if gif_variants:
            gif_menu_path = rf"{parent_path}\gif_cascade"
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, gif_menu_path) as key:
                winreg.SetValueEx(key, "MUIVerb", 0, winreg.REG_SZ, "To GIF")
                winreg.SetValueEx(key, "SubCommands", 0, winreg.REG_SZ, "")

                inner_shell = rf"{gif_menu_path}\shell"
                for g_target in sorted(gif_variants):
                    label = "Standard"
                    if "hq" in g_target: label = "Better Quality (HQ)"
                    if "low" in g_target: label = "Lower Weight (Small)"
                    self._create_verb(inner_shell, g_target, label)

    def _create_verb(self, parent_path: str, target: str, label: str):
        verb_path = rf"{parent_path}\to_{target}"
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, verb_path) as key:
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, label)
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, rf"{verb_path}\command") as cmd_key:
                cmd = f'"{self.python_exe}" "{self.script_path}" "%1" "{target}"'
                winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, cmd)