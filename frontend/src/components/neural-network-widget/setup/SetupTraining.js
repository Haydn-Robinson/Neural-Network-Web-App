import { useState } from 'react'
import DatasetOptions from './dataset-options/DatasetOptions'
import TrainingOptions from './TrainingOptions'

function SetupTraining({setTaskState}) {
  // Dataset state
  const [datasetSelected, setDatasetSelected] = useState(false)
  const [datasetInfo, setDatasetInfo] = useState(null)

  // const fetchDataset = async (dataset) => {
  //   const res = await fetch(`api/data/${dataset}`);
  //   const data = await res.json();
  //   return data
  // }

  const updateDatasetInfo = async (datasetId) => {
    const res = await fetch(`/api/datasetinfo/${datasetId}`);
    const data = await res.json();
    setDatasetInfo(data)
    setDatasetSelected(true)
  }

  return (
    <div className='setup'>
      <DatasetOptions
        updateDatasetInfo={updateDatasetInfo}
        datasetInfo={datasetInfo}
        datasetSelected={datasetSelected}
      />
      <TrainingOptions
        datasetSelected={datasetSelected}
        datasetInfo={datasetInfo}
        setTaskState={setTaskState}
      />
    </div>
  )
}

export default SetupTraining
