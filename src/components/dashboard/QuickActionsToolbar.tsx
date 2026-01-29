import { Undo2, Redo2, Download, Camera, Database, FileSpreadsheet, BarChart3 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useDashboard } from '@/contexts/DashboardContext';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import { cn } from '@/lib/utils';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export function QuickActionsToolbar() {
  const { state, undo, redo, createSnapshot, showMetadata, toggleMetadata } = useDashboard();
  const navigate = useNavigate();

  const canUndo = state.currentHistoryIndex > 0;
  const canRedo = state.currentHistoryIndex < state.history.length - 1;

  const handleExportPowerBI = async () => {
    try {
      const exportData = {
        widgets: state.widgets,
        datasets: state.datasets.map(d => ({
          id: d.id,
          name: d.name,
          columns: d.columns,
          rowCount: d.rowCount,
        })),
      };

      // First try Power BI API (if enabled)
      try {
        const apiResponse = await fetch(`${API_BASE}/api/v1/export/powerbi/api`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(exportData),
        });

        if (apiResponse.ok) {
          const result = await apiResponse.json();
          toast.success(`Dashboard imported to Power BI Service! Import ID: ${result.import_id}`);
          return;
        }
      } catch (apiError) {
        // If API not enabled or fails, fall back to .pbix download
        console.log('Power BI API not available, falling back to .pbix export');
      }

      // Fallback: Download .pbix file
      const response = await fetch(`${API_BASE}/api/v1/export/powerbi`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(exportData),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || 'Failed to export Power BI file');
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `dashboard-${Date.now()}.pbix`;
      a.click();
      URL.revokeObjectURL(url);

      toast.success('Dashboard exported as Power BI file (.pbix). Note: For direct import, configure Power BI API in .env');
    } catch (error) {
      console.error('Export error:', error);
      toast.error(`Failed to export Power BI file: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const handleSnapshot = () => {
    createSnapshot(`Manual snapshot - ${new Date().toLocaleTimeString()}`);
    toast.success('Snapshot created');
  };

  const handleExportCSV = async () => {
    try {
      const exportData = {
        widgets: state.widgets,
        datasets: state.datasets.map(d => ({
          id: d.id,
          name: d.name,
          columns: d.columns,
          rowCount: d.rowCount,
        })),
      };

      const response = await fetch(`${API_BASE}/api/v1/export/csv`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(exportData),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || 'Failed to export CSV file');
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `data-${Date.now()}.csv`;
      a.click();
      URL.revokeObjectURL(url);

      toast.success('CSV exported! Import this into Power BI Desktop along with the JSON definition.');
    } catch (error) {
      console.error('CSV export error:', error);
      toast.error(`Failed to export CSV: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  return (
    <div className="fixed bottom-8 left-1/2 -translate-x-1/2 z-40">
      <div className="flex items-center gap-2 px-4 py-3 glass rounded-2xl border border-white/10 glow-cyan">
        {/* Evaluation Metrics Button - Always visible */}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => navigate('/evaluation')}
          className={cn(
            'rounded-lg transition-all duration-300',
            'hover:bg-purple-500/20 hover:scale-110'
          )}
          title="View Agent Evaluation Metrics"
        >
          <BarChart3 className="w-5 h-5 text-purple-400" />
        </Button>

        {/* Metadata Button - Always visible when datasets exist */}
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleMetadata}
          className={cn(
            'rounded-lg transition-all duration-300',
            showMetadata
              ? 'bg-[#00d9ff]/20 hover:bg-[#00d9ff]/30 hover:scale-110'
              : 'hover:bg-[#00d9ff]/20 hover:scale-110'
          )}
          title="Toggle Metadata"
        >
          <Database className={cn('w-5 h-5', showMetadata ? 'text-[#00d9ff]' : 'text-white/60')} />
        </Button>

        {/* Only show other buttons if widgets exist */}
        {state.widgets.length > 0 && (
          <>
            <div className="w-px h-6 bg-white/10 mx-2" />

            <Button
              variant="ghost"
              size="icon"
              onClick={undo}
              disabled={!canUndo}
              className={cn(
                'rounded-lg transition-all duration-300',
                canUndo ? 'hover:bg-[#00d9ff]/20 hover:scale-110' : 'opacity-30'
              )}
              title="Undo (Ctrl+Z)"
            >
              <Undo2 className="w-5 h-5 text-[#00d9ff]" />
            </Button>

            <Button
              variant="ghost"
              size="icon"
              onClick={redo}
              disabled={!canRedo}
              className={cn(
                'rounded-lg transition-all duration-300',
                canRedo ? 'hover:bg-[#00d9ff]/20 hover:scale-110' : 'opacity-30'
              )}
              title="Redo (Ctrl+Shift+Z)"
            >
              <Redo2 className="w-5 h-5 text-[#00d9ff]" />
            </Button>

            <div className="w-px h-6 bg-white/10 mx-2" />

            <Button
              variant="ghost"
              size="icon"
              onClick={handleExportCSV}
              className={cn(
                'rounded-lg transition-all duration-300',
                'hover:bg-blue-400/20 hover:scale-110'
              )}
              title="Export CSV (for Power BI import)"
            >
              <FileSpreadsheet className="w-5 h-5 text-blue-400" />
            </Button>

            <Button
              variant="ghost"
              size="icon"
              onClick={handleSnapshot}
              className={cn(
                'rounded-lg transition-all duration-300',
                'hover:bg-[#ff006e]/20 hover:scale-110'
              )}
              title="Create Snapshot"
            >
              <Camera className="w-5 h-5 text-[#ff006e]" />
            </Button>

            <Button
              variant="ghost"
              size="icon"
              onClick={handleExportPowerBI}
              className={cn(
                'rounded-lg transition-all duration-300',
                'hover:bg-green-400/20 hover:scale-110'
              )}
              title="Export Power BI (.pbix) - Experimental"
            >
              <Download className="w-5 h-5 text-green-400" />
            </Button>

            {state.history.length > 0 && (
              <>
                <div className="w-px h-6 bg-white/10 mx-2" />
                <div className="text-xs text-white/40 font-mono px-2">
                  {state.currentHistoryIndex + 1}/{state.history.length} states
                </div>
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}
