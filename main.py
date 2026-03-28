import sys
import os
import json
import socket
import ctypes
from converters import ConverterFactory
from registry import RegistryManager


class TaskQueue:
    def __init__(self, port: int = 47538):
        self.port = port

    def dispatch(self, task: dict) -> bool:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('localhost', self.port))
                s.sendall(json.dumps(task).encode('utf-8'))
            return True
        except ConnectionRefusedError:
            return False

    def listen(self, initial_task: dict, timeout: float = 0.5) -> list:
        tasks = [initial_task]
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('localhost', self.port))
        server.listen()
        server.settimeout(timeout)

        try:
            while True:
                conn, _ = server.accept()
                with conn:
                    data = conn.recv(4096)
                    if data:
                        tasks.append(json.loads(data.decode('utf-8')))
        except socket.timeout:
            pass
        finally:
            server.close()

        return tasks


def load_config() -> dict:
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    with open(config_path, "r", encoding='utf-8') as f:
        return json.load(f)


def main():
    if len(sys.argv) == 2:
        if sys.argv[1] == "--install":
            RegistryManager("config.json").install()
            return
        elif sys.argv[1] == "--uninstall":
            RegistryManager("config.json").uninstall()
            return

    if len(sys.argv) < 3:
        return

    input_path = sys.argv[1]
    target_ext = sys.argv[2]

    task = {"path": input_path, "target": target_ext}
    queue = TaskQueue()

    if queue.dispatch(task):
        return

    tasks = queue.listen(task)
    config = load_config()

    ctypes.windll.kernel32.AllocConsole()
    sys.stdout = open("CONOUT$", "w", encoding="utf-8")
    sys.stderr = open("CONOUT$", "w", encoding="utf-8")

    for t in tasks:
        path = t["path"]
        target = t["target"]

        if not os.path.exists(path):
            continue

        _, ext = os.path.splitext(path)
        try:
            print(f"Converting: {os.path.basename(path)} -> {target.upper()}")
            converter = ConverterFactory.get_converter(ext, config)
            converter.convert(path, target)

            if config.get("settings", {}).get("delete_source", False):
                os.remove(path)
        except Exception as e:
            print(f"Failed to convert {path}: {e}")


if __name__ == "__main__":
    main()