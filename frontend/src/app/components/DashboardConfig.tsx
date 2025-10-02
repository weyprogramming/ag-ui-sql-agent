import { useCoAgent, useCoAgentStateRender } from "@copilotkit/react-core";

import type { components } from "../types/accesify";

type AgentState = components["schemas"]["DashboardConfig-Input"]

export default function DashboardState() {

    const { state } = useCoAgent<AgentState>({
        name: "dashboard_agent",
    });

    return (<div>Dashboard Config: {state.title}</div>)
}