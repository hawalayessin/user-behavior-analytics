import { useMemo } from "react"

function safePercent(num, denom) {
  if (!denom || denom === 0) return 0
  return Math.round((num / denom) * 1000) / 10
}

export function useDashboardMetrics(data) {
  return useMemo(() => {
    if (!data) return null
    if (!data.users) return null
    if (!data.subscriptions) return null
    if (!data.churn) return null
    if (!data.churn.dropoff) return null
    if (!data.revenue) return null
    if (!data.engagement) return null
    if (!Array.isArray(data.top_services)) return null

    const { users, subscriptions, churn, revenue, engagement } = data

    const activeUserRate = safePercent(users.active, users.total)
    const billingSuccessRate = safePercent(
      revenue.billing_success,
      revenue.billing_success + revenue.billing_failed
    )

    const isChurnCritical = (churn.churn_rate_month_pct ?? 0) > 5
    const isConversionBelowBM = (subscriptions.conversion_rate_pct ?? 0) < 18
    const isBillingAlert = (revenue.failed_pct ?? 0) > 5
    const isStickinessLow = (engagement.stickiness_pct ?? 0) < 20
    const isVoluntaryDominant = (churn.voluntary_pct ?? 0) >= (churn.technical_pct ?? 0)
    const isMostCriticalDay3 =
      (churn.dropoff.day3 ?? 0) >= (churn.dropoff.day1 ?? 0) &&
      (churn.dropoff.day3 ?? 0) >= (churn.dropoff.day2 ?? 0)

    const subscriptionPieData = [
      { name: "Actifs", value: subscriptions.active ?? 0, fill: "#10B981" },
      { name: "A Risque", value: subscriptions.billing_failed ?? 0, fill: "#F59E0B" },
      { name: "Annulés", value: subscriptions.cancelled ?? 0, fill: "#EF4444" },
      { name: "Pending OTP", value: subscriptions.pending ?? 0, fill: "#94A3B8" },
    ]

    const churnPieData = [
      { name: "Volontaire", value: churn.voluntary_pct ?? 0, fill: "#EF4444" },
      { name: "Technique", value: churn.technical_pct ?? 0, fill: "#F59E0B" },
    ]

    const dropoffBarData = [
      { label: "Jour 1\n0–24h", value: churn.dropoff.day1 ?? 0, fill: "#6366F1" },
      { label: "Jour 2\n24–48h", value: churn.dropoff.day2 ?? 0, fill: "#F59E0B" },
      { label: "Jour 3\n48–72h ⚠", value: churn.dropoff.day3 ?? 0, fill: "#EF4444" },
    ]

    const stickiness = engagement.stickiness_pct ?? 0

    const engagementBars = [
      {
        label: "DAU/MAU Stickiness",
        value: stickiness,
        target: 20,
        sublabel: `Cible ≥ 20% · Actuel : ${stickiness}%`,
        color: stickiness >= 20 ? "#10B981" : stickiness >= 10 ? "#F59E0B" : "#EF4444",
      },
      {
        label: "Taux utilisateurs actifs",
        value: activeUserRate,
        target: 70,
        sublabel: `${(users.active ?? 0).toLocaleString()} actifs / ${(users.total ?? 0).toLocaleString()} total`,
        color: activeUserRate > 70 ? "#10B981" : activeUserRate > 50 ? "#F59E0B" : "#EF4444",
      },
      {
        label: "Pending OTP",
        value: safePercent(subscriptions.pending, subscriptions.total_with_pending || subscriptions.total),
        target: null,
        sublabel: `${subscriptions.pending ?? 0} souscriptions non completees`,
        color: "#94A3B8",
      },
      {
        label: "Taux de succès billing",
        value: billingSuccessRate,
        target: 95,
        sublabel: `Cible > 95% · ${revenue.billing_failed ?? 0} transactions échouées`,
        color: billingSuccessRate > 95 ? "#10B981" : billingSuccessRate > 90 ? "#F59E0B" : "#EF4444",
      },
    ]

    const biInsights = [
      {
        id: "churn",
        severity: isChurnCritical ? "red" : "green",
        icon: isChurnCritical ? "🔴" : "🟢",
        title: isChurnCritical ? "Alerte Churn" : "Churn Sous Contrôle",
        message: isChurnCritical
          ? `Churn mensuel à ${churn.churn_rate_month_pct}% — dépasse le seuil critique de 5%.`
          : `Churn mensuel à ${churn.churn_rate_month_pct}% — dans la plage acceptable (< 5%).`,
      },
      {
        id: "conversion",
        severity: isConversionBelowBM ? "amber" : "green",
        icon: isConversionBelowBM ? "🟡" : "🟢",
        title: isConversionBelowBM ? "Conversion sous benchmark" : "Conversion atteinte",
        message: isConversionBelowBM
          ? `Conversion à ${subscriptions.conversion_rate_pct}% — sous le benchmark (18–25%).`
          : `Conversion à ${subscriptions.conversion_rate_pct}% — au-dessus du benchmark.`,
      },
      {
        id: "stickiness",
        severity: isStickinessLow ? "amber" : "green",
        icon: isStickinessLow ? "🟡" : "🟢",
        title: isStickinessLow ? "Faible rétention quotidienne" : "Bonne rétention",
        message: isStickinessLow
          ? `Stickiness à ${stickiness}% — envisagez des campagnes de ré-engagement.`
          : `Stickiness à ${stickiness}% — bon engagement produit.`,
      },
      {
        id: "billing",
        severity: isBillingAlert ? "red" : "green",
        icon: isBillingAlert ? "🔴" : "🟢",
        title: isBillingAlert ? "Alerte Billing" : "Billing opérationnel",
        message: isBillingAlert
          ? `${revenue.failed_pct}% d'échecs — ${revenue.billing_failed} transactions échouées.`
          : `Taux d'échec à ${revenue.failed_pct}% — ${revenue.billing_success} transactions réussies.`,
      },
    ]

    return {
      isChurnCritical,
      isConversionBelowBM,
      isBillingAlert,
      isStickinessLow,
      isVoluntaryDominant,
      isMostCriticalDay3,
      activeUserRate,
      billingSuccessRate,
      subscriptionPieData,
      churnPieData,
      dropoffBarData,
      engagementBars,
      biInsights,
    }
    // ✅ data est un objet — JSON.stringify force le recalcul quand le contenu change
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(data)])
}