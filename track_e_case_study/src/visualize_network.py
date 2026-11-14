"""
Railway Network and Routing Visualization Suite
Track E: Railway Route and Transfer Optimization
Assignment 8 - Optimize Anything

Generates 3 publication-ready Matplotlib plots:
1. track_e_case_study/plots/01_railway_network_topology.png
2. track_e_case_study/plots/02_example_journey_route.png
3. track_e_case_study/plots/03_journey_time_breakdown.png
"""

import json
import os
import tempfile

# Prevent matplotlib cache directory warnings
os.environ["MPLCONFIGDIR"] = os.path.join(tempfile.gettempdir(), "matplotlib")

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

from .graph import load_network_from_data
from .dijkstra_baseline import TimeDependentEarliestArrivalDijkstra

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PLOTS_DIR = os.path.join(BASE_DIR, "plots")
RESULTS_DIR = os.path.join(BASE_DIR, "results")


def plot_network_topology(network, output_path: str):
    """Plot physical railway network topology with corridors and interchange junctions."""
    fig, ax = plt.subplots(figsize=(12, 10), dpi=300)

    # Color map for corridors
    corridor_colors = {
        "Main Trunk": "#1f77b4",          # Deep Blue
        "Western Coast": "#2ca02c",       # Green
        "Eastern Industrial": "#ff7f0e",  # Orange
        "Southern Ring": "#9467bd",       # Purple
        "Northern Spur": "#d62728"        # Red
    }

    # Draw track connections
    drawn_segments = set()
    for conn in network.connections:
        u = network.get_station(conn.from_station_id)
        v = network.get_station(conn.to_station_id)
        seg_key = tuple(sorted([u.station_id, v.station_id]))
        if seg_key not in drawn_segments:
            drawn_segments.add(seg_key)
            color = corridor_colors.get(u.corridor, "#7f7f7f")
            ax.plot([u.lon, v.lon], [u.lat, v.lat], color=color, linewidth=2.0, alpha=0.6, zorder=1)

    # Plot stations
    for stn in network.stations.values():
        color = corridor_colors.get(stn.corridor, "#333333")
        if stn.is_junction:
            # Large diamond for interchange junction
            ax.scatter(stn.lon, stn.lat, s=160, color="#d62728", edgecolor="black", linewidth=1.5, marker="D", zorder=3)
            ax.annotate(
                f"{stn.name} [{stn.code}]\n({stn.min_transfer_min}m buffer)",
                (stn.lon, stn.lat),
                textcoords="offset points",
                xytext=(8, -4),
                fontsize=7.5,
                weight="bold",
                bbox=dict(boxstyle="round,pad=0.2", fc="yellow", alpha=0.4, ec="grey", lw=0.5),
                zorder=4
            )
        else:
            # Circle for regular station
            ax.scatter(stn.lon, stn.lat, s=60, color=color, edgecolor="black", linewidth=0.8, marker="o", zorder=2)
            ax.annotate(
                f"{stn.code}",
                (stn.lon, stn.lat),
                textcoords="offset points",
                xytext=(5, 4),
                fontsize=6.5,
                color="#222222",
                zorder=4
            )

    # Corridor legend
    for corr, col in corridor_colors.items():
        ax.plot([], [], color=col, linewidth=2.5, label=f"{corr} Corridor")
    ax.scatter([], [], s=140, color="#d62728", edgecolor="black", marker="D", label="Interchange Junction")
    ax.scatter([], [], s=60, color="#555555", edgecolor="black", marker="o", label="Standard Station")

    ax.set_title("Intercity Regional Railway Network (28 Stations, 7 Junctions)", fontsize=14, weight="bold", pad=15)
    ax.set_xlabel("Longitude (°E)", fontsize=11)
    ax.set_ylabel("Latitude (°N)", fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc="lower right", frameon=True, fontsize=8.5)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"  Plot 1 saved: {output_path}")


