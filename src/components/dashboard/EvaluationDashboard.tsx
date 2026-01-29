import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BarChart3, Clock, DollarSign, CheckCircle2, XCircle, TrendingUp, Activity, ArrowLeft, RefreshCw } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { cn } from '@/lib/utils';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface EvaluationSummary {
  total_tasks: number;
  task_success_rate: number;
  average_latency_ms: number;
  average_action_correctness: number;
  total_estimated_cost: number;
  average_reasoning_length: {
    prompt: number;
    response: number;
    total: number;
  };
  tool_usage_accuracy: number;
  metrics_by_action_type: Record<string, any>;
}

interface EvaluationResult {
  id: string;
  task_id: string;
  timestamp: string;
  user_command: string;
  action_type: string;
  success: boolean;
  latency_ms: number;
  estimated_cost: number;
  action_correctness_score: number;
  tool_usage_correct: boolean;
}

export function EvaluationDashboard() {
  const navigate = useNavigate();
  const [summary, setSummary] = useState<EvaluationSummary | null>(null);
  const [results, setResults] = useState<EvaluationResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSummary = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/evaluation/summary`);
      if (!response.ok) throw new Error('Failed to fetch summary');
      const data = await response.json();
      setSummary(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load evaluation data');
    }
  };

  const fetchResults = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/evaluation/results?limit=50`);
      if (!response.ok) throw new Error('Failed to fetch results');
      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load results');
    }
  };

  const loadData = async () => {
    setLoading(true);
    setError(null);
    await Promise.all([fetchSummary(), fetchResults()]);
    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleClearHistory = async () => {
    if (!confirm('Are you sure you want to clear all evaluation history?')) return;
    
    try {
      const response = await fetch(`${API_BASE}/api/v1/evaluation/clear`, { method: 'DELETE' });
      if (!response.ok) throw new Error('Failed to clear history');
      await Promise.all([fetchSummary(), fetchResults()]);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to clear history');
    }
  };

  const handleExport = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/evaluation/export`, { method: 'POST' });
      if (!response.ok) throw new Error('Failed to export');
      const data = await response.json();
      alert(`Results exported to ${data.filepath}`);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to export');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-[#0a0e14] to-[#1a1f2e] p-6 flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="inline-block p-4 rounded-xl bg-[#00d9ff]/10 border border-[#00d9ff]/20">
            <Activity className="w-8 h-8 text-[#00d9ff] animate-pulse" />
          </div>
          <div className="text-white/60">Loading evaluation data...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-[#0a0e14] to-[#1a1f2e] p-6">
        <div className="max-w-4xl mx-auto space-y-4">
          <div className="flex items-center gap-4">
            <Button
              onClick={() => navigate('/')}
              variant="ghost"
              size="icon"
              className="hover:bg-[#00d9ff]/20"
            >
              <ArrowLeft className="w-5 h-5 text-white" />
            </Button>
            <div>
              <h2 className="text-2xl font-bold text-white">Agent Evaluation Dashboard</h2>
            </div>
          </div>
          <Card className="bg-red-500/10 border-red-500/30">
            <CardHeader>
              <CardTitle className="text-red-400">Error Loading Data</CardTitle>
              <CardDescription className="text-red-300/80">{error}</CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                onClick={loadData}
                className="bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/30"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Retry
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (!summary || summary.total_tasks === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-[#0a0e14] to-[#1a1f2e] p-6">
        <div className="max-w-4xl mx-auto space-y-6">
          <div className="flex items-center gap-4">
            <Button
              onClick={() => navigate('/')}
              variant="ghost"
              size="icon"
              className="hover:bg-[#00d9ff]/20"
            >
              <ArrowLeft className="w-5 h-5 text-white" />
            </Button>
            <div>
              <h2 className="text-2xl font-bold text-white">Agent Evaluation Dashboard</h2>
              <p className="text-white/60 text-sm mt-1">
                Comprehensive metrics and performance analysis
              </p>
            </div>
          </div>
          <Card className="bg-black/30 border-white/10">
            <CardHeader>
              <CardTitle className="text-white">Agent Evaluation</CardTitle>
              <CardDescription className="text-white/60">
                No evaluation data yet. Start using the AI agent to generate metrics.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                onClick={() => navigate('/')}
                className="bg-[#00d9ff]/20 hover:bg-[#00d9ff]/30 text-white border border-[#00d9ff]/30"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Go to Dashboard
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0a0e14] to-[#1a1f2e] p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            onClick={() => navigate('/')}
            variant="ghost"
            size="icon"
            className="hover:bg-[#00d9ff]/20"
          >
            <ArrowLeft className="w-5 h-5 text-white" />
          </Button>
          <div>
            <h2 className="text-2xl font-bold text-white">Agent Evaluation Dashboard</h2>
            <p className="text-white/60 text-sm mt-1">
              Comprehensive metrics and performance analysis
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button
            onClick={loadData}
            variant="outline"
            size="icon"
            className="bg-black/30 border-white/10 text-white hover:bg-black/50"
            title="Refresh Data"
          >
            <RefreshCw className="w-4 h-4" />
          </Button>
          <Button
            onClick={handleExport}
            variant="outline"
            className="bg-black/30 border-white/10 text-white hover:bg-black/50"
          >
            Export Results
          </Button>
          <Button
            onClick={handleClearHistory}
            variant="outline"
            className="bg-red-500/10 border-red-500/30 text-red-400 hover:bg-red-500/20"
          >
            Clear History
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Task Success Rate"
          value={`${(summary.task_success_rate * 100).toFixed(1)}%`}
          icon={CheckCircle2}
          color="text-green-400"
          bgColor="bg-green-500/10"
          borderColor="border-green-500/30"
        />
        <MetricCard
          title="Avg Latency"
          value={`${summary.average_latency_ms.toFixed(0)}ms`}
          icon={Clock}
          color="text-blue-400"
          bgColor="bg-blue-500/10"
          borderColor="border-blue-500/30"
        />
        <MetricCard
          title="Action Correctness"
          value={`${(summary.average_action_correctness * 100).toFixed(1)}%`}
          icon={TrendingUp}
          color="text-purple-400"
          bgColor="bg-purple-500/10"
          borderColor="border-purple-500/30"
        />
        <MetricCard
          title="Total Cost"
          value={`$${summary.total_estimated_cost.toFixed(4)}`}
          icon={DollarSign}
          color="text-yellow-400"
          bgColor="bg-yellow-500/10"
          borderColor="border-yellow-500/30"
        />
      </div>

      {/* Detailed Metrics */}
      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="bg-black/30 border-white/10">
          <TabsTrigger value="overview" className="text-white">Overview</TabsTrigger>
          <TabsTrigger value="metrics" className="text-white">Detailed Metrics</TabsTrigger>
          <TabsTrigger value="results" className="text-white">Recent Results</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="bg-black/30 border-white/10">
              <CardHeader>
                <CardTitle className="text-white text-lg">Reasoning Length</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex justify-between text-white/80">
                  <span>Prompt Tokens:</span>
                  <span className="font-mono">{summary.average_reasoning_length.prompt.toFixed(0)}</span>
                </div>
                <div className="flex justify-between text-white/80">
                  <span>Response Tokens:</span>
                  <span className="font-mono">{summary.average_reasoning_length.response.toFixed(0)}</span>
                </div>
                <div className="flex justify-between text-white font-semibold pt-2 border-t border-white/10">
                  <span>Total Tokens:</span>
                  <span className="font-mono">{summary.average_reasoning_length.total.toFixed(0)}</span>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-black/30 border-white/10">
              <CardHeader>
                <CardTitle className="text-white text-lg">Tool Usage</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-white mb-2">
                  {(summary.tool_usage_accuracy * 100).toFixed(1)}%
                </div>
                <p className="text-white/60 text-sm">
                  Correct tool/action usage rate
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="metrics" className="space-y-4">
          <Card className="bg-black/30 border-white/10">
            <CardHeader>
              <CardTitle className="text-white">Metrics by Action Type</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {Object.entries(summary.metrics_by_action_type).map(([actionType, metrics]: [string, any]) => (
                  <div key={actionType} className="p-4 bg-black/20 rounded-lg border border-white/5">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-white font-semibold">{actionType}</span>
                      <span className="text-white/60 text-sm">{metrics.count} tasks</span>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-white/60">Success Rate:</span>
                        <span className="text-white ml-2">{(metrics.success_rate * 100).toFixed(1)}%</span>
                      </div>
                      <div>
                        <span className="text-white/60">Avg Latency:</span>
                        <span className="text-white ml-2">{metrics.avg_latency_ms.toFixed(0)}ms</span>
                      </div>
                      <div>
                        <span className="text-white/60">Avg Cost:</span>
                        <span className="text-white ml-2">${metrics.avg_cost.toFixed(4)}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="results" className="space-y-4">
          <Card className="bg-black/30 border-white/10">
            <CardHeader>
              <CardTitle className="text-white">Recent Evaluation Results</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {results.map((result) => (
                  <div
                    key={result.id}
                    className={cn(
                      "p-4 rounded-lg border",
                      result.success
                        ? "bg-green-500/5 border-green-500/20"
                        : "bg-red-500/5 border-red-500/20"
                    )}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          {result.success ? (
                            <CheckCircle2 className="w-4 h-4 text-green-400" />
                          ) : (
                            <XCircle className="w-4 h-4 text-red-400" />
                          )}
                          <span className="text-white font-medium">{result.action_type}</span>
                          <span className="text-white/40 text-xs">
                            {new Date(result.timestamp).toLocaleString()}
                          </span>
                        </div>
                        <p className="text-white/70 text-sm mb-2">{result.user_command}</p>
                        <div className="flex gap-4 text-xs text-white/60">
                          <span>Latency: {result.latency_ms.toFixed(0)}ms</span>
                          <span>Correctness: {(result.action_correctness_score * 100).toFixed(0)}%</span>
                          <span>Cost: ${result.estimated_cost.toFixed(4)}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

interface MetricCardProps {
  title: string;
  value: string;
  icon: any;
  color: string;
  bgColor: string;
  borderColor: string;
}

function MetricCard({ title, value, icon: Icon, color, bgColor, borderColor }: MetricCardProps) {
  return (
    <Card className={cn("bg-black/30 border", borderColor)}>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-white/80 text-sm font-medium">{title}</CardTitle>
        <div className={cn("p-2 rounded-lg", bgColor)}>
          <Icon className={cn("w-4 h-4", color)} />
        </div>
      </CardHeader>
      <CardContent>
        <div className={cn("text-2xl font-bold", color)}>{value}</div>
      </CardContent>
    </Card>
  );
}

