import cv2
import numpy as np
from functools import cmp_to_key
import utils

MIN_CELL_DIGIT_HEIGHT_RATIO = 2.5

# Function to check if two lines should be merged
def should_merge_lines(line_a, line_b, rho_distance, theta_distance):
    rho_a, theta_a = line_a[0].copy()
    rho_b, theta_b = line_b[0].copy()

    if rho_b == rho_a and theta_b == theta_b:
        return False

    theta_b = int(180 * theta_b / np.pi)
    theta_a = int(180 * theta_a / np.pi)

    if rho_b < 0:
        theta_b = theta_b - 180

    if rho_a < 0:
        theta_a = theta_a - 180

    rho_a = np.abs(rho_a)
    rho_b = np.abs(rho_b)

    diff_theta = np.abs(theta_a - theta_b)
    rho_diff = np.abs(rho_a - rho_b)

    if rho_diff < rho_distance and diff_theta < theta_distance:
        return True

    return False

# Function to merge two lines
def merge_lines(line_a, line_b):
    rho_b, theta_b = line_b[0]
    rho_a, theta_a = line_a[0]

    if rho_b < 0:
        rho_b = np.abs(rho_b)
        theta_b = theta_b - np.pi

    if rho_a < 0:
        rho_a = np.abs(rho_a)
        theta_a = theta_a - np.pi

    average_theta = (theta_a + theta_b) / 2
    average_rho = (rho_a + rho_b) / 2

    if average_theta < 0:
        average_rho = -average_rho
        average_theta = np.abs(average_theta)

    return [[average_rho, average_theta]]

# Function to merge nearby lines
def merge_nearby_lines(lines, rho_distance=30, degree_distance=20):
    lines = lines if lines is not None else []
    estimated_lines = []

    for line in lines:
        if line is False:
            continue

        estimated_line = get_merged_line(lines, line, rho_distance, degree_distance)
        estimated_lines.append(estimated_line)

    return estimated_lines

# Function to draw lines on an image
def draw_lines(lines, img):
    if lines is not None:
        for line in lines:
            rho, theta = line[0]
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            pt1 = (int(x0 + 10000*(-b)), int(y0 + 10000*(a)))
            pt2 = (int(x0 - 10000*(-b)), int(y0 - 10000*(a)))
            cv2.line(img, pt1, pt2, (255, 255, 255), 2)

# Function to sort bounding rectangles by upper left position
def sort_by_upper_left_pos(rect_a, rect_b):
    x_a, y_a, _, _ = rect_a
    x_b, y_b, w_b, _ = rect_b

    x_b_offset_positive = x_b + w_b / 3
    x_b_offset_negative = x_b - w_b / 3
    is_same_column = x_a < x_b_offset_positive and x_a > x_b_offset_negative

    if is_same_column:
        return y_a - y_b
    return (x_a - x_b_offset_positive)

# Function to get the merged line
def get_merged_line(lines, line_a, rho_distance, degree_distance):
    for i, line_b in enumerate(lines):
        if line_b is False:
            continue

        if should_merge_lines(line_a, line_b, rho_distance, degree_distance):
            line_a = merge_lines(line_a, line_b)
            lines[i] = False

    return line_a

# Function to filter bounding rectangles by dimensions
def filter_by_dim(val, target_width, target_height):
    offset_width = target_width * 0.3
    offset_height = target_height * 0.3
    _, _, w, h = val
    return target_width - offset_width < w < target_width + offset_width and target_height - offset_height < h < target_height + offset_height

# Function to find the most common area among bounding rectangles
def get_most_common_area(bounding_rects, cell_resolution):
    cell_areas = [int(w*h/cell_resolution) for _, _, w, h in bounding_rects]
    counts = np.bincount(cell_areas)
    return bounding_rects[np.argmax(counts)]

# Function to validate and find the sign sheet cell
def validate_and_find_sign_sheet_cell(cells, bounding_rect):
    roi_x, roi_y, roi_w, roi_h = bounding_rect
    roi_center_x = roi_x + int(roi_w/2)
    roi_center_y = roi_y + int(roi_h/2)

    _, _, cell_width, cell_height = cells[0]

    if not 2 < roi_w < cell_width or not (cell_height/MIN_CELL_DIGIT_HEIGHT_RATIO) < roi_h < cell_height:
        return None

    found_cell = None

    for rect in cells:
        x, y, w, h = rect
        if x < roi_center_x < x + w and y < roi_center_y < y + h:
            found_cell = rect
            break

    return found_cell

# Function to get sign sheet cells bounding rectangles
def get_sign_sheet_cells_bounding_rects(img_binary_grid, num_rows_in_grid=19, max_num_cols=20):
    binary_grid_contours, _ = cv2.findContours(img_binary_grid, cv2.RETR_LIST,
                                               cv2.CHAIN_APPROX_SIMPLE)

    sheet_width = img_binary_grid.shape[1]

    cell_min_width = (sheet_width/max_num_cols)
    sign_sheet_cells_bounding_rects = [cv2.boundingRect(cnt) for cnt in binary_grid_contours if utils.wider_than(cnt, cell_min_width)]

    cell_resolution = (sheet_width/50) ** 2

    _, _, target_width, target_height = get_most_common_area(sign_sheet_cells_bounding_rects, cell_resolution)

    if len(sign_sheet_cells_bounding_rects) < num_rows_in_grid:
        print("ERROR: No grid cells found.")

    sign_sheet_cells_bounding_rects = list(filter(lambda x: filter_by_dim(x, target_width, target_height), sign_sheet_cells_bounding_rects))

    num_cells = len(sign_sheet_cells_bounding_rects)
    correct_num_cells_in_grid = (num_cells >= num_rows_in_grid and num_cells % num_rows_in_grid == 0)

    if not correct_num_cells_in_grid:
        print("ERROR: num found:", num_cells)

    sign_sheet_grid_bounding_rect = utils.concatenate_bounding_rects(sign_sheet_cells_bounding_rects)

    shift_x, shift_y, _, _ = sign_sheet_grid_bounding_rect
    sign_sheet_cells_bounding_rects = list(map(lambda x: utils.move_bounding_rect(x, -shift_x, -shift_y), sign_sheet_cells_bounding_rects))
    sign_sheet_cells_bounding_rects = sorted(sign_sheet_cells_bounding_rects, key=cmp_to_key(sort_by_upper_left_pos))
    
    return sign_sheet_cells_bounding_rects, sign_sheet_grid_bounding_rect
