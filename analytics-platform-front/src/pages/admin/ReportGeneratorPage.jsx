import { useState, useEffect, useRef } from 'react';
import { FileText, ChevronRight, Check, Loader2, Download, AlertCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import AppLayout from '../../components/layout/AppLayout';
import { useAuth } from '../../context/AuthContext';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const REPORT_TYPES = [
  {
    id: 'executive',
    label: 'Executive Summary',
    desc: 'High-level KPI overview for leadership',
    color: '#3b82f6',
    badge: null,
  },
  {
    id: 'churn',
    label: 'Churn & Retention Analysis',
    desc: 'Unsubscription trends and cohort analysis',
    color: '#ef4444',
    badge: null,
  },
  {
    id: 'ai_segmentation',
    label: 'AI Insights & Segmentation',
    desc: 'ML predictions and subscriber segments',
    color: '#a855f7',
    badge: 'Recommended',
    badgeColor: '#06b6d4',
  },
  {
    id: 'full',
    label: 'Complete Report',
    desc: 'Full analysis across all modules',
    color: '#22c55e',
    badge: 'Comprehensive',
    badgeColor: '#f59e0b',
  },
];

const SECTIONS = [
  {
    id: 'summary',
    label: 'Executive Summary',
    desc: 'High-level overview and key metrics',
    default: true,
  },
  {
    id: 'activity',
    label: 'User Activity',
    desc: 'DAU · WAU · MAU · Stickiness ratio',
    default: true,
  },
  {
    id: 'churn',
    label: 'Churn Analysis',
    desc: 'Churn rate · Trends · Key drivers',
    default: true,
  },
  {
    id: 'retention',
    label: 'Retention & Cohorts',
    desc: 'D7 · D14 · D30 retention by service',
    default: true,
  },
  {
    id: 'trial',
    label: 'Free Trial Behavior',
    desc: 'Conversion · Dropoff D1/D2/D3',
    default: true,
  },
  {
    id: 'campaigns',
    label: 'Campaign Impact (SMS)',
    desc: 'ROI · Conversion · Campaign timeline',
    default: true,
  },
  {
    id: 'ai_segmentation',
    label: 'AI & Segmentation',
    desc: 'Churn prediction · K-Means clustering',
    default: true,
  },
  {
    id: 'raw_data',
    label: 'Raw Data Export',
    desc: 'Detailed data tables',
    default: false,
  },
];

const DEFAULT_SERVICES = [
  { id: 'ElJournal', color: '#3b82f6', abbr: 'EJ' },
  { id: 'Esports.tn', color: '#06b6d4', abbr: 'ES' },
  { id: 'ttoons', color: '#22c55e', abbr: 'TT' },
  { id: 'Tawer', color: '#a855f7', abbr: 'TW' },
];

const GENERATION_STEPS = [
  'Extracting KPIs from analytics database',
  'Analyzing churn and retention metrics',
  'Generating AI insights (Gemini)',
  'Building PDF visualizations',
  'Compiling final document',
];

const REPORT_TYPE_SECTIONS = {
  executive: ['summary', 'activity'],
  churn: ['churn', 'retention', 'trial'],
  ai_segmentation: ['summary', 'ai_segmentation', 'campaigns'],
  full: SECTIONS.map((s) => s.id),
};

export default function ReportGeneratorPage() {
  const navigate = useNavigate();
  const { access_token, logout } = useAuth();
  const [reportType, setReportType] = useState('full');
  const [selectedServices, setSelectedServices] = useState([
    'ElJournal',
    'Esports.tn',
    'ttoons',
    'Tawer',
  ]);
  const [services, setServices] = useState(DEFAULT_SERVICES);
  const [selectedSections, setSelectedSections] = useState(
    SECTIONS.filter((s) => s.default).map((s) => s.id)
  );
  const [includeAI, setIncludeAI] = useState(true);
  const [includeRecs, setIncludeRecs] = useState(true);
  const [reportLanguage, setReportLanguage] = useState('fr');
  const [geminiPromptTemplate, setGeminiPromptTemplate] = useState('');
  const [periodStart, setPeriodStart] = useState('2025-09-01');
  const [periodEnd, setPeriodEnd] = useState('2025-10-31');

  const [activeRun, setActiveRun] = useState(null);
  const [reportId, setReportId] = useState(null);
  const [isLaunching, setIsLaunching] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [error, setError] = useState(null);

  const [history, setHistory] = useState([]);
  const [histLoading, setHistLoading] = useState(false);

  const pollingRef = useRef(null);

  const allServiceIds = services.map((s) => s.id);
  const allServicesSelected = selectedServices.length === allServiceIds.length;

  const handleServicesDropdown = (event) => {
    const value = event.target.value;
    if (value === '__all__') {
      setSelectedServices(allServicesSelected ? [] : allServiceIds);
      return;
    }
    if (!value) return;
    setSelectedServices((prev) =>
      prev.includes(value) ? prev.filter((s) => s !== value) : [...prev, value]
    );
  };

  const toggleSection = (id) => {
    setSelectedSections((prev) =>
      prev.includes(id) ? prev.filter((s) => s !== id) : [...prev, id]
    );
  };

  const toggleAllSections = () => {
    if (selectedSections.length === SECTIONS.length) {
      setSelectedSections([]);
    } else {
      setSelectedSections(SECTIONS.map((s) => s.id));
    }
  };

  const startPolling = (id) => {
    if (!access_token) return;
    if (pollingRef.current) clearInterval(pollingRef.current);

    pollingRef.current = setInterval(async () => {
      try {
        const res = await fetch(
          `${API_BASE}/reports/status/${id}`,
          {
            headers: { Authorization: `Bearer ${access_token}` },
          }
        );
        if (res.status === 401) {
          logout();
          navigate('/login');
          return;
        }
        const data = await res.json();
        setActiveRun(data);

        if (data.status === 'success' || data.status === 'failed') {
          clearInterval(pollingRef.current);
          pollingRef.current = null;
          if (data.status === 'success') {
            fetchHistory();
          }
        }
      } catch {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
    }, 2000);
  };

  useEffect(() => {
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, []);

  useEffect(() => {
    const fetchServices = async () => {
      if (!access_token) return;
      try {
        const res = await fetch(`${API_BASE}/services`, {
          headers: { Authorization: `Bearer ${access_token}` },
        });
        if (!res.ok) return;
        const data = await res.json();
        const list = Array.isArray(data) ? data : data?.items || [];
        const mapped = list
          .map((s, idx) => {
            const name = s.service_name || s.name || s.id;
            if (!name) return null;
            const palette = ['#3b82f6', '#06b6d4', '#22c55e', '#a855f7', '#f59e0b', '#ef4444', '#14b8a6'];
            return {
              id: String(name),
              color: palette[idx % palette.length],
              abbr: String(name).slice(0, 2).toUpperCase(),
            };
          })
          .filter(Boolean);
        if (mapped.length > 0) {
          setServices(mapped);
          setSelectedServices(mapped.map((x) => x.id));
        }
      } catch {
        // keep defaults
      }
    };
    fetchServices();
  }, [access_token]);

  useEffect(() => {
    const mapped = REPORT_TYPE_SECTIONS[reportType] || [];
    setSelectedSections(mapped);
  }, [reportType]);

  const handleGenerate = async () => {
    if (!access_token) {
      setError('Session expirée. Veuillez vous reconnecter.');
      navigate('/login');
      return;
    }
    setError(null);
    if (selectedServices.length === 0) {
      setError('Please select at least one service.');
      return;
    }
    if (selectedSections.length === 0) {
      setError('Please select at least one report section.');
      return;
    }
    if (!periodStart || !periodEnd || periodStart > periodEnd) {
      setError('Please choose a valid date range.');
      return;
    }
    setIsLaunching(true);
    setShowModal(true);
    setActiveRun({
      status: 'generating',
      current_step: GENERATION_STEPS[0],
      current_step_num: 1,
      total_steps: 5,
      progress_pct: 0,
    });

    try {
      const res = await fetch(`${API_BASE}/reports/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${access_token}`,
        },
        body: JSON.stringify({
          report_type: reportType,
          period_start: periodStart,
          period_end: periodEnd,
          services_included: selectedServices,
          sections_included: selectedSections,
          distribution_format: 'pdf',
          include_ai_insights: includeAI,
          include_recommendations: includeRecs,
          language: reportLanguage,
          gemini_prompt_template: geminiPromptTemplate,
        }),
      });

      const data = await res.json();
      if (res.status === 401) {
        logout();
        navigate('/login');
        return;
      }

      if (!res.ok) {
        throw new Error(data.detail || 'Erreur de génération');
      }

      setReportId(data.report_id);
      startPolling(data.report_id);
    } catch (err) {
      setError(err.message);
      setActiveRun((prev) => ({
        ...prev,
        status: 'failed',
        error: err.message,
      }));
    } finally {
      setIsLaunching(false);
    }
  };

  const handleDownload = async (id) => {
    if (!access_token) {
      setError('Session expirée. Veuillez vous reconnecter.');
      navigate('/login');
      return;
    }
    try {
      const res = await fetch(
        `${API_BASE}/reports/download/${id}`,
        {
          headers: { Authorization: `Bearer ${access_token}` },
        }
      );
      if (res.status === 401) {
        logout();
        navigate('/login');
        return;
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `digmaco_report_${id}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      setError('Téléchargement impossible.');
    }
  };

  const fetchHistory = async () => {
    if (!access_token) return;
    setHistLoading(true);
    try {
      const res = await fetch(`${API_BASE}/reports/history`, {
        headers: { Authorization: `Bearer ${access_token}` },
      });
      if (res.status === 401) {
        logout();
        navigate('/login');
        return;
      }
      const data = await res.json();
      setHistory(data);
    } catch {
      console.error('History fetch failed');
    } finally {
      setHistLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [access_token]);

  return (
    <AppLayout pageTitle="Report Generator">
      <div style={styles.page}>
      <main style={styles.mainContent}>
        <div style={styles.contentWrapper}>
          {/* LEFT CONFIG PANEL */}
          <section style={styles.leftPanel}>
            {/* Header */}
            <div style={styles.pageHeader}>
              <div style={styles.headerLeft}>
                <div style={styles.headerIcon}>
                  <FileText size={24} color="var(--color-primary)" />
                </div>
                <div>
                  <h1 style={styles.pageTitle}>Report Generator</h1>
                  <p style={styles.pageDesc}>
                    Generate custom PDF reports enriched with AI-powered insights and analytics
                  </p>
                </div>
              </div>
              <div style={styles.headerBadge}>
                <span style={styles.badgeIcon}>💡</span>
                <span style={styles.badgeText}>AI-Powered</span>
              </div>
            </div>

            {/* Config Card */}
            <div style={styles.configCard}>
              {/* STEP 1: Report Type */}
              <div style={styles.stepSection}>
                <div style={styles.stepLabel}>
                  <span style={styles.stepNumber}>01</span>
                  <h3 style={styles.stepTitle}>Report Type</h3>
                </div>
                <div style={styles.reportTypeGrid}>
                  {REPORT_TYPES.map((type) => (
                    <button
                      key={type.id}
                      onClick={() => setReportType(type.id)}
                      style={{
                        ...styles.reportTypeCard,
                        ...(reportType === type.id && {
                          borderColor: type.color,
                          borderWidth: '2px',
                          backgroundColor: `${type.color}15`,
                        }),
                      }}
                    >
                      <div style={styles.reportTypeHeader}>
                        <div
                          style={{
                            ...styles.reportTypeIcon,
                            color: type.color,
                          }}
                        >
                          <FileText size={20} />
                        </div>
                        {reportType === type.id && (
                          <div
                            style={{
                              ...styles.checkIcon,
                              backgroundColor: type.color,
                            }}
                          >
                            <Check size={14} color="white" />
                          </div>
                        )}
                      </div>
                      {type.badge && (
                        <span
                          style={{
                            ...styles.typeBadge,
                            backgroundColor: `${type.badgeColor}20`,
                            color: type.badgeColor,
                          }}
                        >
                          {type.badge}
                        </span>
                      )}
                      <h4 style={styles.reportTypeName}>{type.label}</h4>
                      <p style={styles.reportTypeDesc}>{type.desc}</p>
                    </button>
                  ))}
                </div>
              </div>

              {/* STEP 2: Services */}
              <div style={styles.stepSection}>
                <div style={styles.stepLabel}>
                  <span style={styles.stepNumber}>02</span>
                  <h3 style={styles.stepTitle}>Included Services</h3>
                </div>
                <div style={styles.dateRangeRow}>
                  <div style={styles.dateField}>
                    <label style={styles.aiConfigLabel}>Start date</label>
                    <input
                      type="date"
                      value={periodStart}
                      onChange={(e) => setPeriodStart(e.target.value)}
                      style={styles.aiConfigSelect}
                    />
                  </div>
                  <div style={styles.dateField}>
                    <label style={styles.aiConfigLabel}>End date</label>
                    <input
                      type="date"
                      value={periodEnd}
                      onChange={(e) => setPeriodEnd(e.target.value)}
                      style={styles.aiConfigSelect}
                    />
                  </div>
                </div>
                <div style={styles.serviceDropdownWrap}>
                  <select
                    onChange={handleServicesDropdown}
                    value=""
                    style={styles.serviceDropdown}
                  >
                    <option value="" disabled>
                      {allServicesSelected
                        ? 'All services selected'
                        : `${selectedServices.length} service(s) selected`}
                    </option>
                    <option value="__all__">
                      {allServicesSelected ? 'Unselect all services' : 'Select all services'}
                    </option>
                    {services.map((service) => (
                      <option key={service.id} value={service.id}>
                        {selectedServices.includes(service.id) ? '✓ ' : ''}{service.id}
                      </option>
                    ))}
                  </select>
                  <div style={styles.selectedServicesChips}>
                    {selectedServices.map((serviceId) => (
                      <span key={serviceId} style={styles.selectedServiceChip}>
                        {serviceId}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* STEP 3: Sections */}
              <div style={styles.stepSection}>
                <div style={styles.stepLabel}>
                  <span style={styles.stepNumber}>03</span>
                  <h3 style={styles.stepTitle}>Report Sections</h3>
                </div>
                <button
                  onClick={toggleAllSections}
                  style={styles.selectAllButton}
                >
                  {selectedSections.length === SECTIONS.length
                    ? 'Deselect All'
                    : 'Select All'}
                </button>
                <div style={styles.sectionsList}>
                  {SECTIONS.map((section) => (
                    <label
                      key={section.id}
                      style={styles.sectionRow}
                    >
                      <div style={styles.sectionCheckbox}>
                        <input
                          type="checkbox"
                          checked={selectedSections.includes(section.id)}
                          onChange={() => toggleSection(section.id)}
                          style={styles.checkboxInput}
                        />
                        {selectedSections.includes(section.id) && (
                          <Check
                            size={14}
                            color="white"
                            style={styles.checkmark}
                          />
                        )}
                      </div>
                      <div style={styles.sectionInfo}>
                        <span style={styles.sectionLabelText}>
                          {section.label}
                        </span>
                        <p style={styles.sectionDesc}>
                          {section.desc}
                        </p>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {/* STEP 4: AI Options */}
              <div style={styles.stepSection}>
                <div style={styles.stepLabel}>
                  <span style={{ ...styles.stepNumber, color: '#f59e0b' }}>
                    04
                  </span>
                  <h3 style={styles.stepTitle}>AI Options</h3>
                </div>
                <div style={styles.aiOptionsGrid}>
                  <div style={styles.aiOptionCard}>
                    <div style={styles.aiOptionLeft}>
                      <div style={styles.aiOptionTitle}>
                        AI Insights Generation
                        <span style={styles.apiBadge}>Gemini API</span>
                      </div>
                      <p style={styles.aiOptionDesc}>
                        Advanced behavioral anomaly detection.
                      </p>
                    </div>
                    <button
                      onClick={() => setIncludeAI(!includeAI)}
                      style={{
                        ...styles.toggleSwitch,
                        backgroundColor: includeAI
                          ? 'var(--color-primary)'
                          : 'var(--color-border)',
                      }}
                    >
                      <div
                        style={{
                          ...styles.toggleThumb,
                          transform: includeAI
                            ? 'translateX(20px)'
                            : 'translateX(0)',
                        }}
                      />
                    </button>
                  </div>

                  <div style={styles.aiOptionCard}>
                    <div style={styles.aiOptionLeft}>
                      <div style={styles.aiOptionTitle}>
                        Strategic Recommendations
                      </div>
                      <p style={styles.aiOptionDesc}>
                        Recommended actions for retention.
                      </p>
                    </div>
                    <button
                      onClick={() => setIncludeRecs(!includeRecs)}
                      style={{
                        ...styles.toggleSwitch,
                        backgroundColor: includeRecs
                          ? 'var(--color-primary)'
                          : 'var(--color-border)',
                      }}
                    >
                      <div
                        style={{
                          ...styles.toggleThumb,
                          transform: includeRecs
                            ? 'translateX(20px)'
                            : 'translateX(0)',
                        }}
                      />
                    </button>
                  </div>
                </div>
                <div style={styles.aiConfigRow}>
                  <div style={styles.aiConfigBlock}>
                    <label style={styles.aiConfigLabel}>Report language</label>
                    <select
                      value={reportLanguage}
                      onChange={(e) => setReportLanguage(e.target.value)}
                      style={styles.aiConfigSelect}
                    >
                      <option value="fr">Français</option>
                      <option value="en">English</option>
                    </select>
                  </div>
                  <div style={styles.aiConfigBlock}>
                    <label style={styles.aiConfigLabel}>Gemini custom prompt</label>
                    <textarea
                      value={geminiPromptTemplate}
                      onChange={(e) => setGeminiPromptTemplate(e.target.value)}
                      placeholder="Ex: Prioritize concise recommendations, include quantified impact and confidence score."
                      style={styles.aiConfigTextarea}
                    />
                  </div>
                </div>
              </div>

              {/* Generate Button */}
              <button
                onClick={handleGenerate}
                disabled={isLaunching}
                style={{
                  ...styles.generateButton,
                  ...(isLaunching && styles.generateButtonDisabled),
                }}
              >
                {isLaunching ? (
                  <>
                    <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} />
                    Generating Report...
                  </>
                ) : (
                  <>
                    <span style={styles.generateIcon}>✨</span>
                    <div style={styles.generateButtonText}>
                      <span style={styles.generateButtonMain}>
                        Generate Report
                      </span>
                      <span style={styles.generateButtonSub}>
                        ~15 seconds
                      </span>
                    </div>
                  </>
                )}
              </button>
            </div>
          </section>

          {/* RIGHT PREVIEW & HISTORY PANEL */}
          <section style={styles.rightPanel}>
            {/* PDF Preview */}
            <div style={styles.previewCard}>
              <div style={styles.previewHeader}>
                <h3 style={styles.previewTitle}>Document Preview</h3>
                <div style={styles.previewDots}>
                  <div style={{ ...styles.dot, backgroundColor: '#ef4444' }} />
                  <div style={{ ...styles.dot, backgroundColor: '#f59e0b' }} />
                  <div style={{ ...styles.dot, backgroundColor: '#3b82f6' }} />
                </div>
              </div>

              <div style={styles.previewContent}>
                {/* 3D Page Stack */}
                <div style={styles.pageStack}>
                  {/* Back page */}
                  <div
                    style={{
                      ...styles.stackedPage,
                      transform: 'rotate(6deg) translateX(48px) translateY(16px)',
                      opacity: 0.3,
                      zIndex: 1,
                    }}
                  />

                  {/* Mid page */}
                  <div
                    style={{
                      ...styles.stackedPage,
                      transform: 'rotate(3deg) translateX(24px) translateY(8px)',
                      opacity: 0.6,
                      zIndex: 2,
                    }}
                  />

                  {/* Front page */}
                  <div
                    style={{
                      ...styles.stackedPage,
                      zIndex: 10,
                      padding: '24px',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '12px',
                    }}
                  >
                    <div style={styles.pageHeaderBar}>
                      <div style={styles.pageLogoArea}>
                        <div style={styles.pageLogoBadge}>
                          <FileText size={20} color="#adc6ff" />
                        </div>
                        <span style={styles.pageLogoText}>DIGMACO</span>
                      </div>
                      <span style={styles.pageRefId}>ID: REF-2025-042</span>
                    </div>

                    <div style={styles.pageTitleArea}>
                      <h4 style={styles.pageMainTitle}>
                        RAPPORT
                        <br />
                        ANALYTIQUE
                      </h4>
                      <p style={styles.pageDateRange}>
                        Septembre – Octobre 2025
                      </p>
                    </div>

                    <div style={styles.pageTableOfContents}>
                      <p style={styles.tocLabel}>Table of Contents</p>
                      <div style={styles.tocEntry}>
                        <span style={styles.tocItem}>
                          01. Executive Summary
                        </span>
                        <span style={styles.tocPage}>p.02</span>
                      </div>
                      <div style={styles.tocEntry}>
                        <span style={styles.tocItem}>
                          02. Churn Analytics
                        </span>
                        <span style={styles.tocPage}>p.04</span>
                      </div>
                      <div style={styles.tocEntry}>
                        <span style={styles.tocItem}>
                          03. AI & Segmentation
                        </span>
                        <span style={styles.tocPage}>p.08</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div style={styles.previewStats}>
                <span style={styles.statChip}>~18 pages estimated</span>
                <span style={styles.statChip}>PDF Format</span>
                <span style={styles.statChip}>Gemini AI included</span>
                <span style={styles.statChip}>
                  {selectedServices.length} services
                </span>
              </div>
            </div>

            {/* History */}
            <div style={styles.historyCard}>
              <div style={styles.historyHeader}>
                <h3 style={styles.historyTitle}>Recent Reports</h3>
                <button style={styles.seeAllButton}>View all →</button>
              </div>

              {history.length === 0 ? (
                <div style={styles.emptyState}>
                  <div style={styles.emptyIcon}>📄</div>
                  <h3 style={styles.emptyTitle}>No Reports Generated</h3>
                  <p style={styles.emptyDesc}>
                    Configure and launch your first report to see
                    your report history here.
                  </p>
                  <button
                    onClick={handleGenerate}
                    style={styles.emptyButton}
                  >
                    Generate Now
                  </button>
                </div>
              ) : (
                <div style={styles.historyList}>
                  {history.map((item) => (
                    <div key={item.id} style={styles.historyItem}>
                      <div style={styles.historyItemLeft}>
                        <div style={styles.historyIcon}>
                          <FileText
                            size={18}
                            color="#ef4444"
                          />
                        </div>
                        <div style={styles.historyInfo}>
                          <p style={styles.historyName}>
                            {item.file_name?.substring(0, 28)}...
                          </p>
                          <p style={styles.historyMeta}>
                            {new Date(item.created_at).toLocaleDateString()} •{' '}
                            {(item.file_size_kb / 1024).toFixed(1)} MB
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDownload(item.id)}
                        style={styles.downloadButton}
                      >
                        <Download size={16} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </section>
        </div>
      </main>

      {/* GENERATION MODAL */}
      {showModal && activeRun && (
        <div style={styles.modalOverlay}>
          <div style={styles.modalCard}>
            <div style={styles.modalGlowTop} />
            <div style={styles.modalGlowBottom} />

            <div style={styles.modalContent}>
              {/* Progress Circle */}
              <div style={styles.progressCircleContainer}>
                <svg
                  style={styles.progressSvg}
                  viewBox="0 0 128 128"
                >
                  <circle
                    cx="64"
                    cy="64"
                    r="58"
                    fill="none"
                    stroke="var(--color-border)"
                    strokeWidth="6"
                  />
                  <circle
                    cx="64"
                    cy="64"
                    r="58"
                    fill="none"
                    stroke="var(--color-primary)"
                    strokeWidth="8"
                    strokeDasharray={`${364.4}`}
                    strokeDashoffset={`${
                      364.4 - (364.4 * activeRun.progress_pct) / 100
                    }`}
                    style={{
                      transform: 'rotate(-90deg)',
                      transformOrigin: 'center',
                      transition: 'stroke-dashoffset 0.5s ease',
                    }}
                  />
                </svg>
                <div style={styles.progressText}>
                  <span style={styles.progressPercent}>
                    {activeRun.progress_pct || 0}%
                  </span>
                </div>
              </div>

              {/* Title */}
              <h3 style={styles.modalTitle}>
                {activeRun.status === 'success'
                  ? 'Report Generated ✅'
                  : activeRun.status === 'failed'
                  ? 'Generation Failed ❌'
                  : 'Generating Report...'}
              </h3>

              <p style={styles.modalSubtitle}>
                {activeRun.status === 'success'
                  ? 'Your PDF report is ready to download'
                  : 'AI is analyzing your DigMaco data...'}
              </p>

              {/* Steps List */}
              {activeRun.status === 'generating' && (
                <div style={styles.stepsList}>
                  {GENERATION_STEPS.map((step, idx) => {
                    const stepNum = idx + 1;
                    const isDone = stepNum < activeRun.current_step_num;
                    const isCurrent = stepNum === activeRun.current_step_num;

                    return (
                      <div
                        key={idx}
                        style={{
                          ...styles.stepsItem,
                          ...(isDone && styles.stepsItemDone),
                          ...(isCurrent && styles.stepsItemCurrent),
                        }}
                      >
                        <div style={styles.stepsIcon}>
                          {isDone ? (
                            <Check size={16} color="var(--color-success)" />
                          ) : isCurrent ? (
                            <Loader2
                              size={16}
                              style={{
                                color: 'var(--color-primary)',
                                animation: 'spin 1s linear infinite',
                              }}
                            />
                          ) : (
                            <span style={styles.stepsPending}>
                              {stepNum}
                            </span>
                          )}
                        </div>
                        <span style={styles.stepsLabel}>{step}</span>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Progress Bar */}
              <div style={styles.progressBar}>
                <div
                  style={{
                    ...styles.progressBarFill,
                    width: `${activeRun.progress_pct || 0}%`,
                  }}
                />
              </div>

              {/* Status Text */}
              {activeRun.status === 'generating' && (
                <p style={styles.statusText}>
                  Step {activeRun.current_step_num} of 5 — Estimated time: ~10s
                </p>
              )}

              {/* Error Message */}
              {activeRun.status === 'failed' && activeRun.error && (
                <div style={styles.errorBox}>
                  <AlertCircle size={16} />
                  <span>{activeRun.error}</span>
                </div>
              )}

              {/* Action Buttons */}
              <div style={styles.modalButtons}>
                {activeRun.status === 'generating' && (
                  <>
                    <button
                      onClick={() => {
                        clearInterval(pollingRef.current);
                        pollingRef.current = null;
                        setShowModal(false);
                      }}
                      style={styles.buttonOutlined}
                    >
                      Cancel
                    </button>
                  </>
                )}

                {activeRun.status === 'success' && (
                  <>
                    <button
                      onClick={() => {
                        handleDownload(reportId);
                      }}
                      style={styles.buttonPrimary}
                    >
                      <Download size={16} />
                      Download PDF
                    </button>
                    <button
                      onClick={() => setShowModal(false)}
                      style={styles.buttonOutlined}
                    >
                      Close
                    </button>
                  </>
                )}

                {activeRun.status === 'failed' && (
                  <>
                    <button
                      onClick={handleGenerate}
                      style={styles.buttonPrimary}
                    >
                      Retry
                    </button>
                    <button
                      onClick={() => setShowModal(false)}
                      style={styles.buttonOutlined}
                    >
                      Close
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>

          <style>{`
            @keyframes spin {
              from { transform: rotate(0deg); }
              to { transform: rotate(360deg); }
            }
          `}</style>
        </div>
      )}
    </div>
    </AppLayout>
  );
}

const styles = {
  page: {
    width: '100%',
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
  },
  mainContent: {
    flex: 1,
    overflow: 'auto',
    backgroundColor: 'var(--color-bg-primary)',
  },
  contentWrapper: {
    display: 'flex',
    minHeight: '100%',
  },

  /* LEFT PANEL */
  leftPanel: {
    flex: '0 0 40%',
    borderRight: '1px solid var(--color-border)',
    padding: '32px',
    overflowY: 'auto',
  },

  pageHeader: {
    display: 'flex',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    marginBottom: '32px',
  },
  headerLeft: {
    display: 'flex',
    gap: '16px',
    alignItems: 'flex-start',
  },
  headerIcon: {
    width: '48px',
    height: '48px',
    borderRadius: '10px',
    backgroundColor: 'rgba(77, 141, 255, 0.18)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  pageTitle: {
    fontSize: '28px',
    fontWeight: 700,
    color: 'var(--color-text-primary)',
    margin: 0,
    lineHeight: 1.2,
  },
  pageDesc: {
    fontSize: '14px',
    color: 'var(--color-text-secondary)',
    margin: '4px 0 0 0',
    maxWidth: '280px',
  },

  headerBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '8px 12px',
    backgroundColor: 'rgba(77, 141, 255, 0.2)',
    borderRadius: '999px',
    border: '1px solid rgba(77, 141, 255, 0.55)',
  },
  badgeIcon: {
    fontSize: '14px',
  },
  badgeText: {
    fontSize: '11px',
    fontWeight: 700,
    color: '#9CC2FF',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  },

  configCard: {
    backgroundColor: 'var(--color-bg-card)',
    border: '1px solid var(--color-border)',
    borderRadius: '12px',
    padding: '28px',
    display: 'flex',
    flexDirection: 'column',
    gap: '32px',
  },

  stepSection: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  stepLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  },
  stepNumber: {
    width: '28px',
    height: '28px',
    borderRadius: '50%',
    backgroundColor: 'rgba(77, 141, 255, 0.24)',
    color: '#A8C8FF',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '11px',
    fontWeight: 700,
  },
  stepTitle: {
    fontSize: '13px',
    fontWeight: 700,
    color: '#E3ECFF',
    textTransform: 'uppercase',
    letterSpacing: '0.08em',
    margin: 0,
  },

  reportTypeGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '12px',
  },
  reportTypeCard: {
    padding: '16px',
    borderRadius: '10px',
    border: '1px solid var(--color-border)',
    backgroundColor: 'var(--color-bg-elevated)',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    textAlign: 'left',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  reportTypeHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '4px',
  },
  reportTypeIcon: {
    display: 'flex',
    alignItems: 'center',
  },
  checkIcon: {
    width: '20px',
    height: '20px',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  typeBadge: {
    fontSize: '9px',
    fontWeight: 700,
    padding: '3px 6px',
    borderRadius: '4px',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    alignSelf: 'flex-start',
  },
  reportTypeName: {
    fontSize: '14px',
    fontWeight: 700,
    color: 'var(--color-text-primary)',
    margin: 0,
  },
  reportTypeDesc: {
    fontSize: '12px',
    color: 'var(--color-text-muted)',
    margin: 0,
  },

  servicesGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '10px',
  },
  serviceDropdownWrap: {
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
  },
  dateRangeRow: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '10px',
  },
  dateField: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  serviceDropdown: {
    width: '100%',
    padding: '10px 12px',
    borderRadius: '10px',
    border: '1px solid var(--color-border)',
    backgroundColor: 'var(--color-bg-elevated)',
    color: 'var(--color-text-primary)',
    fontSize: '13px',
  },
  selectedServicesChips: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '8px',
  },
  selectedServiceChip: {
    padding: '5px 10px',
    borderRadius: '999px',
    fontSize: '11px',
    fontWeight: 600,
    color: 'var(--color-primary)',
    border: '1px solid var(--color-border)',
    backgroundColor: 'var(--color-bg-elevated)',
  },
  serviceCard: {
    padding: '12px 14px',
    borderRadius: '10px',
    backgroundColor: 'var(--color-bg-elevated)',
    borderBottom: '3px solid',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '8px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },
  serviceAbbr: {
    width: '36px',
    height: '36px',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '12px',
    fontWeight: 700,
  },
  serviceName: {
    fontSize: '11px',
    fontWeight: 700,
    color: 'var(--color-text-primary)',
    textTransform: 'uppercase',
    letterSpacing: '0.03em',
  },

  selectAllButton: {
    alignSelf: 'flex-end',
    fontSize: '12px',
    fontWeight: 600,
    color: 'var(--color-primary)',
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    padding: '4px 0',
    textDecoration: 'underline',
  },

  sectionsList: {
    borderRadius: '10px',
    overflow: 'hidden',
    border: '1px solid var(--color-border)',
    backgroundColor: 'var(--color-bg-elevated)',
  },
  sectionRow: {
    padding: '12px 14px',
    borderBottom: '1px solid var(--color-border)',
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    cursor: 'pointer',
    transition: 'background-color 0.15s ease',
  },
  sectionCheckbox: {
    width: '20px',
    height: '20px',
    borderRadius: '4px',
    border: '2px solid var(--color-primary)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
    flexShrink: 0,
  },
  checkboxInput: {
    position: 'absolute',
    opacity: 0,
    cursor: 'pointer',
    width: '100%',
    height: '100%',
  },
  checkmark: {
    position: 'absolute',
  },
  sectionInfo: {
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
    flex: 1,
  },
  sectionLabelText: {
    fontSize: '13px',
    fontWeight: 600,
    color: 'var(--color-text-primary)',
  },
  sectionDesc: {
    fontSize: '11px',
    color: 'var(--color-text-muted)',
    margin: 0,
  },

  aiOptionsGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '12px',
  },
  aiOptionCard: {
    padding: '14px',
    borderRadius: '10px',
    backgroundColor: 'var(--color-bg-elevated)',
    border: '1px solid var(--color-border)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: '12px',
  },
  aiOptionLeft: {
    flex: 1,
  },
  aiOptionTitle: {
    fontSize: '12px',
    fontWeight: 700,
    color: 'var(--color-text-primary)',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  apiBadge: {
    fontSize: '8px',
    fontWeight: 700,
    padding: '2px 6px',
    borderRadius: '3px',
    backgroundColor: 'rgba(100, 210, 255, 0.22)',
    color: '#9FDFFF',
    textTransform: 'uppercase',
  },
  aiOptionDesc: {
    fontSize: '11px',
    color: 'var(--color-text-muted)',
    margin: '4px 0 0 0',
  },
  aiConfigRow: {
    display: 'grid',
    gridTemplateColumns: '1fr',
    gap: '12px',
  },
  aiConfigBlock: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  aiConfigLabel: {
    fontSize: '12px',
    fontWeight: 600,
    color: 'var(--color-text-secondary)',
  },
  aiConfigSelect: {
    backgroundColor: 'var(--color-bg-elevated)',
    color: 'var(--color-text-primary)',
    border: '1px solid var(--color-border)',
    borderRadius: '8px',
    padding: '10px 12px',
    fontSize: '13px',
  },
  aiConfigTextarea: {
    minHeight: '84px',
    resize: 'vertical',
    backgroundColor: 'var(--color-bg-elevated)',
    color: 'var(--color-text-primary)',
    border: '1px solid var(--color-border)',
    borderRadius: '8px',
    padding: '10px 12px',
    fontSize: '13px',
    lineHeight: 1.4,
    fontFamily: 'inherit',
  },

  toggleSwitch: {
    width: '40px',
    height: '24px',
    borderRadius: '12px',
    border: 'none',
    cursor: 'pointer',
    position: 'relative',
    transition: 'background-color 0.2s ease',
    flexShrink: 0,
  },
  toggleThumb: {
    position: 'absolute',
    top: '2px',
    left: '2px',
    width: '20px',
    height: '20px',
    backgroundColor: 'white',
    borderRadius: '50%',
    transition: 'transform 0.2s ease',
    boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
  },

  generateButton: {
    width: '100%',
    padding: '20px 16px',
    borderRadius: '10px',
    backgroundColor: 'var(--color-primary)',
    color: 'white',
    fontSize: '15px',
    fontWeight: 700,
    border: 'none',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '12px',
    transition: 'all 0.2s ease',
    letterSpacing: '0.03em',
    boxShadow: '0 4px 12px var(--color-primary), opacity: 0.1',
  },
  generateButtonDisabled: {
    backgroundColor: 'var(--color-border)',
    cursor: 'not-allowed',
    boxShadow: 'none',
  },
  generateIcon: {
    fontSize: '18px',
  },
  generateButtonText: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  generateButtonMain: {
    fontSize: '15px',
    fontWeight: 700,
  },
  generateButtonSub: {
    fontSize: '11px',
    opacity: 0.6,
    borderLeft: '1px solid rgba(255,255,255,0.2)',
    paddingLeft: '8px',
  },

  /* RIGHT PANEL */
  rightPanel: {
    flex: '0 0 60%',
    padding: '32px',
    overflowY: 'auto',
    display: 'flex',
    flexDirection: 'column',
    gap: '32px',
  },

  previewCard: {
    backgroundColor: 'var(--color-bg-card)',
    border: '1px solid var(--color-border)',
    borderRadius: '12px',
    padding: '24px',
  },
  previewHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: '20px',
  },
  previewTitle: {
    fontSize: '13px',
    fontWeight: 700,
    color: 'var(--color-text-secondary)',
    textTransform: 'uppercase',
    letterSpacing: '0.08em',
    margin: 0,
  },
  previewDots: {
    display: 'flex',
    gap: '8px',
  },
  dot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
  },

  previewContent: {
    backgroundColor: 'var(--color-bg-elevated)',
    borderRadius: '10px',
    padding: '32px',
    minHeight: '280px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: '20px',
  },
  pageStack: {
    position: 'relative',
    width: '240px',
    height: '320px',
  },
  stackedPage: {
    position: 'absolute',
    width: '100%',
    height: '100%',
    backgroundColor: 'white',
    borderRadius: '6px',
    boxShadow: '0 8px 24px rgba(0,0,0,0.2)',
  },

  pageHeaderBar: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingBottom: '12px',
    borderBottom: '1px solid #e5e7eb',
  },
  pageLogoArea: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
  pageLogoBadge: {
    width: '24px',
    height: '24px',
    backgroundColor: '#0f1e35',
    borderRadius: '4px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  pageLogoText: {
    fontSize: '10px',
    fontWeight: 700,
    color: '#1f2937',
    letterSpacing: '0.05em',
  },
  pageRefId: {
    fontSize: '9px',
    color: '#9ca3af',
    fontFamily: 'monospace',
  },

  pageTitleArea: {
    paddingTop: '8px',
    borderLeft: '3px solid var(--color-primary)',
    paddingLeft: '12px',
  },
  pageMainTitle: {
    fontSize: '16px',
    fontWeight: 700,
    color: '#1f2937',
    margin: 0,
    lineHeight: 1.3,
  },
  pageDateRange: {
    fontSize: '11px',
    color: '#6b7280',
    margin: '4px 0 0 0',
  },

  pageTableOfContents: {
    marginTop: '12px',
  },
  tocLabel: {
    fontSize: '10px',
    fontWeight: 700,
    color: '#1f2937',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    margin: '0 0 6px 0',
    paddingBottom: '4px',
    borderBottom: '1px solid #f3f4f6',
  },
  tocEntry: {
    fontSize: '10px',
    color: '#4b5563',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'baseline',
    paddingBottom: '4px',
    marginBottom: '4px',
    borderBottom: '1px dotted #d1d5db',
  },
  tocItem: {
    flex: 1,
  },
  tocPage: {
    fontWeight: 700,
    color: '#1f2937',
  },

  previewStats: {
    display: 'grid',
    gridTemplateColumns: 'repeat(4, 1fr)',
    gap: '10px',
  },
  statChip: {
    fontSize: '11px',
    fontWeight: 600,
    color: 'var(--color-text-primary)',
    backgroundColor: 'var(--color-bg-elevated)',
    padding: '8px 12px',
    borderRadius: '999px',
    border: '1px solid var(--color-border)',
    textAlign: 'center',
  },

  historyCard: {
    backgroundColor: 'var(--color-bg-card)',
    border: '1px solid var(--color-border)',
    borderRadius: '12px',
    padding: '20px',
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
  },
  historyHeader: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: '16px',
  },
  historyTitle: {
    fontSize: '13px',
    fontWeight: 700,
    color: 'var(--color-text-secondary)',
    textTransform: 'uppercase',
    letterSpacing: '0.08em',
    margin: 0,
  },
  seeAllButton: {
    fontSize: '12px',
    fontWeight: 600,
    color: 'var(--color-primary)',
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    textDecoration: 'underline',
  },

  emptyState: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '12px',
  },
  emptyIcon: {
    fontSize: '48px',
    opacity: 0.3,
  },
  emptyTitle: {
    fontSize: '20px',
    fontWeight: 700,
    color: 'var(--color-text-primary)',
    margin: 0,
  },
  emptyDesc: {
    fontSize: '14px',
    color: 'var(--color-text-muted)',
    textAlign: 'center',
    margin: '0 0 12px 0',
    maxWidth: '240px',
  },
  emptyButton: {
    padding: '10px 16px',
    backgroundColor: 'var(--color-primary)',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '13px',
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'opacity 0.2s ease',
  },

  historyList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  historyItem: {
    padding: '12px 14px',
    borderRadius: '8px',
    backgroundColor: 'var(--color-bg-elevated)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    transition: 'background-color 0.2s ease',
  },
  historyItemLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    flex: 1,
  },
  historyIcon: {
    width: '36px',
    height: '36px',
    borderRadius: '6px',
    backgroundColor: '#ef4444',
    opacity: 0.15,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
  },
  historyInfo: {
    flex: 1,
  },
  historyName: {
    fontSize: '13px',
    fontWeight: 600,
    color: 'var(--color-text-primary)',
    margin: 0,
  },
  historyMeta: {
    fontSize: '11px',
    color: 'var(--color-text-muted)',
    margin: '2px 0 0 0',
  },

  downloadButton: {
    width: '32px',
    height: '32px',
    borderRadius: '6px',
    backgroundColor: 'var(--color-bg-elevated)',
    border: 'none',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'var(--color-text-secondary)',
    transition: 'all 0.2s ease',
  },

  /* MODAL */
  modalOverlay: {
    position: 'fixed',
    inset: 0,
    backgroundColor: 'rgba(0,0,0,0.6)',
    backdropFilter: 'blur(8px)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  },
  modalCard: {
    backgroundColor: 'var(--color-bg-card)',
    border: '1px solid var(--color-border)',
    borderRadius: '16px',
    width: '480px',
    maxWidth: '90vw',
    padding: '40px',
    position: 'relative',
    boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
  },
  modalGlowTop: {
    position: 'absolute',
    top: '-40px',
    right: '-40px',
    width: '160px',
    height: '160px',
    backgroundColor: 'var(--color-primary)',
    borderRadius: '50%',
    filter: 'blur(60px)',
    opacity: 0.08,
  },
  modalGlowBottom: {
    position: 'absolute',
    bottom: '-40px',
    left: '-40px',
    width: '160px',
    height: '160px',
    backgroundColor: 'var(--color-warning)',
    borderRadius: '50%',
    filter: 'blur(60px)',
    opacity: 0.08,
  },

  modalContent: {
    position: 'relative',
    zIndex: 1,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    textAlign: 'center',
  },

  progressCircleContainer: {
    position: 'relative',
    width: '128px',
    height: '128px',
    marginBottom: '24px',
  },
  progressSvg: {
    width: '100%',
    height: '100%',
  },
  progressText: {
    position: 'absolute',
    inset: 0,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  progressPercent: {
    fontSize: '28px',
    fontWeight: 700,
    color: 'var(--color-text-primary)',
  },

  modalTitle: {
    fontSize: '20px',
    fontWeight: 700,
    color: 'var(--color-text-primary)',
    margin: '0 0 8px 0',
  },
  modalSubtitle: {
    fontSize: '14px',
    color: 'var(--color-text-muted)',
    margin: '0 0 20px 0',
  },

  stepsList: {
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    marginBottom: '20px',
  },
  stepsItem: {
    padding: '10px 14px',
    borderRadius: '8px',
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    backgroundColor: 'transparent',
    border: 'none',
  },
  stepsItemDone: {
    backgroundColor: 'var(--color-success)',
    opacity: 0.08,
    borderColor: 'var(--color-success)',
    borderWidth: '1px',
  },
  stepsItemCurrent: {
    backgroundColor: 'var(--color-primary)',
    opacity: 0.08,
    borderColor: 'var(--color-primary)',
    borderWidth: '1px',
  },
  stepsIcon: {
    width: '24px',
    height: '24px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
  },
  stepsPending: {
    fontSize: '12px',
    fontWeight: 600,
    color: 'var(--color-text-muted)',
  },
  stepsLabel: {
    fontSize: '12px',
    fontWeight: 500,
    color: 'var(--color-text-primary)',
  },

  progressBar: {
    width: '100%',
    height: '8px',
    backgroundColor: 'var(--color-border)',
    borderRadius: '4px',
    overflow: 'hidden',
    marginBottom: '12px',
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: 'var(--color-primary)',
    transition: 'width 0.5s ease',
    borderRadius: '4px',
  },

  statusText: {
    fontSize: '12px',
    color: 'var(--color-text-muted)',
    margin: '0 0 20px 0',
  },

  errorBox: {
    width: '100%',
    padding: '12px 14px',
    backgroundColor: '#ef4444',
    opacity: 0.1,
    border: '1px solid #ef4444',
    borderRadius: '6px',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '12px',
    color: '#ef4444',
    marginBottom: '20px',
  },

  modalButtons: {
    display: 'flex',
    gap: '12px',
    width: '100%',
  },
  buttonPrimary: {
    flex: 1,
    padding: '12px 16px',
    backgroundColor: 'var(--color-primary)',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '13px',
    fontWeight: 600,
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    transition: 'opacity 0.2s ease',
  },
  buttonOutlined: {
    flex: 1,
    padding: '12px 16px',
    backgroundColor: 'transparent',
    color: 'var(--color-text-secondary)',
    border: '1px solid var(--color-border)',
    borderRadius: '6px',
    fontSize: '13px',
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'all 0.2s ease',
  },
};
