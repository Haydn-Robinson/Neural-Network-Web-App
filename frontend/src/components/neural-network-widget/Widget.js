import { useState } from 'react'
import SetupTraining from './setup/SetupTraining'
import Progress from './Progress'
import Results from './Results'
import '../../css/widget/setup.css';
import '../../css/widget/form-elements.css';
import '../../css/widget/progress.css';
import '../../css/widget/results.css';

function Widget() {
  // Dataset state
  const [taskState, setTaskState] = useState('SETUP')

  const setDisplay = () => { 
    if (taskState === 'SETUP') {
      return (
        <>
          <h1>Train A Neural Network</h1>
          <SetupTraining
          setTaskState={setTaskState}
          />
        </>
      )
    } else if (taskState === 'PROGRESS') {
      return (
        <div className='progress'>
          <h1>Training In Progress</h1>
          <Progress setTaskState={setTaskState}/>
        </div>
      )
    } else if (taskState === 'COMPLETE') {
      return (
        <>
          <h1>Results</h1>
          <Results/>
        </>
      )
    }
  }

  return (
    <div className='widget'>  
        {setDisplay()}
    </div>
  )
}

export default Widget
