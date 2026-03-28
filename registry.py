import os
import sys
import winreg
import json


class RegistryManager:
    def __init__(self, config_path: str):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.python_exe = sys.executable
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
        for category in self.config.keys():
            base_path = rf"SystemFileAssociations\{category}\shell\{self.app_key_name}"
            self._delete_key_tree(winreg.HKEY_CLASSES_ROOT, base_path)

    def install(self):
        self.uninstall()
        try:
            for category, data in self.config.items():
                base_path = rf"SystemFileAssociations\{category}\shell\{self.app_key_name}"
                with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, base_path) as key:
                    winreg.SetValueEx(key, "MUIVerb", 0, winreg.REG_SZ, "Convert")
                    winreg.SetValueEx(key, "SubCommands", 0, winreg.REG_SZ, "")

                    shell_path = rf"{base_path}\shell"
                    with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, shell_path) as shell_key:
                        self._register_targets(shell_path, data.get("targets", []))
        except PermissionError:
            sys.exit(1)

    def _register_targets(self, parent_path: str, targets: list):
        for target in sorted(targets):
            cmd_path = rf"{parent_path}\to_{target}"
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, cmd_path) as cmd_key:
                winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, f"To {target.upper()}")
                with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, rf"{cmd_path}\command") as run_key:
                    cmd = f'"{self.python_exe}" "{self.script_path}" "%1" "{target}"'
                    winreg.SetValueEx(run_key, "", 0, winreg.REG_SZ, cmd)