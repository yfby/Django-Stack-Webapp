#!/usr/bin/env python3
"""Portable commands for the website and its separate test suites."""
import argparse
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time
from urllib.request import urlopen
import webbrowser

ROOT = Path(__file__).resolve().parent.parent
COMMANDS = {
    "tests": ["tests"], "queue": ["challenge.test_queue"],
    "linked": ["challenge.test_linked_list"], "activity": ["challenge"],
    "all": ["tests", "challenge"],
}


def browser_when_ready(url):
    for _ in range(40):
        try:
            with urlopen(url + "health/", timeout=1) as response:
                if response.status == 200:
                    webbrowser.open(url)
                    return
        except OSError:
            pass
        time.sleep(0.25)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["serve", *COMMANDS])
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--lan", action="store_true")
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--no-reload", action="store_true")
    args = parser.parse_args()
    try:
        import django
    except ImportError:
        print("Run SETUP.bat or python3 scripts/bootstrap.py first.")
        return 2
    if args.command != "serve":
        label = "APPLICATION CHECKS: expected to pass before and after student changes." if args.command == "tests" else "GOAL CHECKS: intentional failures occur until the relevant student tasks are complete."
        print("\n" + label + "\n", flush=True)
        try:
            return subprocess.run([sys.executable, str(ROOT / "manage.py"), "test", *COMMANDS[args.command], "--noinput", "-v", "2"], cwd=ROOT, timeout=120).returncode
        except subprocess.TimeoutExpired:
            print("Checks stopped after 120 seconds. Look for a traversal that never reaches None.")
            return 2
    if not 1 <= args.port <= 65535:
        parser.error("Port must be between 1 and 65535.")
    with socket.socket() as probe:
        if probe.connect_ex(("127.0.0.1", args.port)) == 0:
            print(f"Port {args.port} is already in use. Stop the old server or use --port {args.port+1}.")
            return 2
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    host = "0.0.0.0" if args.lan else "127.0.0.1"
    url = f"http://127.0.0.1:{args.port}/"
    print(f"\nPrintPilot: {url}", flush=True)
    if args.lan:
        addresses = sorted({x for x in socket.gethostbyname_ex(socket.gethostname())[2] if not x.startswith("127.")})
        allowed = env.get("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,[::1]")
        env["DJANGO_ALLOWED_HOSTS"] = ",".join([allowed, *addresses])
        for address in addresses:
            print(f"Same Wi-Fi phone link: http://{address}:{args.port}/", flush=True)
        if not addresses:
            print("Find the computer's IPv4 address with ipconfig and add it to DJANGO_ALLOWED_HOSTS.", flush=True)
    if not args.no_browser:
        threading.Thread(target=browser_when_ready, args=(url,), daemon=True).start()
    command = [sys.executable, str(ROOT / "manage.py"), "runserver", f"{host}:{args.port}"]
    if args.no_reload:
        command.append("--noreload")
    print("Keep this terminal open. Ctrl+C stops the server. Python changes reload automatically.\n", flush=True)
    try:
        return subprocess.run(command, cwd=ROOT, env=env).returncode
    except KeyboardInterrupt:
        print("\nServer stopped.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
