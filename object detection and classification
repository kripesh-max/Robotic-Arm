import time
import torch
import cv2
import sys
import json
import warnings
import paho.mqtt.client as mqtt
warnings.filterwarnings("ignore")
# MQTT Broker settings
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "coordinates_topic"
# Callback function for when a message is published to the broker
def on_publish(client, userdata, mid):
print(f"Message with MID {mid} published.")
# Initialize the MQTT client and set the publish callback
client = mqtt.Client()
client.on_publish = on_publish
client.connect(MQTT_BROKER, MQTT_PORT, 60)
# Start the network loop in a separate thread
client.loop_start()
# Load the YOLOv5 model
model = torch.hub.load("yolov5", 'custom',
path=r"C:\Users\SG\Desktop\work\yolov5\runs\train\exp\weights\best.pt", source='local')
# Configure the model
model.cpu()
model.conf = 0.25
model.iou = 0.4
model.agnostic = False
model.multi_label = False
model.classes = None
model.max_det = 3
model.amp = False
def draw_centroids_on_image_and_get_labels(output_image, json_results,
scale_factor=25):
data = json.loads(json_results)
coordinates_labels = []
for obj in data:
label = obj["name"]
xmin = obj["xmin"]
ymin = obj["ymin"]
xmax = obj["xmax"]
ymax = obj["ymax"]
cx = int((xmin + xmax) / 2.0)
cy = int((ymin + ymax) / 2.0)
# Scale down the coordinates by the scale_factor
cx_scaled = cx // scale_factor
cy_scaled = cy // scale_factor
coordinates_labels.append({"label": label, "x": cx_scaled, "y": cy_scaled})
# Draw the original coordinates for visualization
cv2.circle(output_image, (cx, cy), 2, (0, 0, 255), 2, cv2.FILLED)
# Display the scaled down coordinates and label
cv2.putText(output_image, f"{label}: {cx_scaled}, {cy_scaled}", (cx - 40, cy + 30),
cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
return output_image, coordinates_labels
if __name__ == "__main__":
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) # Adjust the capture source as needed
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
# Define the interval in seconds
CAPTURE_INTERVAL = 5
# Get the current time at the beginning
last_capture_time = time.time()
try:
while True:
current_time = time.time()
ret, frame = cap.read()
if not ret:
print("Failed to grab frame")
break
cv2.imshow("Output", frame)
# Capture the image automatically at the defined interval
if current_time - last_capture_time > CAPTURE_INTERVAL:
# Save the capture time of the current image
last_capture_time = current_time
cv2.imwrite("captured_image.jpg", frame) # Save the image
image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
results = model(image)
json_results = results.pandas().xyxy[0].to_json(orient="records")
rendered_image = results.render()
output_image, coordinates_labels =
draw_centroids_on_image_and_get_labels(rendered_image[0], json_results,
scale_factor=25)
for detection in coordinates_labels:
json_detection = json.dumps(detection)
result, mid = client.publish(MQTT_TOPIC, json_detection)
if result != mqtt.MQTT_ERR_SUCCESS:
print("Failed to publish message")
cv2.imshow("Captured Frame", cv2.cvtColor(output_image,
cv2.COLOR_RGB2BGR))
key = cv2.waitKey(1) & 0xFF
# Break the loop if 'q' is pressed
if key == ord('q'):
break
except KeyboardInterrupt:
print("Interrupted by user")
except Exception as e:
print(f"An error occurred: {e}")
finally:
cap.release()
cv2.destroyAllWindows()
client.loop_stop()
client.disconnect()
sys.exit()
