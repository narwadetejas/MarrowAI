#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
VERSION="0.2.0"
ARCH="amd64"
PACKAGE_NAME="marrowai"
OUTPUT_DEB="${PACKAGE_NAME}_${VERSION}_${ARCH}.deb"

# Use /tmp for staging to preserve Linux POSIX permissions even when building on NTFS mounts (e.g. WSL)
STAGING_DIR="$(mktemp -d /tmp/marrowai_deb_XXXXXX)"
BUILD_ROOT="${STAGING_DIR}/${PACKAGE_NAME}_${VERSION}_${ARCH}"

trap 'rm -rf "$STAGING_DIR"' EXIT

mkdir -p "$BUILD_ROOT/DEBIAN" "$BUILD_ROOT/usr/bin" "$BUILD_ROOT/opt/marrowai/python"

cp -R src/marrowai "$BUILD_ROOT/opt/marrowai/python/"
find "$BUILD_ROOT" -type d -name __pycache__ -prune -exec rm -rf {} +

cat > "$BUILD_ROOT/DEBIAN/control" <<EOF
Package: ${PACKAGE_NAME}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: ${ARCH}
Depends: python3, python3-tk, ffmpeg, espeak-ng, git, curl, xdotool
Maintainer: MarrowAI Team <team@marrowai.local>
Description: Offline-first local assistant with safe planning, voice, and scaffolding
EOF

cat > "$BUILD_ROOT/DEBIAN/postinst" <<'EOF'
#!/usr/bin/env bash
set -e

if ! command -v ollama >/dev/null 2>&1; then
	echo "Installing Ollama for MarrowAI..."
	if ! curl -fsSL https://ollama.com/install.sh | sh; then
		echo "Warning: Ollama installation failed. Run 'marrowai-setup' later to retry." >&2
	fi
fi

if command -v systemctl >/dev/null 2>&1 && systemctl list-unit-files ollama.service >/dev/null 2>&1; then
	systemctl enable --now ollama.service || true
fi

exit 0
EOF

cat > "$BUILD_ROOT/usr/bin/marrowai" <<'EOF'
#!/usr/bin/env bash
export PYTHONPATH="/opt/marrowai/python${PYTHONPATH:+:${PYTHONPATH}}"
exec python3 -m marrowai.cli "$@"
EOF

cat > "$BUILD_ROOT/usr/bin/marrowai-doctor" <<'EOF'
#!/usr/bin/env bash
export PYTHONPATH="/opt/marrowai/python${PYTHONPATH:+:${PYTHONPATH}}"
exec python3 -m marrowai.doctor "$@"
EOF

cat > "$BUILD_ROOT/usr/bin/marrowai-chat" <<'EOF'
#!/usr/bin/env bash
export PYTHONPATH="/opt/marrowai/python${PYTHONPATH:+:${PYTHONPATH}}"
exec python3 -m marrowai.interactive "$@"
EOF

cat > "$BUILD_ROOT/usr/bin/marrowai-gui" <<'EOF'
#!/usr/bin/env bash
export PYTHONPATH="/opt/marrowai/python${PYTHONPATH:+:${PYTHONPATH}}"
exec python3 -m marrowai.gui "$@"
EOF

cat > "$BUILD_ROOT/usr/bin/marrowai-web" <<'EOF'
#!/usr/bin/env bash
export PYTHONPATH="/opt/marrowai/python${PYTHONPATH:+:${PYTHONPATH}}"
exec python3 -m marrowai.web_gui "$@"
EOF

cat > "$BUILD_ROOT/usr/bin/marrowai-scaffold" <<'EOF'
#!/usr/bin/env bash
export PYTHONPATH="/opt/marrowai/python${PYTHONPATH:+:${PYTHONPATH}}"
exec python3 -m marrowai.scaffold "$@"
EOF

cat > "$BUILD_ROOT/usr/bin/marrowai-voice" <<'EOF'
#!/usr/bin/env bash
export PYTHONPATH="/opt/marrowai/python${PYTHONPATH:+:${PYTHONPATH}}"
exec python3 -m marrowai.voice_engine "$@"
EOF

cat > "$BUILD_ROOT/usr/bin/marrowai-setup" <<'EOF'
#!/usr/bin/env bash
export PYTHONPATH="/opt/marrowai/python${PYTHONPATH:+:${PYTHONPATH}}"
exec python3 -m marrowai.ubuntu_setup "$@"
EOF

chmod 755 "$BUILD_ROOT/usr/bin"/*
chmod 755 "$BUILD_ROOT/DEBIAN" "$BUILD_ROOT/opt" "$BUILD_ROOT/opt/marrowai" "$BUILD_ROOT/opt/marrowai/python"
chmod 644 "$BUILD_ROOT/DEBIAN/control"
chmod 755 "$BUILD_ROOT/DEBIAN/postinst"

mkdir -p dist
dpkg-deb --build --root-owner-group "$BUILD_ROOT" "${STAGING_DIR}/${OUTPUT_DEB}"

cp "${STAGING_DIR}/${OUTPUT_DEB}" "$OUTPUT_DEB"
cp "${STAGING_DIR}/${OUTPUT_DEB}" "dist/${OUTPUT_DEB}"

printf '\nCreated: %s and dist/%s\n' "$OUTPUT_DEB" "$OUTPUT_DEB"
ls -lh "$OUTPUT_DEB"
