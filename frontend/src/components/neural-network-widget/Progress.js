import { useState, useEffect } from "react"
import ProgressCircle from "./common/ProgressCircle"

function Progress({setTaskState}) {
  const [progress, setProgress] = useState(10)

  useEffect(() => {
    const eventSource = new EventSource('/api/progress')
    eventSource.addEventListener('progress', (e) => {setProgress(e.data)})
    eventSource.addEventListener('redirect', () => {setTaskState('COMPLETE')})
    return () => {
      eventSource.close()
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }},[])

  return (
      <ProgressCircle size={250} strokeWidth={15} colour='FireBrick' percent={progress}/>
  )
}

export default Progress
