import { useState, useEffect } from 'react';
import Button from './common/Button'

function Results() {
  const [data, setData] = useState({})

  useEffect(() => {
    const getResults = async () => {
      const res = await fetch('/api/results');
      const data = await res.json();
      setData(data)
    }
    getResults()
  }, [])

  return (

    <div>
      <h2>Auroc: {data.auroc}</h2>
      {data.training_failed && (
              <p>
              Warning, the trained network has performance that is no better than random chance.<br/><br />
              This may be because the selected options are not appropriate. If the suggested options were used
              the optimiser may have got stuck during the training process.<br /><br />
              Click this message to return to the setup screen and try again.
          </p>
      )}
      <Button
        colour='FireBrick'
        text='Download Training Summary'
        onClick={() => window.location.href='/api/trainingsummary'}
      />
    </div>
  )
}

export default Results
