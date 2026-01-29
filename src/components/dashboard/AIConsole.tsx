import { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Lightbulb } from 'lucide-react';
import { useDashboard } from '@/contexts/DashboardContext';
import { AIMessage } from '@/types/dashboard';
import { processAICommand } from '@/utils/aiProcessor';
import { cn } from '@/lib/utils';

// Example prompts organized by category
const EXAMPLE_PROMPTS = {
  visualization: [
    "Create a bar chart showing sales by region",
    "Show me KPIs for total revenue and orders",
    "Add a line chart for revenue over time",
    "Generate a complete dashboard",
    "Create a pie chart showing product distribution"
  ],
  questions: [
    "What are the top 5 products by sales?",
    "What's the average revenue per region?",
    "Which region has the highest sales?",
    "How many records are in the dataset?",
    "What's the total revenue?"
  ],
  analysis: [
    "Explain this chart",
    "What insights can I get from this data?",
    "What does the revenue trend tell us?",
    "Show me the statistics for sales"
  ]
};

export function AIConsole() {
  const { state, addAIMessage, addWidget, createSnapshot } = useDashboard();
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [showExamples, setShowExamples] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [state.aiMessages]);

  // Hide examples when user starts typing or has messages
  useEffect(() => {
    if (state.aiMessages.length > 0 || input.length > 0) {
      setShowExamples(false);
    } else {
      setShowExamples(true);
    }
  }, [state.aiMessages.length, input.length]);

  const handleExampleClick = (example: string) => {
    setInput(example);
    inputRef.current?.focus();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isProcessing || state.datasets.length === 0) return;

    const userMessage: AIMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    addAIMessage(userMessage);
    const commandText = input.trim();
    setInput('');
    setIsProcessing(true);

    try {
      const response = await processAICommand(commandText, state);
      
      // For explain_chart, only show the explanation text, not JSON
      const isExplanation = response.explanation !== undefined;
      
      const assistantMessage: AIMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.message,  // Backend already provides clean text for explanations
        timestamp: new Date(),
        // Only include JSON for non-explanation responses (for debugging)
        json: isExplanation ? undefined : response.json,
      };

      addAIMessage(assistantMessage);

      // Handle different response types
      if (response.widgets && Array.isArray(response.widgets) && response.widgets.length > 0) {
        response.widgets.forEach(widget => {
          if (widget && widget.id) {
            addWidget(widget);
          }
        });
        if (response.widgets.length > 0) {
          createSnapshot(`AI: ${commandText.slice(0, 50)}...`);
        }
      } else if (response.update) {
        // Handle widget update - frontend context handles this
        console.log('Widget update:', response.update);
      } else if (response.remove) {
        // Handle widget removal - frontend context handles this
        console.log('Widget removal:', response.remove);
      }
    } catch (error) {
      console.error('AI command error:', error);
      const errorMessage: AIMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Error: ${error instanceof Error ? error.message : 'Unknown error'}. Please check backend is running.`,
        timestamp: new Date(),
      };
      addAIMessage(errorMessage);
    } finally {
      setIsProcessing(false);
      inputRef.current?.focus();
    }
  };

  return (
    <div className="w-full h-[40vh] flex flex-col bg-gradient-to-b from-[#0a0e14] to-[#1a1f2e] border-b-2 border-[#00d9ff]/20">
      {/* Header */}
      <div className="px-6 py-4 border-b border-white/5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Sparkles className="w-5 h-5 text-[#00d9ff]" />
            <h2 className="text-lg font-bold text-[#00d9ff]">AI Command Console</h2>
            <span className="text-xs text-white/40 font-mono">v1.0.0</span>
          </div>
          {state.aiMessages.length > 0 && (
            <a
              href="/evaluation"
              className="text-xs text-white/40 hover:text-[#00d9ff] transition-colors font-mono"
              title="View evaluation metrics"
            >
              View Metrics →
            </a>
          )}
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {state.aiMessages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center space-y-4 max-w-2xl px-4">
              <div className="inline-block p-4 rounded-xl bg-[#00d9ff]/10 border border-[#00d9ff]/20">
                <Sparkles className="w-8 h-8 text-[#00d9ff]" />
              </div>
              <div>
                <p className="text-white/80 text-base font-semibold mb-2">
                  {state.datasets.length === 0 
                    ? 'Upload a dataset to start building your dashboard with AI'
                    : 'Ready to help! Ask me anything about your data'}
                </p>
                {state.datasets.length > 0 && (
                  <p className="text-white/50 text-sm">
                    Click on the example prompts below to get started, or type your own question
                  </p>
                )}
              </div>
            </div>
          </div>
        ) : (
          <>
            {state.aiMessages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  'flex gap-3 animate-in fade-in slide-in-from-bottom-2 duration-300',
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                )}
              >
                <div
                  className={cn(
                    'max-w-[70%] p-4 rounded-xl',
                    message.role === 'user'
                      ? 'bg-[#00d9ff]/10 border border-[#00d9ff]/30 ml-auto'
                      : 'bg-[#ff006e]/10 border border-[#ff006e]/30'
                  )}
                >
                  <p className="text-sm text-white/90 leading-relaxed whitespace-pre-wrap">{message.content}</p>
                  {/* Only show JSON for debugging - hidden in collapsible details */}
                  {message.json && (
                    <details className="mt-2">
                      <summary className="text-xs text-white/40 cursor-pointer hover:text-white/60 font-mono">
                        Show technical details
                      </summary>
                      <pre className="mt-2 p-3 bg-black/30 rounded-lg text-xs text-[#00d9ff] overflow-x-auto font-mono">
                        {JSON.stringify(message.json, null, 2)}
                      </pre>
                    </details>
                  )}
                  <span className="text-[10px] text-white/30 mt-2 block font-mono">
                    {message.timestamp.toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Example Prompts */}
      {showExamples && state.datasets.length > 0 && (
        <div className="px-6 py-3 border-t border-white/5 bg-black/20">
          <div className="flex items-center gap-2 mb-3">
            <Lightbulb className="w-4 h-4 text-[#00d9ff]" />
            <span className="text-xs font-semibold text-white/60 uppercase tracking-wider">Example Prompts</span>
          </div>
          <div className="space-y-3">
            {/* Visualization Examples */}
            <div>
              <span className="text-xs text-white/40 mb-2 block">Visualizations</span>
              <div className="flex flex-wrap gap-2">
                {EXAMPLE_PROMPTS.visualization.map((prompt, idx) => (
                  <button
                    key={`viz-${idx}`}
                    type="button"
                    onClick={() => handleExampleClick(prompt)}
                    className={cn(
                      'px-3 py-1.5 text-xs rounded-lg border transition-all duration-200',
                      'bg-[#00d9ff]/5 border-[#00d9ff]/20 text-white/70',
                      'hover:bg-[#00d9ff]/10 hover:border-[#00d9ff]/40 hover:text-white/90',
                      'active:scale-95 font-mono'
                    )}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
            
            {/* Question Examples */}
            <div>
              <span className="text-xs text-white/40 mb-2 block">Ask Questions</span>
              <div className="flex flex-wrap gap-2">
                {EXAMPLE_PROMPTS.questions.map((prompt, idx) => (
                  <button
                    key={`q-${idx}`}
                    type="button"
                    onClick={() => handleExampleClick(prompt)}
                    className={cn(
                      'px-3 py-1.5 text-xs rounded-lg border transition-all duration-200',
                      'bg-[#ff006e]/5 border-[#ff006e]/20 text-white/70',
                      'hover:bg-[#ff006e]/10 hover:border-[#ff006e]/40 hover:text-white/90',
                      'active:scale-95 font-mono'
                    )}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
            
            {/* Analysis Examples */}
            <div>
              <span className="text-xs text-white/40 mb-2 block">Analysis</span>
              <div className="flex flex-wrap gap-2">
                {EXAMPLE_PROMPTS.analysis.map((prompt, idx) => (
                  <button
                    key={`analysis-${idx}`}
                    type="button"
                    onClick={() => handleExampleClick(prompt)}
                    className={cn(
                      'px-3 py-1.5 text-xs rounded-lg border transition-all duration-200',
                      'bg-white/5 border-white/10 text-white/70',
                      'hover:bg-white/10 hover:border-white/20 hover:text-white/90',
                      'active:scale-95 font-mono'
                    )}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="p-6 border-t border-white/5">
        <div className="relative">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={
              state.datasets.length === 0
                ? 'Upload a dataset first...'
                : 'Ask a question or describe what you want to visualize...'
            }
            disabled={isProcessing || state.datasets.length === 0}
            className={cn(
              'w-full px-6 py-4 pr-14 bg-black/30 rounded-xl',
              'border-2 transition-all duration-300 font-mono text-sm',
              'placeholder:text-white/30 text-white/90',
              'focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed',
              isProcessing
                ? 'border-[#00d9ff]/50 glow-cyan animate-pulse'
                : 'border-[#00d9ff]/30 hover:border-[#00d9ff]/50 focus:border-[#00d9ff] focus:glow-cyan'
            )}
          />
          <button
            type="submit"
            disabled={isProcessing || !input.trim() || state.datasets.length === 0}
            className={cn(
              'absolute right-2 top-1/2 -translate-y-1/2',
              'p-2.5 rounded-lg bg-[#00d9ff]/20 border border-[#00d9ff]/30',
              'hover:bg-[#00d9ff]/30 hover:scale-105',
              'transition-all duration-300',
              'disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100'
            )}
          >
            <Send className="w-4 h-4 text-[#00d9ff]" />
          </button>
        </div>
      </form>
    </div>
  );
}
