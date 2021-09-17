function DatasetInfo({datasetInfo}) {
  return (
    <div className='dataset-info'>
      <h3>Description</h3>
      <p>{datasetInfo.description}</p>
      <h3>Variables</h3>
      <ol>{datasetInfo.variables.map((variable, index) => <li key={index}>{variable}</li>)}</ol>
      <h3>Visualisation</h3>
      {datasetInfo.visualisation ? <p>Visualisation Goes here.</p> : <p>No visualisation is available for this dataset.</p>}
    </div>
  )
}

export default DatasetInfo
