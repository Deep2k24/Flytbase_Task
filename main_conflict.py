# `get_test_scenarios` provides test data for drone missions
# `check_conflict` checks for conflicts between drone missions
# `animate_missions` visualizes the drone missions and conflicts
from conflict_data import get_test_scenarios
from deconflict import check_conflict, animate_missions

# Function to explain detected conflicts in a human-readable format
def explain_conflicts(conflicts):
    print("\n=== Conflict Explanation ===")
    for idx, conflict in enumerate(conflicts, 1):  # Enumerate conflicts for display
        time = conflict['time'].strftime("%Y-%m-%d %H:%M:%S")  # Format conflict time
        loc = conflict['location_primary']  # Location of the primary drone
        other_idx = conflict['other_mission_idx'] + 1  # Adjust index for human readability
        print(f"Conflict {idx}:")
        print(f"Time     : {time}")
        print(f"Location : X={loc[0]:.2f}, Y={loc[1]:.2f}, Z={loc[2]:.2f}")
        print(f"Between  : Primary Drone and Other Drone {other_idx}")
        print(f"Distance : {conflict['distance']:.2f} meters\n")  # Distance between drones

# Main function to execute the conflict detection and animation
def main():
    # Retrieve test scenarios for the primary drone and other drones
    primary, others = get_test_scenarios()

    # Check for conflicts between the primary drone and others with a buffer distance of 2.0 meters
    conflicts = check_conflict(primary, others, buffer=2.0)

    # Display the conflict detection results
    print("\n=== Conflict Detection Result ===")
    if conflicts != "CLEAR":  # If conflicts are detected
        print("CONFLICTS DETECTED!")
        explain_conflicts(conflicts)  # Explain the detected conflicts
    else:
        print("No Conflicts Detected (CLEAR)")  # No conflicts found

    # Animate the drone trajectories and save the animation as a video file
    print("Animating drone trajectories...")
    animate_missions(primary, others, conflicts, interval=300, save_path="drone_conflict.mp4")

# Entry point of the script
if __name__ == "__main__":
    main()