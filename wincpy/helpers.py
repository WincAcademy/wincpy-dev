from argparse import ArgumentParser
import importlib
import os
import pathlib
import subprocess
import sys

import pandas as pd

LATEST_RELEASE_API = "https://api.github.com/repos/WincAcademy/wincpy-dist/releases/latest"

def get_iddb():
    # THIS FUNCTION WAS CHANGED, MIGHT NOT WORK WITH NON-WINDOWS OS
    iddb_url = f"{pathlib.Path(__file__).parent.resolve()}/iddb.json"
    try:
        iddb = pd.read_json(iddb_url)
        print("this works!")
    except Exception:
        from wincpy import ui
        ui.report_error("iddb_load_fail")
        exit(6)
    return iddb


def get_student_module(path):
    from wincpy import ui

    arg_abspath = os.path.abspath(path)
    parent_abspath, student_module_name = os.path.split(arg_abspath)
    sys.path.insert(0, arg_abspath)

    # Redirect stdout to the void while importing
    ui.mute_stdout()
    try:
        student_module = importlib.import_module("main")
    except Exception as e:
        ui.unmute_stdout()
        ui.report_error(
            "module_import_fail",
            module_name=student_module_name,
            dir=parent_abspath,
            exception=str(e),
        )
        exit(51)

    if not hasattr(student_module, "__winc_id__"):
        ui.unmute_stdout()
        ui.report_error(
            "module_no_winc_id", module_name=student_module_name, dir=parent_abspath
        )
        exit(52)

    # Restore stdout
    ui.unmute_stdout()
    return student_module


def parse_args():
    parser = ArgumentParser(description="The Winc Python tool.")
    subparsers = parser.add_subparsers(
        dest="action", required=True, help="What wincpy should do in this run."
    )
    start_parser = subparsers.add_parser("start", help="Start a new assignment.")
    check_parser = subparsers.add_parser("check", help="Check an existing assignment.")
    solve_parser = subparsers.add_parser("solve", help="Place Winc's solution here.")

    subparsers.add_parser("update", help="Update wincpy using pip.")
    subparsers.add_parser("version", help="Print wincpy's version.")

    start_parser.add_argument(
        "winc_id", type=str, help="Winc ID of an assignment to start."
    )
    check_parser.add_argument(
        "path",
        type=str,
        nargs="?",
        default=os.getcwd(),
        help="Path containing assignment to check.",
    )
    solve_parser.add_argument(
        "path",
        type=str,
        nargs="?",
        default=os.getcwd(),
        help="Path containing assignment to check.",
    )

    return parser.parse_args()


def get_latest_release_info():
    try:
        import requests
    except ImportError as e:
        raise RuntimeError("The 'requests' package is required for updates") from e

    response = requests.get(LATEST_RELEASE_API, timeout=10)
    response.raise_for_status()
    release = response.json()

    latest_version = release["tag_name"].removeprefix("v")

    wheel_url = None
    for asset in release["assets"]:
        name = asset["name"]
        if name.startswith("wincpy-") and name.endswith(".whl"):
            wheel_url = asset["browser_download_url"]
            break

    if not wheel_url:
        raise RuntimeError("No wincpy wheel found in the latest release")

    return {
        "version": latest_version,
        "wheel_url": wheel_url,
    }


def update():
    try:
        release_info = get_latest_release_info()
        wheel_url = release_info["wheel_url"]

        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", wheel_url],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError("Failed to update wincpy") from e
    except Exception as e:
        raise RuntimeError("Could not determine the latest wincpy release") from e