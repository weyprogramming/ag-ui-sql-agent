"use client";

import { useCoAgent, useCopilotAction } from "@copilotkit/react-core";
import { CopilotKitCSSProperties, CopilotChat, Markdown } from "@copilotkit/react-ui";

import SQLMarkdown from "./components/SQLMarkdown";
import PythonMarkdown from "./components/PythonMarkdown";
import PandasDataFrame from "./components/PandasDataFrame";
import PlotlyFigure from "./components/PlotlyFigure";

export default function CopilotKitPage() {

  return (
    <main>
      <MainContent />
    </main>
  );
}

const MainContent = () => {
  useCopilotAction({
    name: "execute_sql_query",
    available: "frontend",
    render: ({ status, args, result }) => {
      return (<div className="text-black">
        <SQLMarkdown query={args.query} />
        {status === "complete" && <PandasDataFrame
          data={result.data}
          columns={result.columns}
          index={result.index}
        />}
      </div>);
    },
  }),
  useCopilotAction({
    name: "execute_plotly_code",
    available: "frontend",
    render: ({ status, args, result }) => {
      return (<div className="text-black">
        <PythonMarkdown code={args.executable_python_code} />
        {status === "complete" && <PlotlyFigure figure={result} />}
      </div>);
    },
  });
  return (
    <CopilotChat/>
  )
}