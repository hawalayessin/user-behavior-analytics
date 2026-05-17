import React from 'react';

export default function PremiumPDFTemplate({ data = {} }) {
  const {
    reportTitle = 'DigMaco Analytics Report',
    dateRange = 'September 1 - October 31, 2025',
    generatedDate = new Date().toLocaleDateString(),
    platformScore = 92,
    services = [],
  } = data;

  const colors = {
    primary: '#5B5FEF',
    secondary: '#7C4DFF',
    success: '#00C896',
    warning: '#FFB020',
    danger: '#FF5A5F',
    background: '#F7F9FC',
    text: '#1F2937',
    lightText: '#6B7280',
    border: '#E5E7EB',
    card: '#FFFFFF',
  };

  return (
    <div style={styles.container(colors)}>
      {/* ===== PAGE 1: COVER PAGE ===== */}
      <div style={styles.page(colors)}>
        <div style={styles.coverGradient}>
          <div style={styles.coverContent}>
            {/* Logo & Platform */}
            <div style={styles.coverLogo}>
              <div style={styles.logoBadge(colors)}>
                <span style={styles.logoText}>DA</span>
              </div>
              <h2 style={styles.logoName(colors)}>DigMaco Analytics</h2>
            </div>

            {/* Main Title */}
            <div style={styles.coverTitleSection}>
              <h1 style={styles.coverTitle(colors)}>
                Behavioral Analytics Report
              </h1>
              <p style={styles.coverSubtitle(colors)}>
                AI-Powered Insights & Recommendations
              </p>
            </div>

            {/* Report Details */}
            <div style={styles.reportDetails(colors)}>
              <div style={styles.detailRow}>
                <span style={styles.detailLabel(colors)}>Report Period</span>
                <span style={styles.detailValue(colors)}>{dateRange}</span>
              </div>
              <div style={styles.detailRow}>
                <span style={styles.detailLabel(colors)}>Generated Date</span>
                <span style={styles.detailValue(colors)}>{generatedDate}</span>
              </div>
              <div style={styles.detailRow}>
                <span style={styles.detailLabel(colors)}>Services Analyzed</span>
                <span style={styles.detailValue(colors)}>{services.length || 4}</span>
              </div>
            </div>

            {/* Platform Health Score */}
            <div style={styles.healthScoreCard(colors)}>
              <div style={styles.scoreTitle(colors)}>Platform Health Score</div>
              <div style={styles.scoreContainer}>
                <div style={styles.scoreCircle(colors, platformScore)}>
                  <span style={styles.scoreValue}>{platformScore}%</span>
                </div>
                <div style={styles.scoreLabels(colors)}>
                  <p style={styles.scoreLabel}>Excellent performance</p>
                  <p style={styles.scoreSubLabel}>All systems optimal</p>
                </div>
              </div>
            </div>

            {/* Footer */}
            <div style={styles.coverFooter(colors)}>
              <p style={styles.footerText(colors)}>
                Premium Analytics Intelligence for Executive Leadership
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* ===== PAGE 2: EXECUTIVE SUMMARY ===== */}
      <div style={styles.page(colors)}>
        <div style={styles.pageHeader(colors)}>
          <h1 style={styles.pageTitle(colors)}>Executive Summary</h1>
          <div style={styles.pageHeaderLine(colors)} />
        </div>

        <div style={styles.pageContent}>
          {/* KPI Cards */}
          <div style={styles.kpiGrid}>
            <div style={styles.kpiCard(colors)}>
              <div style={styles.kpiLabel(colors)}>Total Users</div>
              <div style={styles.kpiValue}>1.2M</div>
              <div style={styles.kpiTrend(colors, 'up')}>↑ 12.5% vs last month</div>
            </div>

            <div style={styles.kpiCard(colors)}>
              <div style={styles.kpiLabel(colors)}>Monthly Churn Rate</div>
              <div style={styles.kpiValue}>4.2%</div>
              <div style={styles.kpiTrend(colors, 'down')}>↓ 1.3% improvement</div>
            </div>

            <div style={styles.kpiCard(colors)}>
              <div style={styles.kpiLabel(colors)}>Retention (D30)</div>
              <div style={styles.kpiValue}>68.4%</div>
              <div style={styles.kpiTrend(colors, 'up')}>↑ 3.2% vs target</div>
            </div>

            <div style={styles.kpiCard(colors)}>
              <div style={styles.kpiLabel(colors)}>Premium ARPU</div>
              <div style={styles.kpiValue}>$28.50</div>
              <div style={styles.kpiTrend(colors, 'up')}>↑ 8.1% growth</div>
            </div>
          </div>

          {/* AI Summary Box */}
          <div style={styles.aiSummaryBox(colors)}>
            <div style={styles.aiHeader(colors)}>
              <span style={styles.aiIcon}>✨</span>
              <span style={styles.aiTitle(colors)}>AI-Generated Executive Summary</span>
            </div>
            <p style={styles.aiText(colors)}>
              DigMaco's platform demonstrated strong performance this period with exceptional user 
              growth and improved retention metrics. The AI analysis identified three key opportunities: 
              (1) Trial conversion optimization could increase revenue by ~$120K annually, 
              (2) Churn prediction model indicates high-risk segments requiring targeted retention campaigns, 
              and (3) Cross-service migration shows potential for premium upsell strategies.
            </p>
          </div>

          {/* Key Metrics Grid */}
          <div style={styles.metricsGrid(colors)}>
            <div style={styles.metricBox(colors)}>
              <div style={styles.metricLabel(colors)}>DAU / MAU Ratio</div>
              <div style={styles.metricValue}>42% stickiness</div>
            </div>
            <div style={styles.metricBox(colors)}>
              <div style={styles.metricLabel(colors)}>Free Trial Conversion</div>
              <div style={styles.metricValue}>18.3% premium</div>
            </div>
            <div style={styles.metricBox(colors)}>
              <div style={styles.metricLabel(colors)}>SMS Campaign ROI</div>
              <div style={styles.metricValue}>3.2x return</div>
            </div>
          </div>
        </div>
      </div>

      {/* ===== PAGE 3: CHURN ANALYTICS ===== */}
      <div style={styles.page(colors)}>
        <div style={styles.pageHeader(colors)}>
          <h1 style={styles.pageTitle(colors)}>Churn & Risk Analysis</h1>
          <div style={styles.pageHeaderLine(colors)} />
        </div>

        <div style={styles.pageContent}>
          {/* Risk Gauge */}
          <div style={styles.sectionRow}>
            <div style={styles.riskGauge(colors)}>
              <div style={styles.gaugeTitle(colors)}>Churn Risk Level</div>
              <div style={styles.gaugeVisual}>
                <div style={styles.gaugeFill(colors, 35)} />
              </div>
              <div style={styles.gaugeLabel(colors)}>35% - Moderate Risk</div>
            </div>

            <div style={styles.highRiskBox(colors)}>
              <div style={styles.boxTitle(colors)}>High-Risk Users</div>
              <div style={styles.riskStats(colors)}>
                <div style={styles.riskStat}>
                  <span style={styles.riskNumber}>4,200</span>
                  <span style={styles.riskLabel}>Users at risk</span>
                </div>
                <div style={styles.riskStat}>
                  <span style={styles.riskNumber}>$89K</span>
                  <span style={styles.riskLabel}>Revenue at stake</span>
                </div>
              </div>
            </div>
          </div>

          {/* Churn Drivers */}
          <div style={styles.driversSection(colors)}>
            <h3 style={styles.sectionSubtitle(colors)}>Top Churn Drivers</h3>
            <div style={styles.driversList}>
              <div style={styles.driverItem(colors)}>
                <div style={styles.driverRank}>1</div>
                <div style={styles.driverInfo}>
                  <div style={styles.driverName(colors)}>Low Engagement</div>
                  <div style={styles.driverImpact(colors)}>35% of churned users</div>
                </div>
                <div style={styles.driverBar(colors, 35)} />
              </div>
              <div style={styles.driverItem(colors)}>
                <div style={styles.driverRank}>2</div>
                <div style={styles.driverInfo}>
                  <div style={styles.driverName(colors)}>Price Sensitivity</div>
                  <div style={styles.driverImpact(colors)}>28% of churned users</div>
                </div>
                <div style={styles.driverBar(colors, 28)} />
              </div>
              <div style={styles.driverItem(colors)}>
                <div style={styles.driverRank}>3</div>
                <div style={styles.driverInfo}>
                  <div style={styles.driverName(colors)}>Product Fit Issues</div>
                  <div style={styles.driverImpact(colors)}>22% of churned users</div>
                </div>
                <div style={styles.driverBar(colors, 22)} />
              </div>
            </div>
          </div>

          {/* AI Recommendations */}
          <div style={styles.recommendationBox(colors)}>
            <div style={styles.recTitle(colors)}>💡 AI Recommendations</div>
            <ul style={styles.recList(colors)}>
              <li style={styles.recItem(colors)}>Launch re-engagement campaign for inactive users (potential 5.2% churn reduction)</li>
              <li style={styles.recItem(colors)}>Implement tiered pricing strategy to address price sensitivity</li>
              <li style={styles.recItem(colors)}>A/B test feature discovery onboarding to improve product fit</li>
            </ul>
          </div>
        </div>
      </div>

      {/* ===== PAGE 4: USER SEGMENTATION ===== */}
      <div style={styles.page(colors)}>
        <div style={styles.pageHeader(colors)}>
          <h1 style={styles.pageTitle(colors)}>User Segmentation & Clustering</h1>
          <div style={styles.pageHeaderLine(colors)} />
        </div>

        <div style={styles.pageContent}>
          <p style={styles.sectionDescription(colors)}>
            K-Means clustering analysis identified 5 distinct user segments based on behavioral, 
            engagement, and revenue patterns. Each segment requires tailored retention strategies.
          </p>

          {/* Segment Cards */}
          <div style={styles.segmentGrid}>
            <div style={styles.segmentCard(colors, '#5B5FEF')}>
              <div style={styles.segmentName(colors)}>Premium Power Users</div>
              <div style={styles.segmentStats(colors)}>
                <div>23% of base</div>
                <div>$89 ARPU</div>
                <div>84% retention</div>
              </div>
            </div>

            <div style={styles.segmentCard(colors, '#00C896')}>
              <div style={styles.segmentName(colors)}>Active Growers</div>
              <div style={styles.segmentStats(colors)}>
                <div>31% of base</div>
                <div>$24 ARPU</div>
                <div>72% retention</div>
              </div>
            </div>

            <div style={styles.segmentCard(colors, '#FFB020')}>
              <div style={styles.segmentName(colors)}>Casual Users</div>
              <div style={styles.segmentStats(colors)}>
                <div>28% of base</div>
                <div>$8 ARPU</div>
                <div>58% retention</div>
              </div>
            </div>

            <div style={styles.segmentCard(colors, '#FF5A5F')}>
              <div style={styles.segmentName(colors)}>At-Risk Churners</div>
              <div style={styles.segmentStats(colors)}>
                <div>18% of base</div>
                <div>$5 ARPU</div>
                <div>22% retention</div>
              </div>
            </div>
          </div>

          {/* Comparison Table */}
          <div style={styles.comparisonTable(colors)}>
            <div style={styles.tableHeader(colors)}>Segment Comparison</div>
            <table style={styles.table(colors)}>
              <thead>
                <tr style={styles.tableRow(colors)}>
                  <th style={styles.tableCell(colors, 'header')}>Segment</th>
                  <th style={styles.tableCell(colors, 'header')}>Users</th>
                  <th style={styles.tableCell(colors, 'header')}>ARPU</th>
                  <th style={styles.tableCell(colors, 'header')}>D30 Retention</th>
                  <th style={styles.tableCell(colors, 'header')}>Strategy</th>
                </tr>
              </thead>
              <tbody>
                <tr style={styles.tableRow(colors)}>
                  <td style={styles.tableCell(colors)}>Premium Power Users</td>
                  <td style={styles.tableCell(colors)}>275K</td>
                  <td style={styles.tableCell(colors)}>$89</td>
                  <td style={styles.tableCell(colors)}>84%</td>
                  <td style={styles.tableCell(colors)}>VIP Retention</td>
                </tr>
                <tr style={styles.tableRow(colors)}>
                  <td style={styles.tableCell(colors)}>Active Growers</td>
                  <td style={styles.tableCell(colors)}>372K</td>
                  <td style={styles.tableCell(colors)}>$24</td>
                  <td style={styles.tableCell(colors)}>72%</td>
                  <td style={styles.tableCell(colors)}>Upgrade Path</td>
                </tr>
                <tr style={styles.tableRow(colors)}>
                  <td style={styles.tableCell(colors)}>Casual Users</td>
                  <td style={styles.tableCell(colors)}>336K</td>
                  <td style={styles.tableCell(colors)}>$8</td>
                  <td style={styles.tableCell(colors)}>58%</td>
                  <td style={styles.tableCell(colors)}>Engagement</td>
                </tr>
                <tr style={styles.tableRow(colors)}>
                  <td style={styles.tableCell(colors)}>At-Risk Churners</td>
                  <td style={styles.tableCell(colors)}>216K</td>
                  <td style={styles.tableCell(colors)}>$5</td>
                  <td style={styles.tableCell(colors)}>22%</td>
                  <td style={styles.tableCell(colors)}>Win-Back</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* ===== PAGE 5: USER BEHAVIOR ===== */}
      <div style={styles.page(colors)}>
        <div style={styles.pageHeader(colors)}>
          <h1 style={styles.pageTitle(colors)}>User Behavior Analytics</h1>
          <div style={styles.pageHeaderLine(colors)} />
        </div>

        <div style={styles.pageContent}>
          {/* Retention Cohorts */}
          <div style={styles.behaviorSection(colors)}>
            <h3 style={styles.sectionSubtitle(colors)}>Retention Cohort Analysis</h3>
            <p style={styles.sectionDescription(colors)}>
              Day-30 retention rates by cohort vintage showing product-market fit stability.
            </p>
            <div style={styles.cohortTable(colors)}>
              <table style={styles.table(colors)}>
                <thead>
                  <tr style={styles.tableRow(colors)}>
                    <th style={styles.tableCell(colors, 'header')}>Cohort</th>
                    <th style={styles.tableCell(colors, 'header')}>D1</th>
                    <th style={styles.tableCell(colors, 'header')}>D7</th>
                    <th style={styles.tableCell(colors, 'header')}>D14</th>
                    <th style={styles.tableCell(colors, 'header')}>D30</th>
                  </tr>
                </thead>
                <tbody>
                  <tr style={styles.tableRow(colors)}>
                    <td style={styles.tableCell(colors)}>Sept 2025</td>
                    <td style={styles.tableCell(colors)}>92%</td>
                    <td style={styles.tableCell(colors)}>84%</td>
                    <td style={styles.tableCell(colors)}>76%</td>
                    <td style={styles.tableCell(colors)}>68%</td>
                  </tr>
                  <tr style={styles.tableRow(colors)}>
                    <td style={styles.tableCell(colors)}>Aug 2025</td>
                    <td style={styles.tableCell(colors)}>91%</td>
                    <td style={styles.tableCell(colors)}>82%</td>
                    <td style={styles.tableCell(colors)}>74%</td>
                    <td style={styles.tableCell(colors)}>66%</td>
                  </tr>
                  <tr style={styles.tableRow(colors)}>
                    <td style={styles.tableCell(colors)}>Jul 2025</td>
                    <td style={styles.tableCell(colors)}>90%</td>
                    <td style={styles.tableCell(colors)}>81%</td>
                    <td style={styles.tableCell(colors)}>72%</td>
                    <td style={styles.tableCell(colors)}>64%</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Engagement Metrics */}
          <div style={styles.engagementGrid(colors)}>
            <div style={styles.engagementCard(colors)}>
              <div style={styles.engagementMetric(colors)}>
                <div style={styles.metricLabel(colors)}>Avg Session Length</div>
                <div style={styles.metricValueLarge(colors)}>8.4 min</div>
              </div>
            </div>
            <div style={styles.engagementCard(colors)}>
              <div style={styles.engagementMetric(colors)}>
                <div style={styles.metricLabel(colors)}>Sessions per User</div>
                <div style={styles.metricValueLarge(colors)}>12.3</div>
              </div>
            </div>
            <div style={styles.engagementCard(colors)}>
              <div style={styles.engagementMetric(colors)}>
                <div style={styles.metricLabel(colors)}>Feature Adoption Rate</div>
                <div style={styles.metricValueLarge(colors)}>67%</div>
              </div>
            </div>
          </div>

          {/* Migration Flow */}
          <div style={styles.migrationSection(colors)}>
            <h3 style={styles.sectionSubtitle(colors)}>Service Migration Patterns</h3>
            <p style={styles.sectionDescription(colors)}>
              User movement across service offerings shows strong cross-service stickiness and 
              opportunities for premium tier migration.
            </p>
            <div style={styles.migrationFlow(colors)}>
              <div style={styles.flowBox}>
                <div style={styles.flowLabel(colors)}>ElJournal → Esports</div>
                <div style={styles.flowPercent(colors)}>32%</div>
              </div>
              <div style={styles.flowArrow}>→</div>
              <div style={styles.flowBox}>
                <div style={styles.flowLabel(colors)}>Esports → TToons</div>
                <div style={styles.flowPercent(colors)}>28%</div>
              </div>
              <div style={styles.flowArrow}>→</div>
              <div style={styles.flowBox}>
                <div style={styles.flowLabel(colors)}>TToons → Premium</div>
                <div style={styles.flowPercent(colors)}>18%</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ===== PAGE 6: ANOMALIES ===== */}
      <div style={styles.page(colors)}>
        <div style={styles.pageHeader(colors)}>
          <h1 style={styles.pageTitle(colors)}>Anomaly Detection</h1>
          <div style={styles.pageHeaderLine(colors)} />
        </div>

        <div style={styles.pageContent}>
          <p style={styles.sectionDescription(colors)}>
            Z-score and statistical anomaly detection identified unusual patterns requiring 
            investigation and potential action.
          </p>

          {/* Alert Cards */}
          <div style={styles.alertsList}>
            <div style={styles.alertCard(colors, 'critical')}>
              <div style={styles.alertHeader(colors, 'critical')}>
                <span style={styles.alertIcon}>⚠️</span>
                <span style={styles.alertType(colors)}>Critical Anomaly</span>
              </div>
              <div style={styles.alertContent(colors)}>
                <p style={styles.alertTitle(colors)}>
                  Sudden Spike in Trial Cancellations
                </p>
                <p style={styles.alertDesc(colors)}>
                  Trial-to-premium conversion dropped 24% on Oct 18. Root cause likely related to 
                  pricing page update. Recommend A/B test revert.
                </p>
              </div>
            </div>

            <div style={styles.alertCard(colors, 'warning')}>
              <div style={styles.alertHeader(colors, 'warning')}>
                <span style={styles.alertIcon}>⚡</span>
                <span style={styles.alertType(colors)}>Warning Anomaly</span>
              </div>
              <div style={styles.alertContent(colors)}>
                <p style={styles.alertTitle(colors)}>
                  Unusual Bot Activity Detected
                </p>
                <p style={styles.alertDesc(colors)}>
                  3.2K artificial sessions from IP range 192.168.x.x. Recommend IP blacklisting 
                  to improve data quality.
                </p>
              </div>
            </div>

            <div style={styles.alertCard(colors, 'info')}>
              <div style={styles.alertHeader(colors, 'info')}>
                <span style={styles.alertIcon}>ℹ️</span>
                <span style={styles.alertType(colors)}>Notable Trend</span>
              </div>
              <div style={styles.alertContent(colors)}>
                <p style={styles.alertTitle(colors)}>
                  Increase in Weekend Usage
                </p>
                <p style={styles.alertDesc(colors)}>
                  Weekend DAU increased 18% vs weekday average. May indicate new user segment 
                  or campaign resonance.
                </p>
              </div>
            </div>
          </div>

          {/* Timeline */}
          <div style={styles.timelineSection(colors)}>
            <h3 style={styles.sectionSubtitle(colors)}>Alert Timeline</h3>
            <div style={styles.timeline(colors)}>
              <div style={styles.timelineEvent(colors)}>
                <div style={styles.timelineDate(colors)}>Oct 22</div>
                <div style={styles.timelineContent}>Anomaly detected and flagged</div>
              </div>
              <div style={styles.timelineEvent(colors)}>
                <div style={styles.timelineDate(colors)}>Oct 20</div>
                <div style={styles.timelineContent}>Bot activity spike begins</div>
              </div>
              <div style={styles.timelineEvent(colors)}>
                <div style={styles.timelineDate(colors)}>Oct 18</div>
                <div style={styles.timelineContent}>Trial conversion drop detected</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ===== PAGE 7: RECOMMENDATIONS ===== */}
      <div style={styles.page(colors)}>
        <div style={styles.pageHeader(colors)}>
          <h1 style={styles.pageTitle(colors)}>Strategic Recommendations</h1>
          <div style={styles.pageHeaderLine(colors)} />
        </div>

        <div style={styles.pageContent}>
          {/* Priority Recommendations */}
          <div style={styles.recommendationsGrid}>
            <div style={styles.priorityCard(colors, 'p1')}>
              <div style={styles.priorityHeader(colors, 'p1')}>
                <span style={styles.priorityBadge(colors, 'p1')}>P1</span>
                <span style={styles.priorityTitle(colors)}>Trial Conversion Optimization</span>
              </div>
              <div style={styles.priorityContent(colors)}>
                <div style={styles.impactBox(colors)}>
                  <div style={styles.impactLabel(colors)}>Potential Impact</div>
                  <div style={styles.impactValue(colors)}>+$420K Annual Revenue</div>
                </div>
                <p style={styles.priorityDesc(colors)}>
                  Implement progressive profiling and feature tours. A/B test pricing presentation 
                  to increase trial-to-paid conversion by 8-12%.
                </p>
                <div style={styles.actionItems(colors)}>
                  <div style={styles.actionItem(colors)}>✓ Design feature discovery flow</div>
                  <div style={styles.actionItem(colors)}>✓ Launch 3-variant pricing test</div>
                  <div style={styles.actionItem(colors)}>✓ 2-week conversion tracking</div>
                </div>
              </div>
            </div>

            <div style={styles.priorityCard(colors, 'p2')}>
              <div style={styles.priorityHeader(colors, 'p2')}>
                <span style={styles.priorityBadge(colors, 'p2')}>P2</span>
                <span style={styles.priorityTitle(colors)}>Churn Reduction Campaign</span>
              </div>
              <div style={styles.priorityContent(colors)}>
                <div style={styles.impactBox(colors)}>
                  <div style={styles.impactLabel(colors)}>Potential Impact</div>
                  <div style={styles.impactValue(colors)}>+$189K Annual Revenue</div>
                </div>
                <p style={styles.priorityDesc(colors)}>
                  Implement AI-driven churn prediction with personalized win-back campaigns 
                  targeting high-risk users identified in segmentation analysis.
                </p>
                <div style={styles.actionItems(colors)}>
                  <div style={styles.actionItem(colors)}>✓ Deploy churn prediction model</div>
                  <div style={styles.actionItem(colors)}>✓ Design retention messaging</div>
                  <div style={styles.actionItem(colors)}>✓ Launch re-engagement sequence</div>
                </div>
              </div>
            </div>

            <div style={styles.priorityCard(colors, 'p3')}>
              <div style={styles.priorityHeader(colors, 'p3')}>
                <span style={styles.priorityBadge(colors, 'p3')}>P3</span>
                <span style={styles.priorityTitle(colors)}>Cross-Service Bundling</span>
              </div>
              <div style={styles.priorityContent(colors)}>
                <div style={styles.impactBox(colors)}>
                  <div style={styles.impactLabel(colors)}>Potential Impact</div>
                  <div style={styles.impactValue(colors)}>+$94K Annual Revenue</div>
                </div>
                <p style={styles.priorityDesc(colors)}>
                  Create premium bundle offerings leveraging strong cross-service migration patterns 
                  identified in cohort analysis.
                </p>
                <div style={styles.actionItems(colors)}>
                  <div style={styles.actionItem(colors)}>✓ Design 3 bundle SKUs</div>
                  <div style={styles.actionItem(colors)}>✓ Create upgrade paths</div>
                  <div style={styles.actionItem(colors)}>✓ Launch soft beta program</div>
                </div>
              </div>
            </div>
          </div>

          {/* Summary */}
          <div style={styles.summaryBox(colors)}>
            <h3 style={styles.summaryTitle(colors)}>Total Opportunity: $703K Annual Revenue Uplift</h3>
            <p style={styles.summaryText(colors)}>
              Implementing all three priority recommendations in sequence could increase annual 
              revenue by $703,000 while simultaneously improving customer retention metrics by 12-15% 
              and platform engagement scores across all segments.
            </p>
          </div>

          {/* Footer */}
          <div style={styles.reportFooter(colors)}>
            <p style={styles.footerNote(colors)}>
              Report generated by DigMaco Analytics AI on {generatedDate}. 
              For questions or further analysis, contact the analytics team.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: (colors) => ({
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    backgroundColor: colors.background,
    color: colors.text,
  }),

  page: (colors) => ({
    width: '100%',
    minHeight: '100vh',
    pageBreakAfter: 'always',
    backgroundColor: colors.card,
    display: 'flex',
    flexDirection: 'column',
    padding: '40px 50px',
    boxSizing: 'border-box',
  }),

  // COVER PAGE
  coverGradient: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'space-between',
    background: 'linear-gradient(135deg, #5B5FEF 0%, #7C4DFF 100%)',
    borderRadius: '16px',
    padding: '60px 40px',
    color: 'white',
  },

  coverContent: {
    display: 'flex',
    flexDirection: 'column',
    gap: '60px',
  },

  coverLogo: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },

  logoBadge: (colors) => ({
    width: '56px',
    height: '56px',
    borderRadius: '12px',
    backgroundColor: 'rgba(255,255,255,0.2)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '20px',
    fontWeight: 'bold',
    color: 'white',
  }),

  logoText: {
    fontWeight: 'bold',
  },

  logoName: (colors) => ({
    fontSize: '24px',
    fontWeight: 'bold',
    margin: 0,
    color: 'white',
  }),

  coverTitleSection: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },

  coverTitle: (colors) => ({
    fontSize: '48px',
    fontWeight: 'bold',
    margin: 0,
    lineHeight: 1.2,
    color: 'white',
  }),

  coverSubtitle: (colors) => ({
    fontSize: '20px',
    opacity: 0.9,
    margin: 0,
    color: 'white',
  }),

  reportDetails: (colors) => ({
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    backgroundColor: 'rgba(255,255,255,0.1)',
    padding: '24px',
    borderRadius: '12px',
    borderLeft: '3px solid rgba(255,255,255,0.3)',
  }),

  detailRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },

  detailLabel: (colors) => ({
    fontSize: '12px',
    opacity: 0.8,
    textTransform: 'uppercase',
    color: 'white',
  }),

  detailValue: (colors) => ({
    fontSize: '14px',
    fontWeight: '600',
    color: 'white',
  }),

  healthScoreCard: (colors) => ({
    backgroundColor: 'rgba(255,255,255,0.15)',
    padding: '24px',
    borderRadius: '12px',
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  }),

  scoreTitle: (colors) => ({
    fontSize: '14px',
    fontWeight: '600',
    opacity: 0.9,
    color: 'white',
  }),

  scoreContainer: {
    display: 'flex',
    alignItems: 'center',
    gap: '24px',
  },

  scoreCircle: (colors, score) => ({
    width: '80px',
    height: '80px',
    borderRadius: '50%',
    background: `conic-gradient(#00C896 0deg ${(score / 100) * 360}deg, rgba(255,255,255,0.2) ${(score / 100) * 360}deg)`,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
  }),

  scoreValue: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: 'white',
  },

  scoreLabels: (colors) => ({
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  }),

  scoreLabel: {
    fontSize: '14px',
    fontWeight: '600',
    margin: 0,
    color: 'white',
  },

  scoreSubLabel: {
    fontSize: '12px',
    opacity: 0.8,
    margin: 0,
    color: 'white',
  },

  coverFooter: (colors) => ({
    textAlign: 'center',
    borderTop: '1px solid rgba(255,255,255,0.2)',
    paddingTop: '20px',
  }),

  footerText: (colors) => ({
    fontSize: '13px',
    opacity: 0.8,
    margin: 0,
    color: 'white',
  }),

  // PAGE HEADER
  pageHeader: (colors) => ({
    marginBottom: '32px',
    paddingBottom: '24px',
  }),

  pageTitle: (colors) => ({
    fontSize: '36px',
    fontWeight: 'bold',
    margin: '0 0 16px 0',
    color: colors.primary,
  }),

  pageHeaderLine: (colors) => ({
    width: '60px',
    height: '4px',
    backgroundColor: colors.primary,
    borderRadius: '2px',
  }),

  pageContent: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    gap: '24px',
  },

  // KPI CARDS
  kpiGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(4, 1fr)',
    gap: '16px',
  },

  kpiCard: (colors) => ({
    backgroundColor: colors.background,
    padding: '20px',
    borderRadius: '12px',
    border: `1px solid ${colors.border}`,
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  }),

  kpiLabel: (colors) => ({
    fontSize: '11px',
    fontWeight: '600',
    color: colors.lightText,
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  }),

  kpiValue: {
    fontSize: '28px',
    fontWeight: 'bold',
    color: '#1F2937',
  },

  kpiTrend: (colors, direction) => ({
    fontSize: '12px',
    color: direction === 'up' ? colors.success : colors.success,
    fontWeight: '500',
  }),

  // AI SUMMARY
  aiSummaryBox: (colors) => ({
    backgroundColor: `${colors.primary}08`,
    border: `1px solid ${colors.primary}30`,
    borderRadius: '12px',
    padding: '20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  }),

  aiHeader: (colors) => ({
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  }),

  aiIcon: {
    fontSize: '18px',
  },

  aiTitle: (colors) => ({
    fontSize: '13px',
    fontWeight: '700',
    color: colors.primary,
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  }),

  aiText: (colors) => ({
    fontSize: '13px',
    lineHeight: '1.6',
    color: colors.text,
    margin: 0,
  }),

  // METRICS GRID
  metricsGrid: (colors) => ({
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '16px',
  }),

  metricBox: (colors) => ({
    backgroundColor: colors.background,
    padding: '16px',
    borderRadius: '10px',
    border: `1px solid ${colors.border}`,
    textAlign: 'center',
  }),

  metricLabel: (colors) => ({
    fontSize: '11px',
    fontWeight: '600',
    color: colors.lightText,
    textTransform: 'uppercase',
    marginBottom: '8px',
  }),

  metricValue: {
    fontSize: '18px',
    fontWeight: 'bold',
    color: colors.primary,
  },

  metricValueLarge: (colors) => ({
    fontSize: '24px',
    fontWeight: 'bold',
    color: colors.primary,
  }),

  // RISK GAUGE
  sectionRow: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '20px',
  },

  riskGauge: (colors) => ({
    backgroundColor: colors.background,
    padding: '20px',
    borderRadius: '12px',
    border: `1px solid ${colors.border}`,
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  }),

  gaugeTitle: (colors) => ({
    fontSize: '13px',
    fontWeight: '700',
    color: colors.text,
  }),

  gaugeVisual: {
    height: '24px',
    backgroundColor: colors.border,
    borderRadius: '12px',
    overflow: 'hidden',
  },

  gaugeFill: (colors, percent) => ({
    height: '100%',
    width: `${percent}%`,
    backgroundColor: colors.danger,
  }),

  gaugeLabel: (colors) => ({
    fontSize: '12px',
    fontWeight: '600',
    color: colors.text,
  }),

  highRiskBox: (colors) => ({
    backgroundColor: `${colors.danger}08`,
    border: `1px solid ${colors.danger}30`,
    borderRadius: '12px',
    padding: '20px',
  }),

  boxTitle: (colors) => ({
    fontSize: '13px',
    fontWeight: '700',
    color: colors.text,
    marginBottom: '12px',
  }),

  riskStats: (colors) => ({
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '12px',
  }),

  riskStat: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },

  riskNumber: {
    fontSize: '18px',
    fontWeight: 'bold',
    color: colors.danger,
  },

  riskLabel: {
    fontSize: '11px',
    color: colors.lightText,
  },

  // SECTIONS
  driversSection: (colors) => ({
    marginTop: '12px',
  }),

  sectionSubtitle: (colors) => ({
    fontSize: '14px',
    fontWeight: '700',
    color: colors.text,
    marginBottom: '12px',
  }),

  sectionDescription: (colors) => ({
    fontSize: '12px',
    color: colors.lightText,
    lineHeight: '1.5',
    marginBottom: '12px',
  }),

  driversList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },

  driverItem: (colors) => ({
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '12px',
    backgroundColor: colors.background,
    borderRadius: '10px',
    border: `1px solid ${colors.border}`,
  }),

  driverRank: {
    fontSize: '14px',
    fontWeight: 'bold',
    color: colors.primary,
    minWidth: '24px',
  },

  driverInfo: {
    flex: 1,
  },

  driverName: (colors) => ({
    fontSize: '12px',
    fontWeight: '600',
    color: colors.text,
  }),

  driverImpact: (colors) => ({
    fontSize: '11px',
    color: colors.lightText,
    marginTop: '2px',
  }),

  driverBar: (colors, percent) => ({
    minWidth: '60px',
    height: '6px',
    backgroundColor: colors.border,
    borderRadius: '3px',
    overflow: 'hidden',
    background: `linear-gradient(90deg, ${colors.primary} 0%, ${colors.primary} ${percent}%, ${colors.border} ${percent}%)`,
  }),

  // RECOMMENDATION BOX
  recommendationBox: (colors) => ({
    backgroundColor: `${colors.primary}08`,
    border: `1px solid ${colors.primary}30`,
    borderRadius: '12px',
    padding: '16px',
  }),

  recTitle: (colors) => ({
    fontSize: '13px',
    fontWeight: '700',
    color: colors.text,
    marginBottom: '8px',
  }),

  recList: (colors) => ({
    margin: 0,
    paddingLeft: '20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  }),

  recItem: (colors) => ({
    fontSize: '12px',
    color: colors.text,
    lineHeight: '1.4',
  }),

  // SEGMENTATION
  segmentGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(4, 1fr)',
    gap: '12px',
    marginBottom: '20px',
  },

  segmentCard: (colors, accentColor) => ({
    backgroundColor: colors.background,
    border: `2px solid ${accentColor}20`,
    borderRadius: '10px',
    padding: '16px',
    borderLeft: `4px solid ${accentColor}`,
  }),

  segmentName: (colors) => ({
    fontSize: '13px',
    fontWeight: '700',
    color: colors.text,
    marginBottom: '8px',
  }),

  segmentStats: (colors) => ({
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  }),

  // TABLE
  comparisonTable: (colors) => ({
    backgroundColor: colors.background,
    border: `1px solid ${colors.border}`,
    borderRadius: '10px',
    overflow: 'hidden',
  }),

  tableHeader: (colors) => ({
    fontSize: '12px',
    fontWeight: '700',
    padding: '12px 16px',
    backgroundColor: colors.primary,
    color: 'white',
  }),

  table: (colors) => ({
    width: '100%',
    borderCollapse: 'collapse',
  }),

  tableRow: (colors) => ({
    borderBottom: `1px solid ${colors.border}`,
  }),

  tableCell: (colors, type = 'cell') => ({
    padding: '10px 12px',
    fontSize: '11px',
    textAlign: 'left',
    color: type === 'header' ? 'white' : colors.text,
    backgroundColor: type === 'header' ? colors.primary : colors.card,
  }),

  cohortTable: (colors) => ({
    marginTop: '12px',
  }),

  // ENGAGEMENT
  engagementGrid: (colors) => ({
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '12px',
  }),

  engagementCard: (colors) => ({
    backgroundColor: colors.background,
    padding: '16px',
    borderRadius: '10px',
    border: `1px solid ${colors.border}`,
  }),

  engagementMetric: (colors) => ({
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  }),

  // MIGRATION
  migrationSection: (colors) => ({
    marginTop: '16px',
  }),

  migrationFlow: (colors) => ({
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginTop: '12px',
    flexWrap: 'wrap',
  }),

  flowBox: {
    backgroundColor: colors.background,
    border: `1px solid ${colors.border}`,
    borderRadius: '8px',
    padding: '12px',
    textAlign: 'center',
  },

  flowLabel: (colors) => ({
    fontSize: '11px',
    fontWeight: '600',
    color: colors.lightText,
  }),

  flowPercent: (colors) => ({
    fontSize: '16px',
    fontWeight: 'bold',
    color: colors.primary,
    marginTop: '4px',
  }),

  flowArrow: {
    fontSize: '18px',
    color: colors.lightText,
  },

  // ALERTS
  alertsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },

  alertCard: (colors, severity) => {
    const severityColors = {
      critical: '#FF5A5F',
      warning: '#FFB020',
      info: '#5B5FEF',
    };
    return {
      backgroundColor: `${severityColors[severity]}08`,
      border: `1px solid ${severityColors[severity]}30`,
      borderRadius: '10px',
      padding: '16px',
    };
  },

  alertHeader: (colors, severity) => {
    const severityColors = {
      critical: '#FF5A5F',
      warning: '#FFB020',
      info: '#5B5FEF',
    };
    return {
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      marginBottom: '8px',
      color: severityColors[severity],
    };
  },

  alertIcon: {
    fontSize: '16px',
  },

  alertType: (colors) => ({
    fontSize: '12px',
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  }),

  alertContent: (colors) => ({
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  }),

  alertTitle: (colors) => ({
    fontSize: '12px',
    fontWeight: '700',
    color: colors.text,
    margin: 0,
  }),

  alertDesc: (colors) => ({
    fontSize: '11px',
    color: colors.lightText,
    lineHeight: '1.4',
    margin: 0,
  }),

  // TIMELINE
  timelineSection: (colors) => ({
    marginTop: '16px',
  }),

  timeline: (colors) => ({
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    marginTop: '12px',
    paddingLeft: '20px',
    borderLeft: `2px solid ${colors.primary}`,
  }),

  timelineEvent: (colors) => ({
    display: 'flex',
    gap: '12px',
  }),

  timelineDate: (colors) => ({
    fontSize: '11px',
    fontWeight: '700',
    color: colors.primary,
    minWidth: '50px',
    marginLeft: '-32px',
    textAlign: 'right',
  }),

  timelineContent: {
    fontSize: '12px',
    color: colors.text,
  },

  // RECOMMENDATIONS
  recommendationsGrid: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },

  priorityCard: (colors, priority) => {
    const priorityColors = {
      p1: '#FF5A5F',
      p2: '#FFB020',
      p3: '#5B5FEF',
    };
    return {
      backgroundColor: `${priorityColors[priority]}08`,
      border: `1px solid ${priorityColors[priority]}30`,
      borderRadius: '12px',
      padding: '16px',
    };
  },

  priorityHeader: (colors, priority) => {
    const priorityColors = {
      p1: '#FF5A5F',
      p2: '#FFB020',
      p3: '#5B5FEF',
    };
    return {
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      marginBottom: '12px',
      color: priorityColors[priority],
    };
  },

  priorityBadge: (colors, priority) => {
    const priorityColors = {
      p1: '#FF5A5F',
      p2: '#FFB020',
      p3: '#5B5FEF',
    };
    return {
      fontSize: '12px',
      fontWeight: 'bold',
      padding: '4px 8px',
      borderRadius: '4px',
      backgroundColor: `${priorityColors[priority]}20`,
      color: priorityColors[priority],
    };
  },

  priorityTitle: (colors) => ({
    fontSize: '13px',
    fontWeight: '700',
    color: colors.text,
  }),

  priorityContent: (colors) => ({
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
  }),

  priorityDesc: (colors) => ({
    fontSize: '12px',
    color: colors.text,
    lineHeight: '1.5',
    margin: 0,
  }),

  impactBox: (colors) => ({
    backgroundColor: colors.card,
    padding: '10px 12px',
    borderRadius: '6px',
    border: `1px solid ${colors.border}`,
  }),

  impactLabel: (colors) => ({
    fontSize: '10px',
    fontWeight: '600',
    color: colors.lightText,
    textTransform: 'uppercase',
  }),

  impactValue: (colors) => ({
    fontSize: '14px',
    fontWeight: 'bold',
    color: colors.primary,
    marginTop: '2px',
  }),

  actionItems: (colors) => ({
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
    paddingTop: '4px',
  }),

  actionItem: (colors) => ({
    fontSize: '11px',
    color: colors.text,
    lineHeight: 1.3,
  }),

  // SUMMARY
  summaryBox: (colors) => ({
    backgroundColor: colors.primary,
    color: 'white',
    borderRadius: '12px',
    padding: '20px',
    marginTop: '12px',
  }),

  summaryTitle: (colors) => ({
    fontSize: '14px',
    fontWeight: 'bold',
    margin: '0 0 8px 0',
    color: 'white',
  }),

  summaryText: (colors) => ({
    fontSize: '12px',
    lineHeight: '1.6',
    margin: 0,
    opacity: 0.95,
    color: 'white',
  }),

  // FOOTER
  reportFooter: (colors) => ({
    marginTop: '32px',
    paddingTop: '20px',
    borderTop: `1px solid ${colors.border}`,
    textAlign: 'center',
  }),

  footerNote: (colors) => ({
    fontSize: '11px',
    color: colors.lightText,
    margin: 0,
  }),
};
