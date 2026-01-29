import React, { createContext, useContext, useReducer, useCallback, ReactNode } from 'react';
import { DashboardState, Dataset, Widget, AIMessage, DashboardSnapshot } from '@/types/dashboard';

interface DashboardContextType {
  state: DashboardState;
  showMetadata: boolean;
  toggleMetadata: () => void;
  addDataset: (dataset: Dataset) => void;
  addWidget: (widget: Widget) => void;
  updateWidget: (id: string, updates: Partial<Widget>) => void;
  removeWidget: (id: string) => void;
  selectWidget: (id: string | null) => void;
  addAIMessage: (message: AIMessage) => void;
  createSnapshot: (label: string) => void;
  restoreSnapshot: (index: number) => void;
  undo: () => void;
  redo: () => void;
}

const DashboardContext = createContext<DashboardContextType | undefined>(undefined);

type Action =
  | { type: 'ADD_DATASET'; payload: Dataset }
  | { type: 'ADD_WIDGET'; payload: Widget }
  | { type: 'UPDATE_WIDGET'; payload: { id: string; updates: Partial<Widget> } }
  | { type: 'REMOVE_WIDGET'; payload: string }
  | { type: 'SELECT_WIDGET'; payload: string | null }
  | { type: 'ADD_AI_MESSAGE'; payload: AIMessage }
  | { type: 'CREATE_SNAPSHOT'; payload: string }
  | { type: 'RESTORE_SNAPSHOT'; payload: number };

const initialState: DashboardState = {
  datasets: [],
  widgets: [],
  selectedWidget: null,
  aiMessages: [],
  history: [],
  currentHistoryIndex: -1,
};

function dashboardReducer(state: DashboardState, action: Action): DashboardState {
  switch (action.type) {
    case 'ADD_DATASET':
      return { ...state, datasets: [...state.datasets, action.payload] };
    
    case 'ADD_WIDGET':
      return { ...state, widgets: [...state.widgets, action.payload] };
    
    case 'UPDATE_WIDGET':
      return {
        ...state,
        widgets: state.widgets.map(w =>
          w.id === action.payload.id ? { ...w, ...action.payload.updates } : w
        ),
      };
    
    case 'REMOVE_WIDGET':
      return {
        ...state,
        widgets: state.widgets.filter(w => w.id !== action.payload),
        selectedWidget: state.selectedWidget === action.payload ? null : state.selectedWidget,
      };
    
    case 'SELECT_WIDGET':
      return { ...state, selectedWidget: action.payload };
    
    case 'ADD_AI_MESSAGE':
      return { ...state, aiMessages: [...state.aiMessages, action.payload] };
    
    case 'CREATE_SNAPSHOT':
      const snapshot: DashboardSnapshot = {
        id: Date.now().toString(),
        timestamp: new Date(),
        widgets: JSON.parse(JSON.stringify(state.widgets)),
        label: action.payload,
      };
      return {
        ...state,
        history: [...state.history.slice(0, state.currentHistoryIndex + 1), snapshot],
        currentHistoryIndex: state.currentHistoryIndex + 1,
      };
    
    case 'RESTORE_SNAPSHOT':
      if (action.payload >= 0 && action.payload < state.history.length) {
        return {
          ...state,
          widgets: JSON.parse(JSON.stringify(state.history[action.payload].widgets)),
          currentHistoryIndex: action.payload,
        };
      }
      return state;
    
    default:
      return state;
  }
}

export function DashboardProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(dashboardReducer, initialState);
  const [showMetadata, setShowMetadata] = React.useState(false);
  
  const toggleMetadata = useCallback(() => {
    setShowMetadata(prev => !prev);
  }, []);

  const addDataset = useCallback((dataset: Dataset) => {
    dispatch({ type: 'ADD_DATASET', payload: dataset });
  }, []);

  const addWidget = useCallback((widget: Widget) => {
    dispatch({ type: 'ADD_WIDGET', payload: widget });
  }, []);

  const updateWidget = useCallback((id: string, updates: Partial<Widget>) => {
    dispatch({ type: 'UPDATE_WIDGET', payload: { id, updates } });
  }, []);

  const removeWidget = useCallback((id: string) => {
    dispatch({ type: 'REMOVE_WIDGET', payload: id });
  }, []);

  const selectWidget = useCallback((id: string | null) => {
    dispatch({ type: 'SELECT_WIDGET', payload: id });
  }, []);

  const addAIMessage = useCallback((message: AIMessage) => {
    dispatch({ type: 'ADD_AI_MESSAGE', payload: message });
  }, []);

  const createSnapshot = useCallback((label: string) => {
    dispatch({ type: 'CREATE_SNAPSHOT', payload: label });
  }, []);

  const restoreSnapshot = useCallback((index: number) => {
    dispatch({ type: 'RESTORE_SNAPSHOT', payload: index });
  }, []);

  const undo = useCallback(() => {
    if (state.currentHistoryIndex > 0) {
      dispatch({ type: 'RESTORE_SNAPSHOT', payload: state.currentHistoryIndex - 1 });
    }
  }, [state.currentHistoryIndex]);

  const redo = useCallback(() => {
    if (state.currentHistoryIndex < state.history.length - 1) {
      dispatch({ type: 'RESTORE_SNAPSHOT', payload: state.currentHistoryIndex + 1 });
    }
  }, [state.currentHistoryIndex, state.history.length]);

  return (
    <DashboardContext.Provider
      value={{
        state,
        showMetadata,
        toggleMetadata,
        addDataset,
        addWidget,
        updateWidget,
        removeWidget,
        selectWidget,
        addAIMessage,
        createSnapshot,
        restoreSnapshot,
        undo,
        redo,
      }}
    >
      {children}
    </DashboardContext.Provider>
  );
}

export function useDashboard() {
  const context = useContext(DashboardContext);
  if (!context) {
    throw new Error('useDashboard must be used within DashboardProvider');
  }
  return context;
}
