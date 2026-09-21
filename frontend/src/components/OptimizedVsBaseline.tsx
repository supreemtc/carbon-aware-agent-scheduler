import React from 'react';
import { Scale, TrendingDown, Leaf, DollarSign, Zap } from 'lucide-react';
import type { CompareResponse } from '../types';

interface OptimizedVsBaselineProps {
  comparisonData: CompareResponse;
}

export const OptimizedVsBaseline: React.FC<OptimizedVsBaselineProps> = ({ comparisonData }) => {
  const { optimized_plan, baseline_plan, comparison } = comparisonData;

  const metrics = [
    {
      name: 'Carbon Emissions',
      unit: 'g CO₂eq',
      optimized: optimized_plan.total_estimated_carbon_g,
      baseline: baseline_plan.total_estimated_carbon_g,
      savingsPct: comparison.carbon_savings_pct,
      delta: comparison.carbon_delta_g,
      color: 'text-emerald-400',
      barColor: 'bg-emerald-500',
      icon: Leaf,
      format: (v: number) => v.toFixed(5),
    },
    {
      name: 'Monetary Cost',
      unit: 'USD ($)',
      optimized: optimized_plan.total_estimated_cost,
      baseline: baseline_plan.total_estimated_cost,
      savingsPct: comparison.cost_savings_pct,
      delta: comparison.cost_delta,
      color: 'text-amber-400',
      barColor: 'bg-amber-500',
      icon: DollarSign,
      format: (v: number) => `$${v.toFixed(6)}`,
    },
    {
      name: 'Energy Consumption',
      unit: 'Watt-hours (Wh)',
      optimized: optimized_plan.total_estimated_energy_wh,
      baseline: baseline_plan.total_estimated_energy_wh,
      savingsPct: comparison.energy_savings_pct,
      delta: comparison.energy_delta_wh,
      color: 'text-blue-400',
      barColor: 'bg-blue-500',
      icon: Zap,
      format: (v: number) => `${v.toFixed(4)} Wh`,
    },
  ];

  return (
    <div className="bg-slate-900/70 border border-slate-800/90 rounded-2xl p-5 shadow-xl backdrop-blur-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-5 border-b border-slate-800/80 gap-2">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-lg bg-teal-500/10 text-teal-400 border border-teal-500/20">
            <Scale className="h-4 w-4" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-white tracking-tight m-0">
              Multi-Objective Trade-Off: Optimized vs Baseline
            </h2>
            <p className="text-xs text-slate-400 m-0">
              Benchmark comparison against standard highest-accuracy greedy baseline (gemini-1.5-pro / local immediate execution)
            </p>
          </div>
        </div>

        <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 px-3 py-1 rounded-full self-start sm:self-auto">
          {comparison.carbon_savings_pct.toFixed(1)}% Carbon Reduction
        </span>
      </div>

      {/* Comparison Table */}
      <div className="overflow-x-auto mb-6">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-mono">
              <th className="py-2.5 px-3">Metric Dimension</th>
              <th className="py-2.5 px-3 text-emerald-400 bg-emerald-950/20 rounded-t-lg">
                ★ Scheduler Optimized
              </th>
              <th className="py-2.5 px-3 text-slate-400 bg-slate-800/40 rounded-t-lg">
                Greedy Feasible Baseline
              </th>
              <th className="py-2.5 px-3 text-right">Net Savings</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {metrics.map((m) => {
              const Icon = m.icon;
              return (
                <tr key={m.name} className="hover:bg-slate-800/30 transition">
                  <td className="py-3 px-3 font-sans font-medium text-slate-200 flex items-center gap-2">
                    <Icon className={`h-4 w-4 ${m.color}`} />
                    <span>{m.name}</span>
                  </td>
                  <td className="py-3 px-3 font-bold text-white bg-emerald-950/10">
                    {m.format(m.optimized)}
                  </td>
                  <td className="py-3 px-3 text-slate-400 bg-slate-800/20">
                    {m.format(m.baseline)}
                  </td>
                  <td className="py-3 px-3 text-right">
                    <span className="inline-flex items-center gap-1 font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                      <TrendingDown className="h-3 w-3" />
                      -{m.savingsPct.toFixed(1)}%
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Visual Relative Savings Comparison Bars */}
      <div className="space-y-4 pt-2 border-t border-slate-800/80">
        <h3 className="text-xs uppercase font-bold tracking-wider text-slate-400 mb-3">
          Relative Footprint Comparison
        </h3>

        {metrics.map((m) => {
          const optPct = m.baseline > 0 ? Math.min(100, Math.max(2, (m.optimized / m.baseline) * 100)) : 100;

          return (
            <div key={m.name} className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3">
              <div className="flex justify-between text-xs mb-1.5">
                <span className="text-slate-300 font-medium">{m.name}</span>
                <span className="font-mono text-emerald-400 font-bold">
                  {m.savingsPct.toFixed(1)}% Less Footprint
                </span>
              </div>

              <div className="space-y-1.5">
                <div className="flex items-center gap-2 text-[11px]">
                  <span className="w-18 text-emerald-400 font-mono text-[10px] uppercase">Optimized:</span>
                  <div className="flex-1 bg-slate-900 h-3 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${m.barColor} transition-all duration-500`}
                      style={{ width: `${optPct}%` }}
                    ></div>
                  </div>
                  <span className="w-24 text-right font-mono text-white text-[11px]">
                    {m.format(m.optimized)}
                  </span>
                </div>

                <div className="flex items-center gap-2 text-[11px]">
                  <span className="w-18 text-slate-500 font-mono text-[10px] uppercase">Baseline:</span>
                  <div className="flex-1 bg-slate-900 h-3 rounded-full overflow-hidden">
                    <div className="h-full bg-slate-600 rounded-full w-full"></div>
                  </div>
                  <span className="w-24 text-right font-mono text-slate-400 text-[11px]">
                    {m.format(m.baseline)}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Step Assignments: Optimized vs Baseline Breakdown */}
      <div className="mt-6 pt-4 border-t border-slate-800/80">
        <h3 className="text-xs uppercase font-bold tracking-wider text-slate-400 mb-3">
          Step Model & Regional Routing Comparison
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {optimized_plan.scheduled_steps.map((optStep, idx) => {
            const baseStep = baseline_plan.scheduled_steps[idx];
            return (
              <div
                key={optStep.step_id}
                className="bg-slate-950/70 border border-slate-800 rounded-xl p-3.5 text-xs"
              >
                <div className="font-mono font-bold text-white mb-2 pb-1.5 border-b border-slate-800/80 flex items-center justify-between">
                  <span>{optStep.step_id}</span>
                  <span className="text-[10px] text-slate-400 font-normal">
                    Step {idx + 1}
                  </span>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between p-2 rounded bg-emerald-950/20 border border-emerald-500/20">
                    <div>
                      <span className="text-[10px] uppercase text-emerald-400 font-bold block">Optimized Schedule</span>
                      <span className="font-mono text-slate-100 font-bold">{optStep.selected_model}</span>
                      <span className="text-slate-400 text-[11px] block">
                        📍 {optStep.selected_region} ({optStep.scheduled_offset_seconds === 0 ? '0s offset' : `+${optStep.scheduled_offset_seconds}s offset`})
                      </span>
                    </div>
                    <span className="font-mono text-emerald-400 font-semibold">
                      {optStep.estimated_latency_ms} ms
                    </span>
                  </div>

                  {baseStep && (
                    <div className="flex items-center justify-between p-2 rounded bg-slate-900/60 border border-slate-800/80">
                      <div>
                        <span className="text-[10px] uppercase text-slate-400 font-bold block">Greedy Baseline</span>
                        <span className="font-mono text-slate-300 font-semibold">{baseStep.selected_model}</span>
                        <span className="text-slate-400 text-[11px] block">
                          📍 {baseStep.selected_region} (+0s immediate)
                        </span>
                      </div>
                      <span className="font-mono text-slate-400">
                        {baseStep.estimated_latency_ms} ms
                      </span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
