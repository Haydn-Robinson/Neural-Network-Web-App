function DataPreprocessing({normalise, setNormalise, usePCA, setUsePCA}) {
  return (
    <div>
      <div className="checkbox-list">
        <span>
          <input
            type="checkbox"
            checked={normalise}
            onChange={() => setNormalise(!normalise)}
          />
          <label>Normalise Data</label>
        </span>
        <div>
          <input
            type="checkbox"
            checked={usePCA}
            onChange={() => setUsePCA(!usePCA)}
          />
          <label>Principle Components Analysis</label>
        </div>
      </div>
    </div>
  )
}

export default DataPreprocessing
