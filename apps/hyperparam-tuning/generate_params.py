import yaml
import itertools
import os


def generate_hyperparameters(param_names, *param_values):
    hyperparameters = list(itertools.product(*param_values))
    hyperparam_list = []

    for idx, params in enumerate(hyperparameters):
        hyperparam_dict = {'index': idx}
        for param_name, param_value in zip(param_names, params):
            hyperparam_dict[param_name] = param_value
        hyperparam_list.append(hyperparam_dict)

    return hyperparam_list


if __name__ == "__main__":
    # Define hyperparameter names and ranges
    output_file = os.getenv('OUTPUT_FILE', '../datasets/hyperparameters.yml')
    param_names = os.getenv(
        'PARAM_NAMES', 'n_estimators,max_depth,min_samples_split,min_samples_leaf').split(',')
    n_estimators = list(
        map(int, os.getenv('N_ESTIMATORS', '50,100,150').split(',')))
    max_depth = list(map(lambda x: None if x == 'None' else int(
        x), os.getenv('MAX_DEPTH', 'None,10,20').split(',')))
    min_samples_split = list(
        map(int, os.getenv('MIN_SAMPLES_SPLIT', '2,5,10').split(',')))
    min_samples_leaf = list(
        map(int, os.getenv('MIN_SAMPLES_LEAF', '1,2,4').split(',')))

    # Generate hyperparameters with an index
    hyperparams_list = generate_hyperparameters(
        param_names, n_estimators, max_depth, min_samples_split, min_samples_leaf)

    # Save hyperparameters to YAML file
    with open(output_file, 'w') as f:
        yaml.dump(hyperparams_list, f)

    print(f"Hyperparameters generated and saved to {output_file}.")
