import UIKit
import Capacitor
import GameKit

// v56: the game's own bridge view controller, so the app can register its Game Center plugin
class GameBridgeViewController: CAPBridgeViewController {
    override func capacitorDidLoad() {
        bridge?.registerPluginInstance(GameCenterPlugin())
    }
}

// v56: Game Center (sign in, leaderboards, achievements). The game calls it from JavaScript as Capacitor.Plugins.GameCenter.
// Every method quietly does nothing until the player is signed in, so the game never waits on it.
@objc(GameCenterPlugin)
public class GameCenterPlugin: CAPPlugin, CAPBridgedPlugin, GKGameCenterControllerDelegate {
    public let identifier = "GameCenterPlugin"
    public let jsName = "GameCenter"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "signIn", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "submitScore", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "unlockAchievement", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "showDashboard", returnType: CAPPluginReturnPromise)
    ]
    private var answered = false

    @objc func signIn(_ call: CAPPluginCall) {
        DispatchQueue.main.async {
            if GKLocalPlayer.local.isAuthenticated { call.resolve(["authenticated": true]); return }
            self.answered = false
            GKLocalPlayer.local.authenticateHandler = { [weak self] vc, error in
                guard let self = self else { return }
                if let vc = vc { self.bridge?.viewController?.present(vc, animated: true); return }
                if !self.answered { self.answered = true; call.resolve(["authenticated": GKLocalPlayer.local.isAuthenticated, "error": error?.localizedDescription ?? ""]) }
            }
        }
    }

    @objc func submitScore(_ call: CAPPluginCall) {
        guard GKLocalPlayer.local.isAuthenticated, let id = call.getString("leaderboard") else { call.resolve(["ok": false]); return }
        let score = call.getInt("score") ?? 0
        GKLeaderboard.submitScore(score, context: 0, player: GKLocalPlayer.local, leaderboardIDs: [id]) { error in
            call.resolve(["ok": error == nil])
        }
    }

    @objc func unlockAchievement(_ call: CAPPluginCall) {
        guard GKLocalPlayer.local.isAuthenticated, let id = call.getString("id") else { call.resolve(["ok": false]); return }
        let a = GKAchievement(identifier: id)
        a.percentComplete = 100
        a.showsCompletionBanner = call.getBool("banner") ?? false
        GKAchievement.report([a]) { error in call.resolve(["ok": error == nil]) }
    }

    @objc func showDashboard(_ call: CAPPluginCall) {
        DispatchQueue.main.async {
            guard GKLocalPlayer.local.isAuthenticated else { call.resolve(["ok": false]); return }
            let vc: GKGameCenterViewController
            if let id = call.getString("leaderboard") {
                vc = GKGameCenterViewController(leaderboardID: id, playerScope: .global, timeScope: .allTime)
            } else {
                vc = GKGameCenterViewController(state: .dashboard)
            }
            vc.gameCenterDelegate = self
            self.bridge?.viewController?.present(vc, animated: true)
            call.resolve(["ok": true])
        }
    }

    public func gameCenterViewControllerDidFinish(_ gameCenterViewController: GKGameCenterViewController) {
        gameCenterViewController.dismiss(animated: true)
    }
}

class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    var window: UIWindow?

    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options connectionOptions: UIScene.ConnectionOptions) {
        guard let windowScene = scene as? UIWindowScene else { return }

        window = UIWindow(windowScene: windowScene)
        window?.rootViewController = GameBridgeViewController()
        window?.makeKeyAndVisible()

        SceneDelegateProxy.shared.scene(scene, willConnectTo: session, options: connectionOptions)
        applyFoldOrientation(windowScene)
    }

    // Folding iPhones: the closed (cover) screen is small and nearly square, so the game turns upright there and stays
    // portrait; opened up, it follows the way the phone is held again. Ordinary iPhones and iPads are never affected.
    private var lastFolded: Bool?

    func windowScene(_ windowScene: UIWindowScene, didUpdate previousCoordinateSpace: UICoordinateSpace,
                     interfaceOrientation previousInterfaceOrientation: UIInterfaceOrientation,
                     traitCollection previousTraitCollection: UITraitCollection) {
        applyFoldOrientation(windowScene)
    }

    private func isFolded(_ windowScene: UIWindowScene) -> Bool {
        guard UIDevice.current.userInterfaceIdiom == .phone else { return false }
        let size = windowScene.screen.bounds.size
        let short = min(size.width, size.height), long = max(size.width, size.height)
        return short > 0 && short < 520 && long / short < 1.6
    }

    private func applyFoldOrientation(_ windowScene: UIWindowScene) {
        let folded = isFolded(windowScene)
        if folded == lastFolded { return }
        lastFolded = folded
        AppDelegate.orientationMask = folded ? .portrait : .allButUpsideDown
        if #available(iOS 16.0, *) {
            window?.rootViewController?.setNeedsUpdateOfSupportedInterfaceOrientations()
            if folded {
                windowScene.requestGeometryUpdate(.iOS(interfaceOrientations: .portrait)) { _ in }
            }
        } else {
            UIViewController.attemptRotationToDeviceOrientation()
        }
    }

    func scene(_ scene: UIScene, openURLContexts URLContexts: Set<UIOpenURLContext>) {
        SceneDelegateProxy.shared.scene(scene, openURLContexts: URLContexts)
    }

    func scene(_ scene: UIScene, continue userActivity: NSUserActivity) {
        SceneDelegateProxy.shared.scene(scene, continue: userActivity)
    }
}