def plot_example_journey_route(network, output_path: str):
    """Plot highlighted route for an example multi-transfer journey over the network."""
    router = TimeDependentEarliestArrivalDijkstra(network)
    # Seaside Sands (STN_12) to Canyon Pass (STN_28), 06:00
    res = router.find_earliest_arrival("STN_12", "STN_28", 360)

    fig, ax = plt.subplots(figsize=(12, 10), dpi=300)

    # 1. Background network in muted grey
    for conn in network.connections:
        u = network.get_station(conn.from_station_id)
        v = network.get_station(conn.to_station_id)
        ax.plot([u.lon, v.lon], [u.lat, v.lat], color="#cccccc", linewidth=1.2, zorder=1)

    for stn in network.stations.values():
        ax.scatter(stn.lon, stn.lat, s=35, color="#bbbbbb", marker="o", zorder=2)

    # 2. Highlight traversed journey legs
    service_palette = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
    distinct_services = []
    for leg in res.legs:
        if leg.service_name not in distinct_services:
            distinct_services.append(leg.service_name)

    for leg in res.legs:
        u = network.get_station(leg.from_station_id)
        v = network.get_station(leg.to_station_id)
        c_idx = distinct_services.index(leg.service_name) % len(service_palette)
        c = service_palette[c_idx]

        ax.plot([u.lon, v.lon], [u.lat, v.lat], color=c, linewidth=4.0, alpha=0.9, zorder=3)
        # Direction arrow
        mid_lon = (u.lon + v.lon) / 2.0
        mid_lat = (u.lat + v.lat) / 2.0
        dx = (v.lon - u.lon) * 0.1
        dy = (v.lat - u.lat) * 0.1
        ax.arrow(mid_lon - dx, mid_lat - dy, dx, dy, shape="full", lw=0, length_includes_head=True, head_width=0.03, color=c, zorder=4)

    # 3. Mark origin, destination, and transfer stations
    orig_stn = network.get_station(res.source_id)
    dest_stn = network.get_station(res.destination_id)

    ax.scatter(orig_stn.lon, orig_stn.lat, s=250, color="#2ca02c", edgecolor="black", marker="^", label=f"Origin: {orig_stn.name} (Dep {res.departure_hhmm})", zorder=6)
    ax.scatter(dest_stn.lon, dest_stn.lat, s=250, color="#d62728", edgecolor="black", marker="s", label=f"Destination: {dest_stn.name} (Arr {res.arrival_hhmm})", zorder=6)

    # Transfers
    transfer_stations = [leg.from_station_id for leg in res.legs if leg.is_transfer]
    for xfer_id in transfer_stations:
        xfer_stn = network.get_station(xfer_id)
        ax.scatter(xfer_stn.lon, xfer_stn.lat, s=220, color="#ff7f0e", edgecolor="black", marker="*", zorder=7)
        ax.annotate(
            f"Transfer: {xfer_stn.name}",
            (xfer_stn.lon, xfer_stn.lat),
            textcoords="offset points",
            xytext=(10, 4),
            fontsize=8,
            weight="bold",
            bbox=dict(boxstyle="round,pad=0.2", fc="#ffeedd", alpha=0.8, ec="#ff7f0e", lw=1),
            zorder=8
        )
    ax.scatter([], [], s=200, color="#ff7f0e", edgecolor="black", marker="*", label="Interchange Transfer Point")

    # Legend for services
    for srv in distinct_services:
        c_idx = distinct_services.index(srv) % len(service_palette)
        ax.plot([], [], color=service_palette[c_idx], linewidth=3.5, label=f"Train: {srv[:28]}")

    title_str = (
        f"Example Multi-Transfer Route Itinerary\n"
        f"{orig_stn.name} -> {dest_stn.name} | Total Journey: {res.total_journey_time_min}m ({res.total_journey_time_min/60:.1f}h) | "
        f"Transfers: {res.num_transfers} | Wait: {res.total_waiting_time_min}m"
    )
    ax.set_title(title_str, fontsize=12, weight="bold", pad=15)
    ax.set_xlabel("Longitude (°E)", fontsize=11)
    ax.set_ylabel("Latitude (°N)", fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.legend(loc="lower right", frameon=True, fontsize=8)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"  Plot 2 saved: {output_path}")


