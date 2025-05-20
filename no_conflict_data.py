from datetime import datetime, timedelta
from deconflict import Waypoint, Mission

def get_test_scenarios():
    now = datetime.now()

    # Primary drone path
    primary = Mission([
        Waypoint(0, 0, now + timedelta(seconds=0), z=0),
        Waypoint(10, 10, now + timedelta(seconds=10), z=10)
    ])

    # Drone 1 - far away in space
    drone1 = Mission([
        Waypoint(50, 50, now + timedelta(seconds=0), z=0),
        Waypoint(60, 60, now + timedelta(seconds=10), z=10)
    ])

    # Drone 2 - far in space and time
    drone2 = Mission([
        Waypoint(30, 30, now + timedelta(seconds=20), z=20),
        Waypoint(40, 40, now + timedelta(seconds=30), z=30)
    ])

    # Drone 3 - no overlap with primary (different path & altitude)
    drone3 = Mission([
        Waypoint(20, 0, now + timedelta(seconds=0), z=30),
        Waypoint(30, 10, now + timedelta(seconds=10), z=40)
    ])

    # Drone 4 - completely disjoint
    drone4 = Mission([
        Waypoint(-100, -100, now + timedelta(seconds=0), z=0),
        Waypoint(-90, -90, now + timedelta(seconds=10), z=10)
    ])

    return primary, [drone1, drone2, drone3, drone4]
