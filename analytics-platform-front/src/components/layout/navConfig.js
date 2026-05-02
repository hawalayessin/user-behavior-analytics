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
} from 'lucide-react'

import { Squares2X2Icon } from "@heroicons/react/24/outline"

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
    ],
  },
  {
    section: 'AI INSIGHTS',
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
    section: 'MANAGEMENT',
    items: [
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
    section: 'ADMIN',
    adminOnly: true,
    items: [
      {
        label: 'Import Data',
        icon: Upload,
        route: '/admin/import',
      },
      {
        label: 'Management',
        icon: Squares2X2Icon,
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
