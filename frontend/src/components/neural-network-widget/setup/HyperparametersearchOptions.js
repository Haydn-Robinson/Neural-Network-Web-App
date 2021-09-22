function HyperparametersearchOptions({searchL2Param, setSearchL2Param, foldCount, setFoldCount}) {
  return (
    <div className='hyperparam-search'>
      <h3>Select Serach Parameters:</h3>
      <div className='checkbox-list'>
        <span>
          <input
            type="checkbox"
            checked={searchL2Param}
            onChange={() => setSearchL2Param(!searchL2Param)}
            />
            <label>L2 Parameter</label>
        </span>
      </div>
      <div>
      <label style={{color: searchL2Param ? 'black' : 'gainsboro'}}>Fold Count:</label>
      <input
        type="number"
        step="1"
        min="1"
        size="4"
        value={foldCount}
        onChange={(e) => setFoldCount(e.target.value)}
        disabled={!searchL2Param}/>
      </div>
    </div>
  )
}

export default HyperparametersearchOptions
