import { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Widget } from '@/types/dashboard';
import { useDashboard } from '@/contexts/DashboardContext';

interface BarChartWidgetProps {
  widget: Widget;
}

export function BarChartWidget({ widget }: BarChartWidgetProps) {
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

  const gradient = widget.config.gradient || ['#00d9ff', '#00a8cc'];

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={chartData}>
        <defs>
          <linearGradient id={`gradient-${widget.id}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={gradient[0]} stopOpacity={0.8} />
            <stop offset="100%" stopColor={gradient[1]} stopOpacity={0.4} />
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
            border: '1px solid rgba(0, 217, 255, 0.3)',
            borderRadius: '8px',
            color: '#fff',
            fontSize: '12px',
          }}
          cursor={{ fill: 'rgba(0, 217, 255, 0.1)' }}
        />
        <Bar 
          dataKey="value" 
          fill={`url(#gradient-${widget.id})`}
          radius={[8, 8, 0, 0]}
        >
          {chartData.map((entry, index) => (
            <Cell 
              key={`cell-${index}`}
              style={{
                filter: 'drop-shadow(0 0 8px rgba(0, 217, 255, 0.4))',
              }}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
