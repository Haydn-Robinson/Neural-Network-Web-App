"""
Routes and views for the flask application.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, Response, current_app, send_file
from jinja2 import Environment, FileSystemLoader
import numpy as np
from pathlib import Path
from threading import Thread
#from multiprocessing import Lock
#from multiprocessing.managers import BaseManager, DictProxy, AquirerProxy
import re
from time import sleep
from .persistence import get_manager
from .api import MachineLearningTask, TrainNetwork
import pickle

blueprint = Blueprint('views', __name__)


def get_output(inputs):
    return np.array_str(inputs[1,:])


def do_network_training(train_network_task, root_path):
    train_network_task.run()
    output = train_network_task.get_buffer().getvalue()
    print(output)
    path = Path(root_path + f'/static/dump.txt')
    dump_file = open(path, 'w')
    dump_file.write(output)
    dump_file.close()


def async_train_network(train_network_task, root_path):
    print('thread start')
    thread = Thread(target=do_network_training, args=[train_network_task, root_path])
    thread.start()
    return thread

def compute_progress(max_combinations, max_folds, max_epochs, combination, fold, epoch, search_done_flag, message):
    combination_matches = re.findall(r'Combination: [0-9]+', message)
    fold_matches = re.findall(r'fold [0-9]+', message)
    epoch_matches = re.findall(r'Epoch: +[0-9]+', message)

    if len(combination_matches) > 0:
        combination = int(combination_matches[-1].split(' ')[-1])
    if len(fold_matches) > 0:
        fold = int(fold_matches[-1].split(' ')[-1])
    if len(epoch_matches) > 0:
        epoch = int(epoch_matches[-1].split(' ')[-1])

    total_percent = 100 * (((combination-1)*max_folds*max_epochs +(fold-1)*max_epochs + epoch + max_epochs*int(search_done_flag)*int(max_combinations>1))
                     / (max_combinations*max_folds*max_epochs + max_epochs*int(max_combinations>1)))

    if combination == max_combinations or fold == max_folds or epoch == max_epochs:
        search_done_flag = True

    return round(total_percent), combination, fold, epoch, search_done_flag

@blueprint.route('/')
@blueprint.route('/about')
def about():
    """Renders the home/about page."""
    return render_template("about.html", title='About')


@blueprint.route('/examples')
def examples():
    """Renders the examples page."""
    return render_template("examples.html", title='Examples')


@blueprint.route('/network-widget', methods=['GET', 'POST'])
def network_setup():
    """Renders the network training setup page."""
    if request.method == 'POST':
        return redirect(url_for('views.network_setup', dataset=request.form['dataset']))
    elif request.method == 'GET':  
        if request.args.get('dataset'):
            request_dict = request.args.to_dict(False)
            data_container = MachineLearningTask()
            data_container.initialise(request_dict, current_app.root_path)
            inputs = data_container.inputs
            data_str = get_output(inputs)
            return render_template("setup_network.html", title="Network Setup", dataset=request.args.get('dataset'), data=data_str)
        else:
            return render_template("setup_network.html", title="Network Setup")
    
        
@blueprint.route('/network-widget/train', methods=['GET', 'POST'])
def train_network():
    """Renders the network training page."""
    if request.method == 'POST':
        session['setup_complete'] = True
        dataset = request.form["dataset"]
        normalise = False
        pca = False
        if request.form.get("normalise"):
            normalise = True            
        if request.form.get("pca"):
            pca = True
        hidden_layer_neurons = request.form.getlist("layer_neurons")
        activation_function= request.form["activation_function"]
        if request.form.get("l2_param_check"):
            l2_param = 'search'
        else:
            l2_param = request.form["l2_param"]
        fold_count = request.form.get("fold_count")
        momentum_param = request.form.get("momentum_param")
        mini_batch_size = request.form["mini_batch_size"]
        epochs = request.form["epochs"]
        learning_rate = request.form["learning_rate"]
        return redirect(url_for('views.train_network',
                                dataset= dataset,
                                normalise= normalise,
                                pca= pca,
                                hidden_layer_neurons = hidden_layer_neurons,
                                activation_function = activation_function,
                                algorithm= request.form.get("optimiser"),
                                mini_batch_size= mini_batch_size,
                                epochs= epochs,
                                learning_rate= learning_rate,
                                momentum_param= momentum_param,
                                l2_param= l2_param,
                                fold_count= fold_count))

    elif request.method == 'GET':

        if 'setup_complete' in session:
            session.pop('setup_complete', None)
            manager = get_manager(current_app)
            request_dict = request.args.to_dict(False)
            train_network_task = manager.TrainNetwork()
            train_network_task.initialise(request_dict, current_app.root_path)
            async_train_network(train_network_task, current_app.root_path)
            return render_template("train_network.html", title='Train Network')
        else:
            return redirect(url_for('views.network_setup'))


@blueprint.route('/stream', methods=['GET', 'POST'])
def stream():

    manager = get_manager(current_app)
    train_network_task = manager.TrainNetwork()

    train_params = train_network_task.get_training_parameters()
    print(train_params)
   
    if train_network_task.get_search():
        max_combinations = train_network_task.get_search_case_count()
        max_folds = train_network_task.get_training_parameters()['fold_count']
        max_epochs = train_network_task.get_optimiser_parameters()['epochs']
        print(f'Max combos: {max_combinations}, Max folds: {max_folds}, Max epochs: {max_epochs}')
    else:
        max_combinations = 1
        max_folds = 1
        max_epochs = train_network_task.get_optimiser_parameters()['epochs']

    def epoch_stream(train_network_task):
        prev_length = 0
        combination, fold, epoch = 1,1,0
        search_done_flag = False
        complete = False

        while True:
            message = train_network_task.get_buffer().getvalue()
            if len(message) > prev_length:
                total_percent, combination, fold, epoch, search_done_flag = compute_progress(max_combinations, max_folds, max_epochs,
                                                                                             combination, fold, epoch, search_done_flag, message[prev_length:])
                prev_length = len(message)

            if not complete:
                event = 'progress'
            else:
                event = 'redirect'

            if train_network_task.get_complete():
                complete = True
                sleep(0.1)

            yield f'event:{event}\ndata:{total_percent}\n\n'

    return Response(epoch_stream(train_network_task), mimetype='text/event-stream')
    


@blueprint.route('/network-widget/results')
def results():
    """Renders the network training results page."""

    return render_template("results.html", title="Results")

@blueprint.route('/network-widget/results/download')
def get_training_summary():
    return send_file(f'{current_app.root_path}/static/dump.txt',
                     mimetype='text/plain',
                     attachment_filename='training_summary.txt',
                     as_attachment=True)







