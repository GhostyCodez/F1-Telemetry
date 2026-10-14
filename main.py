import fastf1
import matplotlib.pyplot as plt

session = fastf1.get_session(2025, "Australia", "Q")

session.load(telemetry=False, weather=False, messages=False)

print(session.results[["Abbreviation", "Position"]])

mclaren = session.results[
    session.results["Abbreviation"].isin(["NOR", "PIA"])
]

print("\nMcLaren Qualifying Results:")
print(mclaren[["Abbreviation", "Position", "Q3"]])

times = mclaren.set_index("Abbreviation")["Q3"]

gap = (times["PIA"] - times["NOR"]).total_seconds()

print(f"\nGap between Oscar and Lando: {gap:.3f} seconds")

lap_seconds = times.dt.total_seconds()

# Makes plot Graph with driver lap times in seconds 
plt.plot(lap_seconds.index, lap_seconds.values, "o")
# Add lap time labels to the graph
for driver, seconds in zip(lap_seconds.index, lap_seconds.values):
    plt.annotate(
        f"{seconds:.3f}s",
        (driver, seconds), 
        xytext=(0,10),
        textcoords="offset points", 
        ha="center"
    )
plt.title("Mclaren Australian GP Qualifying")
plt.ylabel("Q3 Lap Time (seconds)")
plt.ylim(75.0, 75.3)

# Save the quali comparison graph 
plt.savefig("mclaren_qualifying.png", dpi=300, bbox_inches="tight")

print("Graph Saved")
plt.show()
