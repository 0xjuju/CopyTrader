import numpy as np


def volatility_of_dataset(dataset: list):
    normalized = normalize_dataset(dataset)
    standard_deviation = np.std(normalized)
    coefficient_of_variable = (standard_deviation / np.mean(normalized)) * 100
    return coefficient_of_variable


def normalize_dataset(dataset: list):
    min_value = min(dataset)
    max_value = max(dataset)
    return [(x - min_value) / (max_value - min_value) for x in dataset]






