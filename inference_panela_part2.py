import os, shutil, json
import numpy as np
import cv2

json_path = 'panela_20m_teste_0.5.json'

with open(json_path) as f:
    data = json.load(f)
    
from inference_panela_part1 import model, predict_yolo, apply_clahe
from inference_panela_part1 import mask_from_polygon, draw_mask
from copy import deepcopy


def convert_box(box, start):
    box = np.array(box)*2
    box[1] += start
    box[3] += start
    return box

def convert_mask(polygon, start):
    polygon = np.array(polygon).reshape(-1, 2)*2
    polygon[..., 1] += start
    return polygon

def adjust_coordinates(results_list, box_roi, start):
    new_results = []
    for result in results_list:
        bbox = convert_box(result['global_bbox'], start)
        cx, cy = (bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2
        print(cx, cy,  bbox, box_roi)
        if box_roi[0] < cx < box_roi[2] and box_roi[1] < cy < box_roi[3]:
            new_results.append(
                {"class" : result["class"],
                "global_bbox" : bbox,
                "global_polygon" : convert_mask(result['global_polygon'], start),
                "area" : result['area']*4,
                "direction": None,
                "thickness" : None
                }
            )
    return new_results


def plot_box(image, box, label, color=(255)):
    cv2.rectangle(image, box[:2], box[2:], color,2)
    cv2.putText(image, label, (box[0], box[1] - 20),cv2.FONT_HERSHEY_SIMPLEX,2,color,2)
    return image

cut_regions = np.array([4096 * i for i in range(5)])

print(cut_regions)

def join_boxes(box, box2):
    
    x_min = min(box[0], box2[0])
    y_min = min(box[1], box2[1])
    x_max = max(box[2], box2[2])
    y_max = max(box[3], box2[3])
    return [x_min, y_min, x_max, y_max]


def plot_results(image, results):

    for detection in results:
        label = detection["class"]
        bbox = detection["global_bbox"]
        polygon = detection["global_polygon"]
        image = plot_box(image, bbox, label)
        mask = mask_from_polygon(polygon, image.shape)
        image = draw_mask(image, mask)

    return image


def check_proximity_boxes(detections, image_path, outdir):
    boxes = []
    for element in detections:
        boxes.append(element['global_bbox'])
        
    remover = []
    
    boxes_to_add = []

    for i, box in enumerate(boxes):
        for j, box2 in enumerate(boxes):
            if i != j:
                point_box1 = np.array([(box[0] + box[2]) / 2 , box[3]])
                point_box2 = np.array([(box2[0] + box2[2]) / 2 , box2[1]])
                distance = np.linalg.norm(point_box2 - point_box1)
                if distance < 100:
                    check2 = np.min(np.abs(cut_regions - point_box2[1]))
                    
                    q = np.argmin(np.abs(cut_regions - point_box2[1]))
                    if check2 < 50:
                        min_y = min(box[1], box2[1])
                        start = cut_regions[q-1] + 2048
                        print(i, j , distance, box, box2, check2, min_y, q, start, start+4096)
                        image = cv2.imread(image_path,0)
                        
                        crop = image[start:start+4096,:]
                        crop = cv2.resize(crop, (2048, 2048))
                        crop_color = cv2.merge((crop, crop, crop))
                        results = predict_yolo(crop_color)
                        join_box = join_boxes(box, box2)
                        new_results = adjust_coordinates(results, join_box, start)
                        image = plot_results(image, new_results)
                        
                        if len(new_results) > 0:
                            boxes_to_add.extend(new_results)
                            save_path = os.path.join(outdir, os.path.basename(image_path))
                            remover.append(i)
                            remover.append(j)
                            cv2.imwrite(save_path, image)
                       
            
    
    for i in sorted(remover, reverse=True):
        del detections[i] 
    
    if len(boxes_to_add) > 0:
        detections.extend(boxes_to_add)
   
      
        
    return detections              
                        
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)

def save_dict(save_path, dictionary):
    with open(save_path, 'w') as json_file:
        json.dump(dictionary, json_file, ensure_ascii=False, cls=NpEncoder, indent=2)                        
                        
                        
outdir = 'overlap'
os.makedirs(outdir, exist_ok=True)

data_fix = {}

for image_path in data:
    detections = data[image_path]
    data_fix[os.path.basename(image_path)] = check_proximity_boxes(detections, image_path, outdir)
    
save_dict('panela_20m_threshold_0.5_filename.json', data_fix)
    