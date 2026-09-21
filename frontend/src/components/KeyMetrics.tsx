import React from 'react';
import { Leaf, DollarSign, Zap, TrendingDown, ArrowDownRight } from 'lucide-react';
import type { CompareComparison, ExecutionPlan } from '../types';

interface KeyMetricsProps {
  plan: ExecutionPlan;
  comparison?: CompareComparison;
}

export const KeyMetrics: React.FC<KeyMetricsProps> = ({ plan, comparison }) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-base font-semibold text-white tracking-tight m-0 flex items-center gap-2">
          <span>Aggregate Workflow Footprint & Benchmark Savings</span>
          {comparison && (
            <span className="text-xs font-normal text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/30">
              Verified by /compare API
            </span>
          )}
        </h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* CARBON CARD */}
        <div className="bg-gradient-to-br from-slate-900/90 to-emerald-950/20 border border-emerald-500/30 rounded-2xl p-5 shadow-xl relative overflow-hidden">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Leaf className="h-4 w-4 text-emerald-400" />
              Total Carbon Emissions
            </span>
            {comparison && (
              <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 px-2 py-0.5 rounded-full flex items-center gap-1">
                <TrendingDown className="h-3.5 w-3.5" />
                {comparison.carbon_savings_pct.toFixed(1)}% Saved
              </span>
            )}
          </div>

          <div className="flex items-baseline space-x-2 my-2">
            <span className="text-3xl font-extrabold font-mono text-white tracking-tight">
              {plan.total_estimated_carbon_g.toFixed(5)}
            </span>
            <span className="text-sm font-medium text-slate-400 font-mono">g CO₂eq</span>
          </div>

          {comparison && (
            <div className="pt-3 border-t border-slate-800/80 text-xs flex items-center justify-between text-slate-400">
              <span>Baseline Reduction:</span>
              <span className="font-mono text-emerald-300 font-semibold flex items-center">
                <ArrowDownRight className="h-3 w-3 mr-0.5" />
                -{comparison.carbon_delta_g.toFixed(5)} g CO₂
              </span>
            </div>
          )}
        </div>

        {/* COST CARD */}
        <div className="bg-gradient-to-br from-slate-900/90 to-amber-950/20 border border-amber-500/30 rounded-2xl p-5 shadow-xl relative overflow-hidden">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <DollarSign className="h-4 w-4 text-amber-400" />
              Total Monetary Cost
            </span>
            {comparison && (
              <span className="text-xs font-bold text-amber-400 bg-amber-500/10 border border-amber-500/30 px-2 py-0.5 rounded-full flex items-center gap-1">
                <TrendingDown className="h-3.5 w-3.5" />
                {comparison.cost_savings_pct.toFixed(1)}% Saved
              </span>
            )}
          </div>

          <div className="flex items-baseline space-x-1.5 my-2">
            <span className="text-3xl font-extrabold font-mono text-white tracking-tight">
              ${plan.total_estimated_cost.toFixed(6)}
            </span>
            <span className="text-sm font-medium text-slate-400 font-mono">USD</span>
          </div>

          {comparison && (
            <div className="pt-3 border-t border-slate-800/80 text-xs flex items-center justify-between text-slate-400">
              <span>Dollar Savings:</span>
              <span className="font-mono text-amber-300 font-semibold flex items-center">
                <ArrowDownRight className="h-3 w-3 mr-0.5" />
                -${comparison.cost_delta.toFixed(6)}
              </span>
            </div>
          )}
        </div>

        {/* ENERGY CARD */}
        <div className="bg-gradient-to-br from-slate-900/90 to-blue-950/20 border border-blue-500/30 rounded-2xl p-5 shadow-xl relative overflow-hidden">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Zap className="h-4 w-4 text-blue-400" />
              Total Energy Consumption
            </span>
            {comparison && (
              <span className="text-xs font-bold text-blue-400 bg-blue-500/10 border border-blue-500/30 px-2 py-0.5 rounded-full flex items-center gap-1">
                <TrendingDown className="h-3.5 w-3.5" />
                {comparison.energy_savings_pct.toFixed(1)}% Saved
              </span>
            )}
          </div>

          <div className="flex items-baseline space-x-2 my-2">
            <span className="text-3xl font-extrabold font-mono text-white tracking-tight">
              {plan.total_estimated_energy_wh.toFixed(4)}
            </span>
            <span className="text-sm font-medium text-slate-400 font-mono">Watt-hours (Wh)</span>
          </div>

          {comparison && (
            <div className="pt-3 border-t border-slate-800/80 text-xs flex items-center justify-between text-slate-400">
              <span>Compute Energy Delta:</span>
              <span className="font-mono text-blue-300 font-semibold flex items-center">
                <ArrowDownRight className="h-3 w-3 mr-0.5" />
                -{comparison.energy_delta_wh.toFixed(4)} Wh
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
