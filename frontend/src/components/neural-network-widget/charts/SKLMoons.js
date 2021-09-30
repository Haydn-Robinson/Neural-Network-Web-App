import { scaleLinear, extent } from 'd3'
import Axes from './base-elements/Axes'
import BinaryClassPoints from './base-elements/marks/BinaryClassPoints'
import '../../../css/widget/chart.css';

function SKLMoons({ width, height, data, margin, marksOptions, accessors, axesLabels }) {

  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  const xScale = scaleLinear()
    .domain(extent(data, accessors.x))
    .range([0, innerWidth])
    .nice();

  const yScale = scaleLinear()
  .domain(extent(data, accessors.y))
  .range([innerHeight, 0])
  .nice();

  return (
    <div className='chart'>
      <svg viewBox={`0 0 ${width} ${height}`} preserveAspectRatio='xMinYMin meet'>
        <g transform={`translate(${margin.left}, ${margin.top})`}>
          <Axes
            xScale={xScale}
            yScale={yScale}
            innerWidth={innerWidth}
            innerHeight={innerHeight}
            labels={axesLabels}
          />
          <BinaryClassPoints
            xScale={xScale}
            yScale={yScale}
            data={data}
            accessors = {accessors}
            colour={marksOptions.pointsOpts.colour}
            radius={marksOptions.pointsOpts.radius}
            toolTipData={{
                xLabel: {pre: '(', post:''},
                yLabel: {pre: ' ', post:')'},
                seperator: ',',
                d3Format: '<4.3'
              }}
        />
        </g>
      </svg>
    </div>
  )
}

export default SKLMoons