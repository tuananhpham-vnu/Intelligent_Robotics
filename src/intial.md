# Initial Plan: TurtleBot4 QR-Based Autonomous Mission with High-Level Reinforcement Learning

## 1. Project Overview

This project focuses on improving the software layer of a TurtleBot4-based intelligent robotics system. The hardware platform is already available, so the main task is to design and implement an autonomous navigation and mission-control framework.

The robot operates inside a fixed square map. The start point is located at the upper-right corner, and the end point is located at the lower-left corner. Several QR codes are placed at fixed positions in the map. Each QR code contains a task command, represented by one of three values: `1`, `2`, or `3`. In the middle area of the map, there are three fixed destination zones. After scanning a QR code, the robot must move to the corresponding destination zone. After all QR codes have been processed, the robot must return to the end point.

The project can be viewed as a fixed-map autonomous mission planning problem. The robot does not need to learn low-level wheel control from scratch. Instead, the system should use ROS2 and navigation tools for movement, while a mission manager controls the task flow. Reinforcement Learning can be added later as a high-level planner to optimize the order of visiting QR locations and completing tasks.

## 2. Main Objective

The main objective is to build an autonomous TurtleBot4 system that can:

1. Start from the predefined start position.
2. Move automatically to QR-code locations.
3. Scan each QR code and read the task value.
4. Move to the destination corresponding to the scanned value.
5. Continue until all QR-code tasks are completed.
6. Move to the final end position.
7. Optionally use Reinforcement Learning to optimize the task order and reduce unnecessary movement.

## 3. Why Reinforcement Learning Should Be Used Carefully

Reinforcement Learning can be applied to this project, but it should not directly control the robot's wheel velocity at the beginning.

A risky design would be:

```text
RL policy -> /cmd_vel -> robot wheels
```

This approach is difficult because the agent must learn collision avoidance, turning, speed control, and localization behavior directly. It also requires many training episodes and a good simulator. If trained directly on the real robot, the robot may move unstably or collide with objects.

A safer and more practical design is:

```text
RL / Planner -> choose next target point -> Nav2 moves the robot
```

In this design, RL only decides the next high-level action, such as which QR code to visit next or whether the robot should go to a destination. The low-level movement is handled by Nav2 or another navigation module. This makes the system easier to implement, safer to test, and easier to explain in a robotics report.

## 4. Proposed Software Architecture

The system should be divided into independent ROS2 nodes. Each node is responsible for one specific function.

```text
qr_reader_node
        |
        v
mission_manager_node
        |
        v
nav2_client_node
        |
        v
TurtleBot4 / Nav2
```

### 4.1 qr_reader_node

This node handles QR-code recognition.

Responsibilities:

- Read image data from the robot camera.
- Detect QR codes.
- Decode the QR content.
- Convert the result into an integer task value: `1`, `2`, or `3`.
- Publish the result to a ROS2 topic.

Suggested topic:

```text
/qr_result
```

Suggested message type:

```text
std_msgs/Int8
```

Example output:

```text
1 -> go to destination 1
2 -> go to destination 2
3 -> go to destination 3
```

### 4.2 mission_manager_node

This is the main control node of the system. It manages the whole mission process.

Responsibilities:

- Store the current mission state.
- Track which QR codes have already been visited.
- Receive QR results from `qr_reader_node`.
- Decide which destination should be visited next.
- Request navigation to QR locations, destinations, and the end point.
- Decide when the mission is completed.

This node should be implemented as a finite-state machine.

### 4.3 nav2_client_node

This node is responsible for sending navigation goals to the robot.

Responsibilities:

- Load target coordinates from `waypoints.yaml`.
- Convert a target name such as `qr_1` or `dest_2` into a navigation pose.
- Send the goal to Nav2.
- Wait for the result.
- Return success, failure, or timeout to the mission manager.

Example interface:

```python
navigate_to("qr_1")
navigate_to("dest_2")
navigate_to("end")
```

### 4.4 rl_planner_node

This node should be added only after the rule-based version works correctly.

Responsibilities:

- Receive the current mission state.
- Choose the next high-level action.
- Return the next target point to the mission manager.
- Load a saved Q-table or trained policy model.

The RL planner should not publish velocity commands directly.

## 5. Waypoint Configuration

All fixed positions should be stored in a YAML file instead of being hard-coded in Python.

Suggested file:

```text
config/waypoints.yaml
```

Example:

```yaml
start:
  x: 4.0
  y: 4.0
  yaw: 3.14

end:
  x: 0.0
  y: 0.0
  yaw: 0.0

qr_1:
  x: 3.5
  y: 3.2
  yaw: 0.0

qr_2:
  x: 2.0
  y: 3.5
  yaw: 0.0

qr_3:
  x: 1.0
  y: 2.5
  yaw: 0.0

dest_1:
  x: 1.2
  y: 1.2
  yaw: 0.0

dest_2:
  x: 2.5
  y: 2.0
  yaw: 0.0

dest_3:
  x: 3.4
  y: 1.4
  yaw: 0.0
```

The exact coordinates should be measured from the real map or from RViz.

