import cv2
import numpy as np
import onnxruntime as ort
import os
from utils.tracker import SimpleTracker

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load the pre-trained person model and your custom plate model
person_session = ort.InferenceSession(os.path.join(BASE_DIR, "models", "yolov8n.onnx"), providers=["CPUExecutionProvider"])
food_session = ort.InferenceSession(os.path.join(BASE_DIR, "models", "best.onnx"), providers=["CPUExecutionProvider"])

# The classes your custom model was trained on
FOOD_CLASSES = ["Bowl", "Cup", "Fork", "Gripper", "Knife", "Plate", "Spoon", "food"]

# Global tracker instance for live feed
tracker = SimpleTracker()

def process_frame(image, is_live=False):
    """Runs models, tracks people if live, and returns counts and image."""
    original_h, original_w = image.shape[:2]
    
    # Prepare image for YOLO (resize to 640x640 and normalize)
    img = cv2.resize(image, (640, 640))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32) / 255.0
    img = np.transpose(img, (2, 0, 1))
    img = np.expand_dims(img, axis=0)

    # Run both models
    person_out = person_session.run(None, {person_session.get_inputs()[0].name: img})[0][0].T
    food_out = food_session.run(None, {food_session.get_inputs()[0].name: img})[0][0].T

    annotated = image.copy()
    x_scale, y_scale = original_w / 640, original_h / 640

    # Helper to process YOLO output
    def parse_output(output, is_person_model):
        boxes, scores, class_ids = [], [], []
        for det in output:
            conf = float(np.max(det[4:]))
            if conf < 0.40: continue
            
            class_id = int(np.argmax(det[4:]))
            # If using the person model, only keep Class 0 (Person)
            if is_person_model and class_id != 0: continue
            
            x, y, w, h = det[:4]
            left, top = int((x - w/2) * x_scale), int((y - h/2) * y_scale)
            width, height = int(w * x_scale), int(h * y_scale)
            
            boxes.append([left, top, width, height])
            scores.append(conf)
            class_ids.append(class_id)

        # Remove overlapping boxes (Non-Maximum Suppression)
        indices = cv2.dnn.NMSBoxes(boxes, scores, 0.40, 0.45)
        results = []
        if len(indices) > 0:
            for i in np.array(indices).flatten():
                results.append({"box": boxes[i], "confidence": scores[i], "class_id": class_ids[i]})
        return results

    # 1. Process Persons (and Track them if it's live video)
    person_dets = parse_output(person_out, True)
    if is_live:
        person_dets = tracker.update(person_dets)
        # Show how many people are currently being tracked (active + recently lost)
        total_unique_students = len(tracker.tracks)
    else:
        total_unique_students = len(person_dets)

    # 2. Process Plates using your custom model
    food_dets = parse_output(food_out, False)
    plate_count = 0
    
    for det in food_dets:
        cid = det["class_id"]
        # Check if the detected class is "Plate" (Index 5 in your list)
        label = FOOD_CLASSES[cid] if cid < len(FOOD_CLASSES) else "Food"
        if label.lower() == "plate":
            plate_count += 1

    # 3. Draw the boxes on the image
    for det in person_dets:
        x, y, w, h = det["box"]
        track_id = det.get("track_id", "")
        label = f"Student ID: {track_id}" if track_id else "Student"
        cv2.rectangle(annotated, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(annotated, label, (x, max(y-10, 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    for det in food_dets:
        cid = det["class_id"]
        if FOOD_CLASSES[cid].lower() == "plate":
            x, y, w, h = det["box"]
            cv2.rectangle(annotated, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(annotated, "Plate", (x, max(y-10, 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    return {
        "students": total_unique_students,
        "plates": plate_count
    }, annotated
