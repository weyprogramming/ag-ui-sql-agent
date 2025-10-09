import type { components } from "../app/types/accesify";

type DashboardConfigInput = components["schemas"]["DashboardConfig-Input"];
type DashboardConfigOutput = components["schemas"]["DashboardConfig-Output"];
type DashboardConfigModel = components["schemas"]["DashboardConfigModel"];
type DashboardEvaluationRequest = components["schemas"]["DashboardEvaluationRequest"];
type DashboardEvaluationResult = components["schemas"]["DashboardEvaluationResult"];
type DashboardState = components["schemas"]["DashboardState"];
type ValidationError = components["schemas"]["HTTPValidationError"];
type SqlDependencyCreateRequest = components["schemas"]["SQLBaseDependencyCreateRequest"];
type SqlDependencyModel = components["schemas"]["SQLBaseDependencyModel"];

export interface AccesifyClientOptions {
  /** Override the base URL for the FastAPI service (e.g. http://localhost:8000). */
  baseUrl?: string;
  /** Provide a custom fetch implementation (useful for testing). */
  fetchImpl?: typeof fetch;
}

export type ApiErrorBody =
  | ValidationError
  | { detail?: string; [key: string]: unknown }
  | null;

export class AccesifyClient {
  private readonly baseUrl: string;
  private readonly fetchImpl: typeof fetch;

  constructor(options: AccesifyClientOptions = {}) {
    const defaultBase =
      typeof process !== "undefined"
        ? process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"
        : "http://localhost:8000";

    this.baseUrl = options.baseUrl ?? defaultBase;

    const candidateFetch = options.fetchImpl ?? fetch;
    this.fetchImpl = candidateFetch.bind(globalThis);
  }

  private buildUrl(path: string): string {
    if (!this.baseUrl) {
      return path;
    }

    const normalizedBase = this.baseUrl.replace(/\/$/, "");
    return `${normalizedBase}${path}`;
  }

  private async request<T>(path: string, init: RequestInit): Promise<T> {
    const response = await this.fetchImpl(this.buildUrl(path), {
      ...init,
      headers: {
        Accept: "application/json",
        ...(init.headers ?? {}),
      },
    });

    const contentType = response.headers.get("content-type") ?? "";
    const isJson = contentType.includes("application/json");
    const payload = isJson ? await response.json() : await response.text();

    if (!response.ok) {
      const error = new Error(
        typeof payload === "object" && payload !== null && "detail" in payload
          ? String((payload as { detail: unknown }).detail)
          : response.statusText || "Request failed"
      ) as Error & { status: number; body: ApiErrorBody | string };
      error.status = response.status;
      error.body = (payload as ApiErrorBody) ?? null;
      throw error;
    }

    return payload as T;
  }

  /** GET /api/dashboard-config */
  async getDashboards(): Promise<DashboardConfigModel[]> {
    return this.request<DashboardConfigModel[]>("/api/dashboard-config", {
      method: "GET",
    });
  }

  /** POST /api/dashboard-config */
  async createDashboardConfig(
    payload: DashboardConfigInput
  ): Promise<DashboardConfigOutput> {
    return this.request<DashboardConfigOutput>("/api/dashboard-config", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  }

  /** POST /api/dashboard-evaluation */
  async evaluateDashboard(
    payload: DashboardEvaluationRequest
  ): Promise<DashboardEvaluationResult> {
    return this.request<DashboardEvaluationResult>("/api/dashboard-evaluation", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  }

  /** GET /api/state/{state_id} */
  async getAgentState(stateId: string): Promise<DashboardState> {
    return this.request<DashboardState>(`/api/state/${encodeURIComponent(stateId)}`, {
      method: "GET",
    });
  }

  /** GET /api/sql-dependency */
  async getSqlDependencies(): Promise<SqlDependencyModel[]> {
    return this.request<SqlDependencyModel[]>("/api/sql-dependency", {
      method: "GET",
    });
  }

  /** POST /api/sql-dependency */
  async createSqlDependency(
    payload: SqlDependencyCreateRequest
  ): Promise<SqlDependencyModel> {
    return this.request<SqlDependencyModel>("/api/sql-dependency", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  }
}

export type {
  DashboardConfigInput,
  DashboardConfigOutput,
  DashboardConfigModel,
  DashboardEvaluationRequest,
  DashboardEvaluationResult,
  DashboardState,
  ValidationError,
  SqlDependencyCreateRequest,
  SqlDependencyModel,
};

export const accesifyClient = new AccesifyClient();
