import cv2
from PIL import Image
import numpy as np
from ultralytics import YOLO
from glob import glob
import os
import json
from tqdm import tqdm


def apply_clahe(img, output_path=None, clip_limit=2.0, tile_grid_size=(8, 8)):
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    img_clahe = clahe.apply(img)
    return img_clahe

def convert_box(box, image_number):
    box = np.array(box)*2
    box[1] = box[1] + 4096 * image_number
    box[3] = box[3] + 4096 * image_number
    return box

def convert_mask(polygon, image_number):
    polygon = np.array(polygon).reshape(-1, 2)*2
    polygon[..., 1] += 4096*image_number
    return polygon

def adjust_coordinates(results_list, image_number):
    new_results = []
    for result in results_list:
        new_results.append(
            {"class" : result["class"],
             "global_bbox" : convert_box(result['global_bbox'], image_number),
             "global_polygon" : convert_mask(result['global_polygon'], image_number),
             "area" : result['area']*4,
             "direction": None,
             "thickness" : None
             }
        )
    return new_results

model = YOLO('best_inter.pt')

def get_box_from_mask(mask, shape):
    points = np.int32(mask.xy).reshape(-1, 2)
    #print(points)
    min_x = min(points[..., 0])
    min_x = max(min_x, 0)
    min_y = min(points[..., 1])
    min_y = max(min_y, 0)
    max_x = max(points[..., 0])
    max_x = min(max_x, shape[1])
    max_y = max(points[..., 1])
    max_y = min(max_y, shape[0])
    return [min_x, min_y, max_x, max_y]


def mask_from_polygon(mask, shape):
    points = np.int32(mask).reshape(-1, 2)
    image_mask = np.zeros(shape, dtype=np.uint8)
    cv2.fillPoly(image_mask, [points], (255))
    #cv2.imwrite('polygon.png', image_mask)
    return image_mask


def simplify_polygon(mask, shape, min_area=0):
    #print('original', len(mask[0]))
    mask = mask_from_polygon(mask, shape)
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    polygons = []
    height, width = mask.shape

    contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)

    # Pega o maior contorno, se existir
    if contours_sorted:
        largest_contour = contours_sorted[0]
        area = cv2.contourArea(largest_contour)

        if area > min_area:
            epsilon = 0.002 * cv2.arcLength(largest_contour, True)
            approx = cv2.approxPolyDP(largest_contour, epsilon, True)

            if len(approx) >= 3:
                points = []
                for point in approx:
                    x, y = point[0]
                    points.extend([x, y])

                if len(points) >= 6:
                    polygons.append(points)

    return polygons


def predict_yolo(image):
    result = model(image, verbose=False, conf=0.5)[0]
    shape = result.orig_shape
    boxes = result.boxes
    masks = result.masks
    labels = boxes.cls.tolist()
    scores = boxes.conf.tolist()
    boxes = boxes.xyxy.tolist()
    boxes = [tuple(map(int,y)) for y in boxes]
    labels = [int(y) for y in labels]

    if masks is None:
        masks = []
    results = []

    for label, score, mask in zip(labels, scores, masks):
        box = get_box_from_mask(mask, shape)
        polygon = simplify_polygon(mask.xy, shape)
        mask = mask_from_polygon(polygon, shape)
        area_mask = cv2.countNonZero(mask)
        results.append(
            {"class" : classes_dict[label],
             "global_bbox" : box,
             "global_polygon" : polygon,
             "area" : area_mask,
             "direction": None,
             "thickness" : None
             }
            )
        
    return results

classes_dict = model.names

def draw_mask(image, mask_generated) :
  masked_image = image.copy()

  masked_image = np.where(mask_generated.astype(int),
                          np.array([255], dtype='uint8'),
                          masked_image)

  masked_image = masked_image.astype(np.uint8)

  return cv2.addWeighted(image, 0.7, masked_image, 0.3, 0)

def plot_box(image, box, label):
    cv2.rectangle(image, box[:2], box[2:], (255),2)
    cv2.putText(image, label, (box[0], box[1] - 20),cv2.FONT_HERSHEY_SIMPLEX,2,(255),2)
    return image


def plot_results(image, results):

    for detection in results:
        label = detection["class"]
        bbox = detection["global_bbox"]
        polygon = detection["global_polygon"]
        image = plot_box(image, bbox, label)
        mask = mask_from_polygon(polygon, image.shape)
        image = draw_mask(image, mask)

    return image


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



def process_image(image_path, outdir='output'):

    img = Image.open(image_path)
    img = np.array(img)
    h, w = img.shape
    dh = h // 5
    dw = w
    output = []
    os.makedirs(outdir, exist_ok=True)
    save_path = os.path.join(outdir, os.path.basename(image_path))

    for i in range(5):
        img2 = img[i*dh:(i+1)*dh, 0:dw]
        img2 = cv2.resize(img2, (2048, 2048))
        #img2 = apply_clahe(img2)

        results = predict_yolo(cv2.merge((img2, img2, img2)))
        #print(results)
        new_results = adjust_coordinates(results, i)
        #print(new_results)
        # img2 = plot_results(img2, results)
        img = plot_results(img, new_results)
        # cv2.imwrite(f'final_{i}.png', img2)
        # # #cv2.imwrite(f'plot.png', img)
        cv2.imwrite(save_path, img)

        if len(new_results) > 0:
            output.extend(new_results)

    return output


if __name__ == "__main__":

    save_json = {}

    images_dir = 'output_20m_teste_clahe'
    images = glob(images_dir + '/*.png')
    # images = images[:10]

    for image_path in tqdm(images):
        output = process_image(image_path)
        save_json[image_path] = output
        
    save_dict('panela_20m_teste_0.5.json', save_json)
    
