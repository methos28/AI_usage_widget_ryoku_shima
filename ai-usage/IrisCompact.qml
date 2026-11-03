pragma ComponentBehavior: Bound

// AI usage — the Shima Island's AI page, laid out like Vorssaint's Dynamic
// Island page: a grid of small cards.
//
//   [ Limits | Now ]  ← Limits only when the cache reports a real plan
//   [    Trend     ]
//   [    Models    ]
//
// Every card is an IrisSurface on Shima tokens; the data is the shared usage
// cache (~/.cache/<tool>-usage.json) and nothing here writes usage anywhere.
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

Item {
    id: root

    property string irisSlot: ""
    property var targetScreen

    // ── config (written by Shima Settings; read null-guarded here) ──
    readonly property string tool: CustomWidgets.getConfigValue("ai-usage", "tool", "opencode")
    readonly property var labels: ({ opencode: "OpenCode", claude: "Claude" })
    readonly property string toolLabel: root.labels[root.tool] ?? root.tool

    // The Island's Desktop page body is iris.bar.pageWidth minus its 20px
    // padding each side; a wider card would overflow the chassis and clip.
    readonly property int pageBody: Math.max(280,
        Math.max(360, Math.min(600, Number(Config.options?.iris?.bar?.pageWidth ?? 440)))
        - 2 * Math.round(20 * IrisStyle.density))
    readonly property int cardWidth: Math.max(280, Math.min(root.pageBody,
        Number(CustomWidgets.getConfigValue("ai-usage", "moduleWidth", 480))))
    readonly property int topModels: Math.max(1, Math.min(3,
        Number(CustomWidgets.getConfigValue("ai-usage", "topModels", 3))))

    readonly property var periodOptions: [
        { value: "today", label: "Today" },
        { value: "24h", label: "Last 24 hours" },
        { value: "7", label: "Last 7 days" },
        { value: "30", label: "Last 30 days" },
        { value: "all", label: "All time" }
    ]
    readonly property string periodKey: {
        const stored = String(CustomWidgets.getConfigValue("ai-usage", "period", "30"))
        return ["today", "24h", "7", "30", "all"].includes(stored) ? stored : "30"
    }
    readonly property bool hourly: root.periodKey === "today" || root.periodKey === "24h"
    readonly property int periodDays: root.periodKey === "all" ? 0 : Number(root.periodKey)
    readonly property string periodLabel: {
        const option = root.periodOptions.find(entry => entry.value === root.periodKey)
        return option ? option.label : "Last 30 days"
    }
    readonly property string periodNoun: root.periodLabel.toLowerCase()

    readonly property int pad: Math.round(10 * IrisStyle.density)
    readonly property int gap: Math.round(10 * IrisStyle.density)
    readonly property int radius: IrisStyle.radiusTile
    readonly property int step: Math.round(2 * IrisStyle.density)

    implicitWidth: root.cardWidth
    implicitHeight: grid.implicitHeight

    UsageModel {
        id: usage
        tool: root.tool
    }

    // Everything on the page follows this one period.
    readonly property var activePeriod: usage.period(root.periodKey)
    readonly property var periodModels: root.activePeriod ? root.activePeriod.models : []
    readonly property int periodTokens: root.activePeriod
        ? Number(root.activePeriod.tokens) : usage.today
    readonly property real periodCacheRate: root.activePeriod
        ? Number(root.activePeriod.cacheRate) : 0
    readonly property real periodCost: root.activePeriod
        ? Number(root.activePeriod.cost) : 0
    readonly property bool hasSpend: root.periodCost > 0.0005
    readonly property bool hasPlan: usage.hasPlan

    // Layout 1 was the single long card, layout 2 the fixed 60/90/180 control.
    // Run once, then the stored values are the person's own.
    Component.onCompleted: {
        const version = Number(CustomWidgets.getConfigValue("ai-usage", "layoutVersion", 1))
        if (version < 2) {
            CustomWidgets.setConfigValue("ai-usage", "moduleWidth", 480)
            CustomWidgets.setConfigValue("ai-usage", "topModels", 3)
        }
        if (version < 3) {
            const stored = String(CustomWidgets.getConfigValue("ai-usage", "period", "30"))
            if (!["7", "30", "all"].includes(stored))
                CustomWidgets.setConfigValue("ai-usage", "period", "30")
            CustomWidgets.setConfigValue("ai-usage", "layoutVersion", 3)
        }
    }

    // ── trend buckets: hourly for Today / 24 hours, daily for the rest ──
    readonly property var trend: {
        if (root.hourly) {
            const allHours = usage.hours
            if (!allHours || allHours.length === 0)
                return ({ buckets: [], total: 0, peak: 1, span: 0, unit: "hours" })
            const hourBuckets = []
            let hourTotal = 0
            let hourPeak = 1
            if (root.periodKey === "today") {
                // The whole day as 24 slots, so the shape of the day is the
                // same at 02:00 and at 22:00; hours still to come stay empty.
                const midnight = new Date()
                midnight.setHours(0, 0, 0, 0)
                const byStart = ({})
                for (const hour of allHours)
                    byStart[Number(hour?.start ?? 0)] = root.historyWeight(hour)
                for (let i = 0; i < 24; i++) {
                    const start = midnight.getTime() + i * 3600000
                    const tokens = Number(byStart[start] ?? 0)
                    hourBuckets.push({ start: start, tokens: tokens })
                    hourTotal += tokens
                    hourPeak = Math.max(hourPeak, tokens)
                }
                return ({ buckets: hourBuckets, total: hourTotal, peak: hourPeak,
                         span: 24, unit: "hours" })
            }
            const list = allHours.slice(Math.max(0, allHours.length - 24))
            for (const hour of list) {
                const tokens = root.historyWeight(hour)
                hourBuckets.push({ start: Number(hour?.start ?? 0), tokens: tokens })
                hourTotal += tokens
                hourPeak = Math.max(hourPeak, tokens)
            }
            return ({ buckets: hourBuckets, total: hourTotal, peak: hourPeak,
                     span: list.length, unit: "hours" })
        }
        const all = usage.days
        if (!all || all.length === 0)
            return ({ buckets: [], total: 0, peak: 1, span: 0, unit: "days" })
        const want = root.periodDays > 0 ? root.periodDays : all.length
        const list = all.slice(Math.max(0, all.length - want))
        const weekly = list.length > 100
        const buckets = []
        let total = 0
        let peak = 1
        if (!weekly) {
            for (const day of list) {
                const tokens = root.historyWeight(day)
                buckets.push({ date: String(day?.date ?? ""), tokens: tokens })
                total += tokens
                peak = Math.max(peak, tokens)
            }
        } else {
            const groups = []
            for (let end = list.length; end > 0; end -= 7) {
                const start = Math.max(0, end - 7)
                let tokens = 0
                for (let i = start; i < end; i++) tokens += root.historyWeight(list[i])
                groups.unshift({ date: String(list[start]?.date ?? ""), tokens: tokens })
            }
            for (const group of groups) {
                buckets.push(group)
                total += group.tokens
                peak = Math.max(peak, group.tokens)
            }
        }
        return ({ buckets: buckets, total: total, peak: peak, span: list.length, unit: "days" })
    }
    readonly property var trendBuckets: root.trend.buckets

    // Every chart weighs tokens plus cache reads, like the Activity card.
    function historyWeight(entry) {
        return Number(entry?.tokens ?? 0) + Number(entry?.cacheRead ?? 0)
    }

    function dayLabel(date: string): string {
        const parsed = new Date(String(date) + "T12:00:00")
        if (isNaN(parsed.getTime())) return ""
        return Qt.formatDate(parsed, "d MMM")
    }
    function bucketLabel(bucket: var): string {
        if (root.trend.unit === "hours") {
            const moment = new Date(Number(bucket?.start ?? 0))
            return isNaN(moment.getTime()) ? "" : Qt.formatTime(moment, "HH:mm")
        }
        return root.dayLabel(String(bucket?.date ?? ""))
    }
    function money(value: real): string {
        return "$" + Number(value || 0).toFixed(2)
    }
    function elapsedLabel(startMs: double): string {
        usage.tick   // a binding that calls this re-evaluates when the ticker moves
        const mins = Math.max(0, Math.floor((Date.now() - Number(startMs || 0)) / 60000))
        if (mins < 60) return mins + "m"
        const m = mins % 60
        return Math.floor(mins / 60) + "h " + (m < 10 ? "0" : "") + m + "m"
    }
    function modelDetail(model: var): string {
        if (!model) return ""
        const parts = ["I " + (model.inputLabel || "0"), "O " + (model.outputLabel || "0")]
        if (String(model.reasoningLabel ?? "0") !== "0") parts.push("R " + model.reasoningLabel)
        if (String(model.cacheReadLabel ?? "0") !== "0") parts.push("CR " + model.cacheReadLabel)
        if (String(model.cacheWriteLabel ?? "0") !== "0") parts.push("CW " + model.cacheWriteLabel)
        let text = parts.join("  ")
        if (model.cacheRate !== undefined && model.cacheRate !== null)
            text += " · " + Math.round(Number(model.cacheRate) * 100) + "% cached"
        return text
    }

    // The period menu sits above the grid so no card clips it.
    function openPeriodMenu(trigger: Item): void {
        const point = trigger.mapToItem(root, 0, trigger.height)
        periodMenu.x = Math.max(0, Math.min(root.cardWidth - periodMenu.width,
            Math.round(point.x + (trigger.width - periodMenu.width) / 2)))
        periodMenu.y = Math.max(0, Math.min(Math.round(point.y + 4 * IrisStyle.density),
            Math.round(root.implicitHeight - periodMenu.height - 2)))
        periodMenu.open = true
    }

    Column {
        id: grid
        width: root.cardWidth
        spacing: root.gap

        Row {
            id: primaryRow
            width: parent.width
            spacing: root.gap
            visible: usage.has
            // Spending pairs with Now only when there is no Limits card to
            // pair with; three cards would not fit one row.
            readonly property bool spendHere: root.hasSpend && !root.hasPlan
            readonly property int count: (root.hasPlan ? 1 : 0) + 1 + (spendHere ? 1 : 0)
            readonly property real half: Math.round((width - spacing) / 2)
            readonly property real rowHeight: Math.max(
                root.hasPlan ? limitsCard.implicitHeight : 0,
                nowCard.implicitHeight,
                primaryRow.spendHere ? spendCard.implicitHeight : 0)

            AiLimits {
                id: limitsCard
                visible: root.hasPlan
                width: primaryRow.count > 1 ? primaryRow.half : primaryRow.width
                height: primaryRow.rowHeight
            }
            AiNow {
                id: nowCard
                width: primaryRow.count > 1 ? primaryRow.half : primaryRow.width
                height: primaryRow.rowHeight
            }
            AiSpend {
                id: spendCard
                visible: primaryRow.spendHere
                width: primaryRow.count > 1 ? primaryRow.half : primaryRow.width
                height: primaryRow.rowHeight
            }
        }

        AiSpend {
            width: parent.width
            visible: root.hasSpend && root.hasPlan
        }

        AiTrend {
            width: parent.width
            visible: usage.has && root.trendBuckets.length > 0
        }

        AiModels {
            width: parent.width
            visible: usage.has && root.periodModels.length > 0
        }

        AiActivity {
            width: parent.width
            visible: usage.has && usage.days.length > 0
        }

        AiEmpty {
            width: parent.width
            height: implicitHeight
            visible: !usage.has
        }
    }

    // ── period menu ──────────────────────────────────────────────────────
    MouseArea {
        anchors.fill: parent
        visible: periodMenu.open
        z: 90
        onClicked: periodMenu.open = false
    }
    IrisSurface {
        id: periodMenu
        property bool open: false
        visible: open
        z: 91
        raised: true
        outlined: true
        width: Math.round(158 * IrisStyle.density)
        height: menuColumn.implicitHeight + 2 * Math.round(6 * IrisStyle.density)
        radius: IrisStyle.radiusTile
        Rectangle {
            anchors.fill: parent
            radius: periodMenu.radius
            color: "transparent"
            border.width: 1
            border.color: IrisStyle.borderStrong
        }
        Column {
            id: menuColumn
            x: Math.round(6 * IrisStyle.density)
            y: Math.round(6 * IrisStyle.density)
            width: periodMenu.width - 2 * Math.round(6 * IrisStyle.density)
            Repeater {
                model: root.periodOptions
                Item {
                    id: menuRow
                    required property var modelData
                    width: menuColumn.width
                    height: Math.round(28 * IrisStyle.density)
                    readonly property bool current: menuRow.modelData.value === root.periodKey
                    Rectangle {
                        anchors.fill: parent
                        radius: IrisStyle.radiusSmall
                        color: rowArea.containsMouse ? IrisStyle.fillHover : "transparent"
                    }
                    IrisText {
                        anchors.left: parent.left
                        anchors.leftMargin: Math.round(8 * IrisStyle.density)
                        anchors.verticalCenter: parent.verticalCenter
                        text: menuRow.modelData.label
                        font.pixelSize: IrisStyle.typeLabel
                        color: menuRow.current ? IrisStyle.accent : IrisStyle.text
                    }
                    MaterialSymbol {
                        anchors.right: parent.right
                        anchors.rightMargin: Math.round(8 * IrisStyle.density)
                        anchors.verticalCenter: parent.verticalCenter
                        visible: menuRow.current
                        text: "check"
                        iconSize: Math.round(14 * IrisStyle.density)
                        color: IrisStyle.accent
                    }
                    MouseArea {
                        id: rowArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            CustomWidgets.setConfigValue("ai-usage", "period",
                                String(menuRow.modelData.value))
                            periodMenu.open = false
                        }
                    }
                }
            }
        }
    }

    // ─── cards ───────────────────────────────────────────────────────────

    // A card is a pane of glass: the blurred wallpaper behind the island,
    // clipped to the card radius, under a thin tint and a hairline. The tint
    // keeps the text off the wallpaper's own light and dark patches.
    //
    // The wallpaper image is screen-fixed and its blur is a layer of the image
    // itself, never of the card: a card-sized layer is re-made whenever the
    // page resizes, and the frame it spent rebuilding read as the card going
    // dark. The clip is a ClippingRectangle, which re-masks without a layer.
    component GlassPane: ClippingRectangle {
        id: pane
        radius: root.radius
        // A transparent ClippingRectangle stops painting its children (see
        // IrisIsland's chassis); this is the same near-transparent body clip.
        color: IrisStyle.bodyClip
        readonly property var screen: pane.QsWindow.window?.screen ?? root.targetScreen
        readonly property point at: {
            // mapToItem does not track its ancestors as binding dependencies, so
            // a layout that moves the page (opening, a card growing, a new
            // workspace) left this point at the one it had before the move: the
            // glass sampled the wallpaper near the screen's top edge and read as
            // a dark card until some unrelated resize re-evaluated it. Read every
            // ancestor's position to keep the binding honest.
            let walk = pane
            while (walk) {
                void (walk.x + walk.y)
                walk = walk.parent
            }
            void (pane.width + pane.height)
            return pane.mapToItem(null, 0, 0)
        }

        Image {
            id: wallpaper
            x: -pane.at.x
            y: -pane.at.y
            width: pane.screen?.width ?? 1920
            height: pane.screen?.height ?? 1080
            source: WallpaperListener.wallpaperUrlForScreen(pane.screen)
            fillMode: Image.PreserveAspectCrop
            cache: true
            asynchronous: true
            sourceSize.width: width
            sourceSize.height: height
            visible: status === Image.Ready
            layer.enabled: visible
            layer.effect: MultiEffect {
                source: wallpaper
                anchors.fill: source
                blurEnabled: true
                blurMax: 64
                blur: 1
                saturation: 0.08
            }
        }

        Rectangle {
            anchors.fill: parent
            color: ColorUtils.applyAlpha(IrisStyle.surfaceOpaque, 0.38)
        }
    }

    component GlassCard: IrisSurface {
        id: card
        quiet: true
        radius: root.radius

        GlassPane {
            anchors.fill: parent
            z: -1
        }

        Rectangle {
            anchors.fill: parent
            radius: card.radius
            z: -1
            color: "transparent"
            border.width: 1
            border.color: ColorUtils.applyAlpha(IrisStyle.text, 0.10)
        }
    }

    component AiLimits: GlassCard {
        id: card
        radius: root.radius
        implicitHeight: body.implicitHeight + 2 * root.pad

        Column {
            id: body
            x: root.pad
            y: root.pad
            width: card.width - 2 * root.pad
            spacing: root.step * 3

            Item {
                width: parent.width
                height: Math.max(agentName.implicitHeight, planText.implicitHeight)
                IrisText {
                    id: agentName
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    text: root.toolLabel
                    font.pixelSize: Math.round(12 * IrisStyle.density)
                    font.weight: IrisStyle.weight(Font.DemiBold)
                }
                IrisText {
                    id: planText
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    role: IrisText.Meta
                    color: IrisStyle.muted
                    font.pixelSize: Math.round(10 * IrisStyle.density)
                    text: usage.plan.length > 0 ? usage.plan : ""
                }
            }

            Item {
                width: parent.width
                height: todayRow.implicitHeight
                Row {
                    id: todayRow
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: Math.round(7 * IrisStyle.density)
                    IrisText {
                        id: todayMetric
                        role: IrisText.Metric
                        text: usage.kmg(usage.today)
                        font.pixelSize: Math.round(26 * IrisStyle.density)
                    }
                    IrisText {
                        anchors.baseline: todayMetric.baseline
                        role: IrisText.Meta
                        color: IrisStyle.muted
                        font.pixelSize: Math.round(10 * IrisStyle.density)
                        text: "tokens today"
                    }
                }
            }

            AiWindow {
                width: parent.width
                label: "5h"
                caption: usage.windowTokens
                share: usage.pct5h + "% used"
                proportion: usage.pct5h / 100
            }
            AiWindow {
                width: parent.width
                label: "7d"
                caption: usage.weekTokens
                share: usage.percent7d + "% used"
                proportion: usage.percent7d / 100
            }

            IrisText {
                width: parent.width
                visible: usage.has && !usage.fresh
                role: IrisText.Meta
                font.pixelSize: Math.round(10 * IrisStyle.density)
                color: IrisStyle.muted
                text: "Stale — tap ↻ to re-run the collector."
                wrapMode: Text.WordWrap
            }
        }
    }

    component AiNow: GlassCard {
        id: card
        radius: root.radius
        implicitHeight: body.implicitHeight + 2 * root.pad

        Column {
            id: body
            x: root.pad
            y: root.pad
            width: card.width - 2 * root.pad
            spacing: root.step * 2

            Item {
                width: parent.width
                height: Math.max(agentLine.implicitHeight, agoText.implicitHeight)
                Row {
                    id: agentLine
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: Math.round(5 * IrisStyle.density)
                    Rectangle {
                        id: liveDot
                        anchors.verticalCenter: parent.verticalCenter
                        width: Math.round(5 * IrisStyle.density)
                        height: width
                        radius: width / 2
                        readonly property bool live: usage.runningSessions.length > 0
                        // A live run breathes; an idle one sits still.
                        property real pulse: 1
                        color: liveDot.live ? IrisStyle.success
                            : ColorUtils.applyAlpha(IrisStyle.accent, 0.45)
                        opacity: liveDot.live ? liveDot.pulse : 1
                        SequentialAnimation on pulse {
                            running: liveDot.live
                            loops: Animation.Infinite
                            NumberAnimation {
                                from: 0.35
                                to: 1
                                duration: 800
                                easing.type: Easing.InOutQuad
                            }
                            NumberAnimation {
                                from: 1
                                to: 0.35
                                duration: 800
                                easing.type: Easing.InOutQuad
                            }
                        }
                    }
                    IrisText {
                        anchors.verticalCenter: parent.verticalCenter
                        text: root.toolLabel
                        font.pixelSize: Math.round(12 * IrisStyle.density)
                        font.weight: IrisStyle.weight(Font.DemiBold)
                    }
                }
                IrisText {
                    id: agoText
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    role: IrisText.Meta
                    color: IrisStyle.muted
                    font.pixelSize: Math.round(10 * IrisStyle.density)
                    text: usage.relative(usage.lastActivityMs)
                }
            }

            // At most two live sessions; when none runs, say so.
            Column {
                width: parent.width
                spacing: Math.round(2 * IrisStyle.density)
                Repeater {
                    model: usage.runningSessions.slice(0, 2)
                    Column {
                        required property var modelData
                        width: parent.width
                        spacing: 0
                        IrisText {
                            width: parent.width
                            text: modelData?.title ?? ""
                            font.pixelSize: Math.round(11 * IrisStyle.density)
                            elide: Text.ElideRight
                            maximumLineCount: 1
                        }
                        IrisText {
                            width: parent.width
                            role: IrisText.Meta
                            color: IrisStyle.muted
                            font.pixelSize: Math.round(9 * IrisStyle.density)
                            elide: Text.ElideRight
                            maximumLineCount: 1
                            text: root.elapsedLabel(modelData?.started ?? 0) + " · "
                                + usage.kmg(Number(modelData?.tokens ?? 0)) + " tokens"
                        }
                    }
                }
                IrisText {
                    width: parent.width
                    visible: usage.runningSessions.length === 0
                    role: IrisText.Meta
                    color: IrisStyle.muted
                    font.pixelSize: Math.round(10 * IrisStyle.density)
                    text: "no session running"
                }
            }
        }
    }

    component AiSpend: GlassCard {
        id: card
        radius: root.radius
        implicitHeight: body.implicitHeight + 2 * root.pad

        Column {
            id: body
            x: root.pad
            y: root.pad
            width: card.width - 2 * root.pad
            spacing: root.step * 3

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
                    text: "API value"
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
                        text: root.money(root.periodCost)
                        font.pixelSize: Math.round(24 * IrisStyle.density)
                    }
                    IrisText {
                        anchors.baseline: spendMetric.baseline
                        role: IrisText.Meta
                        color: IrisStyle.muted
                        font.pixelSize: Math.round(10 * IrisStyle.density)
                        text: root.periodNoun
                    }
                }
                IrisText {
                    visible: card.width > Math.round(360 * IrisStyle.density)
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    role: IrisText.Eyebrow
                    color: IrisStyle.muted
                    font.pixelSize: Math.round(10 * IrisStyle.density)
                    elide: Text.ElideRight
                    text: usage.kmg(root.periodTokens) + " tokens · "
                        + Math.round(root.periodCacheRate * 100) + "% from cache"
                }
            }

            IrisText {
                width: parent.width
                visible: card.width <= Math.round(360 * IrisStyle.density)
                role: IrisText.Eyebrow
                color: IrisStyle.muted
                font.pixelSize: Math.round(10 * IrisStyle.density)
                elide: Text.ElideRight
                text: usage.kmg(root.periodTokens) + " tokens · "
                    + Math.round(root.periodCacheRate * 100) + "% from cache"
            }
        }
    }

    // One foldable card's header: title left, accessories right, chevron far
    // right. A click anywhere but an accessory flips the card.
    component FoldHeader: Item {
        id: header
        property string title: ""
        property bool expanded: false
        signal toggled()
        default property alias accessories: accessoryRow.data
        width: parent ? parent.width : 0
        height: Math.max(Math.round(24 * IrisStyle.density), titleText.implicitHeight,
            accessoryRow.implicitHeight, chevronIcon.implicitHeight)

        MouseArea {
            anchors.fill: parent
            cursorShape: Qt.PointingHandCursor
            onClicked: header.toggled()
        }
        IrisText {
            id: titleText
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            text: header.title
            font.pixelSize: Math.round(12 * IrisStyle.density)
            font.weight: IrisStyle.weight(Font.DemiBold)
        }
        Row {
            id: accessoryRow
            anchors.right: chevronIcon.left
            anchors.rightMargin: Math.round(8 * IrisStyle.density)
            anchors.verticalCenter: parent.verticalCenter
            spacing: Math.round(6 * IrisStyle.density)
        }
        MaterialSymbol {
            id: chevronIcon
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            text: "expand_more"
            iconSize: Math.round(16 * IrisStyle.density)
            color: IrisStyle.subtext
            rotation: header.expanded ? 180 : 0
            Behavior on rotation {
                NumberAnimation {
                    duration: IrisStyle.duration(160)
                    easing.type: Easing.BezierSpline
                }
            }
        }
    }

    component AiTrend: GlassCard {
        id: card
        property bool expanded: false
        radius: root.radius
        implicitHeight: body.implicitHeight + 2 * root.pad

        readonly property string caption: {
            const buckets = root.trendBuckets
            if (buckets.length === 0) return ""
            if (chart.hovered >= 0 && chart.hovered < buckets.length) {
                const bucket = buckets[chart.hovered]
                return root.bucketLabel(bucket) + " · " + usage.kmg(bucket.tokens) + " tokens"
            }
            const first = buckets.length > 0 ? root.bucketLabel(buckets[0]) : ""
            const last = buckets.length > 0 ? root.bucketLabel(buckets[buckets.length - 1]) : ""
            const range = first === last ? first : first + " – " + last
            if (root.trend.unit === "hours") {
                return range + " · " + usage.kmg(root.trend.total) + " tokens · peak "
                    + usage.kmg(root.trend.peak) + "/h"
            }
            return range + " · " + usage.kmg(root.trend.total)
                + " tokens · peak " + usage.kmg(root.trend.peak)
        }

        Column {
            id: body
            x: root.pad
            y: root.pad
            width: card.width - 2 * root.pad
            spacing: root.step * 2

            FoldHeader {
                title: "Trend"
                expanded: card.expanded
                onToggled: card.expanded = !card.expanded
                // Static subtext like the Models count; it only becomes the
                // period control while the card is open.
                Item {
                    id: periodText
                    width: periodLabelText.implicitWidth
                    height: periodLabelText.implicitHeight
                    IrisText {
                        id: periodLabelText
                        anchors.centerIn: parent
                        role: IrisText.Meta
                        color: card.expanded && periodArea.containsMouse
                            ? IrisStyle.accent : IrisStyle.muted
                        font.pixelSize: Math.round(10 * IrisStyle.density)
                        text: root.periodLabel
                    }
                    MouseArea {
                        id: periodArea
                        anchors.fill: parent
                        hoverEnabled: true
                        enabled: card.expanded
                        cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
                        onClicked: root.openPeriodMenu(periodText)
                    }
                }
            }

            Column {
                id: content
                width: parent.width
                visible: card.expanded
                spacing: root.step * 2

                IrisText {
                    width: parent.width
                    role: IrisText.Meta
                    color: IrisStyle.muted
                    font.pixelSize: Math.round(10 * IrisStyle.density)
                    elide: Text.ElideRight
                    maximumLineCount: 1
                    text: card.caption
                }

                Item {
                    id: chart
                    width: parent.width
                    height: Math.round(36 * IrisStyle.density)
                    property int hovered: -1
                    readonly property int count: root.trendBuckets.length
                    readonly property int barGap: count > 30
                        ? Math.round(1 * IrisStyle.density) : Math.round(2 * IrisStyle.density)

                    Row {
                        id: barRow
                        anchors.fill: parent
                        spacing: chart.barGap
                        Repeater {
                            model: root.trendBuckets
                            Item {
                                id: barSlot
                                required property var modelData
                                required property int index
                                width: (barRow.width - barRow.spacing * Math.max(0, chart.count - 1))
                                    / Math.max(1, chart.count)
                                height: barRow.height
                                readonly property bool future: {
                                    if (!root.hourly) return false
                                    const nowHour = new Date()
                                    nowHour.setMinutes(0, 0, 0)
                                    return Number(modelData?.start ?? 0) > nowHour.getTime()
                                }
                                readonly property bool isToday: {
                                    if (root.hourly) {
                                        const nowHour = new Date()
                                        nowHour.setMinutes(0, 0, 0)
                                        return Number(modelData?.start ?? 0) === nowHour.getTime()
                                    }
                                    return index === chart.count - 1
                                }
                                readonly property real tokens: Number(modelData?.tokens ?? 0)
                                Rectangle {
                                    visible: !barSlot.future
                                    anchors.bottom: parent.bottom
                                    anchors.horizontalCenter: parent.horizontalCenter
                                    width: Math.max(1, parent.width - (parent.width > 6
                                        ? Math.round(2 * IrisStyle.density) : 0))
                                    height: barSlot.tokens > 0
                                        ? Math.max(2, (chart.height - 2) * barSlot.tokens / root.trend.peak)
                                        : Math.max(2, Math.round(2 * IrisStyle.density))
                                    radius: Math.min(Math.round(2 * IrisStyle.density), width / 2)
                                    color: barSlot.tokens <= 0
                                        ? ColorUtils.applyAlpha(IrisStyle.muted, 0.3)
                                        : barSlot.isToday
                                            ? IrisStyle.accent
                                            : chart.hovered === barSlot.index
                                                ? IrisStyle.accent
                                                : ColorUtils.applyAlpha(IrisStyle.accent, 0.42)
                                }
                            }
                        }
                    }

                    MouseArea {
                        id: hoverArea
                        anchors.fill: parent
                        hoverEnabled: true
                        onPositionChanged: function (mouse) {
                            // A page that opens under a still pointer gets a synthetic
                            // move; only a pointer actually inside the chart counts.
                            if (!hoverArea.containsMouse || chart.count === 0) return
                            chart.hovered = Math.max(0, Math.min(chart.count - 1,
                                Math.floor(mouse.x / (chart.width / chart.count))))
                        }
                        onExited: chart.hovered = -1
                    }
                }

            }
        }
    }

    component AiModels: GlassCard {
        id: card
        property bool expanded: false
        radius: root.radius
        implicitHeight: body.implicitHeight + 2 * root.pad

        Column {
            id: body
            x: root.pad
            y: root.pad
            width: card.width - 2 * root.pad
            spacing: root.step * 3

            FoldHeader {
                title: "Models"
                expanded: card.expanded
                onToggled: card.expanded = !card.expanded
                IrisText {
                    id: modelsCount
                    role: IrisText.Meta
                    color: IrisStyle.muted
                    font.pixelSize: Math.round(10 * IrisStyle.density)
                    text: root.periodModels.length > root.topModels
                        ? "top " + root.topModels + " of " + root.periodModels.length
                        : root.periodModels.length + " model"
                            + (root.periodModels.length === 1 ? "" : "s")
                }
            }

            Column {
                id: content
                width: parent.width
                visible: card.expanded
                spacing: root.step * 3

                Repeater {
                    model: root.periodModels.slice(0, root.topModels)
                    AiModelRow {
                        width: content.width
                    }
                }

                IrisText {
                    width: parent.width
                    visible: root.periodModels.length > root.topModels
                    role: IrisText.Meta
                    color: IrisStyle.muted
                    font.pixelSize: Math.round(9 * IrisStyle.density)
                    text: "+" + (root.periodModels.length - root.topModels) + " more model"
                        + (root.periodModels.length - root.topModels === 1 ? "" : "s")
                }
            }
        }
    }

    component AiActivity: GlassCard {
        id: card
        property bool expanded: false
        radius: root.radius
        implicitHeight: body.implicitHeight + 2 * root.pad

        readonly property string todayKey: Qt.formatDate(new Date(), "yyyy-MM-dd")
        readonly property int cellSize: Math.max(7, Math.round(11 * IrisStyle.density))
        readonly property int cellGap: Math.max(2, Math.round(3 * IrisStyle.density))
        readonly property int cellRadius: Math.max(2, Math.round(3 * IrisStyle.density))

        // Everything a day spent, cache reads included.
        function dayWeight(day) {
            return Number(day?.tokens ?? 0) + Number(day?.cacheRead ?? 0)
        }

        // Thirteen week columns ending in the week that holds today, each
        // starting on the locale's first day; days the cache lacks stay empty.
        readonly property var map: {
            const days = usage.days
            if (!days || days.length === 0)
                return ({ weeks: [], total: 0, active: 0, busiest: null, span: 0, thresholds: [] })
            const byDate = ({})
            for (const day of days)
                byDate[String(day?.date ?? "")] = card.dayWeight(day)
            const today = new Date()
            today.setHours(12, 0, 0, 0)
            const weekStart = Number(Qt.locale().firstDayOfWeek ?? 0)
            const cursor = new Date(today.getTime())
            cursor.setDate(cursor.getDate()
                - (((today.getDay() - weekStart) % 7 + 7) % 7) - 12 * 7)
            let active = 0
            let busiest = null
            let span = 0
            const values = []
            const weeks = []
            for (let w = 0; w < 13; w++) {
                const column = []
                for (let r = 0; r < 7; r++) {
                    const key = Qt.formatDate(cursor, "yyyy-MM-dd")
                    const known = byDate[key]
                    if (known === undefined) {
                        column.push(null)
                    } else {
                        const value = Number(known) || 0
                        column.push({ date: key, value: value })
                        if (value > 0) {
                            active += 1
                            values.push(value)
                        }
                        if (!busiest || value > busiest.value)
                            busiest = { date: key, value: value }
                        if (span === 0)
                            span = Math.round((today.getTime() - cursor.getTime()) / 86400000) + 1
                    }
                    cursor.setDate(cursor.getDate() + 1)
                }
                weeks.push(column)
            }
            // A young history starts at its first week instead of padding the
            // map with empty columns on the left.
            while (weeks.length > 0 && weeks[0].every(cell => cell === null))
                weeks.shift()
            values.sort((a, b) => a - b)
            const thresholds = values.length > 0
                ? [0.25, 0.5, 0.75].map(q => values[Math.min(values.length - 1, Math.floor(values.length * q))])
                : []
            return ({ weeks: weeks, active: active, busiest: busiest,
                      span: span, thresholds: thresholds })
        }

        // Consecutive active days ending today; a day still in progress counts
        // back from yesterday rather than breaking the run.
        readonly property int streak: {
            const days = usage.days
            if (!days || days.length === 0) return 0
            const byDate = ({})
            for (const day of days)
                byDate[String(day?.date ?? "")] = card.dayWeight(day)
            const cursor = new Date()
            cursor.setHours(12, 0, 0, 0)
            if (!(Number(byDate[Qt.formatDate(cursor, "yyyy-MM-dd")] ?? 0) > 0))
                cursor.setDate(cursor.getDate() - 1)
            let count = 0
            while (Number(byDate[Qt.formatDate(cursor, "yyyy-MM-dd")] ?? 0) > 0) {
                count += 1
                cursor.setDate(cursor.getDate() - 1)
            }
            return count
        }

        function spanLabel(days: int): string {
            if (days <= 0) return ""
            if (days >= 7 && days % 7 === 0)
                return (days / 7) + (days === 7 ? " week" : " weeks")
            return days + (days === 1 ? " day" : " days")
        }

        // The card's headline is the whole history, not just the mapped weeks.
        readonly property double allTimeTotal: {
            let total = 0
            for (const day of usage.days) total += card.dayWeight(day)
            return total
        }

        function cellColor(cell) {
            if (!cell) return "transparent"
            const value = Number(cell.value ?? 0)
            if (value <= 0) return ColorUtils.applyAlpha(IrisStyle.text, 0.07)
            const level = card.map.thresholds.filter(limit => value > limit).length
            return ColorUtils.applyAlpha(IrisStyle.accent, [0.28, 0.45, 0.65, 0.9][Math.min(3, level)])
        }

        Column {
            id: body
            x: root.pad
            y: root.pad
            width: card.width - 2 * root.pad
            spacing: root.step * 2

            FoldHeader {
                title: "Activity"
                expanded: card.expanded
                onToggled: card.expanded = !card.expanded
                // The run of active days, with its own explanation on hover.
                Item {
                    id: streakBadge
                    visible: card.streak > 1
                    width: streakIcon.width + Math.round(2 * IrisStyle.density) + streakText.width
                    height: Math.max(streakIcon.height, streakText.height)
                    MaterialSymbol {
                        id: streakIcon
                        anchors.left: parent.left
                        anchors.verticalCenter: parent.verticalCenter
                        text: "local_fire_department"
                        iconSize: Math.round(15 * IrisStyle.density)
                        color: IrisStyle.warning
                    }
                    IrisText {
                        id: streakText
                        anchors.left: streakIcon.right
                        anchors.leftMargin: Math.round(2 * IrisStyle.density)
                        anchors.verticalCenter: parent.verticalCenter
                        text: String(card.streak)
                        color: IrisStyle.warning
                        font.pixelSize: Math.round(10 * IrisStyle.density)
                        font.weight: IrisStyle.weight(Font.DemiBold)
                    }
                    MouseArea {
                        id: badgeArea
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: card.expanded = !card.expanded
                    }
                    IrisSurface {
                        id: streakTip
                        visible: badgeArea.containsMouse
                        z: 10
                        raised: true
                        outlined: true
                        radius: IrisStyle.radiusSmall
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.bottom: parent.top
                        anchors.bottomMargin: Math.round(4 * IrisStyle.density)
                        width: streakTipText.implicitWidth + 2 * Math.round(6 * IrisStyle.density)
                        height: streakTipText.implicitHeight + 2 * Math.round(3 * IrisStyle.density)
                        IrisText {
                            id: streakTipText
                            anchors.centerIn: parent
                            role: IrisText.Meta
                            color: IrisStyle.muted
                            font.pixelSize: Math.round(10 * IrisStyle.density)
                            text: card.streak + "-day streak"
                        }
                    }
                }
            }

            Item {
                id: content
                width: parent.width
                height: Math.max(heat.implicitHeight, Math.round(80 * IrisStyle.density))
                visible: card.expanded

                Row {
                    id: heat
                    anchors.left: parent.left
                    anchors.top: parent.top
                    spacing: card.cellGap
                    Repeater {
                        model: card.map.weeks
                        Column {
                            required property var modelData
                            spacing: card.cellGap
                            Repeater {
                                model: modelData
                                Rectangle {
                                    id: heatCell
                                    required property var modelData
                                    width: card.cellSize
                                    height: width
                                    radius: card.cellRadius
                                    color: card.cellColor(heatCell.modelData)
                                    border.width: heatCell.modelData !== null
                                        && String(heatCell.modelData.date) === card.todayKey ? 1 : 0
                                    border.color: IrisStyle.accent
                                }
                            }
                        }
                    }
                }

                // The figures take the rest of the row and sit on the card's
                // inner right edge, as the reference does.
                Item {
                    id: figures
                    anchors.left: heat.right
                    anchors.leftMargin: Math.round(16 * IrisStyle.density)
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom

                    IrisText {
                        id: totalValue
                        anchors.top: parent.top
                        anchors.left: parent.left
                        role: IrisText.Metric
                        text: usage.kmg(card.allTimeTotal)
                        font.pixelSize: Math.round(21 * IrisStyle.density)
                    }
                    IrisText {
                        id: spanValue
                        anchors.top: totalValue.bottom
                        anchors.topMargin: Math.round(1 * IrisStyle.density)
                        anchors.left: parent.left
                        role: IrisText.Eyebrow
                        color: IrisStyle.muted
                        font.pixelSize: Math.round(10 * IrisStyle.density)
                        text: "all time"
                    }
                    Item {
                        id: activeRow
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.bottom: busiestRow.top
                        anchors.bottomMargin: Math.round(3 * IrisStyle.density)
                        height: Math.max(activeLabel.implicitHeight, activeValue.implicitHeight)
                        IrisText {
                            id: activeLabel
                            anchors.left: parent.left
                            anchors.verticalCenter: parent.verticalCenter
                            role: IrisText.Eyebrow
                            color: IrisStyle.muted
                            font.pixelSize: Math.round(10 * IrisStyle.density)
                            text: "Active days"
                        }
                        IrisText {
                            id: activeValue
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            role: IrisText.Meta
                            font.pixelSize: Math.round(10 * IrisStyle.density)
                            text: String(card.map.active)
                        }
                    }
                    Item {
                        id: busiestRow
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.bottom: parent.bottom
                        height: Math.max(busiestLabel.implicitHeight, busiestValue.implicitHeight)
                        IrisText {
                            id: busiestLabel
                            anchors.left: parent.left
                            anchors.verticalCenter: parent.verticalCenter
                            role: IrisText.Eyebrow
                            color: IrisStyle.muted
                            font.pixelSize: Math.round(10 * IrisStyle.density)
                            text: "Busiest day"
                        }
                        IrisText {
                            id: busiestValue
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            role: IrisText.Meta
                            font.pixelSize: Math.round(10 * IrisStyle.density)
                            text: card.map.busiest && card.map.busiest.value > 0
                                ? root.dayLabel(card.map.busiest.date) + " · "
                                    + usage.kmg(card.map.busiest.value)
                                : "—"
                        }
                    }
                }
            }
        }
    }

    component AiEmpty: GlassCard {
        id: card
        radius: root.radius
        implicitHeight: body.implicitHeight + 2 * root.pad

        Column {
            id: body
            x: root.pad
            y: root.pad
            width: card.width - 2 * root.pad
            spacing: root.step * 3

            Item {
                width: parent.width
                height: Math.max(emptyTitle.implicitHeight, refreshBtn.implicitHeight)
                IrisText {
                    id: emptyTitle
                    anchors.left: parent.left
                    anchors.verticalCenter: parent.verticalCenter
                    text: "AI usage · " + root.toolLabel
                    font.pixelSize: Math.round(12 * IrisStyle.density)
                    font.weight: IrisStyle.weight(Font.DemiBold)
                }
                IrisIconButton {
                    id: refreshBtn
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    materialIcon: "refresh"
                    iconSize: Math.round(15 * IrisStyle.density)
                    onClicked: usage.refresh()
                }
            }
            IrisText {
                width: parent.width
                role: IrisText.Meta
                color: IrisStyle.muted
                text: "No " + root.tool + " usage yet. Run " + root.tool
                    + ", then tap ↻ — the collector writes ~/.cache/" + root.tool + "-usage.json."
                wrapMode: Text.WordWrap
            }
        }
    }

    // ─── pieces ──────────────────────────────────────────────────────────

    // A rate window: name and budget left, share right, the meter under both.
    component AiWindow: Column {
        id: windowRow
        property string label: ""
        property string caption: ""
        property string share: ""
        property real proportion: 0
        width: parent ? parent.width : 0
        spacing: Math.round(3 * IrisStyle.density)

        readonly property color ink: windowRow.proportion >= 0.95 ? IrisStyle.danger
            : windowRow.proportion >= 0.8 ? IrisStyle.warning
            : IrisStyle.accent

        Item {
            width: parent.width
            height: Math.max(windowLabel.implicitHeight, windowShare.implicitHeight,
                windowCaption.implicitHeight)
            IrisText {
                id: windowLabel
                anchors.left: parent.left
                anchors.verticalCenter: parent.verticalCenter
                role: IrisText.Eyebrow
                font.pixelSize: Math.round(10 * IrisStyle.density)
                color: IrisStyle.muted
                text: windowRow.label
            }
            IrisText {
                id: windowCaption
                anchors.left: windowLabel.right
                anchors.leftMargin: Math.round(5 * IrisStyle.density)
                anchors.right: windowShare.left
                anchors.rightMargin: Math.round(6 * IrisStyle.density)
                anchors.verticalCenter: parent.verticalCenter
                role: IrisText.Eyebrow
                font.pixelSize: Math.round(9 * IrisStyle.density)
                color: IrisStyle.muted
                elide: Text.ElideRight
                text: windowRow.caption
            }
            IrisText {
                id: windowShare
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                role: IrisText.Meta
                font.pixelSize: Math.round(11 * IrisStyle.density)
                font.weight: IrisStyle.weight(Font.DemiBold)
                font.family: IrisStyle.fontNumbers
                color: windowRow.proportion >= 0.8 ? windowRow.ink : IrisStyle.text
                text: windowRow.share
            }
        }
        Rectangle {
            width: parent.width
            height: Math.round(5 * IrisStyle.density)
            radius: height / 2
            color: ColorUtils.applyAlpha(IrisStyle.muted, 0.22)
            Rectangle {
                height: parent.height
                radius: parent.radius
                width: Math.max(0, Math.min(1, windowRow.proportion)) * parent.width
                color: windowRow.ink
            }
        }
    }

    // One model: name left, its total in front on the right, share meter, parts.
    component AiModelRow: Item {
        id: modelRow
        required property var modelData
        readonly property int rowGap: Math.round(4 * IrisStyle.density)
        readonly property int meterHeight: Math.round(5 * IrisStyle.density)
        readonly property int nameHeight: Math.max(nameText.implicitHeight,
            Math.round(14 * IrisStyle.density))
        height: nameHeight + rowGap + meterHeight + rowGap + detailText.implicitHeight
        implicitHeight: height

        IrisText {
            id: nameText
            anchors.left: parent.left
            anchors.top: parent.top
            width: parent.width * 0.72
            height: modelRow.nameHeight
            text: modelRow.modelData?.nameShort ?? ""
            elide: Text.ElideRight
            font.pixelSize: Math.round(12 * IrisStyle.density)
            font.weight: IrisStyle.weight(Font.Medium)
        }
        IrisText {
            anchors.right: parent.right
            anchors.top: parent.top
            text: modelRow.modelData?.totalWithCacheReadLabel
                ?? modelRow.modelData?.totalLabel ?? ""
            role: IrisText.Metric
            color: IrisStyle.accent
            font.family: IrisStyle.fontNumbers
            font.pixelSize: Math.round(13 * IrisStyle.density)
        }
        Rectangle {
            id: modelMeter
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: nameText.bottom
            anchors.topMargin: modelRow.rowGap
            height: modelRow.meterHeight
            radius: height / 2
            color: ColorUtils.applyAlpha(IrisStyle.muted, 0.18)
            Rectangle {
                width: parent.width * Math.max(0, Math.min(100,
                    Number(modelRow.modelData?.pct ?? 0))) / 100
                height: parent.height
                radius: parent.radius
                color: IrisStyle.accent
                opacity: 0.85
            }
        }
        IrisText {
            id: detailText
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: modelMeter.bottom
            anchors.topMargin: modelRow.rowGap
            text: root.modelDetail(modelRow.modelData)
            elide: Text.ElideRight
            role: IrisText.Eyebrow
            font.pixelSize: Math.round(11 * IrisStyle.density)
            color: IrisStyle.subtext
        }
    }
}
