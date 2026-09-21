import React from 'react';
import { Brain } from 'lucide-react';
import type { ScheduledStep } from '../types';

interface ExplanationCardProps {
  summary: string;
  steps: ScheduledStep[];
}

export const ExplanationCard: React.FC<ExplanationCardProps> = ({ summary, steps }) => {
  if (!summary && (!steps || steps.length === 0)) {
    return null;
  }

  return (
    <div className="bg-slate-900/70 border border-slate-800/90 rounded-2xl p-5 shadow-xl backdrop-blur-sm">
      <div className="flex items-center space-x-2.5 pb-4 mb-4 border-b border-slate-800/80">
        <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          <Brain className="h-4 w-4" />
        </div>
        <div>
          {/* SECTION 8: Label strictly: Why did the scheduler choose this? */}
          <h2 className="text-base font-semibold text-white tracking-tight m-0">
            Why did the scheduler choose this?
          </h2>
          <p className="text-xs text-slate-400 m-0">
            Algorithmic explanation directly from backend multi-objective utility scoring
          </p>
        </div>
      </div>

      {summary && (
        <div className="bg-slate-950/80 border border-emerald-500/20 rounded-xl p-4 mb-4">
          <span className="text-[10px] font-mono uppercase font-bold text-emerald-400 tracking-wider block mb-1">
            Global Execution Summary
          </span>
          <p className="text-sm font-medium text-slate-200 leading-relaxed m-0">
            {summary}
          </p>
        </div>
      )}

      <div className="space-y-3">
        <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
          Per-Task Decision Log
        </span>
        {steps.map((step, idx) => (
          <div
            key={step.step_id || idx}
            className="bg-slate-950/60 border border-slate-800/70 rounded-lg p-3.5 text-xs"
          >
            <div className="flex items-center gap-2 mb-1.5">
              <span className="font-mono font-bold text-emerald-400">
                {step.step_id}:
              </span>
              <span className="text-[11px] font-mono px-1.5 py-0.5 rounded bg-slate-900 text-slate-400 border border-slate-800">
                score = {step.score.toFixed(6)}
              </span>
            </div>
            <p className="text-slate-300 leading-relaxed font-sans m-0">
              {step.reason}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};
