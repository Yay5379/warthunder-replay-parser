import os.path
import sys
from cx_Freeze import setup, Executable

src_path = "src/warthunder-replay-parser/"
packages = ["multiprocessing"]
includes = []
excludes = ["unittest", "pydoc", "construct.examples", "bz2", "lib2to3", "test", "tkinter"]
includefiles = []
zip_include_packages = ["collections", "construct", "ctypes", "encodings", "json", "logging", "importlib", "formats",
                        "zstandard", "xml", "urllib", "distutils", "click", "pkg_resources", "colorama", "bencodepy",
                        "jsondiff", "requests", "chardet", "idna", "urllib3", "email", "http", "certifi", "multiprocessing",
                        "multiprocessing-logging", "blk"]


parse_datablocks = Executable(
    script=os.path.join(src_path, "parse_datablocks.py"),
)

parse_replay = Executable(
    script=os.path.join(src_path, "parse_replay.py")
)

download_replay = Executable(
    script=os.path.join(src_path, "download_replay.py")
)

get_vehicle_info = Executable(
    script=os.path.join(src_path, "get_vehicle_info.py")
)

get_vehicles = Executable(
    script=os.path.join(src_path, "get_vehicles.py")
)

replays_scraper = Executable(
    script=os.path.join(src_path, "replays_scraper.py")
)



setup(
    name="warthunder-replay-parser",
    author='Yay5379',
    description="numerous War Thunder replay related things",
    url="https://github.com/Yay5379/warthunder-replay-parser",
    options={"build_exe": {"includes": includes, "excludes": excludes, "include_files": includefiles,
                           "packages": packages, "zip_include_packages": zip_include_packages,
                           "path": sys.path + [src_path]}},
    executables=[parse_datablocks, parse_replay, download_replay, get_vehicle_info,
                get_vehicles, replays_scraper]
)
