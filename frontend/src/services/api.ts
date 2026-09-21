import type {
  CompareResponse,
  EnvironmentResponse,
  ExecutionPlan,
  WorkflowRequest,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl.replace(/\/+$/, '');
  }

  public getBaseUrl(): string {
    return this.baseUrl;
  }

  /**
   * Check service health (GET /health)
   */
  async checkHealth(): Promise<{ status: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
      });
      if (!response.ok) {
        throw new Error(`Health check failed with status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Could not connect to backend server');
    }
  }

  /**
   * Fetch environment metadata: models, regions, and carbon windows (GET /environment)
   */
  async getEnvironment(): Promise<EnvironmentResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/environment`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to fetch environment (${response.status})`);
      }
      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Failed to retrieve environment data');
    }
  }

  /**
   * Schedule workflow (POST /plan)
   */
  async planWorkflow(request: WorkflowRequest): Promise<ExecutionPlan> {
    try {
      const response = await fetch(`${this.baseUrl}/plan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(request),
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Scheduling failed with status ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Unexpected error submitting workflow to /plan');
    }
  }

  /**
   * Compare optimized schedule against baseline (POST /compare)
   */
  async compareWorkflow(request: WorkflowRequest): Promise<CompareResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/compare`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(request),
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Comparison failed with status ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Unexpected error submitting workflow to /compare');
    }
  }
}

export const api = new ApiService();
