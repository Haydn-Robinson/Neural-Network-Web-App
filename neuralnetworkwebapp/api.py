import numpy as np
import pandas as pd
from pathlib import Path
import csv
from functools import wraps
import io
import sys
import matplotlib.pyplot as plt
from machinelearningpython.neuralnetwork.network import Network
from machinelearningpython.neuralnetwork.modelselection import hyperparameter_search, _generate_search_cases
from machinelearningpython.utilities.preprocessing import dataframe_to_inputs_targets, normalise_data, principle_components_analysis, data_preprocessing
from machinelearningpython.utilities.split import stratified_split
from machinelearningpython.evaluate import classifier as evcls


def capture_print(func):
    @wraps(func)
    def with_print_capture(self, *args, **kwargs):
        sys.stdout = self.BUFFER
        output = func(self, *args, **kwargs)
        sys.stdout = sys.__stdout__
        return output
    return with_print_capture


class MachineLearningTask:

    def __init__(self):

        self.DATA_SET_OUTPUT_FUNCTION = {'skl_moons': 'sigmoid',
                                         'titanic': 'sigmoid',
                                         'pima_indians_diabetes': 'sigmoid',
                                         'cifar10': 'softmax'
                                         }

        self.DATA_SET_INPUT_OUTPUT_COUNT = {'skl_moons': (2,1),
                                            'titanic': (2,1),
                                            'pima_indians_diabetes': (8,1),
                                            'cifar10': (100,10)
                                            }

        self.DATA_SET_TEST_PROPORTION = {'skl_moons': 0.5,
                                         'titanic': 0.2,
                                         'pima_indians_diabetes': 0.2,
                                         'cifar10': 0.2
                                         }


    def initialise(self, request, root_path):
        self.dataset_id = request['dataset'][0]
        self.inputs, self.targets = self._get_data(request['dataset'][0], root_path)


    def _get_data(self, data_id, root_path):
        """ Load the dataset specified in the supplied flask request object from file """
        path = Path(root_path + f'\static\datasets\{data_id}.csv')
        dataframe = pd.read_csv(path)
        inputs, targets = dataframe_to_inputs_targets(dataframe, *self.DATA_SET_INPUT_OUTPUT_COUNT[data_id])
        return inputs, targets


class TrainNetwork(MachineLearningTask):

    def __init__(self):
        super().__init__()


    def initialise(self, request, root_path):
        super().initialise(request, root_path)
        self.BUFFER = io.StringIO()
        self.complete = False
        self.network_parameters = self._get_network_parameters(request)
        self.training_parameters = self._get_training_parameters(request)
        self.optimiser_parameters = self._get_optimiser_parameters(request)


    def _get_network_parameters(self, request):
        """" Process flask request object and produce network parameter dictionary"""

        # Process flask request object
        dataset=request['dataset'][0]
        neurons = [int(val) for val in request["hidden_layer_neurons"]]
        neurons.insert(0, self.DATA_SET_INPUT_OUTPUT_COUNT[dataset][0])
        neurons.append(self.DATA_SET_INPUT_OUTPUT_COUNT[dataset][-1])

        # Build network parameter dictionary
        return {'network_structure': tuple(neurons),
                'hidden_layer_function': request["activation_function"][0],
                'output_function': self.DATA_SET_OUTPUT_FUNCTION[dataset]
                }


    def _get_training_parameters(self, request):
        """" Process flask request object and produce training parameter dictionary"""

        # Process flask request object
        dataset=request['dataset'][0]

        data_preprocessors = []
        if 'normalise' in request:
            data_preprocessors.append('normalise')
        if 'pca' in request:
            data_preprocessors.append('pca')

        if request['l2_param'][0] == 'search':
            l2_param = np.concatenate((np.array([0]), np.logspace(-5, 2, 8)))
            fold_count = int(request['fold_count'][0])
            self.search = True
        else:
            l2_param = float(request['l2_param'][0])
            fold_count = None
            self.search = False

        # Build training parameter dictionary
        return {'fold_count': fold_count,
                'optimiser': request['algorithm'][0],
                'data_preprocessors': data_preprocessors,
                'l2_param': l2_param
                }


    def _get_optimiser_parameters(self, request):
        """" Process flask request object and produce optimiser parameter dictionary"""

        # Process flask request object
        if request['algorithm'][0] == 'nag':
            momentum_param = float(request['momentum_param'][0])
        else:
            momentum_param = None

        # Build optimiser parameter dictionary
        return {'mini_batch_size': int(request['mini_batch_size'][0]),
                'epochs': int(request['epochs'][0]),
                'learning_rate': float(request['learning_rate'][0]),
                'momentum_coefficient': momentum_param,
                'verbose': True,
                'learning_rate_decay_factor': 1,
                'learning_rate_decay_delay': 10,
                'learning_rate_decay_rate': 5
                }

    def get_buffer(self):
        return self.BUFFER

    def get_complete(self):
        return self.complete

    def get_search(self):
        return self.search

    def get_network_parameters(self):
        return self.network_parameters

    def get_training_parameters(self):
        return self.training_parameters

    def get_optimiser_parameters(self):
        return self.optimiser_parameters

    def get_search_case_count(self):
        return self.search_case_count

    @capture_print
    def run(self):
        """ Train network """

        # Split Data
        training_indicies, test_indicies = stratified_split(self.targets, self.DATA_SET_TEST_PROPORTION[self.dataset_id])

        # Preprocess inputs
        preprocessed_training_inputs, preprocessed_test_inputs, self.preprocessing_params = data_preprocessing(self.inputs[training_indicies, ...],
                                                                                                               self.inputs[test_indicies, ...],
                                                                                                               self.training_parameters['data_preprocessors'])
        # Train Network
        if not self.search:
            self.search_case_count = 1
            self.network = Network(**self.network_parameters)
            self.network.train(preprocessed_training_inputs, self.targets[training_indicies, ...], self.training_parameters, self.optimiser_parameters)
        
        # Train Network with hyperparameter optimisation
        else:
            self.search_case_count = len(_generate_search_cases(self.network_parameters, self.training_parameters))
            scores, combinations = hyperparameter_search(self.inputs[training_indicies, ...], self.targets[training_indicies, ...], self.network_parameters, self.training_parameters, self.optimiser_parameters)
            best_combination = combinations[0]
            self.training_parameters['l2_param'] = best_combination['l2_param']
            self.network = Network(**self.network_parameters)
            self.network.train(preprocessed_training_inputs, self.targets[training_indicies, ...], self.training_parameters, self.optimiser_parameters)


        # Evaluate
        test_model_outputs = self.network.feedforward(preprocessed_test_inputs)
        tprs, fprs, accuracies, thresholds = evcls.roc_curve(test_model_outputs, self.targets[test_indicies, ...], plot=False)
        auroc = evcls.auroc(test_model_outputs, self.targets[test_indicies, ...])
        print(f'\nAUROC: {auroc}\n')
        threshold, tpr, fpr, accuracy = evcls.choose_threshold(tprs, fprs, accuracies, thresholds)
        print(f'\nmax accuracy:\t{accuracy}\ntpr:\t{tpr}\nfpr:\t{fpr}\nthreshold:\t{threshold}\n\n')
        #plt.show()

        self.complete = True
