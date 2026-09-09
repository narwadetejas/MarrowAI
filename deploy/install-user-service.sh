#!/bin/sh
set -eu

project_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
service_dir="${XDG_CONFIG_HOME:-$HOME/.config}/systemd/user"
service_path="$service_dir/marrowai.service"

mkdir -p "$service_dir"
sed "s#__PROJECT_DIR__#$project_dir#g" "$project_dir/deploy/systemd/marrowai.service" > "$service_path"
systemctl --user daemon-reload
systemctl --user enable --now marrowai.service
printf 'MarrowAI user service enabled at %s\n' "$service_path"
