import {useEffect, useState} from 'react'

function SelectDataset({updateDatasetInfo}) {
  const [datasetMetadata, setDatasetMetadata] = useState([])

  useEffect(() => {
    const getDatasetMetadata = async () => {
      const res = await fetch('/api/datasetmetadata')
      const metadata = await res.json()
      setDatasetMetadata(metadata)
    }
    getDatasetMetadata();
  },[])

  return (
    <div className='select-dataset'>
      <form>
          <label>Select a dataset to model:</label>
          <select onChange={(e) => updateDatasetInfo(e.target.value)}>
            <option value='' hidden>Select Dataset</option>
            {datasetMetadata.map((metadata) => <option key={metadata.id} value={metadata.id}>{metadata.name}</option>)}
          </select>
      </form>
    </div>
  )
}

export default SelectDataset
