import "@copilotkit/react-ui/styles.css";
import { useCoAgent, useCopilotAction } from "@copilotkit/react-core";
import { CopilotKitCSSProperties, CopilotChat, Markdown, CopilotSidebar } from "@copilotkit/react-ui";

import SQLMarkdown from "../components/SQLMarkdown";
import PandasDataFrame from "../components/PandasDataFrame";


export default function Chat() {
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
      name: "save_dashboard_config",
      available: "frontend",
      render: ({ status, args, result }) => {
        return (<div className="text-black">
          {status === "complete" && <div>
            {result.snapshot.title}
            <SQLMarkdown query={result.snapshot.dashboard_sql_query.parametrized_query} />
          </div>}
        </div>);
      },
    });
    return (
      <CopilotSidebar/>
    )
  }