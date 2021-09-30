import { line } from 'd3'

function LineMark({ xScale, yScale, data, accessors }) {

  return (
    <g className='chart-line'>
      <path 
        stroke='black'
        fill='none'
        d={line()
          .x(d => xScale(accessors.x(d)))
          .y(d => yScale(accessors.y(d)))(data)}
      />
    </g>
  )
}

export default LineMark
