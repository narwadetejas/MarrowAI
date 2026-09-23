#!/usr/bin/env bash
set -e
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip python3-tk ffmpeg espeak-ng git curl xdotool
curl -fsSL https://ollama.com/install.sh | sh
echo 'MarrowAI dependencies installed.'
