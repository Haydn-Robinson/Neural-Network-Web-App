import numpy as np
import pandas as pd
from functools import wraps
import io
import sys
import re
from hrpyml.neuralnetwork.network import Network
from hrpyml.neuralnetwork.modelselection import hyperparameter_search, _generate_search_cases
from hrpyml.utilities.preprocessing import dataframe_to_inputs_targets, data_preprocessing
from hrpyml.utilities.split import stratified_split
from hrpyml.evaluate import classifier as evcls
from threading import Thread, Event
from rq import get_current_job


def capture_print(func):
    @wraps(func)
    def with_print_capture(self, *args, **kwargs):
        sys.stdout = self.BUFFER
        output = func(self, *args, **kwargs)
        sys.stdout = sys.__stdout__
        return output
    return with_print_capture


def compute_progress(max_combinations, max_folds, max_epochs, combination, fold, epoch, search_done_flag, message):
    combination_matches = re.findall(r'Combination: [0-9]+', message)
    fold_matches = re.findall(r'fold [0-9]+', message)
    epoch_matches = re.findall(r'Epoch: +[0-9]+', message)

    if len(combination_matches) > 0:
        combination = int(combination_matches[-1].split(' ')[-1])
        fold = 1
        epoch = 0
    if len(fold_matches) > 0:
        fold = int(fold_matches[-1].split(' ')[-1])
        epoch = 0
    if len(epoch_matches) > 0:
        epoch = int(epoch_matches[-1].split(' ')[-1])

    total_percent = 100 * (((combination-1)*max_folds*max_epochs + (fold-1)*max_epochs + epoch + max_epochs*int(search_done_flag)*int(max_combinations>1))
                     / (max_combinations*max_folds*max_epochs + max_epochs*int(max_combinations>1)))

    if combination == max_combinations and fold == max_folds and epoch == max_epochs:
        search_done_flag = True
        epoch = 0

    return round(total_percent), combination, fold, epoch, search_done_flag


class MachineLearningTask:

    def __init__(self, request):

        self.DATA_URL = {'skl_moons': ('https://gist.githubusercontent.com/Haydn-Robinson/'
                                       'e1e724ea6afa4a8c02959bbfcaf59ade/raw/'
                                       'bd7d1523a9823afc61c1aa730b70c5219a738808/skl_moons.csv'),

                         'pima_indians_diabetes': ('https://gist.githubusercontent.com/Haydn-Robinson/'
                                                   'a63cec7aadd91feb265b99c7b3fc02ed/raw/'
                                                   '6b2fa370a419a6be9184bebd5ba6dd23fd23705a/pima_indians_diabetes.csv'),
                        }

        self.DATA_SET_OUTPUT_FUNCTION = {'skl_moons': 'sigmoid',
                                         'pima_indians_diabetes': 'sigmoid',
                                         }

        self.DATA_SET_INPUT_OUTPUT_COUNT = {'skl_moons': (2,1),
                                            'pima_indians_diabetes': (8,1),
                                            }

        self.DATA_SET_TEST_PROPORTION = {'skl_moons': 0.5,
                                         'pima_indians_diabetes': 0.2,
                                         }

        self.dataset_id = request['dataset'][0]
        self.inputs, self.targets = self._get_data(request['dataset'][0])


    def _get_data(self, data_id):
        """ Load the dataset specified in the supplied flask request object from file """
        dataframe = pd.read_csv(self.DATA_URL[data_id])
        inputs, targets = dataframe_to_inputs_targets(dataframe, *self.DATA_SET_INPUT_OUTPUT_COUNT[data_id])
        return inputs, targets


class TrainNetwork(MachineLearningTask):

    def __init__(self, request):
        super().__init__(request)
        self.BUFFER = io.StringIO()
        self.complete = False
        self.network_parameters = self._get_network_parameters(request)
        self.training_parameters = self._get_training_parameters(request)
        self.optimiser_parameters = self._get_optimiser_parameters(request)
        self.search_case_count = len(_generate_search_cases(self.network_parameters, self.training_parameters))


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
            self.network = Network(**self.network_parameters)
            self.network.train(preprocessed_training_inputs, self.targets[training_indicies, ...], self.training_parameters, self.optimiser_parameters)
        
        # Train Network with hyperparameter optimisation
        else:
            scores, combinations = hyperparameter_search(self.inputs[training_indicies, ...], self.targets[training_indicies, ...], self.network_parameters, self.training_parameters, self.optimiser_parameters)
            best_combination = combinations[0]
            self.training_parameters['l2_param'] = best_combination['l2_param']
            self.network = Network(**self.network_parameters)
            self.network.train(preprocessed_training_inputs, self.targets[training_indicies, ...], self.training_parameters, self.optimiser_parameters)


        # Evaluate
        self.test_model_outputs = self.network.feedforward(preprocessed_test_inputs)
        self.roc_curve = evcls.binary_roc_curve(self.test_model_outputs, self.targets[test_indicies, ...])
        self.auroc = evcls.binary_auroc(self.test_model_outputs, self.targets[test_indicies, ...])
        if self.auroc <= 0.5:
            self.training_failed = True
        else:
            self.training_failed = False
        print(f'\nAUROC: {self.auroc}\n')
        threshold, tpr, fpr, accuracy = evcls.choose_threshold(**self.roc_curve)
        print(f'\nmax accuracy:\t{accuracy}\ntpr:\t{tpr}\nfpr:\t{fpr}\nthreshold:\t{threshold}\n\n')

        self.complete = True


def monitor_progress(train_network_task, rq_job):

    # Identify maximum values for combination, fold and epoch
    if train_network_task.search:
        max_combinations = train_network_task.search_case_count
        max_folds = train_network_task.training_parameters['fold_count']
        max_epochs = train_network_task.optimiser_parameters['epochs']
    else:
        max_combinations = 1
        max_folds = 1
        max_epochs = train_network_task.optimiser_parameters['epochs']

    # initialise counters
    prev_length = 0
    combination, fold, epoch = 1, 1, 0
    search_done_flag = False

    while not train_network_task.complete:
        Event().wait(0.1)
        message = train_network_task.BUFFER.getvalue()
        if len(message) > prev_length:
            total_percent, combination, fold, epoch, search_done_flag = compute_progress(max_combinations, max_folds, max_epochs,
                                                                                        combination, fold, epoch, search_done_flag, message[prev_length:])
            prev_length = len(message)
            rq_job.meta['progress'] = total_percent
            rq_job.save_meta()


def do_network_training(request_dict):
    job = get_current_job()
    train_network_task = TrainNetwork(request_dict)
    monitor_thread = Thread(target=monitor_progress, args=[train_network_task, job])
    monitor_thread.start()
    train_network_task.run()
    monitor_thread.join()
    job.meta['auroc'] = train_network_task.auroc
    job.meta['training_failed'] = train_network_task.training_failed
    job.meta['print_output'] = train_network_task.BUFFER.getvalue()
    job.save_meta()



