import {
  LayoutDashboard,
  Activity,
  FlaskConical,
  TrendingUp,
  UserMinus,
  GitBranch,
  BrainCircuit,
  PieChart,
  Layers,
  Megaphone,
  Users,
  NotebookPen,
  Upload,
  UserCog,
  Settings,
  AlertTriangle,
  Grid2x2,
  FileText,
} from 'lucide-react'

export const navigationConfig = [
  {
    section: 'ANALYTICS',
    items: [
      {
        label: 'overview',
        icon: LayoutDashboard,
        route: '/dashboard',
      },
      {
        label: ' User Activity ',
        icon: Activity,
        route: '/analytics/behaviors',
      },

      {
        label: ' Free Trial Behavior',
        icon: FlaskConical,
        route: '/analytics/trial',
      },
      {
        label: 'Campaign Impact',
        icon: Megaphone,
        route: '/analytics/campaigns',
      },
      {
        label: 'Retention',
        icon: TrendingUp,
        route: '/analytics/retention',
      },

      {
        label: 'Churn Analysis',
        icon: UserMinus,
        route: '/analytics/churn',
      },
      {
        label: 'Cross-Service',
        icon: GitBranch,
        route: '/analytics/cross-service',
      },
      {
        label: 'Subscribers',
        icon: Users,
        route: '/management/subscribers',
      },
      {
        label: 'Analyst Notes',
        icon: NotebookPen,
        route: '/notes',
      },
    ],
  },
  {
    section: 'AI INSIGHTS',
    collapsible: true,
    items: [
      {
        label: 'Anomaly Detection',
        icon: AlertTriangle,
        route: '/analytics/anomalies',
      },
      {
        label: 'Churn Prediction',
        icon: BrainCircuit,
        route: '/analytics/churn-prediction',
      },
      {
        label: 'User Segmentation',
        icon: Users,
        route: '/analytics/segmentation',
      },
    ],
  },
  
  {
    section: 'ADMIN',
    adminOnly: true,
    items: [
      {
        label: 'Report Generator',
        icon: FileText,
        route: '/admin/reports',
      },
      {
        label: 'Run AI Models',
        icon: BrainCircuit,
        route: '/admin/run-ai-models',
      },
      {
        label: 'Import Data',
        icon: Upload,
        route: '/admin/import',
      },
      {
        label: 'services and campaigns',
        icon: Grid2x2,
        route: '/admin/management',
      },
      {
        label: 'Platform Users',
        icon: UserCog,
        route: '/admin/users',
      },
      {
        label: 'System Settings',
        icon: Settings,
        route: '/admin/settings',
      },

    ],
  },
]
