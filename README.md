# ros2-hospital-robot
# ros2-hospital-robot

A ROS 2 project for simulating a hospital delivery robot in Gazebo. The robot can navigate autonomously with Nav2 and receive room goals from a simple GUI.

## Team Members
1. Trần Trăng Sáng - 23134050  
2. Nguyễn Minh Nghĩa - 23134039  
3. Bùi Đình Khôi - 23134032  
4. Phạm Trung Kiên - 23134034  

## Project Overview
This project simulates a hospital service robot using **ROS 2**, **Gazebo**, and **Nav2**.
The system supports:

- Robot simulation in Gazebo
- Robot control with ROS 2
- Autonomous navigation with Nav2
- Room selection through a GUI
- Goal-based delivery in a hospital map

## Main Packages

### `robot_omni`
Robot description and simulation package:
- URDF model
- Gazebo launch files
- ros2_control integration
- Sensor and bridge configuration

### `nav2_simple_navigation`
Navigation package:
- Nav2 configuration
- Behavior Tree
- Navigation launch files
- Map and keepout mask
- RViz configuration

### `room_selector_gui`
User interface package:
- Simple room selection GUI
- Sends navigation goals with `NavigateToPose`
- Scrollable room list
- Predefined room goals

## Requirements
- Ubuntu
- ROS 2
- Gazebo
- Nav2
- colcon

## Build
From the workspace root:

```bash
colcon build
source install/setup.bash
```

## How to Run

### 1. Launch robot simulation
```bash
ros2 launch robot_omni gazebo_control.launch.py
```
### 2. Launch ekf
```bash
ros2 launch nav2_simple_navigation ekf.launch.py 
```
### 3. Launch localization
```bash
ros2 launch nav2_simple_navigation localization.launch.py
```

### 4. Launch navigation
```bash
ros2 launch nav2_simple_navigation nav2.launch.py
```

### 5. Launch room selection GUI
```bash
ros2 run room_selector_gui room_selector
```

## Operation Flow
1. Start the robot simulation in Gazebo  
2. Start the navigation stack  
3. Open the room selection GUI  
4. Select a target room  
5. The robot navigates to the selected goal  

## Current Features
- Robot spawn in Gazebo
- ros2_control integration
- Nav2-based localization and navigation
- Room selection GUI
- Goal-based autonomous movement

## Notes
- Room coordinates are currently defined in `room_selector.py`
- The room list can be moved to a YAML file in future work
- The system can be extended with better robot status handling, stop control, and more delivery functions
