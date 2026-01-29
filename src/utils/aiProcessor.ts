import { DashboardState, Widget } from '@/types/dashboard';

interface AIResponse {
  message: string;
  json?: any;
  widgets?: Widget[];
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function processAICommand(
  command: string,
  state: DashboardState
): Promise<AIResponse> {
  const dataset = state.datasets[0]; // Use first dataset

  if (!dataset) {
    return {
      message: 'Please upload a dataset first.',
    };
  }

  try {
    // Call backend API
    const response = await fetch(`${API_BASE}/api/v1/ai/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        command,
        state: {
          datasets: state.datasets,
          widgets: state.widgets,
        },
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage = `API error: ${response.statusText}`;
      try {
        const errorJson = JSON.parse(errorText);
        errorMessage = errorJson.detail || errorMessage;
      } catch {
        errorMessage = errorText || errorMessage;
      }
      throw new Error(errorMessage);
    }

    const data = await response.json();
    
    // For explain_chart, use the explanation text, not JSON
    if (data.explanation) {
      return {
        message: data.explanation.insights || data.message || 'Chart analysis provided',
        json: undefined,  // Don't show JSON for explanations
        widgets: data.widgets || [],
        update: data.update,
        remove: data.remove,
        explanation: data.explanation,
      };
    }
    
    return {
      message: data.message || 'Command processed',
      json: data.json,
      widgets: data.widgets || [],
      update: data.update,
      remove: data.remove,
    };
  } catch (error) {
    console.error('AI processing error:', error);
    return {
      message: `Error processing command: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again.`,
    };
  }
}
