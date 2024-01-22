import numpy as np


def calculate_frequency_of_dataset(dataset: list, sampling_rate=1):
    # Perform FFT
    fft_result = np.fft.fft(dataset)

    # Calculate frequencies corresponding to FFT result
    frequencies = np.fft.fftfreq(len(dataset), d=sampling_rate)

    # Calculate magnitude of FFT result
    magnitude = np.abs(fft_result)

    # Find index corresponding to the maximum magnitude (excluding DC component)
    max_freq_index = np.argmax(magnitude[1:]) + 1

    # Get the dominant frequency
    dominant_frequency = frequencies[max_freq_index]

    # Calculate a frequency score based on the dominant frequency
    frequency_score = 1 / (1 + np.abs(dominant_frequency))

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






