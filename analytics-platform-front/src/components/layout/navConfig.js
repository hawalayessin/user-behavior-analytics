import {
  LayoutDashboard,
  Activity,
  FlaskConical,
  TrendingUp,
  UserMinus,
  DollarSign,
  BrainCircuit,
  PieChart,
  Layers,
  Megaphone,
  Users,
  Upload,
  UserCog,
  Settings,
} from 'lucide-react'

export const navigationConfig = [
  {
    section: 'ANALYTICS',
    items: [
      {
        label: 'Dashboard',
        icon: LayoutDashboard,
        route: '/dashboard',
      },
      {
        label: 'Behaviors',
        icon: Activity,
        route: '/analytics/behaviors',
      },
      {
        label: 'Trial Analysis',
        icon: FlaskConical,
        route: '/analytics/trial',
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
        label: 'Revenue',
        icon: DollarSign,
        route: '/analytics/revenue',
      },
    ],
  },
  {
    section: 'AI INSIGHTS',
    items: [
      {
        label: 'Churn Prediction',
        icon: BrainCircuit,
        route: '/analytics/churn-prediction',
      },
      {
        label: 'Segmentation',
        icon: PieChart,
        route: '/analytics/segmentation',
      },
    ],
  },
  {
    section: 'MANAGEMENT',
    items: [
      {
        label: 'Services',
        icon: Layers,
        route: '/management/services',
      },
      {
        label: 'Campaigns',
        icon: Megaphone,
        route: '/management/campaigns',
      },
      {
        label: 'Subscribers',
        icon: Users,
        route: '/management/subscribers',
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
