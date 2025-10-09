type PandasDataFrameProps = {
  data: unknown[][];
  columns: string[];
  index?: unknown[];
};

function renderCellValue(cell: unknown): string {
  if (cell === null || cell === undefined) {
    return "";
  }

  if (typeof cell === "object") {
    try {
      return JSON.stringify(cell);
    } catch {
      return String(cell);
    }
  }

  return String(cell);
}

export default function PandasDataFrame({ data, columns }: PandasDataFrameProps) {
  return (
    <div className="max-h-[80vh] overflow-y-auto overflow-x-auto rounded-lg">
      <table className="min-w-full border border-gray-200 bg-white">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((columnName) => (
              <th
                key={columnName}
                className="border-b border-gray-200 px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500"
              >
                {columnName}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {data.map((row, rowIndex) => (
            <tr
              key={`row-${rowIndex}`}
              className="transition-colors duration-150 ease-in-out hover:bg-gray-50"
            >
              {row.map((cell, cellIndex) => (
                <td
                  key={`cell-${rowIndex}-${cellIndex}`}
                  className="whitespace-nowrap border-b border-gray-100 px-6 py-4 text-sm text-gray-900"
                >
                  {renderCellValue(cell)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}