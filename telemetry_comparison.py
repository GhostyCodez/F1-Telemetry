import time

import matplotlib.pyplot as plt
import pandas as pd
import requests

API_URL = "https://api.openf1.org/v1"
SESSION_KEY = 9689


def fetch_data(endpoint, driver_number, date_filter=""):
    """Get one driver's data from the qualifying session."""
    url = (
        f"{API_URL}/{endpoint}"
        f"?session_key={SESSION_KEY}&driver_number={driver_number}{date_filter}"
    )
    time.sleep(0.4)  # Space out requests to stay within OpenF1's free limit.
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return pd.DataFrame(response.json())


def prepare_speed_trace(car_data):
    """Clean the speed samples and estimate distance from speed and time."""
    trace = car_data[["date", "speed"]].copy()
    trace["date"] = pd.to_datetime(trace["date"], utc=True, errors="coerce")
    trace["speed"] = pd.to_numeric(trace["speed"], errors="coerce")
    trace = trace.dropna().sort_values("date").drop_duplicates(subset="date")

    if len(trace) < 2:
        raise ValueError("Need at least two valid speed samples to plot a trace.")

    # Average speed between samples, converted from km/h to m/s.
    speed_mps = trace["speed"] / 3.6
    average_speed = (speed_mps + speed_mps.shift()) / 2
    seconds_between_samples = trace["date"].diff().dt.total_seconds()
    trace["distance_m"] = (average_speed * seconds_between_samples).fillna(0).cumsum()
    return trace


def main():
    drivers = [
        (4, "Lando Norris", "#c45200"),
        (81, "Oscar Piastri", "#0069a8"),
    ]
    fig, ax = plt.subplots(figsize=(12, 5))

    for number, name, colour in drivers:
        # Find the quickest timed lap with a start timestamp.
        laps = fetch_data("laps", number)
        timed_laps = laps.dropna(subset=["lap_duration", "date_start"])
        fastest = timed_laps.loc[timed_laps["lap_duration"].idxmin()]

        # Request only the speed samples recorded during that lap.
        duration = fastest["lap_duration"]
        start = pd.to_datetime(fastest["date_start"], utc=True)
        end = start + pd.to_timedelta(duration, unit="s")
        date_filter = (
            f"&date>={start.strftime('%Y-%m-%dT%H:%M:%S.%f')}"
            f"&date<={end.strftime('%Y-%m-%dT%H:%M:%S.%f')}"
        )
        car_data = fetch_data("car_data", number, date_filter)
        if car_data.empty:
            raise ValueError(f"OpenF1 returned no car data for {name}'s fastest lap.")

        trace = prepare_speed_trace(car_data)
        print(f"{name}: lap {fastest['lap_number']}, {duration:.3f} s")
        ax.plot(trace["distance_m"], trace["speed"], label=name, color=colour)

    ax.set_title("2025 Australian GP Qualifying | Norris vs Piastri")
    ax.set_xlabel("Estimated distance from first speed sample (m)")
    ax.set_ylabel("Speed (km/h)")
    ax.legend()
    ax.grid(alpha=0.25)
    ax.axvspan(3200, 3450, color="grey", alpha=0.15)
    ax.annotate(
        "Speed traces diverge here",
        xy=(3300, 260),
        xytext=(2500, 190),
        arrowprops={"arrowstyle": "->", "color": "#444444"},
    )
    fig.savefig("mclaren_speed_comparison.png", dpi=300, bbox_inches="tight")
    print("Saved mclaren_speed_comparison.png")
    plt.show()


if __name__ == "__main__":
    main()