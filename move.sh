#!/bin/bash

echo "Moving Wheelchair and Scrubs... Press [CTRL+C] to stop."

while true
do
  # --- Move Phase 1 ---
  # Wheelchair moves +Y, Scrubs moves +Y
  gz topic -t "/model/PatientWheelChair_1/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 1.0, y: 0, z: 0}"
  gz topic -t "/model/Scrubs_6/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 1.5, y: 0, z: 0}"
  sleep 10

  # Stop briefly
  gz topic -t "/model/PatientWheelChair_1/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 0, y: 0, z: 0}"
  gz topic -t "/model/Scrubs_6/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 0, y: 0, z: 0}"
  sleep 0.5

  # --- Move Phase 2 ---
  # Both move back -Y
  gz topic -t "/model/PatientWheelChair_1/cmd_vel" -m gz.msgs.Twist -p "linear: {x: -1.0, y: .0, z: 0}"
  gz topic -t "/model/Scrubs_6/cmd_vel" -m gz.msgs.Twist -p "linear: {x: -1.5, y: 0, z: 0}"
  sleep 10

  # Stop briefly
  gz topic -t "/model/PatientWheelChair_1/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 0, y: 0, z: 0}"
  gz topic -t "/model/Scrubs_6/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 0, y: 0, z: 0}"
  sleep 0.5
done
