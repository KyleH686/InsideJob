#!/bin/sh
# Refresh the iOS app's copy of the game after a new build.
# Run from the build folder: python3 build.py && sh sync.sh <path to this app folder>
# build.py writes ios/index.html (offline fonts, safe areas); this copies it into the Xcode project.
set -e
APP="${1:-.}"
cp ios/index.html "$APP/ios/App/App/public/index.html"
mkdir -p "$APP/ios/App/App/public/fonts" && cp ios/fonts/* "$APP/ios/App/App/public/fonts/"
echo "iOS web assets updated"
