import threading
import tkinter as tk
from functools import partial

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from geometry_msgs.msg import PoseStamped, Quaternion
from nav2_msgs.action import NavigateToPose

import time

def yaw_to_quaternion(yaw: float) -> Quaternion:
    import math
    q = Quaternion()
    q.w = math.cos(yaw / 2.0)
    q.z = math.sin(yaw / 2.0)
    q.x = 0.0
    q.y = 0.0
    return q


class RoomSelectorNode(Node):
    def __init__(self):
        super().__init__('room_selector_gui')
        self.current_status = None
        self.current_goal_handle = None
        self.is_moving = False
        self.nav_to_pose_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.last_feedback_log_time = 0.0
        # Tọa độ mẫu, bạn phải thay bằng tọa độ thật trên map của bạn
        self.rooms = {
            "phong_01": {"x": -4.7, "y": 5.1, "z": 0.0, "qx": 0.0, "qy": 0.0, "qz": 0.707, "qw": 0.707},
            "phong_02": {"x": -7.2, "y": 1.4, "z": 0.0, "qx": 0.0, "qy": 0.0, "qz": 0.707, "qw": 0.707},
            
            # --- Các phòng bên trái (X < 0) -> Hướng ngang sang trái (Yaw = 180 độ) ---
            "phong_03": {"x": -10.1, "y": -1.6, "z": 0.0, "qx": 0.0, "qy": 0.0, "qz": 1.0, "qw": 0.0},
            "phong_04": {"x": -10.0, "y": -6.5, "z": 0.0, "qx": 0.0, "qy": 0.0, "qz": 1.0, "qw": 0.0},
            "phong_05": {"x": -8.1, "y": -18.4, "z": 0.0, "qx": 0.0, "qy": 0.0, "qz": 1.0, "qw": 0.0},
            "phong_06": {"x": -12.9, "y": -20.6, "z": 0.0, "qx": 0.0, "qy": 0.0, "qz": 1.0, "qw": 0.0},
            "phong_07": {"x": -8.4, "y": -31.3, "z": 0.0, "qx": 0.0, "qy": 0.0, "qz": 1.0, "qw": 0.0},
            "phong_08": {"x": -8.6, "y": -37.4, "z": 0.0, "qx": 0.0, "qy": 0.0, "qz": 1.0, "qw": 0.0},
            
            # --- Các phòng bên phải (X > 0) -> Hướng ngang sang phải (Yaw = 0 độ) ---
            "phong_09": {"x": 6.5, "y": -40.0, "z": 0.0, "qx": 0.0, "qy": 0.0, "qz": 0.0, "qw": 1.0},
            "phong_10": {"x": 8.3, "y": -32.4, "z": 0.0, "qx": 0.0, "qy": 0.0, "qz": 0.0, "qw": 1.0},
            "phong_11": {"x": 8.1, "y": -18.8, "z": 0.0, "qx": 0.0, "qy": 0.0, "qz": 0.0, "qw": 1.0},
            "phong_12": {"x": 10.3, "y": -6.6, "z": 0.0, "qx": 0.0, "qy": 0.0, "qz": 0.0, "qw": 1.0},
            "phong_13": {"x": 10.5, "y": -1.5, "z": 0.0, "qx": 0.0, "qy": 0.0, "qz": 0.0, "qw": 1.0},
            "phong_14": {"x": 7.7, "y": 2.1, "z": 0.0, "qx": 0.0, "qy": 0.0, "qz": 0.0, "qw": 1.0},
            "phong_15": {"x": 4.5, "y": 5.0, "z": 0.0, "qx": 0.0, "qy": 0.0, "qz": 0.0, "qw": 1.0},

            "phong_16": {"x": 1.3, "y": -14.6, "z": 0.0, "qx": 0.0, "qy": 0.0, "qz": -0.707, "qw": 0.707},
            "phong_17": {"x": -1.1, "y": -15.3, "z": 0.0, "qx": 0.0, "qy": 0.0, "qz": -0.707, "qw": 0.707},
            "phong_18": {"x": 1.5, "y": -25.3, "z": 0.0, "qx": 0.0, "qy": 0.0, "qz": -0.707, "qw": 0.707},
            "phong_19": {"x": -1.7, "y": -23.3, "z": 0.0, "qx": 0.0, "qy": 0.0, "qz": -0.707, "qw": 0.707},
            "phong_20": {"x": 1.9, "y": -30.3, "z": 0.0, "qx": 0.0, "qy": 0.0, "qz": -0.707, "qw": 0.707},
            
            # Hướng ngang quay mặt sang phải (Yaw = 0 độ)
            "phong_21": {"x": -1.1, "y": -28.5, "z": 0.0, "qx": 0.0, "qy": 0.0, "qz": 0.0, "qw": 1.0},
        }

    def set_status(self, new_status: str):
        if self.current_status != new_status:
            self.current_status = new_status
            self.get_logger().info(f'Trạng thái: {new_status}')

    def send_goal(self, room_name: str):
        if room_name not in self.rooms:
            self.get_logger().error(f'Không tìm thấy phòng: {room_name}')
            return

        room = self.rooms[room_name]

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = PoseStamped()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()

        goal_msg.pose.pose.position.x = room["x"]
        goal_msg.pose.pose.position.y = room["y"]
        goal_msg.pose.pose.position.z = room.get("z", 0.0)

        goal_msg.pose.pose.orientation.x = room.get("qx", 0.0)
        goal_msg.pose.pose.orientation.y = room.get("qy", 0.0)
        goal_msg.pose.pose.orientation.z = room["qz"]
        goal_msg.pose.pose.orientation.w = room["qw"]

        self.set_status(f'Nhận goal: {room_name}')

        if not self.nav_to_pose_client.wait_for_server(timeout_sec=3.0):
            self.get_logger().error('Action server navigate_to_pose chưa sẵn sàng')
            return

        send_goal_future = self.nav_to_pose_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.set_status('Dừng')
            self.get_logger().warn('Goal bị từ chối')
            return

        self.current_goal_handle = goal_handle
        self.is_moving = False

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def feedback_callback(self, feedback_msg):
        if not self.is_moving:
            self.is_moving = True
            self.set_status('Di chuyển')

    def result_callback(self, future):
        self.is_moving = False
        self.current_goal_handle = None

        result = future.result()
        status = result.status

        if status == 4:
            self.set_status('Tới goal')
        elif status == 5:
            self.set_status('Dừng')
        else:
            self.set_status('Dừng')

    def cancel_all_goals(self):
        if self.current_goal_handle is not None:
            self.current_goal_handle.cancel_goal_async()
        self.is_moving = False
        self.set_status('Dừng')


