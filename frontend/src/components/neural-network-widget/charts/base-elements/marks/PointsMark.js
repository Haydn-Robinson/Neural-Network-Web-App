import { format } from 'd3'

function PointsMark({ xScale, yScale, data, accessors, colour, radius, toolTipData=null}) {

  const toolTipGenerator = (data, xLabel, yLabel, seperator, d3Format, accessors) => {
    const coordFormat = n => format(d3Format)(n);
    return `${xLabel.pre}${coordFormat(accessors.y(data))}${xLabel.post}${seperator}${yLabel.pre}${coordFormat(accessors.x(data))}${yLabel.post}`
  }

  return (
    <g className='points'>
      {data.map((d, index) => (
        <circle
          key={index}
          cx={xScale(accessors.x(d))}
          cy={yScale(accessors.y(d))}
          r={radius}
          fill={colour}
        >
          {toolTipData && (
            <title>
              {toolTipGenerator(
                d,
                toolTipData.xLabel,
                toolTipData.yLabel,
                toolTipData.seperator,
                toolTipData.d3Format,
                accessors
              )}
            </title>)}
        </circle>
      ))}
    </g>
  )
}

export default PointsMark
