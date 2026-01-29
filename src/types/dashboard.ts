export interface Dataset {
  id: string;
  name: string;
  data: any[];
  columns: ColumnSchema[];
  rowCount: number;
  uploadedAt: Date;
}

export interface ColumnSchema {
  name: string;
  type: 'string' | 'number' | 'date' | 'boolean';
  confidence: number;
}

export interface Widget {
  id: string;
  type: 'bar' | 'line' | 'pie' | 'kpi' | 'table';
  title: string;
  datasetId: string;
  config: WidgetConfig;
  position: { x: number; y: number; w: number; h: number };
}

export interface WidgetConfig {
  xAxis?: string;
  yAxis?: string;
  color?: string;
  gradient?: [string, string];
  aggregation?: 'sum' | 'avg' | 'count' | 'min' | 'max';
  filters?: any[];
}

export interface AIMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  json?: any;
}

export interface DashboardState {
  datasets: Dataset[];
  widgets: Widget[];
  selectedWidget: string | null;
  aiMessages: AIMessage[];
  history: DashboardSnapshot[];
  currentHistoryIndex: number;
}

export interface DashboardSnapshot {
  id: string;
  timestamp: Date;
  widgets: Widget[];
  label: string;
}
