"""Desktop entry point: runs the FastAPI backend in a background thread and
displays the built frontend in a native window via pywebview.

This is the module PyInstaller packages into the standalone LynkOo.app.
"""

from __future__ import annotations

import socket
import threading
import time

import uvicorn
import webview

from app.backend.main import app as fastapi_app

HOST = "127.0.0.1"
PORT = 8800


def _port_is_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.25)
        return sock.connect_ex((host, port)) == 0


def _run_server() -> None:
    uvicorn.run(fastapi_app, host=HOST, port=PORT, log_level="warning")


def main() -> None:
    server_thread = threading.Thread(target=_run_server, daemon=True)
    server_thread.start()

    deadline = time.monotonic() + 15
    while not _port_is_open(HOST, PORT):
        if time.monotonic() > deadline:
            raise RuntimeError("LynkOo backend did not start in time.")
        time.sleep(0.1)

    webview.create_window(
        "LynkOo",
        f"http://{HOST}:{PORT}",
        width=1280,
        height=820,
        min_size=(960, 640),
    )
    webview.start()


if __name__ == "__main__":
    main()
