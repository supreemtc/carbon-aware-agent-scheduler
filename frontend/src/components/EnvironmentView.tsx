import React from 'react';
import { Globe, Cpu, Clock } from 'lucide-react';
import type { EnvironmentResponse } from '../types';

interface EnvironmentViewProps {
  environment: EnvironmentResponse | null;
  loading: boolean;
}

export const EnvironmentView: React.FC<EnvironmentViewProps> = ({ environment, loading }) => {
  if (loading) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-6 animate-pulse">
        <div className="h-6 w-48 bg-slate-800 rounded mb-4"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-28 bg-slate-800/60 rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  if (!environment) {
    return null;
  }

  const getCarbonBadge = (gco2: number) => {
    if (gco2 <= 50) {
      return {
        label: 'Ultra Clean Grid',
        color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
        barColor: 'bg-emerald-500',
      };
    }
    if (gco2 <= 200) {
      return {
        label: 'Moderate Carbon',
        color: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30',
        barColor: 'bg-cyan-500',
      };
    }
    if (gco2 <= 400) {
      return {
        label: 'Medium Grid',
        color: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
        barColor: 'bg-amber-500',
      };
    }
    return {
      label: 'High Carbon Grid',
      color: 'text-rose-400 bg-rose-500/10 border-rose-500/30',
      barColor: 'bg-rose-500',
    };
  };

  return (
    <div className="space-y-6">
      {/* SECTION 10 & 3: Regional Carbon Grid Visualization */}
      <div className="bg-slate-900/70 border border-slate-800/90 rounded-2xl p-5 shadow-xl backdrop-blur-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-4 border-b border-slate-800/80 gap-2">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Globe className="h-4 w-4" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-white tracking-tight m-0">
                Simulated Compute Regions & Carbon Intensity
              </h2>
              <p className="text-xs text-slate-400 m-0">
                Live grid emission factors (gCO₂eq/kWh) and network ping latencies
              </p>
            </div>
          </div>
          <span className="text-xs font-mono text-slate-400 bg-slate-800/80 px-2.5 py-1 rounded-md border border-slate-700/60 self-start sm:self-auto">
            {environment.available_regions.length} Active Regions
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
          {environment.available_regions.map((region) => {
            const badge = getCarbonBadge(region.carbon_intensity_gco2_kwh);
            const windows = environment.execution_windows[region.region_id] || [];
            const pct = Math.min(100, Math.round((region.carbon_intensity_gco2_kwh / 600) * 100));

            return (
              <div
                key={region.region_id}
                className="bg-slate-950/70 border border-slate-800/80 hover:border-slate-700/90 rounded-xl p-4 transition-all duration-200 hover:shadow-lg hover:shadow-emerald-950/20 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span className="font-mono text-xs font-semibold text-white truncate" title={region.region_id}>
                      {region.region_id}
                    </span>
                    <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full border ${badge.color}`}>
                      {badge.label}
                    </span>
                  </div>

                  <p className="text-[11px] text-slate-400 leading-snug line-clamp-2 min-h-[30px] mb-3" title={region.region_name}>
                    {region.region_name}
                  </p>

                  <div className="space-y-2">
                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-slate-400">Carbon Intensity:</span>
                        <span className="font-mono font-bold text-white">
                          {region.carbon_intensity_gco2_kwh}{' '}
                          <span className="text-[10px] font-normal text-slate-400">gCO₂/kWh</span>
                        </span>
                      </div>
                      <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${badge.barColor}`}
                          style={{ width: `${pct}%` }}
                        ></div>
                      </div>
                    </div>

                    <div className="flex justify-between text-xs pt-1">
                      <span className="text-slate-400">Base Ping:</span>
                      <span className="font-mono text-slate-200 font-medium">
                        {region.base_latency_ms} ms
                      </span>
                    </div>
                  </div>
                </div>

                {windows.length > 0 && (
                  <div className="mt-3 pt-2.5 border-t border-slate-800/60 flex items-center justify-between text-[11px] text-slate-400">
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3 text-emerald-400" />
                      Shift Windows:
                    </span>
                    <span className="font-mono text-emerald-300 font-medium">
                      +{windows[windows.length - 1].scheduled_offset_seconds}s ({Math.round((1 - windows[windows.length - 1].carbon_multiplier) * 100)}% cleaner)
                    </span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* SECTION 3: Available LLM Profiles */}
      <div className="bg-slate-900/70 border border-slate-800/90 rounded-2xl p-5 shadow-xl backdrop-blur-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-4 border-b border-slate-800/80 gap-2">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              <Cpu className="h-4 w-4" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-white tracking-tight m-0">
                Simulated AI Model Profiles
              </h2>
              <p className="text-xs text-slate-400 m-0">
                Cost, energy (Wh), latency, and accuracy benchmarks across candidate model tiers
              </p>
            </div>
          </div>
          <span className="text-xs font-mono text-slate-400 bg-slate-800/80 px-2.5 py-1 rounded-md border border-slate-700/60 self-start sm:self-auto">
            {environment.available_models.length} Model Profiles
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {environment.available_models.map((model) => (
            <div
              key={model.model_id}
              className="bg-slate-950/70 border border-slate-800/80 hover:border-cyan-500/40 rounded-xl p-4 transition-all duration-200 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-mono text-sm font-bold text-cyan-300">
                    {model.model_id}
                  </span>
                  <span className="text-xs font-semibold px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
                    {(model.accuracy_score * 100).toFixed(0)}% Acc
                  </span>
                </div>
                <p className="text-xs text-slate-400 mb-3 line-clamp-1" title={model.model_name}>
                  {model.model_name}
                </p>

                <div className="grid grid-cols-2 gap-2 text-xs bg-slate-900/80 p-2.5 rounded-lg border border-slate-800/60 mb-2">
                  <div>
                    <span className="text-slate-500 block text-[10px] uppercase">Avg Latency</span>
                    <span className="font-mono text-slate-200 font-medium">
                      {model.average_latency_ms} ms
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px] uppercase">Context Win</span>
                    <span className="font-mono text-slate-200 font-medium">
                      {(model.context_window / 1000).toFixed(0)}k tokens
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px] uppercase">Cost / 1k</span>
                    <span className="font-mono text-emerald-400 font-medium">
                      ${model.cost_per_1k_tokens.toFixed(6)}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-500 block text-[10px] uppercase">Energy / 1k</span>
                    <span className="font-mono text-amber-300 font-medium">
                      {model.energy_wh_per_1k_tokens} Wh
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
