import "@copilotkit/react-ui/styles.css";
import { useCopilotAction } from "@copilotkit/react-core";
import { CopilotPopup } from "@copilotkit/react-ui";

import SQLMarkdown from "../components/SQLMarkdown";
import PandasDataFrame from "../components/PandasDataFrame";
import PlotlyFigure from "./PlotlyFigure";

export default function Chat() {
    const LoadingSpinner = ({ message, toneClass }: { message: string; toneClass: string }) => (
      <div className={`flex items-center gap-2 font-medium ${toneClass}`} role="status" aria-live="polite">
        <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" aria-hidden="true" />
        <span>{message}</span>
      </div>
    );

    useCopilotAction({
      name: "execute_sql_query",
      available: "frontend",
      render: ({ status, args, result }) => {
        return (<div className="text-black">
          {status === "inProgress" && (
            <LoadingSpinner toneClass="text-sky-600" message="Bereite SQL-Abfrage vor..." />
          )}
          {status === "executing" && (
            <LoadingSpinner toneClass="text-emerald-600" message="Führe SQL-Abfrage aus..." />
          )}
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

    useCopilotAction({
      name: "get_database_table_content",
      available: "frontend",
      render: ({ status, args, result }) => {
        return (<div className="text-black">
          {status === "inProgress" && (
            <LoadingSpinner toneClass="text-sky-600" message="Lade Tabelleninhalt..." />
          )}
          {status === "executing" && (
            <LoadingSpinner toneClass="text-emerald-600" message="Tabelleninhalt wird geladen..." />
          )}
          {status === "complete" && <div>
            <details className="border rounded-lg p-2">
              <summary className="cursor-pointer font-medium">Tabelleninhalt</summary>
              <div className="mt-2 max-h-[500px] overflow-y-auto">
                <div className="py-5 px-2">
                  <SQLMarkdown query={`SELECT * FROM ${args.table_name} LIMIT 5;`} />
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
      }
    })


    useCopilotAction({
      name: "explore_database_table",
      available: "frontend",
      render: ({ status, args, result }) => {
        return (<div className="text-black">
          {status === "inProgress" && (
            <LoadingSpinner toneClass="text-sky-600" message="Lade Tabelleninformationen..." />
          )}
          {status === "executing" && (
            <LoadingSpinner toneClass="text-emerald-600" message="Tabelleninformationen werden geladen..." />
          )}
          {status === "complete" && <div>
            <details className="border rounded-lg p-2">
              <summary className="cursor-pointer font-medium">Tabelleninformationen der Tabelle {result.table_name}</summary>
              <div className="mt-2 max-h-[500px] overflow-y-auto">
                <div className="py-5 px-2">
                  <pre className="bg-gray-100 p-4 rounded-lg overflow-x-auto">
                    <code>{JSON.stringify(result, null, 2)}</code>
                  </pre>
                </div>
              </div>
            </details>
          </div>}
        </div>);
      }
    })

    useCopilotAction({
      name: "save_dashboard_sql_query",
      available: "frontend",
      render: ({ status, args, result }) => {
        return (<div className="text-black">
          {status === "inProgress" && (
            <LoadingSpinner toneClass="text-sky-600" message="Ich überlege mir eine SQL-Abfrage... " />
          )}
          {status === "executing" && (
            <LoadingSpinner toneClass="text-emerald-600" message="Ich teste die SQL-Abfrage..." />
          )}
          {status === "complete" && (
            <div className="pb-5 px-2">
              <details className="border rounded-lg p-2">
                <summary className="cursor-pointer font-medium">Dashboard SQL-Abfrage generiert</summary>
                <div className="mt-2 max-h-[500px] overflow-y-auto">
                  <div className="py-5 px-2">
                    <SQLMarkdown query={args.parametrized_query} />
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
            </div>
          )}
        </div>);
      }
    })


    useCopilotAction({
      name: "add_dashboard_figure_config",
      available: "frontend",
      render: ({ status, args, result }) => {
        return (<div className="text-black">
          {status === "inProgress" && (
            <LoadingSpinner toneClass="text-sky-600" message="Ich überlege mir eine Visualisierung..." />
          )}
          {status === "executing" && (
            <LoadingSpinner toneClass="text-emerald-600" message="Ich erstelle die Visualisierung..." />
          )}
          {status === "complete" && (
            <div className="pb-5 px-2">
              <details className="border rounded-lg p-2">
                <summary className="cursor-pointer font-medium">Dashboard Visualisierung generiert</summary>
                <div className="mt-2 max-h-[500px] overflow-y-auto">
                  <div className="py-5 px-2">
                    <PlotlyFigure
                      data={result.data}
                      layout={result.layout}
                      config={result.config}
                    />
                  </div>
                </div>
              </details>
            </div>
          )}
        </div>
      );
    }
    })

    return (
      <CopilotPopup/>
    )
  }