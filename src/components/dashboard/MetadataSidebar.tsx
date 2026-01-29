import { useState } from 'react';
import { Database, ChevronRight, ChevronLeft, Calendar, Hash, FileText } from 'lucide-react';
import { useDashboard } from '@/contexts/DashboardContext';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export function MetadataSidebar() {
  const { state, showMetadata } = useDashboard();
  const [isCollapsed, setIsCollapsed] = useState(false);

  if (state.datasets.length === 0 || !showMetadata) return null;

  return (
    <div
      className={cn(
        'fixed left-0 top-[40vh] bottom-0 glass border-r border-white/10 transition-all duration-300 z-30 overflow-y-auto',
        isCollapsed ? 'w-12' : 'w-80'
      )}
    >
      {/* Toggle Button */}
      <Button
        variant="ghost"
        size="icon"
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="absolute -right-3 top-6 w-6 h-6 rounded-full bg-[#0a0e14] border border-white/10 hover:bg-[#00d9ff]/20 z-10"
      >
        {isCollapsed ? (
          <ChevronRight className="w-4 h-4 text-[#00d9ff]" />
        ) : (
          <ChevronLeft className="w-4 h-4 text-[#00d9ff]" />
        )}
      </Button>

      {!isCollapsed && (
        <div className="p-6 space-y-6">
          {/* Header */}
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-[#00d9ff]/10 border border-[#00d9ff]/20">
              <Database className="w-5 h-5 text-[#00d9ff]" />
            </div>
            <h2 className="text-lg font-bold text-white">Metadata</h2>
          </div>

          {/* Datasets */}
          <section className="space-y-4">
            <h3 className="text-xs font-bold text-white/60 uppercase tracking-wider">
              Active Datasets
            </h3>
            {state.datasets.map((dataset) => (
              <div
                key={dataset.id}
                className="p-4 rounded-lg bg-black/20 border border-white/10 space-y-3"
              >
                <div className="flex items-start gap-3">
                  <FileText className="w-5 h-5 text-[#00d9ff] flex-shrink-0 mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <h4 className="font-bold text-white text-sm truncate">{dataset.name}</h4>
                    <p className="text-xs text-white/40 font-mono mt-1">
                      ID: {dataset.id}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="flex items-center gap-2 text-xs">
                    <Hash className="w-3 h-3 text-white/40" />
                    <span className="text-white/60">
                      {dataset.rowCount.toLocaleString()} rows
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-xs">
                    <Hash className="w-3 h-3 text-white/40" />
                    <span className="text-white/60">
                      {dataset.columns.length} cols
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-2 text-xs text-white/40">
                  <Calendar className="w-3 h-3" />
                  <span className="font-mono">
                    {dataset.uploadedAt.toLocaleString()}
                  </span>
                </div>

                <div className="pt-3 border-t border-white/10">
                  <div className="text-xs text-white/40 mb-2">Schema Preview:</div>
                  <div className="space-y-1 max-h-32 overflow-y-auto">
                    {dataset.columns.slice(0, 5).map((col, idx) => (
                      <div key={idx} className="flex items-center justify-between text-xs">
                        <span className="text-white/70 font-mono truncate flex-1">
                          {col.name}
                        </span>
                        <span className="text-[#00d9ff] uppercase ml-2 flex-shrink-0">
                          {col.type}
                        </span>
                      </div>
                    ))}
                    {dataset.columns.length > 5 && (
                      <div className="text-xs text-white/30 text-center pt-1">
                        +{dataset.columns.length - 5} more
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </section>

          {/* Active Widgets */}
          <section className="space-y-4">
            <h3 className="text-xs font-bold text-white/60 uppercase tracking-wider">
              Dashboard Stats
            </h3>
            <div className="p-4 rounded-lg bg-black/20 border border-white/10 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-white/60">Active Widgets</span>
                <span className="text-lg font-bold text-[#00d9ff] font-mono">
                  {state.widgets.length}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-white/60">History States</span>
                <span className="text-lg font-bold text-[#ff006e] font-mono">
                  {state.history.length}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-white/60">AI Messages</span>
                <span className="text-lg font-bold text-green-400 font-mono">
                  {state.aiMessages.length}
                </span>
              </div>
            </div>
          </section>

          {/* System Status */}
          <section className="space-y-4">
            <h3 className="text-xs font-bold text-white/60 uppercase tracking-wider">
              System Status
            </h3>
            <div className="space-y-2">
              <StatusIndicator label="Local Storage" status="operational" />
              <StatusIndicator label="AI Engine" status="operational" />
              <StatusIndicator label="Data Parser" status="operational" />
            </div>
          </section>
        </div>
      )}
    </div>
  );
}

function StatusIndicator({ label, status }: { label: string; status: 'operational' | 'warning' | 'error' }) {
  const colors = {
    operational: 'bg-green-400',
    warning: 'bg-yellow-400',
    error: 'bg-red-400',
  };

  return (
    <div className="flex items-center justify-between text-xs">
      <span className="text-white/60">{label}</span>
      <div className="flex items-center gap-2">
        <div className={cn('w-2 h-2 rounded-full', colors[status])} />
        <span className="text-white/40 uppercase font-mono">{status}</span>
      </div>
    </div>
  );
}
