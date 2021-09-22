import Button from "../common/Button"

function NetworkOptions({activationFunc, setActivationFunc, hiddenLayers, setHiddenLayers}) {

  const addLayer = () => {
    const temp = [...hiddenLayers]
    temp.push(10)
    setHiddenLayers(temp);
  }

  const removeLayer = () => {
    if (hiddenLayers.length > 1) {
      const temp = [...hiddenLayers]
      temp.pop(10)
      setHiddenLayers(temp);
    }
  }

  const updateLayer = (index, value) => {
    const temp = [...hiddenLayers]
    temp[index] = value;
    setHiddenLayers(temp);
  }


  return (
    <div className='network-options'>
      <div>
        <label>Activation Function:</label>
        <select value={activationFunc} onChange={(e) => setActivationFunc(e.target.value)}>
          <option key='1' value="relu">ReLu</option>
          <option key='2' value="sigmoid">Sigmoid</option>
          <option key='3' value="tanh">Tanh</option>
        </select>
      </div>
      <div>
        <Button
          colour='ForestGreen'
          text='Add Layer'
          onClick={addLayer}
        />
        <Button
          colour='IndianRed'
          text='Remove Layer'
          onClick={removeLayer}
          disabled={false}
        />
      </div>
      <div>
        <p>No. hidden layers: {hiddenLayers.length}</p>
        {hiddenLayers.map((neuronCount, index) => (
          <div key={index}>
            <input
              id={index}
              type="number"
              min="1"
              step="1"
              size="4"
              max="9999"
              value={neuronCount}
              onChange={(e) => updateLayer(parseInt(e.target.id), e.target.value)}
            />
            <p>neurons in layer [{index + 1}]</p>
          </div>))}
      </div>
    </div>
  )
}

export default NetworkOptions
