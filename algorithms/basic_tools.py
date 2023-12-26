

def flatten_list(data: list):
    flat_data = list()

    if data and isinstance(data[0], list):
        if len(data) > 1:
            for row in data:
                flat_data.extend(row)
        else:
            data = data[0]

    return flat_data if flat_data else data






