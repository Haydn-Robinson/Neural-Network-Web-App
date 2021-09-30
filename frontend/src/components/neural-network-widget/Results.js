import { useState, useEffect } from 'react';
import { format } from 'd3'
import Button from './common/Button'
import AUROC from './charts/AUROC'

function Results() {
  const [data, setData] = useState({})
  const [chartData, setChartData] = useState([])
  const [loaded, setLoaded] = useState(false)

  const chartMargins = {top: 20, right: 20, bottom: 35, left: 35}

  useEffect(() => {
    const getResults = async () => {
      const res = await fetch('/api/results');
      const data = await res.json();
      setData(data)

      const temp = data.roc_curve.fprs.map((fpr, index) => {return {fpr: fpr, tpr: data.roc_curve.tprs[index]}})
      setChartData(temp)
      setLoaded(true)
    }
    getResults()
  }, [])

  return (
    <div className='results'>
      {loaded ? (
        <>
          <h2>Auroc: {format('5.4~')(data.auroc)}</h2>
          {data.training_failed && (
            <p>
              Warning, the trained network has performance that is no better than random chance.<br/><br />
              This may be because the selected options are not appropriate. However, this package is still in development and the optimsier
              sometimes gets stuck during the training process. If the suggested options were used then this is definitely the case.<br /><br />
              Refresh the page to return to the setup screen and try again.
            </p>
          )}
          <div>
            <AUROC
              width='250'
              height='250'
              data={chartData}
              margin={chartMargins}
              marksOptions={{points: false, line: true, pointsOpts: {colour: 'red', radius: 2}}}
              accessors={{x: d => d.fpr, y: d => d.tpr}}
              axesLabels={{x: 'FPR', y: 'TPR'}}
            />
          </div>
          <Button
            colour='FireBrick'
            text='Download Training Summary'
            onClick={() => window.location.href='/api/trainingsummary'}
          />
        </>
      ): <h2>Loading...</h2>}
    </div>
  )
}

export default Results
