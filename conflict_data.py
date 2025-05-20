from datetime import datetime, timedelta
from deconflict import Waypoint, Mission

def get_test_scenarios():
    now = datetime.now()

    primary = Mission([
        Waypoint(0, 0, now + timedelta(seconds=0), z=0),
        Waypoint(10, 10, now + timedelta(seconds=10), z=10)
    ])

    conflict_drone = Mission([
        Waypoint(10, 0, now + timedelta(seconds=0), z=0),
        Waypoint(0, 10, now + timedelta(seconds=10), z=10)
    ])

    safe_drone = Mission([
        Waypoint(20, 20, now + timedelta(seconds=0), z=5),
        Waypoint(30, 30, now + timedelta(seconds=10), z=15)
    ])

    extra_drone = Mission([
        Waypoint(-5, -5, now + timedelta(seconds=0), z=0),
        Waypoint(5, 5, now + timedelta(seconds=10), z=10)
    ])

    another_safe_drone = Mission([
        Waypoint(40, 40, now + timedelta(seconds=0), z=0),
        Waypoint(50, 50, now + timedelta(seconds=10), z=10)
    ])

    return primary, [conflict_drone, safe_drone, extra_drone, another_safe_drone]
