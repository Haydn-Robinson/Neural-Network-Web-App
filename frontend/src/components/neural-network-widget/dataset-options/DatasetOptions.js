import { useState } from 'react'
import SelectDataset from './SelectDataset.js'
import Button from "../Button"
import DatasetInfo from './DatasetInfo.js'

function DatasetOptions({updateDatasetInfo, datasetInfo, datasetSelected}) {
  const [showDatasetInfo, setShowDatasetInfo] = useState(false)


  return (
    <div className='dataset-options'>
      <h3>Dataset:</h3><span>{datasetInfo ? datasetInfo.name : 'No Datset Selected'}</span>
      <div>
        <SelectDataset updateDatasetInfo={updateDatasetInfo}/>
        <Button
        colour={showDatasetInfo ? 'IndianRed' : 'ForestGreen'}
        text={showDatasetInfo ? 'Close' : 'Dataset Info'}
        onClick={() => setShowDatasetInfo(!showDatasetInfo)}
        disabled={!datasetSelected}
        />
      </div>
      {showDatasetInfo && <DatasetInfo datasetInfo={datasetInfo}/>}
    </div>
  )
}

export default DatasetOptions
