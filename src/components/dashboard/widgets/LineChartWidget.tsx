import { useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Widget } from '@/types/dashboard';
import { useDashboard } from '@/contexts/DashboardContext';

interface LineChartWidgetProps {
  widget: Widget;
}

export function LineChartWidget({ widget }: LineChartWidgetProps) {
  const { state } = useDashboard();
  
  const dataset = state.datasets.find(d => d.id === widget.datasetId);
  
  const chartData = useMemo(() => {
    if (!dataset || !widget.config.xAxis || !widget.config.yAxis) return [];
    
    const grouped = dataset.data.reduce((acc: any, row: any) => {
      const key = row[widget.config.xAxis!];
      const value = parseFloat(row[widget.config.yAxis!]) || 0;
      
      if (!acc[key]) {
        acc[key] = { name: key, value: 0, count: 0 };
      }
      
      acc[key].value += value;
      acc[key].count += 1;
      
      return acc;
    }, {});
    
    return Object.values(grouped).map((item: any) => ({
      name: item.name,
      value: widget.config.aggregation === 'avg' ? item.value / item.count : item.value,
    }));
  }, [dataset, widget.config]);

  if (!dataset) {
    return (
      <div className="w-full h-full flex items-center justify-center text-white/40 text-sm">
        Dataset not found
      </div>
    );
  }

  const gradient = widget.config.gradient || ['#a855f7', '#ec4899'];
  const strokeColor = gradient[0];

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={chartData}>
        <defs>
          <linearGradient id={`line-gradient-${widget.id}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={strokeColor} stopOpacity={0.3} />
            <stop offset="100%" stopColor={strokeColor} stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
        <XAxis 
          dataKey="name" 
          stroke="rgba(255,255,255,0.4)"
          tick={{ fill: 'rgba(255,255,255,0.6)', fontSize: 12 }}
          tickLine={{ stroke: 'rgba(255,255,255,0.2)' }}
        />
        <YAxis 
          stroke="rgba(255,255,255,0.4)"
          tick={{ fill: 'rgba(255,255,255,0.6)', fontSize: 12 }}
          tickLine={{ stroke: 'rgba(255,255,255,0.2)' }}
        />
        <Tooltip 
          contentStyle={{
            backgroundColor: 'rgba(26, 31, 46, 0.95)',
            border: `1px solid ${strokeColor}`,
            borderRadius: '8px',
            color: '#fff',
            fontSize: '12px',
          }}
          cursor={{ stroke: strokeColor, strokeWidth: 2, strokeDasharray: '5 5' }}
        />
        <Line 
          type="monotone"
          dataKey="value" 
          stroke={strokeColor}
          strokeWidth={3}
          dot={{ 
            fill: strokeColor, 
            strokeWidth: 2, 
            r: 5,
            filter: `drop-shadow(0 0 8px ${strokeColor})`,
          }}
          activeDot={{ 
            r: 8,
            fill: strokeColor,
            filter: `drop-shadow(0 0 12px ${strokeColor})`,
          }}
          fill={`url(#line-gradient-${widget.id})`}
          style={{
            filter: `drop-shadow(0 0 8px ${strokeColor})`,
          }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
