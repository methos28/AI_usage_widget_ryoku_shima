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

    AiUsageSpendBody {
        id: body
        page: card.page
        anchors.fill: parent
        anchors.margins: page.pad
    }
}
