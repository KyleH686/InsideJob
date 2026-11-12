# Inside Job for iOS

A native iOS wrapper around the game, made with Capacitor 8 (Swift Package Manager, no CocoaPods). The game itself is bundled inside the app, so it runs offline.

## Run it on your iPhone

You need a Mac with the latest Xcode (free from the Mac App Store) and an Apple ID.

1. Get the repo onto the Mac (`git clone https://github.com/KyleH686/InsideJob.git`, or download the ZIP from GitHub).
2. Open `app/ios/App/App.xcodeproj` in Xcode. The first time, Xcode downloads the Capacitor package, which needs the internet and takes a minute.
3. Click **App** at the top of the left sidebar, choose the **App** target, then the **Signing & Capabilities** tab. Tick **Automatically manage signing** and pick your **Team** (your Apple ID).
4. If Xcode says the bundle identifier is taken, change `com.kyleh686.insidejob` to something of your own.
5. Plug in the iPhone, pick it in the device menu at the top, and press **Run** (the play button).
6. The first time, the phone asks you to trust the developer: Settings > General > VPN & Device Management.

With a free Apple ID the app works for 7 days before it needs running from Xcode again. A paid Apple Developer account (99 USD a year) removes that limit and allows TestFlight and the App Store.

## What is in here

- `ios/App/App.xcodeproj`: the Xcode project.
- `ios/App/App/public/`: the game (`index.html`) and its fonts. This is what the app shows.
- `ios/App/App/Assets.xcassets/`: app icon and launch screen image.
- `ios/App/App/Info.plist`: app name, orientations, hidden status bar.
- `capacitor.config.json`: Capacitor settings (copied into the Xcode project).

## Updating the game inside the app

Each new version of the game replaces `ios/App/App/public/index.html`. Pull the repo and press Run again.

## Before an App Store release

- The guard voices use the Piper `en_US-ryan-high` model, which is licensed CC BY-NC-SA (non-commercial). Swap them before selling the app.
- Bump the version and build number in the target's General tab.
- Sound effects are Kenney (CC0), characters are KayKit (CC0), fonts are SIL Open Font License.

## Not yet tested

This project was generated and checked on Linux. It has not been built in Xcode yet, so the first build on a Mac is the real test.
