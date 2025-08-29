import dynamic from 'next/dynamic';

const Plot = dynamic(() => import('react-plotly.js'), { 
  ssr: false,
  loading: () => <div>Loading chart...</div>
});

interface PlotlyFigureProps {
  figure: {
    data: any[];
    layout: any;
    config?: any;
  };
}

export default function PlotlyFigure({ figure }: PlotlyFigureProps) {
  return (
    <div className="w-full h-96 p-4">
      <Plot
        data={figure.data}
        layout={figure.layout}
        config={figure.config || { responsive: true }}
        style={{ width: '100%', height: '100%' }}
      />
    </div>
  );
}