## 6. Mission State Machine

The first working version should use a state machine. This makes the system easier to debug and safer to run.

Suggested states:

```text
INIT
GO_TO_QR
SCAN_QR
GO_TO_DESTINATION
CHECK_FINISH
GO_TO_END
DONE
ERROR
```

Mission flow:

```text
INIT
  -> GO_TO_QR
  -> SCAN_QR
  -> GO_TO_DESTINATION
  -> CHECK_FINISH
  -> GO_TO_QR or GO_TO_END
  -> DONE
```

Pseudo-code:

```python
state = "INIT"
visited_qr = set()
pending_task = None
completed_tasks = []

while state != "DONE":

    if state == "INIT":
        state = "GO_TO_QR"

    elif state == "GO_TO_QR":
        target_qr = select_next_qr()
        success = navigate_to(target_qr)

        if success:
            visited_qr.add(target_qr)
            state = "SCAN_QR"
        else:
            state = "ERROR"

    elif state == "SCAN_QR":
        pending_task = wait_for_qr_result()

        if pending_task in [1, 2, 3]:
            state = "GO_TO_DESTINATION"
        else:
            state = "ERROR"

    elif state == "GO_TO_DESTINATION":
        target_dest = f"dest_{pending_task}"
        success = navigate_to(target_dest)

        if success:
            completed_tasks.append(pending_task)
            pending_task = None
            state = "CHECK_FINISH"
        else:
            state = "ERROR"

    elif state == "CHECK_FINISH":
        if all_qr_visited():
            state = "GO_TO_END"
        else:
            state = "GO_TO_QR"

    elif state == "GO_TO_END":
        success = navigate_to("end")

        if success:
            state = "DONE"
        else:
            state = "ERROR"
```

## 7. Baseline Planner

Before using RL, a simple rule-based planner should be implemented.

Example:

```text
Visit QR codes in a fixed order:
qr_1 -> qr_2 -> qr_3 -> ... -> end
```

This version is important because it provides a stable baseline for comparison. If the rule-based version does not work, the RL version will also be difficult to test.

Baseline metrics:

- Total mission time.
- Total travelled distance.
- Number of successful QR scans.
- Number of failed navigation attempts.
- Whether the robot reached the correct destinations.
- Whether the robot reached the final end point.

## 8. Reinforcement Learning Formulation

After the baseline works, the mission can be modeled as a small RL problem on a fixed graph.

### 8.1 Environment

The environment is not the raw physical world. Instead, it is a graph-based abstraction of the map.

Nodes:

```text
Start
End
QR_1, QR_2, QR_3, ...
Dest_1, Dest_2, Dest_3
```

Edges:

```text
Distance between two fixed points
```

Each episode starts at `Start` and ends when the robot reaches `End` after completing all required tasks.

### 8.2 State

The state should describe the current mission situation.

Suggested state components:

```text
current_node
visited_qr
pending_task
completed_tasks
```

Example:

```python
state = {
    "current_node": "qr_2",
    "visited_qr": [1, 1, 0],
    "pending_task": 3,
    "completed_tasks": [1, 0, 1]
}
```

Meaning:

- The robot is currently at `qr_2`.
- QR 1 and QR 2 have already been visited.
- The current QR task requires destination 3.
- Destination 1 and destination 3 have already been completed.

### 8.3 Action

Actions are high-level decisions.

Example action space:

```text
0 = go_to_qr_1
1 = go_to_qr_2
2 = go_to_qr_3
3 = go_to_dest_1
4 = go_to_dest_2
5 = go_to_dest_3
6 = go_to_end
```

Invalid actions should either be blocked or heavily penalized.

Examples of invalid actions:

- Going to `end` before all tasks are completed.
- Going to a destination when no QR task is pending.
- Going to `dest_1` when the pending task is `2`.
- Visiting the same QR code repeatedly without need.

### 8.4 Reward Design

The reward should encourage the robot to complete the mission correctly and efficiently.

Suggested reward:

```text
+10   for scanning a new QR code
+50   for reaching the correct destination
+100  for completing all QR tasks
+200  for reaching the end point after all tasks are completed

-1    for each action
-0.5  multiplied by travel distance
-20   for revisiting an already visited QR code
-50   for going to the wrong destination
-100  for going to the end point too early
-100  for timeout or collision
```

General formula:

```text
reward = task_reward + finish_reward - distance_cost - invalid_action_penalty
```

Example:

```text
The robot scans a new QR code and then reaches the correct destination.
The travel distance is 3 meters.

reward = 10 + 50 - 0.5 * 3
reward = 58.5
```

## 9. Recommended RL Algorithm

The first RL version should use Q-learning.

Reason:

- The map is fixed.
- The number of QR codes is small.
- The number of destinations is small.
- The state and action spaces can be made discrete.
- Q-learning is easier to implement and explain.
- The learned knowledge can be saved as a Q-table.

Q-learning update rule:

```text
Q(s, a) = Q(s, a) + alpha * [r + gamma * max Q(s', a') - Q(s, a)]
```

Where:

```text
s      = current state
a      = selected action
r      = reward
s'     = next state
alpha  = learning rate
gamma  = discount factor
```

