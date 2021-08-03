
function datasetSwitch(data_id) {

    switch (data_id) {

        case 'skl_moons':
            document.getElementById('normalise').checked = false;
            document.getElementById('pca').checked = false;
            setHiddenLayers(['16', '8', '4', '2'])
            document.getElementById('activation-function').value = 'relu';
            document.getElementById('l2-param-check').checked = false;
            document.getElementById('fold-count').disabled = true;
            document.getElementById("fold-count-label").style.color = "LightGray";
            document.getElementById('fold-count').value = 5;
            document.getElementById('l2-param-value').disabled = false;
            document.getElementById("l2-param-value-label").style.color = "Black";
            document.getElementById('l2-param-value').value = 0.8;
            document.getElementById('optimisation-algorithm').value = 'nag';
            document.getElementById('mini-batch-size').value = 100;
            document.getElementById('epochs').value = 30000;
            document.getElementById('learning-rate').value = 0.005;
            document.getElementById('momentum-param').disabled = false;
            document.getElementById('momentum-param').value = 0.9;
            document.getElementById("momentum-param-label").style.color = "Black";
            break;

        case 'pima_indians_diabetes':
            document.getElementById('normalise').checked = true;
            document.getElementById('pca').checked = true;
            setHiddenLayers(['100'])
            document.getElementById('activation-function').value = 'relu';
            document.getElementById('l2-param-check').checked = true;
            document.getElementById('fold-count').disabled = false;
            document.getElementById("fold-count-label").style.color = "Black";
            document.getElementById('fold-count').value = 5;
            document.getElementById('l2-param-value').disabled = true;
            document.getElementById("l2-param-value-label").style.color = "LightGray";
            document.getElementById('l2-param-value').value = 1;
            document.getElementById('optimisation-algorithm').value = 'nag';
            document.getElementById('mini-batch-size').value = 30;
            document.getElementById('epochs').value = 100;
            document.getElementById('learning-rate').value = 0.001;
            document.getElementById('momentum-param').disabled = false;
            document.getElementById('momentum-param').value = 0.9;
            document.getElementById("momentum-param-label").style.color = "Black";
            break;

    }
}


function setHiddenLayers(layerNeuronCounts) {
    const hiddenLayers = document.getElementById('neuron-inputs--container')

    // Ensure there are no existing layers
    while (hiddenLayers.children.length > 0) {
        hiddenLayers.removeChild(hiddenLayers.lastChild);
}
    // Add the layers
    for (layerNeuronCount of layerNeuronCounts) {
        var input = document.createElement("input");
        input.type = "number";
        input.step = "1";
        input.min = "1";
        input.name = "layer_neurons";
        input.size = "4"
        input.max = "9999"
        input.value = layerNeuronCount
        hiddenLayers.appendChild(input)
    }
}





