import React from 'react';
import { Server, MapPin, Clock, Award, DollarSign, Zap, Leaf, CheckCircle2, Sparkles } from 'lucide-react';
import type { ScheduledStep } from '../types';

interface DecisionStepsProps {
  steps: ScheduledStep[];
  activeScenarioName?: string | null;
  lastUpdatedTimestamp?: string | null;
}

export const DecisionSteps: React.FC<DecisionStepsProps> = ({
  steps,
  activeScenarioName,
  lastUpdatedTimestamp,
}) => {
  if (!steps || steps.length === 0) {
    return null;
  }

  return (
    <div className="bg-slate-900/70 border border-slate-800/90 rounded-2xl p-5 shadow-xl backdrop-blur-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-4 border-b border-slate-800/80 gap-2">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="h-4 w-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-semibold text-white tracking-tight m-0">
                Optimal Task Assignment & Execution Schedule
              </h2>
              {activeScenarioName && (
                <span className="text-[10px] font-bold font-mono px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                  {activeScenarioName} Mode
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 m-0">
              Dispatched model tier, cloud region destination, and temporal delay offset per task
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono self-start sm:self-auto">
          {lastUpdatedTimestamp && (
            <span className="text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 px-2 py-0.5 rounded-md flex items-center gap-1">
              <Sparkles className="h-3 w-3" />
              Updated {lastUpdatedTimestamp}
            </span>
          )}
          <span className="text-slate-300 bg-slate-800/80 border border-slate-700 px-2.5 py-0.5 rounded-md">
            {steps.length} {steps.length === 1 ? 'Step' : 'Steps'}
          </span>
        </div>
      </div>

      <div className="space-y-4">
        {steps.map((step, idx) => {
          return (
            <div
              key={`${step.step_id}-${step.selected_model}-${step.selected_region}`}
              className="bg-slate-950/80 border border-slate-800 rounded-xl p-4.5 hover:border-slate-700 transition-all duration-300 shadow-sm"
            >
              {/* Header: Step ID, Badges */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 pb-3 border-b border-slate-800/70">
                <div className="flex items-center space-x-2.5">
                  <span className="h-6 w-6 rounded-md bg-slate-800 text-slate-300 font-mono text-xs flex items-center justify-center font-bold">
                    #{idx + 1}
                  </span>
                  <span className="font-mono text-sm font-bold text-white">
                    {step.step_id}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-[11px] text-slate-400 flex items-center gap-1 bg-slate-900 border border-slate-800 px-2 py-0.5 rounded">
                    Pareto Score:
                    <strong className="font-mono text-emerald-400 font-bold">{step.score.toFixed(4)}</strong>
                  </span>
                </div>
              </div>

              {/* SECTION 5: Prominent Selected Model, Region, and Offset */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 my-3">
                <div className="bg-gradient-to-r from-cyan-950/40 via-cyan-950/20 to-slate-900/60 border-2 border-cyan-500/40 rounded-xl p-3.5 flex items-center space-x-3 shadow-md shadow-cyan-950/20">
                  <div className="p-2.5 rounded-lg bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
                    <Server className="h-5 w-5" />
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-bold text-cyan-400 tracking-wider block">
                      Assigned Model Tier
                    </span>
                    <span className="font-mono text-base font-extrabold text-white tracking-tight">
                      {step.selected_model}
                    </span>
                  </div>
                </div>

                <div className="bg-gradient-to-r from-emerald-950/40 via-emerald-950/20 to-slate-900/60 border-2 border-emerald-500/40 rounded-xl p-3.5 flex items-center space-x-3 shadow-md shadow-emerald-950/20">
                  <div className="p-2.5 rounded-lg bg-emerald-500/10 text-emerald-300 border border-emerald-500/30">
                    <MapPin className="h-5 w-5" />
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-bold text-emerald-400 tracking-wider block">
                      Target Cloud Region
                    </span>
                    <span className="font-mono text-base font-extrabold text-white tracking-tight">
                      {step.selected_region}
                    </span>
                  </div>
                </div>

                <div className="bg-gradient-to-r from-purple-950/40 via-purple-950/20 to-slate-900/60 border-2 border-purple-500/40 rounded-xl p-3.5 flex items-center space-x-3 shadow-md shadow-purple-950/20">
                  <div className="p-2.5 rounded-lg bg-purple-500/10 text-purple-300 border border-purple-500/30">
                    <Clock className="h-5 w-5" />
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-bold text-purple-400 tracking-wider block">
                      Execution Window Offset
                    </span>
                    <span className="font-mono text-base font-extrabold text-white tracking-tight">
                      {step.scheduled_offset_seconds === 0 ? 'Immediate (+0s)' : `+${step.scheduled_offset_seconds}s Window`}
                    </span>
                  </div>
                </div>
              </div>

              {/* Metrics row */}
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 bg-slate-900/90 p-3 rounded-lg border border-slate-800 text-xs">
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase flex items-center gap-1">
                    <Clock className="h-3 w-3 text-cyan-400" /> Latency
                  </span>
                  <span className="font-mono text-slate-100 font-bold text-sm">
                    {step.estimated_latency_ms.toFixed(1)} ms
                  </span>
                </div>

                <div>
                  <span className="text-slate-400 block text-[10px] uppercase flex items-center gap-1">
                    <Award className="h-3 w-3 text-purple-400" /> Accuracy
                  </span>
                  <span className="font-mono text-purple-300 font-bold text-sm">
                    {(step.estimated_accuracy * 100).toFixed(1)}%
                  </span>
                </div>

                <div>
                  <span className="text-slate-400 block text-[10px] uppercase flex items-center gap-1">
                    <DollarSign className="h-3 w-3 text-amber-400" /> Cost
                  </span>
                  <span className="font-mono text-amber-300 font-bold text-sm">
                    ${step.estimated_cost.toFixed(6)}
                  </span>
                </div>

                <div>
                  <span className="text-slate-400 block text-[10px] uppercase flex items-center gap-1">
                    <Zap className="h-3 w-3 text-blue-400" /> Energy
                  </span>
                  <span className="font-mono text-blue-300 font-bold text-sm">
                    {step.estimated_energy_wh.toFixed(4)} Wh
                  </span>
                </div>

                <div>
                  <span className="text-slate-400 block text-[10px] uppercase flex items-center gap-1">
                    <Leaf className="h-3 w-3 text-emerald-400" /> Carbon
                  </span>
                  <span className="font-mono text-emerald-300 font-bold text-sm">
                    {step.estimated_carbon_g.toFixed(5)} g
                  </span>
                </div>
              </div>

              {/* Explanation / Reason */}
              <div className="mt-3 text-xs bg-slate-900/60 border border-slate-800 rounded-lg p-3 text-slate-300 leading-relaxed">
                <span className="font-semibold text-emerald-400 mr-1.5 font-mono text-[11px] uppercase">
                  Optimizer Rationale:
                </span>
                {step.reason}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
