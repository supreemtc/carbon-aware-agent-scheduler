import React from 'react';
import { RefreshCw, Leaf } from 'lucide-react';

interface HeaderProps {
  backendConnected: boolean | null;
  checkingHealth: boolean;
  onRefreshHealth: () => void;
  backendUrl: string;
}

export const Header: React.FC<HeaderProps> = ({
  backendConnected,
  checkingHealth,
  onRefreshHealth,
  backendUrl,
}) => {
  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div className="flex items-center space-x-3.5">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-emerald-400 via-teal-500 to-cyan-600 flex items-center justify-center shadow-lg shadow-emerald-500/20 ring-1 ring-emerald-400/30">
            <Leaf className="h-5 w-5 text-slate-950 font-bold" />
          </div>
          <div>
            <div className="flex items-center space-x-2.5">
              <h1 className="text-xl font-bold tracking-tight text-white m-0">
                Carbon-Aware Workflow Scheduler
              </h1>
              <span className="px-2 py-0.5 text-xs font-semibold uppercase tracking-wider bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded-md">
                Production Engine
              </span>
            </div>
            <p className="text-xs text-slate-400 m-0 flex items-center gap-1.5 font-medium">
              <span className="text-emerald-400 font-semibold">A2</span>
              <span className="text-slate-600">•</span>
              <span>Intelligent Agent Workflow Optimization</span>
              <span className="text-slate-600">•</span>
              <span className="text-slate-500 font-mono text-[11px]">{backendUrl}</span>
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3 self-end sm:self-auto">
          <div
            className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg border text-xs font-medium transition-all ${
              backendConnected === true
                ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300'
                : backendConnected === false
                ? 'bg-rose-950/40 border-rose-500/40 text-rose-300'
                : 'bg-slate-800/60 border-slate-700 text-slate-400'
            }`}
          >
            <span className="relative flex h-2 w-2">
              {backendConnected === true && (
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              )}
              <span
                className={`relative inline-flex rounded-full h-2 w-2 ${
                  backendConnected === true
                    ? 'bg-emerald-400'
                    : backendConnected === false
                    ? 'bg-rose-400'
                    : 'bg-amber-400'
                }`}
              ></span>
            </span>
            <span>
              Backend: {backendConnected === true ? 'Connected' : backendConnected === false ? 'Offline' : 'Checking...'}
            </span>
          </div>

          <button
            onClick={onRefreshHealth}
            disabled={checkingHealth}
            title="Recheck backend health"
            className="p-1.5 rounded-lg border border-slate-700 hover:border-slate-600 bg-slate-800/80 hover:bg-slate-700/80 text-slate-300 hover:text-white transition disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${checkingHealth ? 'animate-spin text-emerald-400' : ''}`} />
          </button>
        </div>
      </div>
    </header>
  );
};
