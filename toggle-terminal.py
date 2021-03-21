#!/usr/bin/env python

"""
Script for toggling terminal on Linux with a single keypress
(like iTerm2 on mac).
"""

import os.path
import sys
import shlex
import traceback
import subprocess

# -------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------

# Change this to the process name of your terminal
TERMINAL = 'terminator'

# -------------------------------------------------------------------------- #
# Types
# --------------------------------------------------------------------------

ID = int
WindowID = ID
PID = ID
Desktop = int

# -------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------

def main():
    """
    Toggle between terminal and the last active screen.
    """
    terminal_pid = get_terminal_pid()
    active_window_id = get_active_window()
    active_window_pid = get_window_pid(active_window_id)
    if terminal_pid == active_window_pid:
        move_terminal_to_background(active_window_id)
    else:
        move_terminal_to_foreground(terminal_pid)

def move_terminal_to_background(active_window_id : WindowID):
    seen_window = False

    current_desktop_no = get_current_desktop_no()
    window_stack = get_window_stack()
    for window_id in reversed(window_stack):
        if window_id == active_window_id:
            seen_window = True
            continue

        if seen_window and get_desktop_no(window_id) == current_desktop_no:
            log(f"Selecting window: {window_id}")
            activate_window(window_id)
            break

def move_terminal_to_foreground(terminal_pid : PID):
    current_desktop_no = get_current_desktop_no()
    for window_id in get_window_stack():
        is_terminal = get_window_pid(window_id) == terminal_pid
        is_same_desktop = get_desktop_no(window_id) == current_desktop_no
        if is_terminal and is_same_desktop:
            activate_window(window_id)

# -------------------------------------------------------------------------- #
# Windowing Utilities
# -------------------------------------------------------------------------- #

def get_window_stack() -> [WindowID]:
    out = shell("xprop -root | grep '_NET_CLIENT_LIST_STACKING(WINDOW)'")
    return [int(id.strip(), 16) for id in out.split(': window id #')[1].split(',')]

def get_active_window() -> WindowID:
    return int(shell(f"xdotool getwindowfocus"))

def get_terminal_pid() -> PID:
    return int(shell(f"ps ax | grep -v grep | grep {TERMINAL} | awk '{{ print $1 }}' | head -n 1"))

def get_window_pid(window_id : WindowID) -> PID:
    return int(shell(f"xdotool getwindowpid {window_id}"))

def get_current_desktop_no() -> Desktop:
    return int(shell(f'xdotool get_desktop'))

def get_desktop_no(window_id : WindowID) -> Desktop:
    return int(shell(f'xdotool get_desktop_for_window {window_id}'))

def activate_window(window_id: WindowID):
    shell(f"xdotool windowactivate {window_id}")

# -------------------------------------------------------------------------- #
# Helpers
# -------------------------------------------------------------------------- #

log_file = open(os.path.expanduser('~/toggle-terminal.log'), 'a')

def log(msg):
    log_file.write(msg + "\n")
    log_file.flush()

def shell(cmd : str):
    p = subprocess.run(cmd, shell=True, capture_output=True)
    out, err = p.stdout.strip().decode('utf8'), p.stderr.strip().decode('utf8')
    if err:
        log(err)
    return out


if __name__ == '__main__':
    log("Toggling terminal")
    try:
        main()
    except BaseException:
        log(traceback.format_exc())