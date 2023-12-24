

# From dataset of prices from token chart, find all of the large percent changes within 1 week of day
def percent_difference_from_dataset(data: list) -> list[tuple]:
    results = list()

    for index, each in enumerate(data):
        # Default dataset values
        dataset = [0, 0, 0]

        # IndexError occurs when there is no data for a day vs the current num.
        # If we are looking at the last 100 days, day 99 will not be able to calculate data 3 days from then
        try:
            # difference between this day and next day
            next_day = data[index + 1]
            to_next_day_change = (next_day / each)
            dataset[0] = (to_next_day_change - 1) * 100

            # difference between this day and the third
            day_3 = data[index + 2]
            day_3_change = (day_3 / each)
            dataset[1] = (day_3_change - 1) * 100

            # difference between this day and the seventh
            day_7 = data[index + 7]
            day_7_change = (day_7 / each)
            dataset[2] = (day_7_change - 1) * 100

        # We expect to get error. Pass
        except IndexError:
            pass

        results.append(tuple(dataset))

    return results


