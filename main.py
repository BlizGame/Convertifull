import sys
import os
import json
from converters import ConverterFactory
from registry import RegistryManager


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

    if not os.path.exists(input_path):
        return

    _, ext = os.path.splitext(input_path)
    config = load_config()

    try:
        converter = ConverterFactory.get_converter(ext, config)
        converter.convert(input_path, target_ext)

        if config.get("settings", {}).get("delete_source", False):
            os.remove(input_path)
    except Exception:
        pass


if __name__ == "__main__":
    main()