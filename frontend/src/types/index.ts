export interface WorkflowTask {
  step_id: string;
  task_type: string;
  description: string;
  input_text: string;
  estimated_tokens: number;
  minimum_accuracy: number;
  deadline_seconds: number;
  delay_tolerance_seconds: number;
  priority: string;
}

export interface WorkflowRequest {
  workflow_id: string;
  tasks: WorkflowTask[];
  accuracy_importance: number;
  latency_importance: number;
  cost_importance: number;
  carbon_importance: number;
  energy_importance: number;
}

export interface ModelProfile {
  model_id: string;
  model_name: string;
  accuracy_score: number;
  average_latency_ms: number;
  cost_per_1k_tokens: number;
  energy_wh_per_1k_tokens: number;
  context_window: number;
}

export interface RegionProfile {
  region_id: string;
  region_name: string;
  base_latency_ms: number;
  carbon_intensity_gco2_kwh: number;
}

export interface ExecutionWindow {
  window_id: string;
  scheduled_offset_seconds: number;
  carbon_multiplier: number;
}

export interface EnvironmentResponse {
  available_models: ModelProfile[];
  available_regions: RegionProfile[];
  execution_windows: Record<string, ExecutionWindow[]>;
}

export interface ScheduledStep {
  step_id: string;
  selected_model: string;
  selected_region: string;
  scheduled_offset_seconds: number;
  estimated_latency_ms: number;
  estimated_accuracy: number;
  estimated_cost: number;
  estimated_energy_wh: number;
  estimated_carbon_g: number;
  score: number;
  reason: string;
}

export interface ExecutionPlan {
  workflow_id: string;
  total_estimated_cost: number;
  total_estimated_energy_wh: number;
  total_estimated_carbon_g: number;
  scheduled_steps: ScheduledStep[];
}

export interface CompareComparison {
  cost_savings_pct: number;
  energy_savings_pct: number;
  carbon_savings_pct: number;
  cost_delta: number;
  energy_delta_wh: number;
  carbon_delta_g: number;
}

export interface CompareResponse {
  workflow_id: string;
  optimized_plan: ExecutionPlan;
  baseline_plan: ExecutionPlan;
  comparison: CompareComparison;
  summary: string;
}

export type PresetType = 'GREEN' | 'LOW_LATENCY' | 'COST_SAVER' | 'HIGH_ACCURACY';

export interface OptimizationWeights {
  accuracy: number;
  latency: number;
  cost: number;
  carbon: number;
  energy: number;
}
