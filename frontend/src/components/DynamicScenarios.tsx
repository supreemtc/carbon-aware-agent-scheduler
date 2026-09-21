import React from 'react';
import { Play, ArrowRight, RefreshCw, Compass, CheckCircle2, Sparkles } from 'lucide-react';
import type { PresetType } from '../types';

interface DynamicScenariosProps {
  onRunScenario: (preset: PresetType) => void;
  activeScenario: PresetType | null;
  loading: boolean;
  lastUpdatedTimestamp?: string | null;
}

export const DynamicScenarios: React.FC<DynamicScenariosProps> = ({
  onRunScenario,
  activeScenario,
  loading,
  lastUpdatedTimestamp,
}) => {
  const scenarios = [
    {
      id: 'GREEN' as PresetType,
      title: 'Green Priority',
      tagline: 'Route to clean hydro/wind grid (Montreal) with +60s carbon shifting',
      icon: '🌿',
      badge: 'Min Carbon',
      color: 'border-emerald-500/40 bg-emerald-950/20 hover:border-emerald-400 hover:bg-emerald-900/30 text-emerald-300',
      activeColor: 'ring-2 ring-emerald-400 border-emerald-400 bg-emerald-900/40 text-emerald-100 shadow-lg shadow-emerald-500/20',
      expected: 'Routes to northamerica-northeast1 (28 gCO₂/kWh) • ~0.0018g Carbon',
    },
    {
      id: 'LOW_LATENCY' as PresetType,
      title: 'Low Latency',
      tagline: 'Route to local Mumbai hub (25ms ping) for fast response',
      icon: '⚡',
      badge: 'Min Latency',
      color: 'border-cyan-500/40 bg-cyan-950/20 hover:border-cyan-400 hover:bg-cyan-900/30 text-cyan-300',
      activeColor: 'ring-2 ring-cyan-400 border-cyan-400 bg-cyan-900/40 text-cyan-100 shadow-lg shadow-cyan-500/20',
      expected: 'Routes to asia-south1 (25ms ping) • 375ms execution',
    },
    {
      id: 'COST_SAVER' as PresetType,
      title: 'Cost Saver',
      tagline: 'Assign economical Flash-8B tier to reduce dollar spend',
      icon: '💰',
      badge: 'Min Cost',
      color: 'border-amber-500/40 bg-amber-950/20 hover:border-amber-400 hover:bg-amber-900/30 text-amber-300',
      activeColor: 'ring-2 ring-amber-400 border-amber-400 bg-amber-900/40 text-amber-100 shadow-lg shadow-amber-500/20',
      expected: 'Selects gemini-1.5-flash-8b tier • $0.000112 spend',
    },
    {
      id: 'HIGH_ACCURACY' as PresetType,
      title: 'High Accuracy',
      tagline: 'Enforce top benchmark Gemini 1.5 Pro reasoning models',
      icon: '🎯',
      badge: 'Max Quality',
      color: 'border-purple-500/40 bg-purple-950/20 hover:border-purple-400 hover:bg-purple-900/30 text-purple-300',
      activeColor: 'ring-2 ring-purple-400 border-purple-400 bg-purple-900/40 text-purple-100 shadow-lg shadow-purple-500/20',
      expected: 'Selects gemini-1.5-pro tier • 92% benchmark accuracy',
    },
  ];

  const activeObj = scenarios.find((s) => s.id === activeScenario);

  return (
    <div className="bg-gradient-to-r from-slate-900/90 via-slate-900/95 to-slate-900/90 border border-slate-700/80 rounded-2xl p-5 shadow-2xl backdrop-blur-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3.5 mb-4 border-b border-slate-800 gap-2">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            <Compass className="h-4 w-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-semibold text-white tracking-tight m-0">
                Dynamic Scenario Demonstration
              </h2>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center gap-1">
                <Sparkles className="h-3 w-3" />
                Live Reactive Scheduler
              </span>
            </div>
            <p className="text-xs text-slate-400 m-0">
              Click any scenario to dispatch an instant live recalculation to the backend and watch assignments shift
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs text-slate-400 bg-slate-950/80 px-3 py-1.5 rounded-lg border border-slate-800">
          <span className="text-emerald-400 font-semibold">Live Demonstration:</span>
          <span>Priorities Change</span>
          <ArrowRight className="h-3 w-3 text-slate-600" />
          <span className="text-white font-medium">Model & Region Shift</span>
        </div>
      </div>

      {/* Dynamic Scenario Buttons */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        {scenarios.map((sc) => {
          const isActive = activeScenario === sc.id;
          return (
            <button
              key={sc.id}
              type="button"
              disabled={loading}
              onClick={() => onRunScenario(sc.id)}
              className={`p-3.5 rounded-xl border text-left transition-all duration-200 cursor-pointer flex flex-col justify-between group relative overflow-hidden ${
                isActive ? sc.activeColor : sc.color
              }`}
            >
              {isActive && (
                <div className="absolute top-0 right-0 bg-emerald-500 text-slate-950 text-[9px] font-bold px-2 py-0.5 rounded-bl uppercase font-mono tracking-wider">
                  Active
                </div>
              )}

              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-base">{sc.icon}</span>
                  <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded-full bg-slate-950/60 border border-slate-800 font-semibold text-slate-300">
                    {sc.badge}
                  </span>
                </div>
                <h3 className="text-xs font-bold text-white mb-1 group-hover:text-white transition">
                  {sc.title}
                </h3>
                <p className="text-[11px] text-slate-400 line-clamp-2 leading-snug mb-2">
                  {sc.tagline}
                </p>
                <div className="text-[10px] font-mono text-emerald-400/90 bg-slate-950/60 p-1.5 rounded border border-slate-800/80 leading-tight">
                  {sc.expected}
                </div>
              </div>

              <div className="mt-3 pt-2 border-t border-slate-800/60 flex items-center justify-between text-[11px] font-medium">
                <span className={isActive ? 'text-white font-semibold' : 'text-slate-400'}>
                  {isActive ? 'Applied & Active' : 'Run Scenario'}
                </span>
                <span className="flex items-center gap-1 group-hover:translate-x-0.5 transition-transform text-slate-300">
                  {loading && isActive ? (
                    <RefreshCw className="h-3 w-3 animate-spin text-emerald-400" />
                  ) : isActive ? (
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400" />
                  ) : (
                    <Play className="h-3 w-3 fill-current" />
                  )}
                </span>
              </div>
            </button>
          );
        })}
      </div>

      {/* Active Scenario Confirmation Indicator Banner */}
      {activeObj && lastUpdatedTimestamp && (
        <div className="mt-4 p-3 rounded-xl bg-slate-950/80 border border-emerald-500/40 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
          <div className="flex items-center space-x-2">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-ping"></span>
            <span className="font-semibold text-white">Scenario Applied:</span>
            <span className="font-bold text-emerald-400">{activeObj.title}</span>
            <span className="text-slate-400 font-mono">({activeObj.expected})</span>
          </div>
          <div className="flex items-center space-x-2 text-slate-400 self-end sm:self-auto font-mono text-[11px]">
            <span className="text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/30">
              DECISION UPDATED
            </span>
            <span>at {lastUpdatedTimestamp}</span>
          </div>
        </div>
      )}
    </div>
  );
};
