import sys
import os
import time
import json
import socket
import threading
import queue
import ctypes
from concurrent.futures import ThreadPoolExecutor
from converters import ConverterFactory
from registry import RegistryManager

DEFAULT_PORT = 47538
MUTEX_NAME = "Local\\Convertifull_Server_Mutex"
ERROR_ALREADY_EXISTS = 183


def is_master_process() -> tuple[bool, int]:
    kernel32 = ctypes.windll.kernel32
    handle = kernel32.CreateMutexW(None, False, MUTEX_NAME)
    last_error = kernel32.GetLastError()
    return (last_error != ERROR_ALREADY_EXISTS), handle


def close_mutex(handle: int):
    if handle:
        try:
            ctypes.windll.kernel32.CloseHandle(handle)
        except Exception:
            pass


def dispatch_task(task: dict, port: int = DEFAULT_PORT, retries: int = 35, delay: float = 0.1) -> bool:
    payload = (json.dumps(task) + "\n").encode("utf-8")
    for _ in range(retries):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2.0)
                s.connect(('127.0.0.1', port))
                s.sendall(payload)
                ack = s.recv(16)
                if b"OK" in ack:
                    return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            time.sleep(delay)
    return False


def load_config() -> dict:
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    try:
        with open(config_path, "r", encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


class ConversionServer:
    def __init__(self, port: int = DEFAULT_PORT):
        self.port = port
        self.task_queue = queue.Queue()
        self.server_socket = None
        self.is_running = True

    def start_socket_server(self) -> bool:
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('127.0.0.1', self.port))
            self.server_socket.listen(64)
            self.server_socket.settimeout(0.5)
            return True
        except OSError:
            if self.server_socket:
                try:
                    self.server_socket.close()
                except Exception:
                    pass
                self.server_socket = None
            return False

    def listener_worker(self):
        while self.is_running:
            if not self.server_socket:
                break
            try:
                conn, _ = self.server_socket.accept()
            except socket.timeout:
                continue
            except OSError:
                break

            with conn:
                try:
                    conn.settimeout(2.0)
                    buffer = b""
                    while b"\n" not in buffer:
                        chunk = conn.recv(1024)
                        if not chunk:
                            break
                        buffer += chunk

                    if buffer:
                        line = buffer.split(b"\n")[0].decode("utf-8")
                        task = json.loads(line)
                        self.task_queue.put(task)
                        conn.sendall(b"OK\n")
                except Exception:
                    pass

    def convert_file(self, task: dict, config: dict):
        path = task.get("path", "")
        target = task.get("target", "")

        if not os.path.exists(path):
            return

        _, ext = os.path.splitext(path)
        try:
            converter = ConverterFactory.get_converter(ext, config)
            converter.convert(path, target)

            if config.get("settings", {}).get("delete_source", False):
                try:
                    os.remove(path)
                except Exception:
                    pass
        except Exception:
            pass

    def run(self, initial_tasks: list, config: dict) -> bool:
        if not self.start_socket_server():
            return False

        for task in initial_tasks:
            self.task_queue.put(task)

        listener_thread = threading.Thread(target=self.listener_worker, daemon=True)
        listener_thread.start()

        settings = config.get("settings", {})
        max_workers = settings.get("max_workers", 4)
        if not max_workers or max_workers <= 0:
            max_workers = min(8, os.cpu_count() or 4)

        active_futures = set()
        time.sleep(0.15)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            last_activity = time.time()
            idle_timeout = 1.0

            while True:
                got_task = False
                while True:
                    try:
                        task = self.task_queue.get_nowait()
                        got_task = True
                        last_activity = time.time()

                        future = executor.submit(
                            self.convert_file,
                            task,
                            config
                        )
                        active_futures.add(future)
                    except queue.Empty:
                        break

                done_futures = {f for f in active_futures if f.done()}
                active_futures -= done_futures

                if got_task:
                    last_activity = time.time()

                if not active_futures and self.task_queue.empty():
                    if time.time() - last_activity >= idle_timeout:
                        break

                time.sleep(0.05)

        self.is_running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass
        listener_thread.join(timeout=0.5)
        return True


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

    target_ext = sys.argv[-1]
    input_paths = [os.path.abspath(p) for p in sys.argv[1:-1] if os.path.exists(p)]
    if not input_paths:
        return

    tasks = [{"path": p, "target": target_ext} for p in input_paths]

    is_master, mutex_handle = is_master_process()

    if not is_master:
        all_dispatched = True
        for t in tasks:
            if not dispatch_task(t):
                all_dispatched = False
                break
        if all_dispatched:
            close_mutex(mutex_handle)
            return

    server = ConversionServer()
    config = load_config()
    success = server.run(tasks, config)

    close_mutex(mutex_handle)

    if not success:
        for t in tasks:
            dispatch_task(t)


if __name__ == "__main__":
    main()