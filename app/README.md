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
- `ios/App/App/public/`: the loader (`index.html`), the game (`game.html`), `version.json` and the fonts. This is what the app shows.
- `ios/App/App/Assets.xcassets/`: app icon and launch screen image.
- `ios/App/App/Info.plist`: app name, orientations, hidden status bar.
- `capacitor.config.json`: Capacitor settings (copied into the Xcode project).

## Updating the game inside the app

The app updates itself. Each time it opens it asks GitHub Pages whether a newer version of the game is live. If there is one it downloads it (about 6.5 MB, a few seconds), keeps it on the phone and starts it. Game saves are kept.

- No connection, a slow connection or a damaged download: the app starts the newest copy it already has. It always works offline.
- An update that fails to start twice is dropped and the app goes back to the copy it was built with.
- **Skip** on the update screen starts the copy already on the phone.

You only need to rebuild from Xcode when the app itself changes (icon, name, settings, this loader), or, with a free Apple ID, every 7 days when the signing runs out.

How it works: `public/index.html` is a small loader, `public/game.html` is the game built into the app, and `public/version.json` is the version, size and checksum. The same folder is served at `https://kyleh686.github.io/InsideJob/app/ios/App/App/public/`, which is where installed apps look. Updates only change the game page. A future version that needs new files inside the app would raise `shell` in `version.json`, and older apps would then wait for a rebuild.

Note for the App Store: Apple allows updating web content this way as long as the app's purpose does not change.

## Before an App Store release

- The guard voices (15 short lines) use the Piper `en_US-ryan-high` model, which is licensed CC BY-NC-SA (non-commercial). Swap them before selling the app. Control's voice is Kokoro (Apache 2.0) and is fine to sell.
- Bump the version and build number in the target's General tab.
- Sound effects are Kenney (CC0), characters are KayKit (CC0), fonts are SIL Open Font License.

## Not yet tested

This project was generated and checked on Linux. The first Xcode build worked and ran on an iPhone. The self-updating loader was tested in Chromium against a stand-in server (offline, slow, damaged and broken updates) but not yet on a real iPhone.
