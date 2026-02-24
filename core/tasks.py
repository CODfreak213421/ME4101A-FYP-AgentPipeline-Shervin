import os
from celery import shared_task
import time

from core.models import datafile, agent_response

import matlab.engine

from django.conf import settings

import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model # type: ignore

from core.agent import app

@shared_task
def add(x, y):
    time.sleep(5)  # Simulate a long-running task
    return x + y

@shared_task
def psychoacoustics_pipeline(datafile_id):
    
    # Fetch data from database through ID 
    try:
        data_file = datafile.objects.get(id=datafile_id)
    except datafile.DoesNotExist:
        return f"Datafile with ID {datafile_id} does not exist."
    
    # Prepare arugments 
    base_dir = settings.BASE_DIR
    media_dir = os.path.join(base_dir, 'media')
    
    dataset_path = os.path.normpath(os.path.join(media_dir, str(data_file.upload)))
    file_full_name = data_file.filename[:-4]
    loudnessPath = os.path.join(base_dir, 'DataLoudness')
    sharpnessPath = os.path.join(base_dir, 'DataSharpness')
    
    # Matlab pipeline execution
    try:
        eng = matlab.engine.start_matlab()
    except Exception as e:
        return f"Failed to start MATLAB engine: {e}"

    eng.addpath(r"C:\Users\rockv\Desktop\NUS\NUS Y3S1\FYP\EXPERIMENT 2 Codes\AgentPipeline\mscripts", nargout=0)
    eng.psychoacoustics(dataset_path, file_full_name, loudnessPath, sharpnessPath, nargout=0)
    eng.quit()

    # Dictionary 
    gearbox_conditions = {
        0 : 'Broken',
        1 : 'Healthy',
        2 : 'Missing Tooth',
        3 : 'Root Crack',
        4 : 'Wear'
    }

    # Load LOUDNESS 1D CNN Model 
    loudness_model_path = os.path.join(base_dir, 'mlmodels', '1DCNN_25000.keras')
    loudness_model = load_model(loudness_model_path)

    # Prepare Extracted Loudness Data
    try:
        loudness_data_path = os.path.join(base_dir, 'DataLoudness', f'{file_full_name}_loudness.csv')
        loudness_data = pd.read_csv(loudness_data_path)
    except Exception as e:
        return f"Failed to load Loudness Data: {e}"

    # Perform Loudness evaluation 
    loudness_data = np.expand_dims(loudness_data, axis=2)
    loudness_predictions = loudness_model.predict(loudness_data)
    loudness_labels = np.argmax(loudness_predictions, axis=1)

    loudness_result = dict()
    for i in loudness_labels:
        condition = gearbox_conditions[int(i)]
        if condition in loudness_result:
            loudness_result[condition] += 1
        else:
            loudness_result[condition] = 1
    print("Loudness Evaluation: " + str(loudness_result))
    
    # Load Sharpness 1D CNN Model 
    sharpness_model_path = os.path.join(base_dir, 'mlmodels', '1DCNN_sharpness_25000.keras')
    sharpness_model = load_model(sharpness_model_path)

    # Prepare Extracted Sharpness Data 
    try:
        sharpness_data_path = os.path.join(base_dir, 'DataSharpness', f'{file_full_name}_sharpness.csv')
        sharpness_data = pd.read_csv(sharpness_data_path)
    except Exception as e:
        return f"Failed to load Loudness Data: {e}"
    
    # Perform Sharpness Evaluation 
    # Perform Loudness evaluation 
    sharpness_data = np.expand_dims(sharpness_data, axis=2)
    sharpness_predictions = sharpness_model.predict(sharpness_data)
    sharpness_labels = np.argmax(sharpness_predictions, axis=1)

    sharpness_result = dict()
    for i in sharpness_labels:
        condition = gearbox_conditions[int(i)]
        if condition in sharpness_result:
            sharpness_result[condition] += 1
        else:
            sharpness_result[condition] = 1
    print("Sharpness Evaluation: " + str(sharpness_result))

    # Feed into Agent Pipeline 
    langgraph_response = app.invoke(
        {
            "conversation_history":[""],
            "loudness_Data": str(loudness_result),
            "Sharpness_Data": str(sharpness_result),
        }
    )

    print(langgraph_response)
    # Update Model objects for agent response 
    try:
        agent_response_obj = agent_response.objects.create(
            file=data_file,
            response_text=str(langgraph_response.get('agent_response', 'No response text found')),
            actions_to_take=str(langgraph_response.get('agent_action', 'no actions found')),
            gear_Status=str(langgraph_response.get('gearbox_status', 'Unknown')),
        )
        data_file.status = 'Completed'
        data_file.save()
    except Exception as e:
        data_file.status = 'Failed'
        data_file.save()
        return f"Failed to update agent response model: {e}"


    return f"Psychoacoustics pipeline executed successfully. Data analysis complete. {agent_response_obj} created successfully."