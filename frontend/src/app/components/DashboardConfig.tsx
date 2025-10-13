import { useCoAgent } from "@copilotkit/react-core";
import { useCallback, useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";

import SQLMarkdown from "./SQLMarkdown";
import PandasDataFrame from "./PandasDataFrame";
import PlotlyFigure from "./PlotlyFigure";
import CreateSqlDependencyButton from "./CreateSqlDependencyButton";

import {
    accesifyClient,
    type DashboardEvaluationRequest,
    type DashboardEvaluationResponse,
    type SqlDependencyModel,
} from "@/sdk";
import type { components } from "../types/accesify";

type AgentState = components["schemas"]["DashboardState"];
type DashboardParameter = components["schemas"]["DashboardSQLQueryParameter"];
type DashboardParameterValue = components["schemas"]["DashboardSQLQueryParameterValue"];

function defaultParameterValue(param: DashboardParameter): string {
    const { default_value } = param;
    if (default_value === null || default_value === undefined) {
        return "";
    }
    if (typeof default_value === "object") {
        return JSON.stringify(default_value);
    }
    return String(default_value);
}

function getInputType(parameterType: DashboardParameter["type"]): string {
    switch (parameterType) {
        case "int":
        case "float":
            return "number";
        case "date":
            return "date";
        case "time":
            return "time";
        case "datetime":
            return "datetime-local";
        default:
            return "text";
    }
}

function parseParameterValue(
    value: string,
    parameter: DashboardParameter
): string | number | boolean {
    const trimmed = value.trim();
    switch (parameter.type) {
        case "int": {
            const parsed = Number.parseInt(trimmed, 10);
            if (Number.isNaN(parsed)) {
                throw new Error(`Parameter "${parameter.name}" must be an integer.`);
            }
            return parsed;
        }
        case "float": {
            const parsed = Number.parseFloat(trimmed);
            if (Number.isNaN(parsed)) {
                throw new Error(`Parameter "${parameter.name}" must be a number.`);
            }
            return parsed;
        }
        case "bool": {
            const lowered = trimmed.toLowerCase();
            if (["true", "1", "yes", "y", "on"].includes(lowered)) {
                return true;
            }
            if (["false", "0", "no", "n", "off"].includes(lowered)) {
                return false;
            }
            throw new Error(`Parameter "${parameter.name}" must be true or false.`);
        }
        case "date":
        case "datetime":
        case "time":
        case "str":
        default:
            return trimmed;
    }
}

export default function DashboardState() {
    const { state, setState } = useCoAgent<AgentState>({
        name: "dashboard_agent",
    });

    const handleDependencySelect = useCallback(
        (dependency: SqlDependencyModel | null) => {
            setState((previous) => {
                const prior = previous ?? ({} as AgentState);
                return {
                    ...prior,
                    selected_sql_dependency_id: dependency
                        ? dependency.pk ?? dependency.name ?? null
                        : null,
                };
            });
        },
        [setState]
    );

    const [activeTab, setActiveTab] = useState<"dataframe" | "figure" | "query">(
        "figure"
    );
    const [parameterValues, setParameterValues] = useState<Record<string, string>>({});
    const [evaluationResult, setEvaluationResult] =
        useState<DashboardEvaluationResponse | null>(null);
    const [isEvaluating, setIsEvaluating] = useState(false);
    const [errorMessage, setErrorMessage] = useState<string | null>(null);

    const dashboardConfig = state.dashboard_config ?? null;

    const parameters = useMemo(
        () =>
            dashboardConfig?.dashboard_sql_query?.dashboard_sql_query_parameters ??
            [],
        [dashboardConfig]
    );

    useEffect(() => {
        if (!parameters.length) {
            setParameterValues({});
            return;
        }

        setParameterValues((previous) => {
            const next: Record<string, string> = {};
            for (const parameter of parameters) {
                next[parameter.name] =
                    previous[parameter.name] ?? defaultParameterValue(parameter);
            }
            return next;
        });
    }, [parameters]);

    const displayedDataFrame = evaluationResult?.data_frame ?? state.default_dataframe;
    const displayedFigure = evaluationResult?.figure ?? state.default_figure;

    const handleInputChange = (name: string, value: string) => {
        setParameterValues((previous) => ({ ...previous, [name]: value }));
    };

    const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        if (!dashboardConfig) {
            return;
        }

        setIsEvaluating(true);
        setErrorMessage(null);

        try {
            const parameterValuesPayload: DashboardParameterValue[] = parameters.map(
                (parameter) => {
                const rawValue = parameterValues[parameter.name] ?? "";
                if (!rawValue.length) {
                    throw new Error(`Parameter "${parameter.name}" requires a value.`);
                }

                    return {
                        parameter,
                        value: parseParameterValue(rawValue, parameter),
                    };
                }
            );

            const parametrizedQuery =
                dashboardConfig.dashboard_sql_query?.parametrized_query;
            if (!parametrizedQuery) {
                throw new Error("Dashboard SQL query is missing.");
            }

            const sqlDependencyId =
                dashboardConfig.dashboard_sql_query?.sql_dependency_id;
            if (!sqlDependencyId) {
                throw new Error("Dashboard SQL dependency is missing.");
            }

            const chartConfig = dashboardConfig.chart_config;
            if (!chartConfig) {
                throw new Error("Dashboard chart configuration is missing.");
            }

            const evaluationPayload: DashboardEvaluationRequest = {
                dashboard_evaluation_sql_query: {
                    sql_dependency_id: sqlDependencyId,
                    parametrized_query: parametrizedQuery,
                    dashboard_sql_query_parameter_values: parameterValuesPayload,
                },
                chart_config: chartConfig,
            };

            const result = await accesifyClient.evaluateDashboard(evaluationPayload);
            setEvaluationResult(result);
            if (result.figure) {
                setActiveTab("figure");
            } else if (result.data_frame) {
                setActiveTab("dataframe");
            } else if (dashboardConfig.dashboard_sql_query?.parametrized_query) {
                setActiveTab("query");
            } else {
                setActiveTab("dataframe");
            }
        } catch (error) {
            setErrorMessage(
                error instanceof Error ? error.message : "Failed to evaluate dashboard."
            );
        } finally {
            setIsEvaluating(false);
        }
    };

    return (
        <div className="p-4 bg-white min-h-screen">
            <div className="mx-auto flex max-w-6xl flex-col gap-6">
                <CreateSqlDependencyButton onSelect={handleDependencySelect} />
                <section className="rounded-lg border border-gray-200 bg-gray-50 p-4 shadow-sm">
                    <header className="mb-4 flex items-center justify-between">
                        <div>
                            <h2 className="text-lg font-semibold text-gray-900">
                                Dashboard Parameters
                            </h2>
                            <p className="text-sm text-gray-600">
                                Provide values for each SQL parameter, then run an evaluation to
                                preview the dashboard output.
                            </p>
                        </div>
                    </header>

                    {dashboardConfig ? (
                        <div className="space-y-4">

                            <form className="space-y-4" onSubmit={handleSubmit}>
                                <div className="grid gap-4 sm:grid-cols-2">
                                    {parameters.map((parameter) => {
                                        const value = parameterValues[parameter.name] ?? "";
                                        const inputType = getInputType(parameter.type);

                                        return (
                                            <label
                                                key={parameter.name}
                                                className="flex flex-col gap-2 rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
                                            >
                                                <span className="text-sm font-semibold text-gray-800">
                                                    {parameter.name}
                                                    <span className="ml-2 text-xs font-medium uppercase text-gray-500">
                                                        {parameter.type}
                                                    </span>
                                                </span>
                                                {parameter.type === "bool" ? (
                                                    <select
                                                        value={value}
                                                        onChange={(event) =>
                                                            handleInputChange(
                                                                parameter.name,
                                                                event.target.value
                                                            )
                                                        }
                                                        className="rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                                    >
                                                        <option value="true">True</option>
                                                        <option value="false">False</option>
                                                    </select>
                                                ) : (
                                                    <input
                                                        type={inputType}
                                                        value={value}
                                                        onChange={(event) =>
                                                            handleInputChange(
                                                                parameter.name,
                                                                event.target.value
                                                            )
                                                        }
                                                        className="rounded-md border border-gray-300 px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                                    />
                                                )}
                                                {parameter.default_value !== undefined && (
                                                    <span className="text-xs text-gray-500">
                                                        Example: {String(parameter.default_value)}
                                                    </span>
                                                )}
                                            </label>
                                        );
                                    })}
                                    {!parameters.length && (
                                        <p className="text-sm text-gray-600">
                                            This dashboard has no SQL parameters.
                                        </p>
                                    )}
                                </div>

                                {errorMessage && (
                                    <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                                        {errorMessage}
                                    </div>
                                )}

                                <button
                                    type="submit"
                                    disabled={isEvaluating || !parameters.length}
                                    className="inline-flex items-center justify-center rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300"
                                >
                                    {isEvaluating ? "Evaluating..." : "Evaluate Dashboard"}
                                </button>
                            </form>
                        </div>
                    ) : (
                        <p className="text-sm text-gray-600">
                            No dashboard configuration available yet. Ask the agent to create
                            one to begin.
                        </p>
                    )}
                </section>

                <section className="flex-1 rounded-lg border border-gray-200 p-4 shadow-sm">
                    <div className="border-b border-gray-200">
                        <nav className="-mb-px flex space-x-8">
                            <button
                                onClick={() => setActiveTab("dataframe")}
                                className={`${
                                    activeTab === "dataframe"
                                        ? "border-blue-500 text-blue-600"
                                        : "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700"
                                } whitespace-nowrap border-b-2 py-3 px-1 text-sm font-medium transition-colors`}
                            >
                                DataFrame
                            </button>
                            <button
                                onClick={() => setActiveTab("figure")}
                                className={`${
                                    activeTab === "figure"
                                        ? "border-blue-500 text-blue-600"
                                        : "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700"
                                } whitespace-nowrap border-b-2 py-3 px-1 text-sm font-medium transition-colors`}
                            >
                                Figure
                            </button>
                            <button
                                onClick={() => setActiveTab("query")}
                                className={`${
                                    activeTab === "query"
                                        ? "border-blue-500 text-blue-600"
                                        : "border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700"
                                } whitespace-nowrap border-b-2 py-3 px-1 text-sm font-medium transition-colors`}
                            >
                                SQL Query
                            </button>
                        </nav>
                    </div>

                    <div className="mt-4">
                        {activeTab === "dataframe" && displayedDataFrame && (
                            <PandasDataFrame
                                data={displayedDataFrame.data || []}
                                columns={displayedDataFrame.columns || []}
                                index={displayedDataFrame.index || []}
                            />
                        )}

                        {activeTab === "figure" && displayedFigure && (
                            <PlotlyFigure
                                data={displayedFigure.data}
                                layout={displayedFigure.layout}
                                config={displayedFigure.config}
                            />
                        )}

                        {activeTab === "query" && (
                            dashboardConfig?.dashboard_sql_query?.parametrized_query ? (
                                <SQLMarkdown
                                    query={
                                        dashboardConfig.dashboard_sql_query.parametrized_query
                                    }
                                />
                            ) : (
                                <p className="text-sm text-gray-500">
                                    No SQL query available yet. Ask the agent to create one to
                                    view it here.
                                </p>
                            )
                        )}

                        {activeTab === "dataframe" && !displayedDataFrame && (
                            <p className="text-sm text-gray-500">
                                No data available yet. Evaluate the dashboard to view results.
                            </p>
                        )}

                        {activeTab === "figure" && !displayedFigure && (
                            <p className="text-sm text-gray-500">
                                No figure available yet. Evaluate the dashboard to view the
                                chart.
                            </p>
                        )}
                    </div>
                </section>
            </div>
        </div>
    );
}