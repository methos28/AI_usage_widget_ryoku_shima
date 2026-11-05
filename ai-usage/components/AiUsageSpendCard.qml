pragma ComponentBehavior: Bound

// The standalone Spending card OpenCode shows beside Now. The figures are the
// shared body, so this card is only the glass around them.
import QtQuick
import QtQuick.Effects
import Quickshell
import Quickshell.Widgets
import inir
import inir.services
import inir.modules.common
import inir.modules.common.widgets
import inir.modules.common.functions
import inir.modules.iris.style
import inir.modules.iris.components

AiUsageGlassCard {
    required property var usage
    id: card
    radius: page.radius
    implicitHeight: body.implicitHeight + 2 * page.pad
    // The primary row stretches this card to its neighbours' height. Centre the
    // shared body instead of pinning it to the top, so a taller Now card beside
    // it does not leave a blank strip under the figures. At the content-sized
    // height the offset is exactly page.pad, so the card looks unchanged.
    readonly property real spareHeight: card.height - card.implicitHeight

    AiUsageSpendBody {
        id: body
        page: card.page
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.leftMargin: page.pad
        anchors.rightMargin: page.pad
        height: implicitHeight
        y: page.pad + Math.round(Math.max(0, card.spareHeight) / 2)
    }
}
