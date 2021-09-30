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


class TrainNetwork():

    def __init__(self, params, data_url, dataset_params):
        self.inputs, self.targets = self._get_data(data_url, *dataset_params["inputOutputCount"])
        self.BUFFER = io.StringIO()
        self.complete = False
        self.network_parameters = self._get_network_parameters(params, dataset_params)
        self.training_parameters = self._get_training_parameters(params)
        self.optimiser_parameters = self._get_optimiser_parameters(params)
        self.search_case_count = len(_generate_search_cases(self.network_parameters, self.training_parameters))
        self.test_prop = dataset_params["testProportion"]

    def _get_data(self, data_url, input_count, output_count):
        """ Load the dataset at the given url and split into inputs and targets """
        dataframe = pd.read_csv(data_url)
        inputs, targets = dataframe_to_inputs_targets(dataframe, input_count, output_count)
        return inputs, targets

    def _get_network_parameters(self, params, dataset_params):
        """" Process flask request object and produce network parameter dictionary"""

        # Extract parameters
        neurons = params['hiddenLayers']
        neurons.insert(0, dataset_params["inputOutputCount"][0])
        neurons.append(dataset_params["inputOutputCount"][1])

        # Build network parameter dictionary
        return {'network_structure': tuple(neurons),
                'hidden_layer_function': params["activationFunc"],
                'output_function': dataset_params["outputFunction"]
                }

    def _get_training_parameters(self, params):
        """" Process params dict passed from frontend and produce training parameter dictionary"""

        data_preprocessors = []
        if params['normalise']:
            data_preprocessors.append('normalise')
        if params['usePCA']:
            data_preprocessors.append('pca')

        if params['searchL2Param']:
            l2_param = np.concatenate((np.array([0]), np.logspace(-5, 2, 8)))
            fold_count = params['foldCount']
            self.search = True
        else:
            l2_param = params['l2Param']
            fold_count = None
            self.search = False

        # Build training parameter dictionary
        return {'fold_count': fold_count,
                'optimiser': params['optimiser'],
                'data_preprocessors': data_preprocessors,
                'l2_param': l2_param
                }

    def _get_optimiser_parameters(self, params):
        """" Process params dict passed from frontend and produce optimiser parameter dictionary"""

        # Process flask params object
        if params['optimiser'] == 'nag':
            momentum_param = params['momentumParam']
        else:
            momentum_param = None

        # Build optimiser parameter dictionary
        return {'mini_batch_size': params['miniBatchSize'],
                'epochs': params['epochs'],
                'learning_rate': params['learningRate'],
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
        training_indicies, test_indicies = stratified_split(self.targets, self.test_prop)

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


def do_network_training(params, dataset_info):
    job = get_current_job()
    train_network_task = TrainNetwork(params, dataset_info['url'], dataset_info['datasetParams'])
    monitor_thread = Thread(target=monitor_progress, args=[train_network_task, job])
    monitor_thread.start()
    print('START')
    train_network_task.run()
    print('END')
    monitor_thread.join()
    job.meta['auroc'] = train_network_task.auroc
    job.meta['roc_curve'] = train_network_task.roc_curve
    job.meta['training_failed'] = train_network_task.training_failed
    job.meta['print_output'] = train_network_task.BUFFER.getvalue()
    job.save_meta()



