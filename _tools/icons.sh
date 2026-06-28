#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ASSETS_BASE_DIR="${SCRIPT_DIR}/../assets"
SVG="${ASSETS_BASE_DIR}/pyshallow.svg"

if [ ! -f "${SVG}" ]; then
    printf -- "Error: %s not found\n" "${SVG}"
    exit 1
fi

if ! command -v rsvg-convert &> /dev/null; then
    printf -- "Error: rsvg-convert not found. Install librsvg / librsvg2-bin\n"
    exit 1
fi

HAS_CONVERT="1"
if ! command -v magick &> /dev/null; then
    printf -- "Warning: convert not found. Install imagemagick\n"
    HAS_CONVERT=
fi

# Linux .png
printf -- "Generate Linux png\n"
ASSETS_DIR="${ASSETS_BASE_DIR}/linux"
ICON_BASE="pyshallow.png"
ICON="${ASSETS_DIR}/${ICON_BASE}"
mkdir -p "${ASSETS_DIR}"
rsvg-convert -w 128 -h 128 "${SVG}" -o "${ICON}"
printf -- "Created %s\n" "${ICON}"

# macOS .icns
printf -- "Generate MacOS icons\n"
ASSETS_DIR="${ASSETS_BASE_DIR}/macos"
ICONSET="${ASSETS_DIR}/pyshallow.iconset"
ICON_BASE="pyshallow.icns"
ICON="${ASSETS_DIR}/${ICON_BASE}"
mkdir -p "${ICONSET}"
for size in 16 32 128 256 512; do
    rsvg-convert -w ${size} -h ${size} "${SVG}" -o "${ICONSET}/icon_${size}x${size}.png"
    size2=$((size * 2))
    rsvg-convert -w ${size2} -h ${size2} "${SVG}" -o "${ICONSET}/icon_${size}x${size}@2x.png"
done
if [ "$(uname)" = "Darwin" ]; then
    iconutil -c icns -o "${ICON}" "${ICONSET}"
    rm -rf "${ICONSET}"
    printf -- "Created %s\n" "${ICON}"
else
    printf -- "Skipping .icns creation (macOS only)\n"
fi

# Windows .ico
printf -- "Generate Windows icons\n"
ASSETS_DIR="${ASSETS_BASE_DIR}/windows"
ICONSET="${ASSETS_DIR}/pyshallow.icons"
ICON_FILES=()
ICON_BASE="pyshallow.ico"
ICON="${ASSETS_DIR}/${ICON_BASE}"
mkdir -p "${ICONSET}"
for size in 16 32 48 256; do
    _file="${ICONSET}/icon_${size}.png"
    rsvg-convert -w ${size} -h ${size} "${SVG}" -o "${_file}"
    ICON_FILES+=("${_file}")
done

if [ -n "${HAS_CONVERT}" ]; then
    magick "${ICON_FILES[@]}" "${ICON}"
    rm -rf "${ICONSET}"
    printf -- "Created %s\n" "${ICON}"
else
    printf -- "Skipping .ico creation (imagemagick not found)\n"
fi
