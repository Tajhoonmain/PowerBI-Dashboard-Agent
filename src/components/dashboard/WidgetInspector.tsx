import { X, Palette, BarChart3, Settings2, Trash2 } from 'lucide-react';
import { useDashboard } from '@/contexts/DashboardContext';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { cn } from '@/lib/utils';

export function WidgetInspector() {
  const { state, selectWidget, updateWidget, removeWidget } = useDashboard();
  
  const selectedWidget = state.widgets.find(w => w.id === state.selectedWidget);
  const dataset = selectedWidget ? state.datasets.find(d => d.id === selectedWidget.datasetId) : null;

  if (!selectedWidget || !dataset) return null;

  const handleClose = () => selectWidget(null);

  const handleUpdate = (updates: any) => {
    updateWidget(selectedWidget.id, updates);
  };

  const handleDelete = () => {
    removeWidget(selectedWidget.id);
    selectWidget(null);
  };

  const chartTypes = [
    { value: 'bar', label: 'Bar Chart', icon: BarChart3 },
    { value: 'line', label: 'Line Chart', icon: BarChart3 },
    { value: 'kpi', label: 'KPI Card', icon: BarChart3 },
  ];

  const colorPresets = [
    { name: 'Cyan', gradient: ['#00d9ff', '#00a8cc'] },
    { name: 'Magenta', gradient: ['#ff006e', '#cc0058'] },
    { name: 'Purple', gradient: ['#a855f7', '#ec4899'] },
    { name: 'Green', gradient: ['#10b981', '#059669'] },
    { name: 'Yellow', gradient: ['#fbbf24', '#f59e0b'] },
  ];

  return (
    <div 
      className={cn(
        'fixed right-0 top-0 h-full w-96 glass border-l border-white/10',
        'animate-in slide-in-from-right duration-300 z-50',
        'overflow-y-auto'
      )}
    >
      {/* Header */}
      <div className="sticky top-0 bg-[#0a0e14]/90 backdrop-blur-xl p-6 border-b border-white/10 z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-[#00d9ff]/10 border border-[#00d9ff]/20">
              <Settings2 className="w-5 h-5 text-[#00d9ff]" />
            </div>
            <h2 className="text-lg font-bold text-white">Widget Inspector</h2>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={handleClose}
            className="hover:bg-white/10 rounded-lg"
          >
            <X className="w-5 h-5" />
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="p-6 space-y-8">
        {/* Basic Info */}
        <section className="space-y-4">
          <h3 className="text-xs font-bold text-white/60 uppercase tracking-wider">
            Basic Information
          </h3>
          <div className="space-y-3">
            <div className="space-y-2">
              <Label htmlFor="title" className="text-white/80">Title</Label>
              <Input
                id="title"
                value={selectedWidget.title}
                onChange={(e) => handleUpdate({ title: e.target.value })}
                className="bg-black/30 border-white/10 text-white"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="chart-type" className="text-white/80">Chart Type</Label>
              <Select
                value={selectedWidget.type}
                onValueChange={(value) => handleUpdate({ type: value })}
              >
                <SelectTrigger className="bg-black/30 border-white/10 text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {chartTypes.map((type) => (
                    <SelectItem key={type.value} value={type.value}>
                      {type.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </section>

        {/* Data Configuration */}
        {selectedWidget.type !== 'kpi' && (
          <section className="space-y-4">
            <h3 className="text-xs font-bold text-white/60 uppercase tracking-wider">
              Data Configuration
            </h3>
            <div className="space-y-3">
              <div className="space-y-2">
                <Label htmlFor="x-axis" className="text-white/80">X-Axis</Label>
                <Select
                  value={selectedWidget.config.xAxis}
                  onValueChange={(value) => 
                    handleUpdate({ config: { ...selectedWidget.config, xAxis: value } })
                  }
                >
                  <SelectTrigger className="bg-black/30 border-white/10 text-white">
                    <SelectValue placeholder="Select column" />
                  </SelectTrigger>
                  <SelectContent>
                    {dataset.columns.map((col) => (
                      <SelectItem key={col.name} value={col.name}>
                        {col.name} ({col.type})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="y-axis" className="text-white/80">Y-Axis</Label>
                <Select
                  value={selectedWidget.config.yAxis}
                  onValueChange={(value) => 
                    handleUpdate({ config: { ...selectedWidget.config, yAxis: value } })
                  }
                >
                  <SelectTrigger className="bg-black/30 border-white/10 text-white">
                    <SelectValue placeholder="Select column" />
                  </SelectTrigger>
                  <SelectContent>
                    {dataset.columns.filter(c => c.type === 'number').map((col) => (
                      <SelectItem key={col.name} value={col.name}>
                        {col.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="aggregation" className="text-white/80">Aggregation</Label>
                <Select
                  value={selectedWidget.config.aggregation || 'sum'}
                  onValueChange={(value) => 
                    handleUpdate({ config: { ...selectedWidget.config, aggregation: value } })
                  }
                >
                  <SelectTrigger className="bg-black/30 border-white/10 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="sum">Sum</SelectItem>
                    <SelectItem value="avg">Average</SelectItem>
                    <SelectItem value="count">Count</SelectItem>
                    <SelectItem value="min">Minimum</SelectItem>
                    <SelectItem value="max">Maximum</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </section>
        )}

        {selectedWidget.type === 'kpi' && (
          <section className="space-y-4">
            <h3 className="text-xs font-bold text-white/60 uppercase tracking-wider">
              KPI Configuration
            </h3>
            <div className="space-y-3">
              <div className="space-y-2">
                <Label htmlFor="metric" className="text-white/80">Metric Column</Label>
                <Select
                  value={selectedWidget.config.yAxis}
                  onValueChange={(value) => 
                    handleUpdate({ config: { ...selectedWidget.config, yAxis: value } })
                  }
                >
                  <SelectTrigger className="bg-black/30 border-white/10 text-white">
                    <SelectValue placeholder="Select column" />
                  </SelectTrigger>
                  <SelectContent>
                    {dataset.columns.filter(c => c.type === 'number').map((col) => (
                      <SelectItem key={col.name} value={col.name}>
                        {col.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="kpi-aggregation" className="text-white/80">Calculation</Label>
                <Select
                  value={selectedWidget.config.aggregation || 'sum'}
                  onValueChange={(value) => 
                    handleUpdate({ config: { ...selectedWidget.config, aggregation: value } })
                  }
                >
                  <SelectTrigger className="bg-black/30 border-white/10 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="sum">Sum</SelectItem>
                    <SelectItem value="avg">Average</SelectItem>
                    <SelectItem value="count">Count</SelectItem>
                    <SelectItem value="min">Minimum</SelectItem>
                    <SelectItem value="max">Maximum</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </section>
        )}

        {/* Style Presets */}
        <section className="space-y-4">
          <h3 className="text-xs font-bold text-white/60 uppercase tracking-wider flex items-center gap-2">
            <Palette className="w-4 h-4" />
            Color Presets
          </h3>
          <div className="grid grid-cols-2 gap-3">
            {colorPresets.map((preset) => (
              <button
                key={preset.name}
                onClick={() => 
                  handleUpdate({ config: { ...selectedWidget.config, gradient: preset.gradient } })
                }
                className={cn(
                  'p-4 rounded-lg border-2 transition-all duration-300 hover:scale-105',
                  JSON.stringify(selectedWidget.config.gradient) === JSON.stringify(preset.gradient)
                    ? 'border-white/40 glow-cyan'
                    : 'border-white/10 hover:border-white/20'
                )}
                style={{
                  background: `linear-gradient(135deg, ${preset.gradient[0]}, ${preset.gradient[1]})`,
                }}
              >
                <span className="text-white text-sm font-bold drop-shadow-lg">
                  {preset.name}
                </span>
              </button>
            ))}
          </div>
        </section>

        {/* Danger Zone */}
        <section className="space-y-4 pt-4 border-t border-red-500/20">
          <h3 className="text-xs font-bold text-red-400 uppercase tracking-wider">
            Danger Zone
          </h3>
          <Button
            variant="destructive"
            onClick={handleDelete}
            className="w-full bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-red-400"
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Delete Widget
          </Button>
        </section>
      </div>
    </div>
  );
}
