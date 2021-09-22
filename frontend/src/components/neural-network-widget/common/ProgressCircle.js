function ProgressCircle({size, strokeWidth, colour, percent}) {

  const center = size/2;
  const radius = (size - strokeWidth)/2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - percent / 100 * circumference;
  
  return (
  <div className='progress-ring'>
    <div className="svg-container">
      <svg width={size} height={size}>
        <circle
          r={radius}
          cx={center}
          cy={center}
          strokeWidth={strokeWidth}
        />
        <circle
          r={radius}
          cx={center}
          cy={center}
          strokeWidth={strokeWidth}
          stroke={colour}
          strokeDasharray={`${circumference} ${circumference}`}
          strokeDashoffset={offset}
          />
      </svg>
    </div>
    <div style={{color: colour}}>
      {percent}%
    </div>
  </div>
  )
}

export default ProgressCircle
