import { DashboardProvider } from '@/contexts/DashboardContext';
import { AIConsole } from './AIConsole';
import { DashboardCanvas } from './DashboardCanvas';
import { WidgetInspector } from './WidgetInspector';
import { QuickActionsToolbar } from './QuickActionsToolbar';
import { MetadataSidebar } from './MetadataSidebar';
import { DatasetUpload } from './DatasetUpload';
import { SampleDataGenerator } from './SampleDataGenerator';
import { useDashboard } from '@/contexts/DashboardContext';
import { Toaster } from '@/components/ui/sonner';

function DashboardContent() {
  const { state } = useDashboard();

  return (
    <div className="min-h-screen flex flex-col relative noise">
      {/* AI Console - Top Section */}
      <AIConsole />

      {/* Main Content Area */}
      <div className="flex-1 relative overflow-auto">
        {state.datasets.length === 0 ? (
          <div className="max-w-4xl mx-auto p-8 pt-16">
            <div className="mb-8 text-center">
              <h1 className="text-4xl font-bold text-white mb-3">
                Local-First AI BI Dashboard
              </h1>
              <p className="text-white/60 text-lg max-w-2xl mx-auto">
                Upload your data, chat with AI to create visualizations, and customize every detail.
                All processing happens locally — no vendor lock-in, just raw power.
              </p>
            </div>
            <DatasetUpload />
            <SampleDataGenerator />
          </div>
        ) : (
          <DashboardCanvas />
        )}

        {/* Metadata Sidebar */}
        <MetadataSidebar />

        {/* Widget Inspector */}
        {state.selectedWidget && <WidgetInspector />}
      </div>

      {/* Quick Actions Toolbar - Show when datasets exist */}
      {state.datasets.length > 0 && <QuickActionsToolbar />}

      {/* Toast Notifications */}
      <Toaster 
        position="top-right"
        toastOptions={{
          style: {
            background: 'rgba(26, 31, 46, 0.95)',
            border: '1px solid rgba(0, 217, 255, 0.3)',
            color: '#fff',
          },
        }}
      />
    </div>
  );
}

export function Dashboard() {
  return (
    <DashboardProvider>
      <DashboardContent />
    </DashboardProvider>
  );
}
