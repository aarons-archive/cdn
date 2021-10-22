# Future
from __future__ import annotations

# Standard Library
import time

# Packages
import pendulum

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


def snowflake_to_datetime(id: int) -> pendulum.DateTime:

    timestamp = ((id >> 22) + values.EPOCH) / 1000
    return pendulum.from_timestamp(timestamp, tz="UTC")


def generate_snowflake(worker_id: int = 1, data_center_id: int = 1) -> int:

    assert 0 <= worker_id <= max_worker_id
    assert 0 <= data_center_id <= max_data_center_id

    return ((round(time.time() * 1000) - values.EPOCH) << timestamp_left_shift) | (data_center_id << data_center_id_shift) | (worker_id << worker_id_shift)
