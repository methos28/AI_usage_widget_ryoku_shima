pragma ComponentBehavior: Bound

import QtQuick
import inir.modules.iris.style

QtObject {
    id: root

    property real targetValue: 0
    property bool available: true
    property bool active: true
    property bool hold: false
    property string contextKey: ""
    property int duration: IrisStyle.duration(380)
    property int fadeDuration: IrisStyle.duration(180)
    property bool motionEnabled: IrisStyle.motionEnabled && IrisStyle.morphName !== "instant"

    property real value: 0
    property real opacity: 0
    property bool hasValue: false
    property bool _ready: false
    property bool _initialized: false
    property string _context: ""
    readonly property var easingCurve: IrisStyle.curves.gentle.concat([1, 1])

    // Parsing clears and fills the model in one turn. Present only the settled
    // snapshot, so a refresh cannot animate through a temporary zero or dash.
    function schedule(): void {
        if (root._ready) Qt.callLater(root.update)
    }

    function update(): void {
        const moving = root.active && root.motionEnabled
        if (!moving) {
            root.tween.stop()
            root.fade.stop()
            root.opacity = 1
        }
        if (root.hold) return
        const valid = root.available && Number.isFinite(root.targetValue)
        const changedContext = root._context !== root.contextKey
        const changedState = !root._initialized || root.hasValue !== valid || changedContext
        const count = moving && root.duration > 0 && root._initialized
            && root.hasValue && valid && !changedContext
        if (root.tween.running && count && root.tween.to === root.targetValue) return
        root.tween.stop()
        if (count && root.value !== root.targetValue) {
            root.tween.from = root.value
            root.tween.to = root.targetValue
            root.tween.start()
        } else if (valid) {
            root.value = root.targetValue
        }
        root.hasValue = valid
        root._context = root.contextKey
        root._initialized = true
        if (changedState) {
            root.fade.stop()
            root.opacity = moving && root.fadeDuration > 0 ? 0 : 1
            if (root.opacity === 0) root.fade.start()
        }
    }

    readonly property NumberAnimation tween: NumberAnimation {
        target: root
        property: "value"
        duration: root.duration
        easing.type: Easing.BezierSpline
        easing.bezierCurve: root.easingCurve
    }
    readonly property NumberAnimation fade: NumberAnimation {
        target: root
        property: "opacity"
        from: 0
        to: 1
        duration: root.fadeDuration
        easing.type: Easing.BezierSpline
        easing.bezierCurve: root.easingCurve
    }

    onTargetValueChanged: root.schedule()
    onAvailableChanged: root.schedule()
    onActiveChanged: root.schedule()
    onHoldChanged: {
        if (root.hold) {
            root.tween.stop()
            root.fade.stop()
            root._initialized = false
            root.hasValue = false
            root.opacity = 0
        }
        root.schedule()
    }
    onContextKeyChanged: root.schedule()
    onMotionEnabledChanged: root.schedule()
    onDurationChanged: root.schedule()
    Component.onCompleted: { root._ready = true; root.schedule() }
}
