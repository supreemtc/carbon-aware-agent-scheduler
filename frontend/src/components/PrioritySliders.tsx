import React from 'react';
import { Sliders, Leaf, Zap, DollarSign, Clock, Target } from 'lucide-react';
import type { OptimizationWeights, PresetType } from '../types';

interface PrioritySlidersProps {
  weights: OptimizationWeights;
  onWeightsChange: (weights: OptimizationWeights) => void;
  onSelectPreset: (preset: PresetType) => void;
  activePreset: PresetType | null;
}

export const PrioritySliders: React.FC<PrioritySlidersProps> = ({
  weights,
  onWeightsChange,
  onSelectPreset,
  activePreset,
}) => {
  const handleSliderChange = (key: keyof OptimizationWeights, value: number) => {
    onWeightsChange({
      ...weights,
      [key]: value,
    });
  };

  const total = weights.accuracy + weights.latency + weights.cost + weights.carbon + weights.energy;
  const getNormalizedPct = (val: number) => {
    if (total <= 0) return 20;
    return Math.round((val / total) * 100);
  };

  const sliderConfig = [
    {
      key: 'carbon' as const,
      label: 'Carbon Footprint',
      desc: 'Prioritize low regional grid carbon intensity & clean hydro/nuclear hours',
      icon: Leaf,
      color: 'accent-emerald-500 text-emerald-400',
      bgColor: 'bg-emerald-500/10 border-emerald-500/30',
    },
    {
      key: 'latency' as const,
      label: 'Execution Latency',
      desc: 'Minimize inference & network ping latency to meet strict deadlines',
      icon: Clock,
      color: 'accent-cyan-500 text-cyan-400',
      bgColor: 'bg-cyan-500/10 border-cyan-500/30',
    },
    {
      key: 'cost' as const,
      label: 'Monetary Cost',
      desc: 'Optimize token execution pricing with lightweight models',
      icon: DollarSign,
      color: 'accent-amber-500 text-amber-400',
      bgColor: 'bg-amber-500/10 border-amber-500/30',
    },
    {
      key: 'accuracy' as const,
      label: 'Model Accuracy',
      desc: 'Target highest benchmark capability for complex reasoning tasks',
      icon: Target,
      color: 'accent-purple-500 text-purple-400',
      bgColor: 'bg-purple-500/10 border-purple-500/30',
    },
    {
      key: 'energy' as const,
      label: 'Energy Consumption',
      desc: 'Reduce Watt-hour (Wh) compute draw across cloud servers',
      icon: Zap,
      color: 'accent-blue-500 text-blue-400',
      bgColor: 'bg-blue-500/10 border-blue-500/30',
    },
  ];

  return (
    <div className="bg-slate-900/70 border border-slate-800/90 rounded-2xl p-5 shadow-xl backdrop-blur-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-4 border-b border-slate-800/80 gap-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-lg bg-teal-500/10 text-teal-400 border border-teal-500/20">
            <Sliders className="h-4 w-4" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-white tracking-tight m-0">
              Multi-Objective Optimization Priorities
            </h2>
            <p className="text-xs text-slate-400 m-0">
              Adjust weights to drive the deterministic Pareto scoring utility function
            </p>
          </div>
        </div>

        {/* SECTION 2 Presets */}
        <div className="flex flex-wrap items-center gap-1.5">
          <button
            type="button"
            onClick={() => onSelectPreset('GREEN')}
            className={`px-2.5 py-1 rounded-md text-xs font-semibold tracking-wide transition border cursor-pointer ${
              activePreset === 'GREEN'
                ? 'bg-emerald-500 text-slate-950 border-emerald-400 shadow-md shadow-emerald-500/20'
                : 'bg-slate-800/90 hover:bg-slate-700 text-emerald-400 border-slate-700'
            }`}
          >
            🌿 GREEN PRIORITY
          </button>
          <button
            type="button"
            onClick={() => onSelectPreset('LOW_LATENCY')}
            className={`px-2.5 py-1 rounded-md text-xs font-semibold tracking-wide transition border cursor-pointer ${
              activePreset === 'LOW_LATENCY'
                ? 'bg-cyan-500 text-slate-950 border-cyan-400 shadow-md shadow-cyan-500/20'
                : 'bg-slate-800/90 hover:bg-slate-700 text-cyan-400 border-slate-700'
            }`}
          >
            ⚡ LOW LATENCY
          </button>
          <button
            type="button"
            onClick={() => onSelectPreset('COST_SAVER')}
            className={`px-2.5 py-1 rounded-md text-xs font-semibold tracking-wide transition border cursor-pointer ${
              activePreset === 'COST_SAVER'
                ? 'bg-amber-500 text-slate-950 border-amber-400 shadow-md shadow-amber-500/20'
                : 'bg-slate-800/90 hover:bg-slate-700 text-amber-400 border-slate-700'
            }`}
          >
            💰 COST SAVER
          </button>
          <button
            type="button"
            onClick={() => onSelectPreset('HIGH_ACCURACY')}
            className={`px-2.5 py-1 rounded-md text-xs font-semibold tracking-wide transition border cursor-pointer ${
              activePreset === 'HIGH_ACCURACY'
                ? 'bg-purple-500 text-slate-950 border-purple-400 shadow-md shadow-purple-500/20'
                : 'bg-slate-800/90 hover:bg-slate-700 text-purple-400 border-slate-700'
            }`}
          >
            🎯 HIGH ACCURACY
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {sliderConfig.map(({ key, label, desc, icon: Icon, color, bgColor }) => {
          const value = weights[key];
          const pct = getNormalizedPct(value);

          return (
            <div
              key={key}
              className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-3.5 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center space-x-2">
                    <div className={`p-1.5 rounded-md border ${bgColor}`}>
                      <Icon className={`h-3.5 w-3.5 ${color.split(' ')[1]}`} />
                    </div>
                    <span className="text-xs font-semibold text-white">{label}</span>
                  </div>
                  <div className="flex items-center space-x-1.5">
                    <span className="text-xs font-mono font-bold text-white">
                      {value.toFixed(2)}
                    </span>
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                      {pct}%
                    </span>
                  </div>
                </div>
                <p className="text-[11px] text-slate-400 mb-2 leading-relaxed">{desc}</p>
              </div>

              <div>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.05"
                  value={value}
                  onChange={(e) => handleSliderChange(key, parseFloat(e.target.value))}
                  className={`w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer ${color}`}
                />
                <div className="flex justify-between text-[10px] text-slate-500 mt-1 font-mono">
                  <span>0.0 (Ignore)</span>
                  <span>1.0 (Critical)</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
