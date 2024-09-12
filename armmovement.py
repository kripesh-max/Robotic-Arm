import paho.mqtt.client as mqtt
import json
from adafruit_servokit import ServoKit
from time import sleep
# Settings
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "coordinates_topic"
TOLERANCE = 1 # Tolerance for coordinates matching
# Initialize the servo kit
kit = ServoKit(channels=16)
# Preset positions for each base angle and fixed angles for wrist, elbow, and pivot
PRESET_POSITIONS = [
{"base": 0, "elbow": 50, "wrist": 50, "pivot": 70},
{"base": 20, "elbow": 50, "wrist": 50, "pivot": 70},
{"base": 40, "elbow": 50, "wrist": 50, "pivot": 70},
{"base": 60, "elbow": 50, "wrist": 50, "pivot": 70},
{"base": 90, "elbow": 50, "wrist": 50, "pivot": 70},
{"base": 0, "elbow": 40, "wrist": 35, "pivot": 70},
{"base": 20, "elbow": 40, "wrist": 35, "pivot": 70},
{"base": 40, "elbow": 40, "wrist": 35, "pivot": 70},
{"base": 60, "elbow": 40, "wrist": 35, "pivot": 70},
{"base": 90, "elbow": 40, "wrist": 35, "pivot": 70},
{"base": 0, "elbow": 40, "wrist": 25, "pivot": 70},
{"base": 20, "elbow": 40, "wrist": 25, "pivot": 70},
{"base": 40, "elbow": 40, "wrist": 25, "pivot": 70},
{"base": 60, "elbow": 40, "wrist": 25, "pivot": 70},
  {"base": 90, "elbow": 40, "wrist": 25, "pivot": 70},
{"base": 0, "elbow": 40, "wrist": 20, "pivot": 70},
{"base": 20, "elbow": 40, "wrist": 20, "pivot": 70},
{"base": 40, "elbow": 40, "wrist": 20, "pivot": 70},
{"base": 60, "elbow": 40, "wrist": 20, "pivot": 70},
{"base": 90, "elbow": 40, "wrist": 20, "pivot": 70},
]
# Predetermined coordinates that the robot can respond to
PREDEFINED_COORDINATES = [
{"x": 21, "y": 10, "position_index": 0},
{"x": 18, "y": 11, "position_index": 1},
{"x": 13, "y": 10, "position_index": 2},
{"x": 8, "y": 11, "position_index": 3},
{"x": 4, "y": 12, "position_index": 4},
{"x": 21, "y": 9, "position_index": 5},
{"x": 18, "y": 8, "position_index": 6},
{"x": 14, "y": 7, "position_index": 7},
{"x": 8, "y": 9, "position_index": 8},
{"x": 3, "y": 11, "position_index": 9},
{"x": 22, "y": 8, "position_index": 10},
{"x": 19, "y": 6, "position_index": 11},
{"x": 13, "y": 6, "position_index": 12},
{"x": 7, "y": 6, "position_index": 13},
{"x": 2, "y": 10, "position_index": 14},
{"x": 23, "y": 6, "position_index": 15},
{"x": 19, "y": 4, "position_index": 16},
{"x": 13, "y": 3, "position_index": 17},
{"x": 6, "y": 4, "position_index": 18},
{"x": 1, "y": 7, "position_index": 19},
]
# Bin positions for each label
BIN_POSITIONS = {
"Blue Cube": {"base": 150, "elbow": 40, "wrist": 25, "pivot": 70},
"Blue Cylinder": {"base": 150, "elbow": 40, "wrist": 25, "pivot": 70},
"Blue Pyramid": {"base": 150, "elbow": 40, "wrist": 25, "pivot": 70},
"Green Cube": {"base": 150, "elbow": 40, "wrist": 0, "pivot": 100},
"Green Cylinder": {"base": 150, "elbow": 40, "wrist": 0, "pivot": 100},
"Green Pyramid": {"base": 150, "elbow": 40, "wrist": 0, "pivot": 100},
"Red Cube": {"base": 180, "elbow": 40, "wrist": 25, "pivot": 70},
"Red Cylinder": {"base": 180, "elbow": 40, "wrist": 25, "pivot": 70},
"Red Pyramid": {"base": 180, "elbow": 40, "wrist": 25, "pivot": 70},
}
def smooth_move_servo(servo_number, target_angle):
current_angle = kit.servo[servo_number].angle
if current_angle is None:
current_angle = 0 # Set default angle if None
else:
current_angle = int(current_angle)
step = 1 if target_angle > current_angle else -1
for angle in range(current_angle, target_angle, step):
kit.servo[servo_number].angle = angle
sleep(0.01) # Adjust delay as needed for smoother motion
def initialize_robot_arm():
smooth_move_servo(1, 120) # Elbow servo to 120 degrees
smooth_move_servo(0, 0) # Base servo to 0 degrees
smooth_move_servo(2, 0) # Wrist servo to 0 degrees
smooth_move_servo(3, 150) # Pivot servo to 150 degrees
smooth_move_servo(4, 180) # gripper servo to 180 degrees
print("Robot arm initialized to starting position.")
# Function to pick up an object based on the position index and place it at the destination
def move_robot_arm(position_index):
position = PRESET_POSITIONS[position_index]
smooth_move_servo(4, 180) # Open the gripper
smooth_move_servo(0, position['base']) # Move other servos to target position
smooth_move_servo(1, position['elbow'])
smooth_move_servo(2, position['wrist'])
smooth_move_servo(3, position['pivot'])
sleep(1) # Time for the arm to move to the pickup position
smooth_move_servo(4, 0) # Close the gripper to pick up the object
sleep(3) # Time for the gripper to close
smooth_move_servo(1, position['elbow']+60)
def move_to_bin_and_release(label):
if label in BIN_POSITIONS:
position = BIN_POSITIONS[label]
smooth_move_servo(0, position['base']) # Move other servos to target position
smooth_move_servo(1, position['elbow'])
smooth_move_servo(2, position['wrist'])
smooth_move_servo(3, position['pivot'])
sleep(2) # Time for the arm to move to the bin position
smooth_move_servo(4, 180) # Close the gripper to drop the object
sleep(1) # Time for the gripper to close
initialize_robot_arm() # Return to the initial position
print(f"Object with label '{label}' dropped at its designated bin.")
# Function to find a matching coordinate within tolerance
def find_matching_coordinate(x, y):
for coord in PREDEFINED_COORDINATES:
if abs(coord['x'] - x) <= TOLERANCE and abs(coord['y'] - y) <= TOLERANCE:
return coord
return None
# MQTT on_connect callback
def on_connect(client, userdata, flags, rc):
print(f"Connected with result code {rc}")
client.subscribe(MQTT_TOPIC)
# MQTT on_message callback
def on_message(client, userdata, message):
try:
payload = message.payload.decode('utf-8')
received_data = json.loads(payload)
print(f"Received data: {received_data}")
label = received_data.get("label")
x = received_data.get("x")
y = received_data.get("y")
if label and x is not None and y is not None:
matching_coord = find_matching_coordinate(x, y)
if matching_coord:
print(f"Matching coordinate found at index {matching_coord['position_index']}.")
move_robot_arm(matching_coord['position_index'])
move_to_bin_and_release(label)
else:
print("No matching coordinate found.")
else:
print("Received data does not contain a valid label or coordinates.")
except Exception as e:
print(f"Error processing message: {e}")
# Setup and connection to MQTT broker
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT)
# Initialize the robot arm
initialize_robot_arm()
# Start the MQTT loop in a separate thread
client.loop_start()
# Main loop to keep the script running
try:
while True:
sleep(1)
except KeyboardInterrupt:
print("Exiting gracefully...")
client.disconnect()
client.loop_stop()
