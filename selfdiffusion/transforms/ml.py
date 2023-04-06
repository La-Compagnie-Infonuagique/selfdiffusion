import PIL.Image
import face_recognition
import numpy as np

from typing import Tuple, List
from ultralytics import YOLO

def faces_location(image: PIL.Image.Image) -> List[Tuple[int,int]]:
    """ Return the location of the faces in the image. """

    # Convert PIL image to numpy array
    image_array = np.array(image)

    # Find face locations using face_recognition
    face_locations = face_recognition.face_locations(image_array)

    # Calculate center coordinates of the faces
    face_centers = []
    for top, right, bottom, left in face_locations:
        x = left + (right - left) // 2
        y = top + (bottom - top) // 2
        face_centers.append((x, y))

    return face_centers

def persons_location(image: PIL.Image.Image, model_id: str = "yolov8n.pt") -> List[Tuple[int, int, int, int]]:
    # instanciate the yolov8 detection model
    model = YOLO(model_id)

    # give the image to the model for analysis
    results = model(image)

    # extract the one result from the image
    result = results[0]

    # extract the names from the result
    names = result.names

    # filter the only keep the person bounding boxes
    person_rois = []

    for box in result.boxes:
        # extract the class for this box
        cls_index = int(box.cls.item())
        name = names[cls_index]

        if name == "person":
            # unpack the bounding box and append to result list
            x, y, w, h = box.xywh[0].tolist()

            # translate the coordinates of the x,y from the center to the top
            # left corner of the box.
            x = int(x - w / 2)
            y = int(y - h / 2)
            #
            person_rois.append((x, y, w, h))
        else:
            pass

    return person_rois
