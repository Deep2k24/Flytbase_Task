from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
from typing import List, Tuple, Optional, Union

class Waypoint:
    """Represents a waypoint in 3D space with a timestamp."""
    def __init__(self, x: float, y: float, t: Union[datetime, float], z: float = 0):
        self.x = x
        self.y = y
        self.z = z
        self.t = t if isinstance(t, datetime) else datetime.now() + timedelta(seconds=t)

class Mission:
    """Represents a mission consisting of a sequence of waypoints."""
    def __init__(self, waypoints: List[Waypoint]):
        self.waypoints = sorted(waypoints, key=lambda w: w.t)

def check_conflict(primary: Mission, others: List[Mission], buffer: float = 15.0) -> Union[List[dict], str]:
    """
    Checks for conflicts between the primary mission and other missions.
    A conflict occurs when the distance between drones is less than the buffer.
    """
    conflicts = []
    for other_idx, other in enumerate(others):
        for i in range(len(primary.waypoints) - 1):
            for j in range(len(other.waypoints) - 1):
                p1, p2 = primary.waypoints[i], primary.waypoints[i + 1]
                o1, o2 = other.waypoints[j], other.waypoints[j + 1]

                # Time interval overlap
                t_start = max(p1.t.timestamp(), o1.t.timestamp())
                t_end = min(p2.t.timestamp(), o2.t.timestamp())
                if t_start > t_end:
                    continue

                # Durations of segments
                dt_p = p2.t.timestamp() - p1.t.timestamp()
                dt_o = o2.t.timestamp() - o1.t.timestamp()
                if dt_p == 0 or dt_o == 0:
                    continue

                # Velocity vectors for primary and other
                v_px = (p2.x - p1.x) / dt_p
                v_py = (p2.y - p1.y) / dt_p
                v_pz = (p2.z - p1.z) / dt_p

                v_ox = (o2.x - o1.x) / dt_o
                v_oy = (o2.y - o1.y) / dt_o
                v_oz = (o2.z - o1.z) / dt_o

                # Relative position and velocity at segment start
                rel_px = p1.x - o1.x
                rel_py = p1.y - o1.y
                rel_pz = p1.z - o1.z

                rel_vx = v_px - v_ox
                rel_vy = v_py - v_oy
                rel_vz = v_pz - v_oz

                rel_v_sq = rel_vx**2 + rel_vy**2 + rel_vz**2
                if rel_v_sq == 0:
                    # Parallel or same velocity => check only at overlap ends
                    check_times = [t_start, t_end]
                else:
                    # Time t* minimizing distance between linear segments
                    t_star = - (rel_px*rel_vx + rel_py*rel_vy + rel_pz*rel_vz) / rel_v_sq
                    abs_t_star = max(p1.t.timestamp(), o1.t.timestamp()) + t_star
                    # Clamp to overlap interval
                    if abs_t_star < t_start:
                        abs_t_star = t_start
                    elif abs_t_star > t_end:
                        abs_t_star = t_end
                    check_times = [abs_t_star]

                for t_check in check_times:
                    pt_ratio = (t_check - p1.t.timestamp()) / dt_p
                    ot_ratio = (t_check - o1.t.timestamp()) / dt_o

                    px = p1.x + pt_ratio * (p2.x - p1.x)
                    py = p1.y + pt_ratio * (p2.y - p1.y)
                    pz = p1.z + pt_ratio * (p2.z - p1.z)

                    ox = o1.x + ot_ratio * (o2.x - o1.x)
                    oy = o1.y + ot_ratio * (o2.y - o1.y)
                    oz = o1.z + ot_ratio * (o2.z - o1.z)

                    distance = np.sqrt((px - ox)**2 + (py - oy)**2 + (pz - oz)**2)

                    print(f"Checking P seg {i} vs O seg {j}: Dist={distance:.2f} at {datetime.fromtimestamp(t_check)}")

                    if distance < buffer:
                        print(f"*** CONFLICT at {datetime.fromtimestamp(t_check)} Distance: {distance:.2f}")
                        conflicts.append({
                            'time': datetime.fromtimestamp(t_check),
                            'location_primary': (px, py, pz),
                            'location_other': (ox, oy, oz),
                            'distance': distance,
                            'other_mission_idx': other_idx
                        })

    return conflicts if conflicts else "CLEAR"

