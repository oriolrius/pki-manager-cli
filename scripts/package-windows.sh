#!/usr/bin/env bash
# Build the Windows x86-64 (MSVC) package on Linux or WSL, with the same layout as the
# release workflow: dist/pki-cli-<version>-x86_64-pc-windows-msvc.zip
#
# Needs: rustup, clang and lld (Debian/Ubuntu: apt install clang lld), zip, and
# cargo-xwin (cargo install --locked cargo-xwin). cargo-xwin downloads the MSVC CRT and
# the Windows SDK to ~/.cache/cargo-xwin the first time; by using it you accept the
# Microsoft license of those files.
set -euo pipefail
cd "$(dirname "$0")/.."

target=x86_64-pc-windows-msvc
version=$(sed -n 's/^version = "\(.*\)"/\1/p' Cargo.toml | head -1)
name="pki-cli-${version}-${target}"

for tool in clang lld-link zip cargo-xwin; do
  command -v "$tool" >/dev/null || { echo "missing: $tool (see the header of $0)" >&2; exit 1; }
done
rustup target add "$target" >/dev/null

# Static CRT: the .exe needs no Visual C++ redistributable.
# /ignore:4099: the MSVC CRT ships no PDB files; skip the debug-info warnings.
RUSTFLAGS="-C target-feature=+crt-static -C link-arg=/ignore:4099" \
  cargo xwin build --release --locked --target "$target"

exe="target/${target}/release/pki.exe"
staging=$(mktemp -d)
trap 'rm -rf "$staging"' EXIT
mkdir -p dist "$staging/$name"
cp README.md LICENSE "$exe" "$staging/$name/"
rm -f "dist/${name}.zip"
(cd "$staging" && zip -qr "$OLDPWD/dist/${name}.zip" "$name")
echo "dist/${name}.zip"

# On WSL, run the .exe on Windows as a check.
if grep -qi microsoft /proc/version 2>/dev/null; then
  "$exe" --version
fi
