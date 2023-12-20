import time
import os
import pandas as pd
import yaml
import sys
import logging
from sklearn.model_selection import RepeatedStratifiedKFold, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import category_encoders as ce

# Get JOB_ID and BATCH_SIZE from environment variables
job_id = int(os.getenv('JOB_ID', 0))
dataset_folder = os.getenv('DATA_FOLDER', '/mnt/datasets')

# Set up logging configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add a FileHandler to log to a file
log_file_path = os.path.join(dataset_folder, f'car_evaluation_hyperparameter_tuning_{job_id}.log')
file_handler = logging.FileHandler(log_file_path)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

def get_hyperparams():
    with open(f"{dataset_folder}/hyperparameters.yml") as f:
        hyperparams_list = yaml.safe_load(f)
        if job_id >= len(hyperparams_list):
            logger.info(
                f"Invalid JOB_ID: {job_id}. JOB_ID should be between 0 and {len(hyperparams_list) - 1}.")
            sys.exit(1)
        return hyperparams_list[job_id]


def train(X_train, X_test, y_train, y_test, params):
    cv = RepeatedStratifiedKFold(n_splits=10, n_repeats=5, random_state=1)
    # find the best model
    model = GridSearchCV(
        RandomForestClassifier(), params, n_jobs=-1, cv=cv, error_score='raise', verbose=1)
    model.fit(X_train, y_train)
    # pred on test set and report accuracy
    y_pred = model.predict(X_test)
    score = accuracy_score(y_test, y_pred)
    return {
        'model': model.best_estimator_,
        'params': model.best_params_,
        'score': score
    }

def transform_data(X_train, X_test):
    encoder = ce.OrdinalEncoder(cols=['buying', 'maint', 'doors', 'persons', 'lug_boot', 'safety'])
    X_train = encoder.fit_transform(X_train)
    X_test = encoder.transform(X_test)
    return X_train, X_test

if __name__ == "__main__":
    file_path_data = f'{dataset_folder}/data.csv'
    df = pd.read_csv(file_path_data)
    params = get_hyperparams()
    logger.info(f"Performing grid  hyperparameters at index {job_id}: {params}")

    col_names = ['buying', 'maint', 'doors', 'persons', 'lug_boot', 'safety', 'class']
    df.columns = col_names
    X = df.drop(['class'], axis=1)
    y = df['class']
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.33, random_state=42)
    X_train, X_test = transform_data(X_train, X_test)

    start_time = time.time()
    summary = train(X_train, X_test, y_train, y_test, params)
    logger.info(f"Model: {summary['model']}")
    logger.info(f"Best Parameters: {summary['params']}")
    logger.info(f"Accuracy Score: {summary['score']}")
    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"Total Elapsed Time: {elapsed_time} seconds")
