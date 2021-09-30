function Axes({xScale, yScale, innerWidth, innerHeight, labels}) {
  const axisOffset = 25;

  return (
    <g className='axes'>
      <rect className='box' width={innerWidth} height={innerHeight}/>
      <g className='xAxis'>
        <line y2={innerHeight}/>
        {xScale.ticks().map(tickValue => (
          <g key={tickValue} transform={`translate(${xScale(tickValue)}, 0)`}>
            <line y2={innerHeight}/>
            <text y={innerHeight} dy='.9em' textAnchor='middle'>{tickValue}</text>
          </g>
        ))}
        <text x={innerWidth/2} y={innerHeight} dy={axisOffset} textAnchor='middle'>{labels.x}</text>
      </g>
      <g className='yAxis'>
        <line x2={innerWidth}/>
        {yScale.ticks().reverse().map(tickValue => (
          <g key={tickValue} transform={`translate(0, ${yScale(tickValue)})`}>
            <line x2={innerWidth}/>
            <text textAnchor='middle' dy='.32em' dx='-.9em'>{tickValue}</text>
          </g>
        ))}
        <text
        textAnchor='middle'
        transform={`translate(${-axisOffset}, ${innerHeight/2}) rotate(-90)`}>{labels.y}</text>
      </g>
    </g>
  )
}

export default Axes
