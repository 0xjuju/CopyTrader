

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


