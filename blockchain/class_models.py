from typing import Any, Union


class BlockRange:
    from_block: Union[int, None]
    to_block: Union[int, None]

    def __init__(self, from_block: Union[int, None], to_block: Union[int, None]):
        self.from_block = from_block
        self.to_block = to_block


class CoingeckoPriceBreakout:
    day: int
    timestamp: int
    largest_price_move: float

    def __init__(self, day: int, timestamp: int, largest_price_move: float):
        """
        :param day: number of days to look before the start of a price breakout
        :param timestamp: start date of price breakout
        :param largest_price_move: Largest percent price move of token after price breakout
        """
        self.day = day
        self.timestamp = timestamp
        self.largest_price_move = largest_price_move


class Swap:
    sender: str
    transaction: dict[str, Any]
    side: str
    count: int
    amount: int

    def __init__(self, transaction: dict[str, Any], side: str, amount: int, sender: str = "", count: int = 1):
        """
        :param sender: Address of transaction creator
        :param transaction: Transaction data of swap
        :param side: buy or sell event
        :param amount: amount bought or sold
        :param count: number of swaps
        """
        self.transaction = transaction
        self.sender = sender
        self.side = side
        self.amount = amount
        self.count = count

        sides = ["buy", "sell"]
        if side not in sides:
            raise ValueError(f"{side} not a valid options. Choices are {sides}")
