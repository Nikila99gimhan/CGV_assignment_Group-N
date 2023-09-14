import cv2
import os
import numpy as np

DEBUG = False

# Function to set the debug mode
def set_debug(debug):
    global DEBUG
    DEBUG = debug

# Function to check if a contour is wider than a specified width
def wider_than(contour, min_width):
    x, y, w, h = cv2.boundingRect(contour)
    return w > min_width

# Function to move a bounding rectangle by delta_x and delta_y
def move_bounding_rect(rect, delta_x, delta_y):
    x, y, w, h = rect
    return (x+delta_x, y+delta_y, w, h)

# Function to concatenate multiple bounding rectangles into one
def concatenate_bounding_rects(bounding_rects):
    temp_arr = []
    for x, y, w, h in bounding_rects:
        temp_arr.append((x, y))
        temp_arr.append((x+w, y+h))

    return cv2.boundingRect(np.asarray(temp_arr))

# Function to extract the content of a bounding rectangle from an image
def get_bounding_rect_content(img, bounding_rect):
    x, y, w, h = bounding_rect
    return img[y:y+h, x:x+w]

# Function to extract the area inside a contour from an image
def get_contour_area_from_img(img, contour):
    return get_bounding_rect_content(img, cv2.boundingRect(contour))

# Function to rotate an image based on a contour's orientation
def get_rotated_image_from_contour(img, contour):
    rotated_rect = cv2.minAreaRect(contour)
    x_center = int(rotated_rect[0][0])
    y_center = int(rotated_rect[0][1])
    width = int(rotated_rect[1][0])
    height = int(rotated_rect[1][1])
    angle_degrees = rotated_rect[2]

    if(width > height):
        temp_height = height
        height = width
        width = temp_height
        angle_degrees = 90 + angle_degrees
    rotated_rect = ((x_center, y_center), (width, height), angle_degrees)
    rect_box_points = cv2.boxPoints(rotated_rect)

    img_debug_contour = img.copy()
    cv2.drawContours(img_debug_contour, [contour], 0, (0, 0, 255), 3)

    img_debug = img.copy()
    cv2.drawContours(img_debug, [np.int0(rect_box_points)], 0, (0, 0, 255), 3)

    src_pts = rect_box_points.astype("float32")
    dst_pts = np.array([
        [0, height-1],
        [0, 0],
        [width-1, 0],
    ], dtype="float32")

    ROTATION_MAT = cv2.getAffineTransform(src_pts[:3], dst_pts)
    return cv2.warpAffine(img, ROTATION_MAT, (width, height))

# Function to calculate the center shift of an image
def get_com_shift(img):
    M = cv2.moments(img)
    height, width = img.shape
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    shift_x = np.round(width/2.0-cX).astype(int)
    shift_y = np.round(height/2.0-cY).astype(int)
    return shift_x, shift_y

# Function to shift an image by delta_x and delta_y
def shift_by(img, delta_x, delta_y):
    rows, cols = img.shape
    M = np.float32([[1, 0, delta_x], [0, 1, delta_y]])
    return cv2.warpAffine(img, M, (cols, rows))

# Function to draw bounding rectangles on an image
def draw_bounding_rects(img, bounding_rects):
    for index, cell in enumerate(bounding_rects):
        x, y, w, h = cell
        cv2.putText(img, str(index), (x, y + int(h/2)), cv2.FONT_HERSHEY_SIMPLEX, .6, (100, 200, 0), 1, cv2.LINE_AA)
        cv2.rectangle(img, cell, (0, 255, 0), 1)

# Function to get external contours from a 1-channel image
def get_external_contours(img_1_channel):
    contours, _ = cv2.findContours(
        img_1_channel, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

# Function to get all contours and hierarchy from a 1-channel image
def get_contours(img_1_channel):
    contours, hierarchy = cv2.findContours(
        img_1_channel, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    return contours, hierarchy

# Function to compare contours by their bounding rectangle size
def compareBoundingSize(contour):
    contour = cv2.convexHull(contour)
    (_, _), (w, h), _ = cv2.minAreaRect(contour)
    return w*h

# Function to get the biggest contour by bounding rectangle size
def get_biggest_contour(contours):
    sorted_contours = sorted(contours, key=compareBoundingSize, reverse=True)
    biggest_contour = sorted_contours[0]
    return biggest_contour

# Function to get the biggest intensity contour
def get_biggest_intensity_contour(contours):
    sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
    biggest_contour = sorted_contours[0]
    return biggest_contour
