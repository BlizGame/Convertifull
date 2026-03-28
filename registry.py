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
        self.base_key = r"*\shell\PyConverter"

    def install(self):
        try:
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, self.base_key) as key:
                winreg.SetValueEx(key, "MUIVerb", 0, winreg.REG_SZ, "Конвертация")
                winreg.SetValueEx(key, "SubCommands", 0, winreg.REG_SZ, "")

                shell_key_path = rf"{self.base_key}\shell"
                with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, shell_key_path) as shell_key:
                    self._register_formats(shell_key_path)
            print("Контекстное меню успешно установлено.")
        except PermissionError:
            print("Ошибка: Запустите скрипт от имени Администратора.")

    def _register_formats(self, parent_key_path: str):
        targets = set()
        for category in self.config.values():
            targets.update(category.get("targets", []))

        for target in sorted(targets):
            cmd_key_path = rf"{parent_key_path}\to_{target}"
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, cmd_key_path) as cmd_key:
                winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, f"В {target.upper()}")
                with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, rf"{cmd_key_path}\command") as run_key:
                    cmd = f'"{self.python_exe}" "{self.script_path}" "%1" "{target}"'
                    winreg.SetValueEx(run_key, "", 0, winreg.REG_SZ, cmd)