#!/usr/bin/env bash
set -euo pipefail

XVFB_WHD=${XVFB_WHD:-1920x1080x24}

Xvfb :99 -screen 0 "$XVFB_WHD" &
export DISPLAY=:99

x11vnc -display :99 -forever -nopw -shared -rfbport 5900 &

websockify --web=/usr/share/novnc/ 6080 localhost:5900
