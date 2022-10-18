

from web3.exceptions import TransactionNotFound


def transaction_not_found_exception(func):

    def wrapper(*args, **kwargs):
        try:  # Check if Transaction hash exits
            return func(*args, **kwargs)
        except TransactionNotFound:
            return None  # Return None if a transaction hash was not found
        except ValueError:  # String is not a hexstring
            return None

    return wrapper


def check_keyword_args(func):
    def wrapper(*args, **kwargs):

        # using from_block and to_block will not raise error when max block range is exceeded. Address filter is ignored
        if kwargs.get("from_block") or kwargs.get("to_block"):
            raise ValueError("Use fromBlock / toBlock keywords for log filters")

        from_block = kwargs.get("fromBlock")
        to_block = kwargs.get("toBlock")
        if from_block and to_block and from_block > to_block:
            raise ValueError("from_block cannot be greater than to_block")

        return func(*args, **kwargs)

    return wrapper



