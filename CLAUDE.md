# Working on Inside Job

## Building
- `cd src && python3 build.py` builds everything from the repo. It writes `src/web/index.html` (copy to the repo root as `index.html`) and `src/ios/` (`game.html`, `index.html`, `version.json`, copy to `app/ios/App/App/public/`).

## Version numbers (always)
- Bump the game version (`Inside Job · vNN · ` in `src/src.html`) **before** any build is copied into `app/ios/App/App/public/` or the repo root, or shipped. One version number = one build.
- Never reuse a version number, even for a quick fix. The iOS app's loader only downloads an update when the live version is **higher** than the copy it already has, so a phone installed from Xcode with an earlier build of the same number never updates.
- Only raise `shell` in `version.json` when the app shell itself changes in a way older apps can't run. That stops older apps from updating until they're rebuilt in Xcode.

## Shipping
- Don't push, open PRs or merge until Kyle says "ship it".
- Leave the local `app/ios/App/App.xcodeproj/project.pbxproj` signing change (Kyle's Team) and `project.xcworkspace/xcshareddata/swiftpm/` out of commits.
