import "@copilotkit/react-ui/styles.css";
import { useCoAgent, useCopilotAction } from "@copilotkit/react-core";
import { CopilotKitCSSProperties, CopilotChat, Markdown, CopilotSidebar, CopilotPopup } from "@copilotkit/react-ui";
import { type WindowProps, useChatContext } from "@copilotkit/react-ui";
import { CopilotKit } from "@copilotkit/react-core";
import { type MessagesProps } from "@copilotkit/react-ui";

import "@copilotkit/react-ui/styles.css";


import SQLMarkdown from "../components/SQLMarkdown";
import PandasDataFrame from "../components/PandasDataFrame";


export default function Chat() {
    useCopilotAction({
      name: "execute_sql_query",
      available: "frontend",
      render: ({ status, args, result }) => {
        return (<div className="text-black">
          {status === "complete" && <div>
            <details className="border rounded-lg p-2">
              <summary className="cursor-pointer font-medium">Datenabfrage</summary>
              <div className="mt-2 max-h-[500px] overflow-y-auto">
                <div className="py-5 px-2">
                  <SQLMarkdown query={args.query} />
                </div>
                <div className="pb-5 px-2">
                  <PandasDataFrame
                    data={result.data}
                    columns={result.columns}
                    index={result.index}
                  />
                </div>
              </div>
            </details>
          </div>}
        </div>);
      },
    })


    return (
      <CopilotPopup/>
    )
  }