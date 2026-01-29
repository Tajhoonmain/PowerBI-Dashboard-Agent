import { useDashboard } from '@/contexts/DashboardContext';
import { Widget } from '@/types/dashboard';
import { BarChartWidget } from './widgets/BarChartWidget';
import { LineChartWidget } from './widgets/LineChartWidget';
import { KPIWidget } from './widgets/KPIWidget';
import { cn } from '@/lib/utils';
import { Sparkles } from 'lucide-react';

export function DashboardCanvas() {
  const { state, selectWidget } = useDashboard();

  if (state.widgets.length === 0) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center space-y-4 max-w-md">
          <div className="inline-block p-6 rounded-2xl bg-gradient-to-br from-[#00d9ff]/10 to-[#ff006e]/10 border border-white/10">
            <Sparkles className="w-16 h-16 text-[#00d9ff]" />
          </div>
          <h3 className="text-2xl font-bold text-white">Your Canvas Awaits</h3>
          <p className="text-white/60">
            Use the AI console above to generate visualizations from your data, or click widgets to customize them manually.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="grid grid-cols-12 gap-6 auto-rows-[200px]">
        {state.widgets.map((widget, index) => (
          <WidgetContainer
            key={widget.id}
            widget={widget}
            isSelected={state.selectedWidget === widget.id}
            onSelect={() => selectWidget(widget.id)}
            index={index}
          />
        ))}
      </div>
    </div>
  );
}

interface WidgetContainerProps {
  widget: Widget;
  isSelected: boolean;
  onSelect: () => void;
  index: number;
}

function WidgetContainer({ widget, isSelected, onSelect, index }: WidgetContainerProps) {
  const style = {
    gridColumn: `span ${widget.position.w}`,
    gridRow: `span ${widget.position.h}`,
    animationDelay: `${index * 100}ms`,
    animationFillMode: 'backwards',
  };

  return (
    <div
      style={style}
      onClick={onSelect}
      className={cn(
        'group relative rounded-xl glass border transition-all duration-300 cursor-pointer overflow-hidden',
        'animate-in fade-in zoom-in-95',
        isSelected
          ? 'border-[#00d9ff] glow-cyan scale-[1.02] z-10'
          : 'border-white/10 hover:border-[#00d9ff]/50 hover:-translate-y-1 hover:glow-cyan'
      )}
    >
      {/* Widget Title */}
      <div className="absolute top-0 left-0 right-0 p-4 bg-gradient-to-b from-black/40 to-transparent z-10">
        <h3 className="text-sm font-bold text-white/90 truncate">{widget.title}</h3>
      </div>

      {/* Widget Content */}
      <div className="w-full h-full p-4 pt-14">
        {widget.type === 'bar' && <BarChartWidget widget={widget} />}
        {widget.type === 'line' && <LineChartWidget widget={widget} />}
        {widget.type === 'kpi' && <KPIWidget widget={widget} />}
      </div>

      {/* Selection Indicator */}
      {isSelected && (
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-[#00d9ff]" />
          <div className="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-[#00d9ff]" />
          <div className="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-[#00d9ff]" />
          <div className="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-[#00d9ff]" />
        </div>
      )}
    </div>
  );
}