def plot_journey_time_breakdown(output_path: str):
    """Plot stacked bar chart of travel time vs waiting time across benchmark queries."""
    json_path = os.path.join(RESULTS_DIR, "baseline_benchmark_results.json")
    if not os.path.exists(json_path):
        print(f"Warning: {json_path} not found. Run benchmark_baseline.py first.")
        return

    with open(json_path, mode="r", encoding="utf-8") as f:
        data = json.load(f)

    queries = data["queries"]
    names = [q["query_name"] for q in queries]
    travel_times = [q["in_vehicle_travel_time_min"] for q in queries]
    wait_times = [q["transfer_waiting_time_min"] for q in queries]
    transfers = [q["num_transfers"] for q in queries]
    latencies = [q["latency_mean_ms"] for q in queries]

    x = np.arange(len(names))
    width = 0.55

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 10), dpi=300, gridspec_kw={"height_ratios": [3, 1.2]})

    # Subplot 1: Stacked Bar Chart for Journey Time
    p1 = ax1.bar(x, travel_times, width, label="In-Vehicle Travel Time (min)", color="#1f77b4", edgecolor="black", alpha=0.85)
    p2 = ax1.bar(x, wait_times, width, bottom=travel_times, label="Transfer Waiting Time (min)", color="#ff7f0e", edgecolor="black", alpha=0.85)

    # Twin axis for number of transfers
    ax1_twin = ax1.twinx()
    p3 = ax1_twin.plot(x, transfers, color="#d62728", marker="o", linewidth=2.5, markersize=8, label="Transfers Count")
    ax1_twin.set_ylabel("Number of Transfers", fontsize=11, color="#d62728", weight="bold")
    ax1_twin.tick_params(axis="y", labelcolor="#d62728")
    ax1_twin.set_ylim(-0.2, max(transfers) + 1.2)

    ax1.set_title("Benchmark Journey Duration Breakdown & Interchange Transfer Overhead", fontsize=13, weight="bold", pad=12)
    ax1.set_ylabel("Time (Minutes)", fontsize=11, weight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(names, rotation=35, ha="right", fontsize=9)
    ax1.grid(True, axis="y", linestyle="--", alpha=0.5)

    # Combine legends
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax1_twin.get_legend_handles_labels()
    ax1.legend(handles1 + handles2, labels1 + labels2, loc="upper left", frameon=True, fontsize=9)

    # Subplot 2: Execution Latency (ms)
    ax2.bar(x, latencies, width=0.45, color="#2ca02c", edgecolor="black", alpha=0.85)
    ax2.set_ylabel("Latency (ms)", fontsize=10, weight="bold")
    ax2.set_xlabel("Benchmark Query Scenario", fontsize=11, weight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"Q{i+1}" for i in range(len(names))], fontsize=9)
    ax2.set_title("Algorithm Execution Latency (Mean ms per query)", fontsize=11, weight="bold")
    ax2.grid(True, axis="y", linestyle="--", alpha=0.5)

    for i, v in enumerate(latencies):
        ax2.text(i, v + 0.015, f"{v:.3f}ms", ha="center", fontsize=7.5, weight="bold")

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"  Plot 3 saved: {output_path}")


def generate_all_visualizations():
    """Generate all three plots."""
    os.makedirs(PLOTS_DIR, exist_ok=True)
    network = load_network_from_data()

    plot1_path = os.path.join(PLOTS_DIR, "01_railway_network_topology.png")
    plot_network_topology(network, plot1_path)

    plot2_path = os.path.join(PLOTS_DIR, "02_example_journey_route.png")
    plot_example_journey_route(network, plot2_path)

    plot3_path = os.path.join(PLOTS_DIR, "03_journey_time_breakdown.png")
    plot_journey_time_breakdown(plot3_path)

    print("All visualizations created successfully in track_e_case_study/plots/")


if __name__ == "__main__":
    generate_all_visualizations()