class RoomSelectorGUI:
    def __init__(self, ros_node: RoomSelectorNode):
        self.node = ros_node
        self.root = tk.Tk()
        self.root.title("Chọn phòng đến")
        self.root.geometry("420x700")

        title = tk.Label(self.root, text="Robot bệnh viện", font=("Arial", 16, "bold"))
        title.pack(pady=10)

        subtitle = tk.Label(self.root, text="Chọn phòng muốn đi đến", font=("Arial", 12))
        subtitle.pack(pady=5)

        # Khung chính chứa canvas + thanh cuộn
        container = tk.Frame(self.root)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        # Tạo cửa sổ bên trong canvas
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )

        # Cập nhật vùng cuộn khi nội dung thay đổi
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        # Khi canvas đổi kích thước, ép frame bên trong giãn theo chiều ngang
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width)
        )

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Cuộn bằng con lăn chuột
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Các nút phòng
        for room_name in self.node.rooms.keys():
            btn = tk.Button(
                self.scrollable_frame,
                text=room_name,
                height=2,
                command=partial(self.node.send_goal, room_name)
            )
            btn.pack(pady=6, fill="x")

        stop_btn = tk.Button(
            self.scrollable_frame,
            text="Dừng",
            height=2,
            bg="tomato",
            command=self.node.cancel_all_goals
        )
        stop_btn.pack(pady=12, fill="x")

        quit_btn = tk.Button(
            self.scrollable_frame,
            text="Thoát",
            height=2,
            command=self.root.destroy
        )
        quit_btn.pack(pady=6, fill="x")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def run(self):
        self.root.mainloop()

def main(args=None):
    rclpy.init(args=args)
    node = RoomSelectorNode()

    ros_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    ros_thread.start()

    gui = RoomSelectorGUI(node)
    gui.run()

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()