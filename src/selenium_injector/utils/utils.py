import json
import os

import selenium_injector
import socket
from contextlib import closing


def sel_injector_path():
    return os.path.dirname(selenium_injector.__file__) + "/"


def read(filename: str, encoding: str = "utf-8", sel_root: bool = True):
    if sel_root:
        path = sel_injector_path() + filename
    else:
        path = filename
    with open(path, encoding=encoding) as f:
        return f.read()


def write(filename: str, content: str, encoding: str = "utf-8", sel_root: bool = True):
    if sel_root:
        path = sel_injector_path() + filename
    else:
        path = filename
    with open(path, "w+", encoding=encoding) as f:
        return f.write(content)


def read_json(filename: str = 'example.json', encoding: str = "utf-8", sel_root: bool = True):
    if sel_root:
        path = sel_injector_path() + filename
    else:
        path = filename
    with open(path, 'r', encoding=encoding) as f:
        return json.load(f)


def write_json(obj: dict or list, filename: str = "out.json", encoding: str = "utf-8", sel_root=True):
    if sel_root:
        path = sel_injector_path() + filename
    else:
        path = filename
    with open(path, "w", encoding=encoding) as outfile:
        outfile.write(json.dumps(obj))


def random_port(host: str = None):
    if not host:
        host = ''
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind((host, 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]
