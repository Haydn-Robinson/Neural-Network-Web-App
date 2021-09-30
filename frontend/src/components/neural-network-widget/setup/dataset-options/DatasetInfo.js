import { useEffect, useState } from 'react'
import { csv } from 'd3'
import SKLMoons from '../../charts/SKLMoons'

function DatasetInfo({datasetInfo}) {
  const [data, setData] = useState([])
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    csv(datasetInfo.url, d => {
      return {
        input1: +d.input1,
        input2: +d.input2,
        target: !!+d.target
      }})
      .then(setData)
      .then(setLoaded(true))
      // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const chartMargins = {top: 20, right: 20, bottom: 35, left: 35}

  return (
    <div className='dataset-info'>
      <h3>Description</h3>
      <p>{datasetInfo.description}</p>
      <h3>Variables</h3>
      <ol>{datasetInfo.variables.map((variable, index) => <li key={index}>{variable}</li>)}</ol>
      <h3>Visualisation</h3>
      {datasetInfo.visualisation ? (
        loaded ? (
          <SKLMoons
            width='250'
            height='250'
            data={data}
            margin={chartMargins}
            marksOptions={{points: true, line: false, pointsOpts: {colour: 'red', radius: 2}}}
            accessors={{x: d => d.input1, y: d => d.input2}}
            axesLabels={{x: datasetInfo.visOptions.labels.x, y: datasetInfo.visOptions.labels.y}}
          />
        ) : <p>Loading...</p>
      ) : <p>No visualisation is available for this dataset.</p>}
    </div>
  )
}

export default DatasetInfo
