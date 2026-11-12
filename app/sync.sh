#!/bin/sh
# Refresh the iOS app's copy of the game after a new build.
# Run from the build folder: python3 build.py && sh sync.sh <path to this app folder>
# build.py writes ios/index.html (loader), ios/game.html (the game: offline fonts, safe areas) and ios/version.json.
# This copies them into the Xcode project. Once merged to main, installed apps pick the new version up by themselves.
set -e
APP="${1:-.}"
cp ios/index.html ios/game.html ios/version.json "$APP/ios/App/App/public/"
mkdir -p "$APP/ios/App/App/public/fonts" && cp ios/fonts/* "$APP/ios/App/App/public/fonts/"
echo "iOS web assets updated"
