def chunk_list(data: list, size: int) -> list[list]:
    """Splits a list into chunks of a specified size."""
    return [data[i:i + size] for i in range(0, len(data), size)]
