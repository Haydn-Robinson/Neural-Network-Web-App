"""
Routes and views for the flask application.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, Response, current_app, send_file, jsonify
import numpy as np
from pathlib import Path
from time import sleep
import os
import redis
from rq import Queue, Connection
from rq.job import Job
from .api import MachineLearningTask, do_network_training

blueprint = Blueprint('views', __name__)


def get_output(inputs):
    return np.array_str(inputs[1,:])

@blueprint.route('/about')
def about():
    """Renders the home/about page."""
    return render_template("about.html", title='About')


@blueprint.route('/examples')
def examples():
    """Renders the examples page."""
    return render_template("examples.html", title='Examples')

@blueprint.route('/')
@blueprint.route('/network-widget', methods=['GET', 'POST'])
def network_setup():
    """Renders the network training setup page."""
    if request.method == 'POST':
        return redirect(url_for('views.network_setup', dataset=request.form['dataset']))
    elif request.method == 'GET':  
        if request.args.get('dataset'):
            request_dict = request.args.to_dict(False)
            data_container = MachineLearningTask(request_dict)
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
            request_dict = request.args.to_dict(False)

            redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

            with Connection(redis.from_url(redis_url)):
                q = Queue()
                job = q.enqueue(do_network_training, request_dict)
                session['job_id'] = job.id

            return render_template("train_network.html", title='Train Network')
        else:
            return redirect(url_for('views.network_setup'))


@blueprint.route('/stream', methods=['GET', 'POST'])
def stream():
    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    with Connection(redis.from_url(redis_url)):
        job = Job.fetch(session['job_id'])

    def progress_stream(job):
        complete = False
        progress = 0

        while not complete:
            job.refresh()

            if 'progress' in job.meta:
                progress = job.meta['progress']
            else:
                progress = 0

            if job.is_finished:
                complete = True
                sleep(0.1)

            if not complete:
                event = 'progress'
            else:
                event = 'redirect'

            yield f"event:{event}\ndata:{progress}\n\n"
    
    return Response(progress_stream(job), mimetype='text/event-stream')
    

@blueprint.route('/network-widget/results')
def results():
    """Renders the network training results page."""
    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    with Connection(redis.from_url(redis_url)):
        job = Job.fetch(session['job_id'])
    path = Path(current_app.root_path + f'/static/dump.txt')
    dump_file = open(path, 'w')
    dump_file.write(job.meta['print_output'])
    dump_file.close()

    return render_template("results.html", title="Results")


@blueprint.route('/network-widget/results/download')
def get_training_summary():
    return send_file(f'{current_app.root_path}/static/dump.txt',
                     mimetype='text/plain',
                     attachment_filename='training_summary.txt',
                     as_attachment=True)


@blueprint.route('/network-widget/results/get_results')
def get_results():
    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    with Connection(redis.from_url(redis_url)):
        job = Job.fetch(session['job_id'])
    response = {'auroc': job.meta['auroc'], 'training_failed': job.meta['training_failed']}
    return jsonify(response)





