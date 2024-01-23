import numpy as np


def abs_percent_change(value1, value2, decimal_places=2):

    change = abs(
        (value2 - value1) / value1
    ) * 100

    return round(change, decimal_places)


def calculate_avg_abs_percentage_change(data):
    n = len(data)

    # Calculate absolute percentage changes
    abs_percentage_changes = [abs((data[i] - data[i - 1]) / data[i - 1]) * 100 for i in range(1, n)]

    # Calculate average absolute percentage change
    avg_abs_percentage_change = sum(abs_percentage_changes) / (n - 1)

    return avg_abs_percentage_change


def calculate_oscillation_score(dataset: list):
    differences = np.diff(dataset)
    standard_deviation_of_differences = np.std(differences)
    frequency_score = 1 / (1 + standard_deviation_of_differences)
    return frequency_score


def get_average_percent_change(dataset: list):
    count = 0
    pattern = list()

    try:
        while count < len(dataset):
            # Get first two values of dataset and calculate its percent change
            pattern.append(
                abs_percent_change(dataset[count], dataset[count + 1])
            )
            count += 1
    except IndexError:
        pass

    return pattern


def normalize_dataset(dataset: list):
    min_value = min(dataset)
    max_value = max(dataset)
    return [(x - min_value) / (max_value - min_value) for x in dataset]


def volatility_of_dataset(dataset: list):
    normalized = normalize_dataset(dataset)
    standard_deviation = np.std(normalized)
    coefficient_of_variable = (standard_deviation / np.mean(normalized)) * 100
    return coefficient_of_variable




