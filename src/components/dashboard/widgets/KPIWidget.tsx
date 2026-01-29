import { useMemo } from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { Widget } from '@/types/dashboard';
import { useDashboard } from '@/contexts/DashboardContext';

interface KPIWidgetProps {
  widget: Widget;
}

export function KPIWidget({ widget }: KPIWidgetProps) {
  const { state } = useDashboard();
  
  const dataset = state.datasets.find(d => d.id === widget.datasetId);
  
  const kpiValue = useMemo(() => {
    if (!dataset || !widget.config.yAxis) return { value: 0, trend: 0 };
    
    const values = dataset.data
      .map(row => parseFloat(row[widget.config.yAxis!]) || 0)
      .filter(v => !isNaN(v));
    
    if (values.length === 0) return { value: 0, trend: 0 };
    
    let value = 0;
    
    switch (widget.config.aggregation) {
      case 'sum':
        value = values.reduce((sum, v) => sum + v, 0);
        break;
      case 'avg':
        value = values.reduce((sum, v) => sum + v, 0) / values.length;
        break;
      case 'count':
        value = values.length;
        break;
      case 'min':
        value = Math.min(...values);
        break;
      case 'max':
        value = Math.max(...values);
        break;
      default:
        value = values.reduce((sum, v) => sum + v, 0);
    }
    
    // Simple trend calculation (comparing first half vs second half)
    const midpoint = Math.floor(values.length / 2);
    const firstHalf = values.slice(0, midpoint);
    const secondHalf = values.slice(midpoint);
    
    const firstAvg = firstHalf.reduce((sum, v) => sum + v, 0) / firstHalf.length;
    const secondAvg = secondHalf.reduce((sum, v) => sum + v, 0) / secondHalf.length;
    
    const trend = firstAvg !== 0 ? ((secondAvg - firstAvg) / firstAvg) * 100 : 0;
    
    return { value, trend };
  }, [dataset, widget.config]);

  if (!dataset) {
    return (
      <div className="w-full h-full flex items-center justify-center text-white/40 text-sm">
        Dataset not found
      </div>
    );
  }

  const gradient = widget.config.gradient || ['#10b981', '#059669'];
  const isPositive = kpiValue.trend > 0;
  const isNegative = kpiValue.trend < 0;
  const isNeutral = kpiValue.trend === 0;

  const formatValue = (value: number) => {
    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(2)}M`;
    } else if (value >= 1000) {
      return `${(value / 1000).toFixed(2)}K`;
    }
    return value.toFixed(2);
  };

  return (
    <div className="w-full h-full flex flex-col justify-center items-center space-y-4 p-6">
      <div 
        className="text-6xl font-bold font-mono tracking-tight"
        style={{
          background: `linear-gradient(135deg, ${gradient[0]}, ${gradient[1]})`,
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          filter: `drop-shadow(0 0 20px ${gradient[0]}80)`,
        }}
      >
        {formatValue(kpiValue.value)}
      </div>
      
      <div className="flex items-center gap-2">
        {isPositive && (
          <>
            <TrendingUp className="w-5 h-5 text-green-400" />
            <span className="text-lg font-bold text-green-400 font-mono">
              +{Math.abs(kpiValue.trend).toFixed(1)}%
            </span>
          </>
        )}
        {isNegative && (
          <>
            <TrendingDown className="w-5 h-5 text-red-400" />
            <span className="text-lg font-bold text-red-400 font-mono">
              {kpiValue.trend.toFixed(1)}%
            </span>
          </>
        )}
        {isNeutral && (
          <>
            <Minus className="w-5 h-5 text-white/40" />
            <span className="text-lg font-bold text-white/40 font-mono">
              0.0%
            </span>
          </>
        )}
      </div>
      
      <div className="text-sm text-white/40 uppercase tracking-wider font-mono">
        {widget.config.aggregation || 'Total'}
      </div>
    </div>
  );
}
