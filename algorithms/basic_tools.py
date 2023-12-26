

def flatten_list(data: list):
    flat_data = list()
    if len(data) > 1:
        if isinstance(data[0], list):
            for row in data:
                flat_data.extend(row)

    return flat_data if flat_data else data


