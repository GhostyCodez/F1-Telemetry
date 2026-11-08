import pandas as pd
import pytest

from telemetry_comparison import prepare_speed_trace


@pytest.mark.parametrize(
    "speed_kmh, expected_distance_m",
    [(0, 0), (36, 10), (72, 20)],
    ids=["stationary", "36-kmh", "72-kmh"],
)
def test_prepare_speed_trace_distance(speed_kmh, expected_distance_m):
    # Two samples one second apart make the expected distance easy to check.
    car_data = pd.DataFrame(
        {
            "date": [
                "2025-03-15T05:00:00.000Z",
                "2025-03-15T05:00:01.000Z",
            ],
            "speed": [speed_kmh, speed_kmh],
        }
    )

    trace = prepare_speed_trace(car_data)

    assert trace["distance_m"].tolist() == pytest.approx(
        [0, expected_distance_m]
    )