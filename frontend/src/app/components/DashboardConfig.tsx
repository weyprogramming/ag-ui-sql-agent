import { useCoAgent, useCoAgentStateRender } from "@copilotkit/react-core";
import { useState } from "react";

import SQLMarkdown from "../components/SQLMarkdown";
import PandasDataFrame from "../components/PandasDataFrame";
import PlotlyFigure from "./PlotlyFigure";

import type { components } from "../types/accesify";

type AgentState = components["schemas"]["DashboardState"]

export default function DashboardState() {

    const { state } = useCoAgent<AgentState>({
        name: "dashboard_agent",
    });

    const [activeTab, setActiveTab] = useState<'dataframe' | 'figure'>('figure');

    return (<div className="p-4 bg-white h-screen">
        <div>
            <div className="border-b border-gray-200">
                <nav className="-mb-px flex space-x-8">
                    <button
                        onClick={() => setActiveTab('dataframe')}
                        className={`${
                            activeTab === 'dataframe'
                                ? 'border-blue-500 text-blue-600'
                                : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                        } whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium transition-colors`}
                    >
                        DataFrame
                    </button>
                    <button
                        onClick={() => setActiveTab('figure')}
                        className={`${
                            activeTab === 'figure'
                                ? 'border-blue-500 text-blue-600'
                                : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                        } whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium transition-colors`}
                    >
                        Figure
                    </button>
                </nav>
            </div>

            <div className="mt-4">
                {activeTab === 'dataframe' && (
                    <PandasDataFrame 
                        data={state.test_dateframe?.data || []} 
                        columns={state.test_dateframe?.columns || []} 
                        index={state.test_dateframe?.index || []} 
                    />
                )}
                
                {activeTab === 'figure' && state.test_figure && (
                    <PlotlyFigure 
                        data={state.test_figure.data} 
                        layout={state.test_figure.layout} 
                        config={state.test_figure.config} 
                    />
                )}
            </div>
        </div>
    </div>)
}