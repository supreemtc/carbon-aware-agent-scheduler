import React, { useState, useEffect, useCallback } from 'react';
import { api } from './services/api';
import type {
  CompareResponse,
  EnvironmentResponse,
  OptimizationWeights,
  PresetType,
  WorkflowRequest,
  WorkflowTask,
} from './types';
import { Header } from './components/Header';
import { EnvironmentView } from './components/EnvironmentView';
import { WorkflowBuilder } from './components/WorkflowBuilder';
import { PrioritySliders } from './components/PrioritySliders';
import { DynamicScenarios } from './components/DynamicScenarios';
import { KeyMetrics } from './components/KeyMetrics';
import { DecisionSteps } from './components/DecisionSteps';
import { OptimizedVsBaseline } from './components/OptimizedVsBaseline';
import { ExplanationCard } from './components/ExplanationCard';
import {
  AlertCircle,
  Play,
  RefreshCw,
  Sparkles,
  CheckCircle2,
} from 'lucide-react';

const SCENARIO_CONFIGS: Record<
  PresetType,
  {
    name: string;
    weights: OptimizationWeights;
    minAccuracy: number;
    delayTolerance: number;
    deadlineSeconds: number;
    description: string;
  }
> = {
  GREEN: {
    name: 'Green Priority',
    weights: {
      carbon: 0.80,
      energy: 0.15,
      latency: 0.0,
      cost: 0.0,
      accuracy: 0.05,
    },
    minAccuracy: 0.80,
    delayTolerance: 60,
    deadlineSeconds: 4,
    description: 'Routes to cleanest hydro grid (northamerica-northeast1) with +60s temporal shifting',
  },
  LOW_LATENCY: {
    name: 'Low Latency',
    weights: {
      latency: 0.90,
      cost: 0.05,
      accuracy: 0.05,
      carbon: 0.0,
      energy: 0.0,
    },
    minAccuracy: 0.80,
    delayTolerance: 0,
    deadlineSeconds: 2,
    description: 'Routes to Mumbai hub (asia-south1, 25ms ping) for fast 375ms response',
  },
  COST_SAVER: {
    name: 'Cost Saver',
    weights: {
      cost: 0.85,
      latency: 0.05,
      energy: 0.05,
      carbon: 0.05,
      accuracy: 0.0,
    },
    minAccuracy: 0.75, // allows 8B tier
    delayTolerance: 30,
    deadlineSeconds: 4,
    description: 'Selects economical gemini-1.5-flash-8b tier ($0.000112 spend)',
  },
  HIGH_ACCURACY: {
    name: 'High Accuracy',
    weights: {
      accuracy: 1.0,
      latency: 0.0,
      cost: 0.0,
      carbon: 0.0,
      energy: 0.0,
    },
    minAccuracy: 0.90, // demands Gemini 1.5 Pro
    delayTolerance: 30,
    deadlineSeconds: 4,
    description: 'Selects flagship gemini-1.5-pro model (92% benchmark accuracy)',
  },
};

