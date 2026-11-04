import math

class SimpleTracker:
    def __init__(self, max_lost=30):
        self.tracks = {} # {id: {"box": [x,y,w,h], "lost": 0}}
        self.next_id = 1
        self.max_lost = max_lost

    def update(self, detections):
        # Mark all current tracks as "lost" by incrementing lost counter
        for track_id in self.tracks:
            self.tracks[track_id]["lost"] += 1

        # Match detections to existing tracks
        for det in detections:
            x, y, w, h = det["box"]
            center_x, center_y = x + w/2, y + h/2
            
            best_match_id = None
            min_dist = 9999

            for track_id, data in self.tracks.items():
                tx, ty, tw, th = data["box"]
                t_center_x, t_center_y = tx + tw/2, ty + th/2
                
                # Calculate distance between centers
                dist = math.sqrt((center_x - t_center_x)**2 + (center_y - t_center_y)**2)
                
                # If close enough, it's the same person
                if dist < 100 and dist < min_dist:
                    min_dist = dist
                    best_match_id = track_id

            if best_match_id is not None:
                # Update existing track
                self.tracks[best_match_id]["box"] = det["box"]
                self.tracks[best_match_id]["lost"] = 0
                det["track_id"] = best_match_id
            else:
                # Create new track
                self.tracks[self.next_id] = {"box": det["box"], "lost": 0}
                det["track_id"] = self.next_id
                self.next_id += 1

        # Remove tracks that have been lost for too long
        to_remove = [tid for tid, data in self.tracks.items() if data["lost"] > self.max_lost]
        for tid in to_remove:
            del self.tracks[tid]

        return detections

    def get_total_unique_count(self):
        # The highest ID represents the total unique people tracked
        return self.next_id - 1
