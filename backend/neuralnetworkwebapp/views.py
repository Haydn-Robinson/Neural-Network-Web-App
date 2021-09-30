"""
Routes and views for the flask application.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, Response, current_app, send_file, jsonify
import numpy as np
from pathlib import Path
from time import sleep
import json
import os
import redis
from rq import Queue, Connection
from rq.job import Job
from .hrpymlapi import do_network_training
import io

api = Blueprint('api', __name__)
public_routes = Blueprint('public', __name__)


@public_routes.route("/")
def index():
    return current_app.send_static_file('index.html')

@public_routes.app_errorhandler(404)
def page_not_found(error):
    return current_app.send_static_file('index.html')

# Endpoint to serve dataset metadata
@api.route('/api/datasetmetadata', methods=['GET'])
def get_dataset_metadata():
    path = Path(current_app.root_path) / './static/' / 'datasetMetadata.json'
    with open(path) as json_file:
        return jsonify(json.load(json_file))

# Endpoint to serve dataset info
@api.route('/api/datasetinfo/<datasetid>', methods=['GET'])
def get_dataset_info(datasetid):
    path = Path(current_app.root_path) / './static/' / 'datasetInfo.json'
    with open(path) as json_file:
        all_dataset_info = json.load(json_file)
    return all_dataset_info[datasetid]

# Endpoint to add network training task to queue
@api.route('/api/trainnetwork', methods=['POST'])
def register_task():
    if request.method == 'POST':
        params = request.get_json()
        redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

        path = Path(current_app.root_path) / './static/' / 'datasetInfo.json'
        with open(path) as json_file:
            all_dataset_info = json.load(json_file)
            dataset_info = all_dataset_info[params['datasetID']]

        with Connection(redis.from_url(redis_url)):
            q = Queue()
            job = q.enqueue(do_network_training, params, dataset_info)
            session['job_id'] = job.id
            return {'id': job.id}

# Endpoint to get task progress
@api.route('/api/progress', methods=['GET', 'POST'])
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
    
    return Response(progress_stream(job), mimetype='text/event-stream', headers={'Cache-Control': 'no-transform'})


@api.route('/api/trainingsummary')
def results():
    """Renders the network training results page."""
    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    #data_buffer = io.StringIO()
    with Connection(redis.from_url(redis_url)):
        job = Job.fetch(session['job_id'])
    #data_buffer.write(job.meta['print_output'])

    return Response(
        job.meta['print_output'],
        headers = {
            'Content-Type': 'text/plain; charset=utf-8',
            'Content-Disposition': "attachment; filename='training_summary.txt'"
        }
    )

@api.route('/api/results')
def get_results():
    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    with Connection(redis.from_url(redis_url)):
        job = Job.fetch(session['job_id'])
    response = {
        'auroc': job.meta['auroc'],
        'roc_curve': job.meta['roc_curve'],
        'training_failed': job.meta['training_failed']
    }
    return jsonify(response)