import { useState } from 'react'
import { AiOutlineQuestionCircle } from 'react-icons/ai'
import AlgorithmToolTip from './AlgorithmTooltip'

function TrainingParameterOptions({
  l2Param, setL2Param, optimiser, setOptimiser,
  miniBatchSize, setMiniBatchSize, epochs, setEpochs,
  learningRate, setLearningRate, momentumParam, setMomentumParam, searchL2Param
}) {
  const [showAlgorithmInfo, setshowAlgorithmInfo] = useState(false)


  return (
    <div className='trainingparam-options'>
      {showAlgorithmInfo && <AlgorithmToolTip/>}
      <table>
        <tbody>
          <tr>
            <td><label style={{color: searchL2Param ? 'gainsboro' : 'black'}}>L2 Parameter:</label></td>
            <td>
              <input
                type="number"
                step="0.00001"
                size="8"
                min="0"
                value={l2Param}
                onChange={(e) => setL2Param(e.target.value)}
                disabled={searchL2Param}
              />
            </td>
          </tr>
          <tr>
            <td><label>Algorithm:</label></td>
            <td>
              <select value={optimiser} onChange={(e) => setOptimiser(e.target.value)}>
                <option key='1' value="sgd">SGD</option>
                <option key='2' value="nag">NAG</option>
                {/* <option value="adam" disabled>ADAM</option> */}
              </select>
              <AiOutlineQuestionCircle
                className='algorithm-info'
                color = {showAlgorithmInfo ? 'RoyalBlue' : 'black'}
                onClick={() => {setshowAlgorithmInfo(!showAlgorithmInfo)}}
                />
            </td>
          </tr>
          <tr>
          <td><label>Mini-Batch Size:</label></td>
          <td>
              <input
                type="number"
                step="1" min="1"
                size="8"
                value={miniBatchSize}
                onChange={(e) => setMiniBatchSize(e.target.value)}
              />
            </td>
          </tr>
          <tr>
            <td><label>Epochs:</label></td>
            <td>
              <input
                type="number"
                step="1"
                min="1"
                size="8"
                value={epochs}
                onChange={(e) => setEpochs(e.target.value)}
              />
            </td>
          </tr>
          <tr>
            <td><label>Learning Rate:</label></td>
          <td>
              <input
                type="number"
                step="0.0005"
                min="0.0005"
                size="8"
                value={learningRate}
                onChange={(e) => setLearningRate(e.target.value)}
              />
            </td>
          </tr>
          <tr>
            <td><label style={{color: optimiser !== 'nag' ? 'gainsboro' : 'black'}}>Momentum Parameter:</label></td>
            <td>
              <input
                type="number"
                step="0.05"
                min="0"
                max="1"
                size="8"
                value={momentumParam}
                onChange={(e) => setMomentumParam(e.target.value)}
                disabled={optimiser !== 'nag'}
              />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  )
}

export default TrainingParameterOptions