After training, the robot chooses the action with the highest Q-value:

```python
action = argmax(Q[state])
```

## 10. Saving Learned Knowledge

The robot does not need to learn again after every reboot.

If Q-learning is used, the learned knowledge is stored as a Q-table.

Save:

```python
import numpy as np

np.save("models/q_table.npy", q_table)
```

Load after reboot:

```python
q_table = np.load("models/q_table.npy")
```

If a neural network policy is used later, the model can be saved as:

```text
policy_model.pt
model.zip
```

The robot only needs to retrain when:

- QR positions change.
- Destination positions change.
- The map changes significantly.
- The number of QR codes changes.
- The reward function changes.
- The robot behavior in the real world is very different from the simulation.

## 11. Suggested Project Structure

```text
turtlebot4_qr_mission/
├── turtlebot4_qr_mission/
│   ├── qr_reader_node.py
│   ├── mission_manager_node.py
│   ├── nav2_client.py
│   ├── rl_planner.py
│   ├── q_learning_train.py
│   ├── state_encoder.py
│   └── utils.py
├── config/
│   ├── waypoints.yaml
│   ├── mission_config.yaml
│   └── rl_config.yaml
├── models/
│   └── q_table.npy
├── launch/
│   └── qr_mission.launch.py
├── setup.py
└── package.xml
```

## 12. Implementation Roadmap

### Phase 1: ROS2 and TurtleBot4 Setup

Goals:

- Connect to the TurtleBot4.
- Check available ROS2 topics.
- Read odometry data.
- Test basic keyboard teleoperation.
- Confirm camera and LiDAR are available.
- Confirm the robot can be started and shut down safely.

Expected output:

```text
The robot can be controlled manually.
ROS2 topics can be inspected.
The development environment is ready.
```

### Phase 2: Waypoint Measurement

Goals:

- Create or load the map.
- Use RViz to identify the coordinates of:
  - Start
  - End
  - QR locations
  - Destination zones
- Save all positions in `waypoints.yaml`.

Expected output:

```text
A complete waypoint configuration file.
```

### Phase 3: QR Recognition Node

Goals:

- Start the camera.
- Detect QR codes.
- Decode QR values.
- Publish the value to `/qr_result`.

Expected output:

```text
The robot can read QR codes and publish 1, 2, or 3.
```

### Phase 4: Navigation Client

Goals:

- Load target poses from `waypoints.yaml`.
- Send a navigation goal to Nav2.
- Wait for navigation result.
- Return success or failure.

Expected output:

```text
The robot can move automatically to a selected waypoint.
```

### Phase 5: Rule-Based Mission Manager

Goals:

- Implement the finite-state machine.
- Visit QR codes in a fixed order.
- Move to the corresponding destination.
- Return to the end point.

Expected output:

```text
The robot can complete the full mission without RL.
```

### Phase 6: RL Graph Simulation

Goals:

- Build a graph-based simulation of the map.
- Define state, action, and reward.
- Train a Q-learning agent.
- Save the Q-table.

Expected output:

```text
models/q_table.npy
```

### Phase 7: RL Deployment

Goals:

- Load the saved Q-table in the mission manager.
- Replace the rule-based `select_next_qr()` function with the RL policy.
- Test the robot on the real map.
- Compare RL with the rule-based baseline.

Expected output:

```text
The robot uses a learned policy to choose the next target.
```

## 13. Evaluation Plan

The final system should be evaluated using the following metrics:

```text
Mission success rate
Total mission time
Total travel distance
Number of QR scans
Number of failed QR detections
Number of navigation failures
Number of wrong destination attempts
Number of early-end attempts
```

Suggested comparison:

```text
Rule-based planner vs Q-learning planner
```

Example table:

| Method | Success Rate | Time | Distance | Wrong Actions |
|---|---:|---:|---:|---:|
| Rule-based | TBD | TBD | TBD | TBD |
| Q-learning | TBD | TBD | TBD | TBD |

## 14. Expected Final Contribution

The expected contribution of this project is a complete ROS2-based autonomous mission framework for TurtleBot4. The system integrates QR-code recognition, state-machine task control, waypoint-based navigation, and optional high-level Reinforcement Learning.

The main idea is not to make the robot learn low-level motor control. Instead, the robot uses existing navigation tools for safe movement, while Reinforcement Learning is used to optimize high-level decision-making in a fixed map.

## 15. Short Summary

The project should be implemented in this order:

```text
1. Build the ROS2 node structure.
2. Read QR codes from the camera.
3. Save fixed map points in waypoints.yaml.
4. Use Nav2 to move between points.
5. Implement a state-machine mission manager.
6. Complete the mission using a rule-based planner.
7. Build a graph-based RL simulation.
8. Train and save a Q-learning policy.
9. Load the saved policy after reboot.
10. Compare RL with the rule-based baseline.
```

Final design:

```text
QR Recognition + State Machine + Nav2 + High-Level RL Planner
```

The robot does not need to learn again after every reboot. The learned Q-table or model can be saved and loaded when the robot starts.
