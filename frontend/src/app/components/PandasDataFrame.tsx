export default function PandasDataFrame({ data, columns, index }: { data: any[][], columns: string[], index?: any[] }) {
  return (
    <div className="overflow-x-auto rounded-lg max-h-[80vh] overflow-y-auto">
      <table className="min-w-full bg-white border border-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((col, idx) => (
              <th key={idx} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b border-gray-200">
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {data.map((row, rowIndex) => (
            <tr key={rowIndex} className="hover:bg-gray-50 transition-colors duration-150 ease-in-out">
              {row.map((cell, cellIndex) => (
                <td key={cellIndex} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 border-b border-gray-100">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}