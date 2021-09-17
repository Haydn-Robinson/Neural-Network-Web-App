import { useState } from 'react'
import NetworkOptions from "./NetworkOptions"
import CollapseSection from "./CollapseSection"
import DataPreprocessing from "./DataPreprocessing"
import HyperparametersearchOptions from "./HyperparametersearchOptions"
import TrainingParameterOptions from "./TrainingParameterOptions"
import Button from "./Button"

function TrainingOptions({datasetSelected, datasetInfo}) {
  // Collapsibles state
  const [showPreprocessing, setShowPreprocessing] = useState(false)
  const [showNetOpts, setShowNetOpts] = useState(false)
  const [showHypSearch, setShowHypSearch] = useState(false)
  const [showTrainParams, setShowTrainParams] = useState(false)

  // Training options state
  const [normalise, setNormalise] = useState(false)
  const [usePCA, setUsePCA] = useState(false)
  const [activationFunc, setActivationFunc] = useState('relu')
  const [hiddenLayers, setHiddenLayers] = useState([10])
  const [searchL2Param, setSearchL2Param] = useState(false)
  const [foldCount, setFoldCount] = useState(5)
  const [l2Param, setL2Param] = useState(0)
  const [optimiser, setOptimiser] = useState('sgd')
  const [miniBatchSize, setMiniBatchSize] = useState(30)
  const [epochs, setEpochs] = useState(50)
  const [learningRate, setLearningRate] = useState(0.001)
  const [momentumParam, setMomentumParam] = useState(0.9)


  const loadSuggestedOptions = async (optionsToLoad) => {
    setNormalise(optionsToLoad.normalise)
    setUsePCA(optionsToLoad.usePCA)
    setActivationFunc(optionsToLoad.activationFunc)
    setHiddenLayers(optionsToLoad.hiddenLayers)
    setSearchL2Param(optionsToLoad.searchL2Param)
    setFoldCount(optionsToLoad.foldCount)
    setL2Param(optionsToLoad.l2Param)
    setOptimiser(optionsToLoad.optimiser)
    setMiniBatchSize(optionsToLoad.miniBatchSize)
    setEpochs(optionsToLoad.epochs)
    setLearningRate(optionsToLoad.learningRate)
    setMomentumParam(optionsToLoad.momentumParam)
  }

  const makeParamsObject = () => {
    const params = {
      "normalise": normalise,
      "usePCA": usePCA,
      "activationFunc": activationFunc,
      "hiddenLayers": hiddenLayers,
      "searchL2Param": searchL2Param,
      "foldCount": foldCount,
      "l2Param": l2Param,
      "optimiser": optimiser,
      "miniBatchSize": miniBatchSize,
      "epochs": epochs,
      "learningRate": learningRate,
      "momentumParam": momentumParam,
    }
    return params
  }

  const trainNetwork = async () => {
    const params = makeParamsObject()
    const res = await fetch(`api/trainnetwork`, {
      method: 'POST',
      headers: {
          'Content-type': 'application/json'
      },
      body: JSON.stringify(params)
  })
    const id = await res.json()
  }

  return (
    <div>
      <h2>Training Options</h2>
      <div>
        <div>
          <CollapseSection
            title='Data Preprocessing Options'
            toggleCollapse={() => setShowPreprocessing(!showPreprocessing)}
            expanded={showPreprocessing}
          />
          {showPreprocessing && (
            <div className='options-container'>
              <DataPreprocessing
                normalise={normalise}
                setNormalise={setNormalise}
                usePCA={usePCA}
                setUsePCA={setUsePCA}
              />
            </div>
          )}
        </div>
        <div>
          <CollapseSection
            title='Network Hidden Layer Options'
            toggleCollapse={() => setShowNetOpts(!showNetOpts)}
            expanded={showNetOpts}
            />
          {showNetOpts && (
            <div className='options-container'>
              <NetworkOptions
                activationFunc={activationFunc}
                setActivationFunc={setActivationFunc}
                hiddenLayers={hiddenLayers}
                setHiddenLayers={setHiddenLayers}
              />
            </div>
          )}
        </div>
        <div>
          <CollapseSection
            title='Hyperparameter Search'
            toggleCollapse={() => setShowHypSearch(!showHypSearch)}
            expanded={showHypSearch}
            />
          {showHypSearch && (
            <div className='options-container'>
              <HyperparametersearchOptions
                searchL2Param={searchL2Param}
                setSearchL2Param={setSearchL2Param}
                foldCount={foldCount}
                setFoldCount={setFoldCount}
              />
            </div>
          )}
        </div>
        <div>
          <CollapseSection
            title='Training Parameters'
            toggleCollapse={() => setShowTrainParams(!showTrainParams)}
            expanded={showTrainParams}
            />
          {showTrainParams && (
            <div className='options-container'>
              <TrainingParameterOptions
                  l2Param={l2Param}
                  setL2Param={setL2Param}
                  optimiser={optimiser}
                  setOptimiser={setOptimiser}
                  miniBatchSize={miniBatchSize}
                  setMiniBatchSize={setMiniBatchSize}
                  epochs={epochs}
                  setEpochs={setEpochs}
                  learningRate={learningRate}
                  setLearningRate={setLearningRate}
                  momentumParam={momentumParam}
                  setMomentumParam={setMomentumParam}
                  searchL2Param={searchL2Param}
              />
            </div>
          )}
        </div>
      </div>
      <div className='form-control'>
        <Button
          colour='SlateBlue'
          text='Load Suggested Options'
          onClick={() => loadSuggestedOptions(datasetInfo.options)}
          disabled={!datasetSelected}
        />
        <Button
          colour='IndianRed'
          text='Train Network'
          onClick={trainNetwork}
          disabled={!datasetSelected}
        />
      </div>
    </div>
  )
}

export default TrainingOptions
