import UIKit
import Capacitor

class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    var window: UIWindow?

    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options connectionOptions: UIScene.ConnectionOptions) {
        guard let windowScene = scene as? UIWindowScene else { return }

        window = UIWindow(windowScene: windowScene)
        window?.rootViewController = CAPBridgeViewController()
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
