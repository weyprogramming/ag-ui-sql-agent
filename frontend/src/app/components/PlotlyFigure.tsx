import dynamic from 'next/dynamic';

import type { components } from '../types/accesify';

const Plot = dynamic(() => import('react-plotly.js'), { 
  ssr: false,
  loading: () => <div>Loading chart...</div>
});

type PlotlyFigureProps = components["schemas"]["PlotlyFigure"];

export default function PlotlyFigure(figure : PlotlyFigureProps) {
  return (
    <div className="pt-4">
      <div className="w-full p-4 bg-white">
        <Plot
          data={figure.data}
          layout={figure.layout || { autosize: true, title: 'Chart' }}
          config={figure.config || { responsive: true }}
          style={{ width: '100%', height: '100%' }}
        />
      </div>
    </div>
  );
}