def interpolate(mission: Mission, t: float) -> Optional[Tuple[float, float, float]]:
    """
    Interpolates the position of a drone at a given time `t` based on its mission waypoints.
    """
    for i in range(len(mission.waypoints) - 1):
        wp1, wp2 = mission.waypoints[i], mission.waypoints[i + 1]
        t1, t2 = wp1.t.timestamp(), wp2.t.timestamp()
        if t1 <= t <= t2:
            ratio = (t - t1) / (t2 - t1) if t2 > t1 else 0
            x = wp1.x + ratio * (wp2.x - wp1.x)
            y = wp1.y + ratio * (wp2.y - wp1.y)
            z = wp1.z + ratio * (wp2.z - wp1.z)
            return x, y, z
    return None

def initialize_animation(ax, all_missions, colors):
    """
    Initializes the animation elements (dots, lines, and markers).
    """
    drone_dots = []
    drone_lines = []
    for c in colors:
        dot, = ax.plot([], [], [], 'o', color=c)
        line, = ax.plot([], [], [], '-', color=c)
        drone_dots.append(dot)
        drone_lines.append(line)
    return drone_dots, drone_lines

def animate_missions(primary: Mission, others: List[Mission], conflicts=None, interval: int = 300, save_path: Optional[str] = None):
    """
    Animates the missions of drones and visualizes conflicts.
    """
    all_missions = [primary] + others
    all_waypoints = [wp for mission in all_missions for wp in mission.waypoints]
    t_min = min(wp.t.timestamp() for wp in all_waypoints)
    t_max = max(wp.t.timestamp() for wp in all_waypoints)

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')

    ax.set_xlim(min(wp.x for wp in all_waypoints) - 5, max(wp.x for wp in all_waypoints) + 5)
    ax.set_ylim(min(wp.y for wp in all_waypoints) - 5, max(wp.y for wp in all_waypoints) + 5)
    ax.set_zlim(min(wp.z for wp in all_waypoints) - 5, max(wp.z for wp in all_waypoints) + 5)

    colors = ['blue'] + ['red'] * len(others)
    drone_dots, drone_lines = initialize_animation(ax, all_missions, colors)

    past_positions = [[] for _ in all_missions]
    conflict_markers = []
    if conflicts != "CLEAR":
        for c in conflicts:
            x, y, z = c['location_primary']
            marker = ax.plot([x], [y], [z], 'rx', markersize=10, markeredgewidth=2)[0]
            conflict_markers.append(marker)

    time_text = ax.text2D(0.05, 0.95, '', transform=ax.transAxes)

    def update(frame):
        t_now = t_min + (frame / 100.0) * (t_max - t_min)
        for i, mission in enumerate(all_missions):
            pos = interpolate(mission, t_now)
            if pos:
                past_positions[i].append(pos)
                xs, ys, zs = zip(*past_positions[i])
                drone_dots[i].set_data([pos[0]], [pos[1]])
                drone_dots[i].set_3d_properties([pos[2]])
                drone_lines[i].set_data(xs, ys)
                drone_lines[i].set_3d_properties(zs)
        time_text.set_text(f'Time: {t_now - t_min:.1f}s')
        return drone_dots + drone_lines + conflict_markers + [time_text]

    ani = animation.FuncAnimation(fig, update, frames=100, interval=interval, blit=False, repeat=True)

    if save_path:
        ani.save(save_path, writer='ffmpeg', fps=30)
        print(f"Animation saved to {save_path}")

    plt.show()