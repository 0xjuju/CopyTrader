import numpy as np


def calculate_oscillation_score(dataset: list, sampling_rate=1):
    differences = np.diff(dataset)
    standard_deviation_of_differences = np.std(differences)
    frequency_score = 1 / (1 + standard_deviation_of_differences)
    return frequency_score


def volatility_of_dataset(dataset: list):
    normalized = normalize_dataset(dataset)
    standard_deviation = np.std(normalized)
    coefficient_of_variable = (standard_deviation / np.mean(normalized)) * 100
    return coefficient_of_variable


def normalize_dataset(dataset: list):
    min_value = min(dataset)
    max_value = max(dataset)
    return [(x - min_value) / (max_value - min_value) for x in dataset]






