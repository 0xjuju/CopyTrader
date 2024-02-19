from typing import Union


# From dataset of prices from token chart, find the largest percent changes within 1 week of day
def percent_difference_from_dataset(data: list[float]) -> list[list[float]]:
    """

    :param data: Daily Price history of token
    :return: Matrix
    """
    results = list()

    for index, each in enumerate(data):
        dataset = [0., 0., 0.]

        # IndexError occurs when there is no data for a day vs the current num.
        # If we are looking at the last 100 days, day 99 will not be able to calculate data 3 days from then
        try:

            # Matrix containing price of token 1 day, 2 days, and 7 days into the future from each token price
            dataset = [
                data[index + 1], data[index + 2], data[index + 7]
            ]

            # Get the percentage difference of each in dataset relative to the 'each' value
            dataset = [(i / each - 1) * 100 for i in dataset]

        except IndexError:  # We expect to get an index error for end of list
            pass

        results.append(dataset)

    return results