export const App: React.FC = () => {
  // Backend connection status
  const [backendConnected, setBackendConnected] = useState<boolean | null>(null);
  const [checkingHealth, setCheckingHealth] = useState<boolean>(false);

  // Environment data
  const [environment, setEnvironment] = useState<EnvironmentResponse | null>(null);
  const [loadingEnv, setLoadingEnv] = useState<boolean>(true);

  // Workflow State (Section 1 Defaults)
  const [workflowId, setWorkflowId] = useState<string>('wf-demo-001');
  const [tasks, setTasks] = useState<WorkflowTask[]>([
    {
      step_id: 'step-1',
      task_type: 'summarization',
      description: 'Summarize sensor energy logs',
      input_text: 'Sensor energy telemetry and campus load data',
      estimated_tokens: 1500,
      minimum_accuracy: 0.80,
      deadline_seconds: 4,
      delay_tolerance_seconds: 30,
      priority: 'normal',
    },
  ]);

  // Optimization Weights (Section 2)
  const [weights, setWeights] = useState<OptimizationWeights>({
    accuracy: 0.30,
    latency: 0.20,
    cost: 0.20,
    carbon: 0.15,
    energy: 0.15,
  });
  const [activePreset, setActivePreset] = useState<PresetType | null>(null);
  const [lastUpdatedTimestamp, setLastUpdatedTimestamp] = useState<string | null>(null);

  // Execution & Comparison Results
  const [comparisonResult, setComparisonResult] = useState<CompareResponse | null>(null);
  const [optimizing, setOptimizing] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Core execution caller: build WorkflowRequest and POST to /compare
  const runOptimization = useCallback(async (
    customWeights?: OptimizationWeights,
    customTasks?: WorkflowTask[],
    customPreset?: PresetType
  ) => {
    setOptimizing(true);
    setErrorMsg(null);

    const effectiveWeights = customWeights || weights;
    const effectiveTasks = customTasks || tasks;

    const requestPayload: WorkflowRequest = {
      workflow_id: workflowId || 'wf-demo-001',
      tasks: effectiveTasks,
      accuracy_importance: effectiveWeights.accuracy,
      latency_importance: effectiveWeights.latency,
      cost_importance: effectiveWeights.cost,
      carbon_importance: effectiveWeights.carbon,
      energy_importance: effectiveWeights.energy,
    };

    try {
      const result = await api.compareWorkflow(requestPayload);
      setComparisonResult(result);
      setBackendConnected(true);
      const timeStr = new Date().toLocaleTimeString();
      setLastUpdatedTimestamp(timeStr);
      if (customPreset) {
        setActivePreset(customPreset);
      }
    } catch (err: any) {
      console.error('Optimization error:', err);
      setErrorMsg(err.message || 'Failed to schedule workflow');
      if (err.message && err.message.includes('connect')) {
        setBackendConnected(false);
      }
    } finally {
      setOptimizing(false);
    }
  }, [weights, tasks, workflowId]);

  // Check health on mount
  const checkHealthStatus = useCallback(async () => {
    setCheckingHealth(true);
    try {
      await api.checkHealth();
      setBackendConnected(true);
    } catch {
      setBackendConnected(false);
    } finally {
      setCheckingHealth(false);
    }
  }, []);

  // Fetch environment on mount
  const fetchEnvironmentData = useCallback(async () => {
    setLoadingEnv(true);
    try {
      const data = await api.getEnvironment();
      setEnvironment(data);
      setBackendConnected(true);
    } catch (err: any) {
      console.error('Failed to load environment:', err);
      setBackendConnected(false);
    } finally {
      setLoadingEnv(false);
    }
  }, []);

  useEffect(() => {
    checkHealthStatus();
    fetchEnvironmentData();
    // Auto-run initial optimization so the dashboard is pre-populated
    runOptimization();
  }, [checkHealthStatus, fetchEnvironmentData, runOptimization]);

  // Section 2 Preset Button clicked
  const handlePresetSelect = (preset: PresetType) => {
    const config = SCENARIO_CONFIGS[preset];
    setWeights(config.weights);
    setActivePreset(preset);
  };

  // Section 9 Dynamic Scenario Trigger
  const handleDynamicScenario = (preset: PresetType) => {
    const config = SCENARIO_CONFIGS[preset];
    
    // Update weights state
    setWeights(config.weights);
    setActivePreset(preset);

    // Update tasks with scenario-specific requirements (e.g. min_accuracy 0.75 for 8B, 0.90 for Pro)
    const updatedTasks = tasks.map((t) => ({
      ...t,
      minimum_accuracy: config.minAccuracy,
      delay_tolerance_seconds: config.delayTolerance,
    }));
    setTasks(updatedTasks);

    // Dispatch directly to backend /compare
    runOptimization(config.weights, updatedTasks, preset);
  };

  const activeScenarioConfig = activePreset ? SCENARIO_CONFIGS[activePreset] : null;

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col selection:bg-emerald-500/20 selection:text-emerald-300">
      {/* Header with backend health indicator */}
      <Header
        backendConnected={backendConnected}
        checkingHealth={checkingHealth}
        onRefreshHealth={checkHealthStatus}
        backendUrl={api.getBaseUrl()}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-7">
        {/* Backend Offline Warning Banner */}
        {backendConnected === false && (
          <div className="bg-rose-950/40 border border-rose-500/50 rounded-xl p-4 flex items-start space-x-3 text-rose-200">
            <AlertCircle className="h-5 w-5 text-rose-400 mt-0.5 shrink-0" />
            <div className="text-xs">
              <p className="font-bold text-sm text-white mb-0.5">Backend Service Offline</p>
              <p className="m-0 text-slate-300">
                Cannot connect to backend server at <code className="bg-slate-900 px-1 py-0.5 rounded text-rose-300 font-mono">{api.getBaseUrl()}</code>.
                Ensure the FastAPI server is running with <code className="bg-slate-900 px-1 py-0.5 rounded text-rose-300 font-mono">uvicorn backend.main:app --port 8000</code>.
              </p>
            </div>
          </div>
        )}

        {/* Validation / Infeasibility Error Banner */}
        {errorMsg && (
          <div className="bg-amber-950/40 border border-amber-500/50 rounded-xl p-4 flex items-start space-x-3 text-amber-200">
            <AlertCircle className="h-5 w-5 text-amber-400 mt-0.5 shrink-0" />
            <div className="text-xs flex-1">
              <p className="font-bold text-sm text-white mb-0.5">Scheduler Constraint Alert</p>
              <p className="m-0 text-slate-300 leading-relaxed">{errorMsg}</p>
            </div>
            <button
              onClick={() => setErrorMsg(null)}
              className="text-xs text-amber-400 hover:text-white underline cursor-pointer"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* SECTION 9: DYNAMIC SCENARIO DEMONSTRATION */}
        <DynamicScenarios
          onRunScenario={handleDynamicScenario}
          activeScenario={activePreset}
          loading={optimizing}
          lastUpdatedTimestamp={lastUpdatedTimestamp}
        />

        {/* LIVE DECISION UPDATED NOTIFICATION CALLOUT */}
        {activeScenarioConfig && lastUpdatedTimestamp && (
          <div className="bg-gradient-to-r from-emerald-950/40 via-teal-950/30 to-slate-900/60 border border-emerald-500/40 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-lg">
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                <CheckCircle2 className="h-5 w-5 text-emerald-400" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs uppercase font-bold tracking-wider text-emerald-400 font-mono">
                    Decision Updated
                  </span>
                  <span className="text-slate-500">•</span>
                  <span className="text-sm font-bold text-white">
                    {activeScenarioConfig.name} Applied
                  </span>
                </div>
                <p className="text-xs text-slate-300 m-0">
                  {activeScenarioConfig.description}
                </p>
              </div>
            </div>

            <div className="text-right font-mono text-xs text-slate-400 self-end sm:self-auto">
              <span>Recalculated at </span>
              <strong className="text-emerald-400">{lastUpdatedTimestamp}</strong>
            </div>
          </div>
        )}

        {/* SECTION 1 & SECTION 2: WORKFLOW INPUT & OPTIMIZATION PRIORITIES */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-6">
            <WorkflowBuilder
              workflowId={workflowId}
              onWorkflowIdChange={setWorkflowId}
              tasks={tasks}
              onTasksChange={setTasks}
            />
          </div>

          <div className="lg:col-span-6 flex flex-col justify-between">
            <PrioritySliders
              weights={weights}
              onWeightsChange={(w) => {
                setWeights(w);
                setActivePreset(null);
              }}
              onSelectPreset={handlePresetSelect}
              activePreset={activePreset}
            />

            {/* SECTION 4: Prominent Run Scheduler Button */}
            <div className="mt-4 pt-2">
              <button
                type="button"
                disabled={optimizing || backendConnected === false}
                onClick={() => runOptimization()}
                className="w-full py-4 px-6 rounded-2xl font-extrabold text-sm tracking-wide transition-all duration-200 shadow-xl flex items-center justify-center space-x-2.5 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-slate-950 shadow-emerald-500/25 ring-1 ring-emerald-400/50 hover:shadow-emerald-500/40"
              >
                {optimizing ? (
                  <>
                    <RefreshCw className="h-5 w-5 animate-spin text-slate-950" />
                    <span>CALCULATING PARETO TRADE-OFFS...</span>
                  </>
                ) : (
                  <>
                    <Play className="h-5 w-5 fill-current" />
                    <span>OPTIMIZE WORKFLOW</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* SCHEDULER RESULTS (SECTIONS 6, 5, 7, 8) */}
        {comparisonResult && (
          <div className="space-y-6">
            {/* SECTION 6: Key Metrics */}
            <KeyMetrics
              plan={comparisonResult.optimized_plan}
              comparison={comparisonResult.comparison}
            />

            {/* SECTION 5: Scheduler Decisions for each step */}
            <DecisionSteps
              steps={comparisonResult.optimized_plan.scheduled_steps}
              activeScenarioName={activeScenarioConfig?.name}
              lastUpdatedTimestamp={lastUpdatedTimestamp}
            />

            {/* SECTION 7: Optimized vs Baseline Side-by-Side */}
            <OptimizedVsBaseline comparisonData={comparisonResult} />

            {/* SECTION 8: Why did the scheduler choose this? */}
            <ExplanationCard
              summary={comparisonResult.summary}
              steps={comparisonResult.optimized_plan.scheduled_steps}
            />
          </div>
        )}

        {/* Prompt to optimize if no results yet */}
        {!comparisonResult && !optimizing && (
          <div className="bg-slate-900/40 border border-dashed border-slate-800 rounded-2xl p-10 text-center">
            <div className="h-12 w-12 rounded-full bg-emerald-500/10 text-emerald-400 flex items-center justify-center mx-auto mb-3 border border-emerald-500/20">
              <Sparkles className="h-6 w-6" />
            </div>
            <h3 className="text-base font-bold text-white mb-1">Ready for Multi-Objective Scheduling</h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto mb-4">
              Click <strong>OPTIMIZE WORKFLOW</strong> or select a <strong>Dynamic Scenario</strong> above to calculate optimal model assignments, compute regions, and carbon time windows.
            </p>
            <button
              type="button"
              disabled={optimizing || backendConnected === false}
              onClick={() => runOptimization()}
              className="px-5 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs tracking-wide shadow-lg shadow-emerald-500/20 transition cursor-pointer"
            >
              RUN DEMO WORKFLOW NOW
            </button>
          </div>
        )}

        {/* SECTION 3 & 10: ENVIRONMENT & REGIONAL CARBON INTENSITY */}
        <div className="pt-4 border-t border-slate-800/80">
          <EnvironmentView environment={environment} loading={loadingEnv} />
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950/60 py-4 mt-8">
        <div className="max-w-7xl mx-auto px-4 text-center text-xs text-slate-500">
          Carbon- and Latency-Aware Agent Workflow Scheduler • HackDays at MSRIT • Person 4 Dashboard
        </div>
      </footer>
    </div>
  );
};

export default App;
