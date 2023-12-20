import os
import sys
import time
import yaml
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.metrics import mean_absolute_error
from concurrent.futures import ThreadPoolExecutor
import logging

# Get JOB_ID and BATCH_SIZE from environment variables
job_id = int(os.getenv('JOB_ID', 0))
batch_size = int(os.getenv('BATCH_SIZE', 20))
dataset_folder = os.getenv('DATA_FOLDER', '/mnt/datasets')

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add a FileHandler to log to a file
log_file_path = os.path.join(dataset_folder, f'spotify_song_hyperparameter_tuning_{job_id}_{batch_size}.log')
file_handler = logging.FileHandler(log_file_path)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

models_to_search = [
    GradientBoostingRegressor(),
    ExtraTreesRegressor(),
]


def read_hyperparameters(file_path):
    with open(file_path) as f:
        hyperparams_list = yaml.safe_load(f)
    return hyperparams_list


def train_model(model, X_train, y_train, hyperparams_for_model, X_test, y_test):
    # Create a new instance of the model
    model = model.__class__(**model.get_params())
    model.set_params(**hyperparams_for_model)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_pred_rounded = np.round(y_pred)
    mae = mean_absolute_error(y_test, y_pred_rounded)
    return model, hyperparams_for_model, mae


def train_and_evaluate_model(X_train, X_test, y_train, y_test, hyperparams):
    best_model_info = {'model': None, 'params': None, 'mae': float('inf')}
    for model in models_to_search:
        valid_params = model.get_params().keys()
        hyperparams_for_model = {
            key: value for key, value in hyperparams.items() if key in valid_params}
        model, params, mae = train_model(
            model, X_train, y_train, hyperparams_for_model, X_test, y_test)

        # Update the best_model_info if the current model has lower MAE
        if mae < best_model_info['mae']:
            best_model_info['model'] = model
            best_model_info['params'] = params
            best_model_info['mae'] = mae

    return best_model_info


if __name__ == "__main__":
    logger.info(f"Processing job {job_id} with batch size {batch_size}")
    # Load the dataset for training
    file_path_data = f'{dataset_folder}/data.csv'
    data = pd.read_csv(file_path_data)

    # Define features (X) and target variable (y)
    X = data.drop('track_popularity', axis=1)
    X = X.select_dtypes(exclude=['object'])
    y = data['track_popularity']

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Load hyperparameters from YAML file
    hyperparams_list = read_hyperparameters(
        f'{dataset_folder}/hyperparameters.yml')

    if job_id >= len(hyperparams_list):
        logger.info(
            f"Invalid JOB_ID: {job_id}. JOB_ID should be between 0 and {len(hyperparams_list) - 1}.")
        sys.exit(1)

    start_index = job_id
    end_index = len(hyperparams_list)
    step_size = batch_size

    best_model_info = {'model': None, 'params': None, 'mae': float('inf')}

    start_time = time.time()
    # Use thread pool for parallel processing
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for idx in range(start_index, end_index, step_size):
            hyperparams = hyperparams_list[idx]
            logger.info(
                f"Processing Hyperparameter Set {idx + 1}/{len(hyperparams_list)}")
            futures.append(executor.submit(
                train_and_evaluate_model,
                X_train_scaled,
                X_test_scaled,
                y_train,
                y_test,
                hyperparams
            ))

        # Wait for all tasks to complete
        for future in futures:
            result = future.result()
            # Compare with inter-model best
            if result['mae'] < best_model_info['mae']:
                best_model_info = result

    logger.info(f"Best Model: {best_model_info['model']}")
    logger.info(f"Best Parameters: {best_model_info['params']}")
    logger.info(f"Lowest Mean Absolute Error: {best_model_info['mae']}")
    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"Total Elapsed Time: {elapsed_time} seconds")
