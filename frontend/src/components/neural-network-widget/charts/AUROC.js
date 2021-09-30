import { scaleLinear, extent } from 'd3'
import Axes from './base-elements/Axes'
import LineMarks from './base-elements/marks/LineMark'
import PointsMarks from './base-elements/marks/PointsMark'
import '../../../css/widget/chart.css';

function AUROC({ width, height, data, margin, marksOptions, accessors, axesLabels }) {

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
          {marksOptions.line && (
            <LineMarks
              xScale={xScale}
              yScale={yScale}
              data={data}
              accessors = {accessors}
          />
          )}
          {marksOptions.points && (
            <PointsMarks
              xScale={xScale}
              yScale={yScale}
              data={data}
              accessors = {accessors}
              colour={marksOptions.pointsOpts.colour}
              radius={marksOptions.pointsOpts.radius}
              toolTipData={{
                xLabel: {pre: 'FPR: ', post:''},
                yLabel: {pre: 'TPR: ', post:''},
                seperator: '\n',
                d3Format: '<4.3'
              }}
          />
          )}
        </g>
      </svg>
    </div>
  )
}

export default AUROC