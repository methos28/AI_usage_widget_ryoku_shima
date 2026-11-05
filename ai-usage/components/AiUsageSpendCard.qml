pragma ComponentBehavior: Bound

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

    Column {
        id: body
        x: page.pad
        y: page.pad
        width: card.width - 2 * page.pad
        spacing: page.step * 3

        Item {
            width: parent.width
            height: spendTitle.implicitHeight
            IrisText {
                id: spendTitle
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
                text: "Spending"
                font.pixelSize: Math.round(12 * IrisStyle.density)
                font.weight: IrisStyle.weight(Font.DemiBold)
            }
            IrisText {
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                role: IrisText.Meta
                color: IrisStyle.muted
                font.pixelSize: Math.round(10 * IrisStyle.density)
                text: page.hasCostHistory ? "This month" : "API value"
            }
        }

        Item {
            width: parent.width
            height: spendMetric.implicitHeight
            Row {
                id: spendRow
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
                spacing: Math.round(6 * IrisStyle.density)
                IrisText {
                    id: spendMetric
                    role: IrisText.Metric
                    text: page.money(page.hasCostHistory ? page.monthly.current : page.periodCost)
                    font.pixelSize: Math.round(24 * IrisStyle.density)
                }
                IrisText {
                    anchors.baseline: spendMetric.baseline
                    role: IrisText.Meta
                    color: IrisStyle.muted
                    font.pixelSize: Math.round(10 * IrisStyle.density)
                    text: page.hasCostHistory
                        ? page.monthly.label
                        : page.periodNoun
                }
            }
        }

        IrisText {
            width: parent.width
            visible: !page.hasCostHistory
            role: IrisText.Meta
            color: IrisStyle.muted
            font.pixelSize: Math.round(10 * IrisStyle.density)
            text: "No cost recorded in this cache."
        }
    }
}

// One foldable card's header: title left, accessories right, chevron far
