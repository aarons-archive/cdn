# Future
from __future__ import annotations

# Standard Library
import time

# My stuff
from core import values


worker_id_bits = 5
data_center_id_bits = 5
max_worker_id = -1 ^ (-1 << worker_id_bits)
max_data_center_id = -1 ^ (-1 << data_center_id_bits)
sequence_bits = 12
worker_id_shift = sequence_bits
data_center_id_shift = sequence_bits + worker_id_bits
timestamp_left_shift = sequence_bits + worker_id_bits + data_center_id_bits


def snowflake_to_timestamp(snowflake: int) -> int:

    snowflake >>= 22
    snowflake += values.EPOCH
    snowflake /= 1000
    return snowflake


def generate_snowflake(worker_id: int, data_center_id: int) -> int:

    assert 0 <= worker_id <= max_worker_id
    assert 0 <= data_center_id <= max_data_center_id

    timestamp = round(time.time()*1000)

    return ((timestamp - values.EPOCH) << timestamp_left_shift) | (data_center_id << data_center_id_shift) | (worker_id << worker_id_shift)
