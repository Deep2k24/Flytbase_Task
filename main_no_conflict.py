from no_conflict_data import get_test_scenarios
from deconflict import check_conflict, animate_missions
from typing import List, Union

def explain_conflicts(conflicts: List[dict]) -> None:
    """
    Explains detected conflicts in a human-readable format.

    Args:
        conflicts (List[dict]): List of detected conflicts with details.
    """
    print("\n=== Conflict Explanation ===")
    for idx, conflict in enumerate(conflicts, 1):  # Enumerate conflicts for display
        time = conflict['time'].strftime("%Y-%m-%d %H:%M:%S")  # Format conflict time
        loc = conflict['location_primary']  # Location of the primary drone
        other_idx = conflict['other_mission_idx'] + 1  # Adjust index for human readability
        print(f"Conflict {idx}:")
        print(f"  Time     : {time}")
        print(f"  Location : X={loc[0]:.2f}, Y={loc[1]:.2f}, Z={loc[2]:.2f}")
        print(f"  Between  : Primary Drone and Other Drone {other_idx}")
        print(f"  Distance : {conflict['distance']:.2f} meters\n")  # Distance between drones

def display_results(conflicts: Union[List[dict], str]) -> None:
    """
    Displays the results of conflict detection.

    Args:
        conflicts (Union[List[dict], str]): Detected conflicts or "CLEAR" if no conflicts.
    """
    print("\n=== Conflict Detection Result ===")
    if conflicts != "CLEAR":  # If conflicts are detected
        print("CONFLICTS DETECTED!")
        explain_conflicts(conflicts)  # Explain the detected conflicts
    else:
        print("No Conflicts Detected (CLEAR)")  # No conflicts found

def main(buffer_distance: float = 2.0, save_path: str = "no_conflict.mp4") -> None:
    """
    Main function to execute the conflict detection and animation.

    Args:
        buffer_distance (float): Minimum distance to detect conflicts (in meters).
        save_path (str): File path to save the animation video.
    """
    # Retrieve test scenarios for the primary drone and other drones
    primary, others = get_test_scenarios()

    # Check for conflicts between the primary drone and others
    conflicts = check_conflict(primary, others, buffer=buffer_distance)

    # Display the conflict detection results
    display_results(conflicts)

    # Animate the drone trajectories and save the animation as a video file
    print("Animating drone trajectories...")
    animate_missions(primary, others, conflicts, interval=300, save_path=save_path)

# Entry point of the script
if __name__ == "__main__":
    main()