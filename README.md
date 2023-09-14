
### 2. Image Preprocessing

The steps include:

1. **Reading the Image**: The image is read from the `Samples` directory based on the filename provided as an argument.
   
2. **Image Scaling**: The image is resized to 40% of its original size for easier processing and speed optimization.
    
3. **Adaptive Binary Conversion**:
    - The image is converted to grayscale.
    - Gaussian Blur is applied for noise reduction.
    - Adaptive thresholding is used to obtain a binary image with the `cv2.ADAPTIVE_THRESH_GAUSSIAN_C` method.

4. **Image Rotation and Cropping**:
    - External contours of the binary image are identified.
    - The largest contour, assumed to be the sign sheet, is isolated.
    - The image is rotated based on the orientation of the largest contour to ensure it's aligned correctly.
    - The image is further cropped to focus on the relevant sections.

### 3. Text Extraction and Signature Detection

1. **Text Extraction**:
    - Using the `easyocr` library, the program reads text data from the processed sections of the image. 
    - The OCR results are then cleaned, with certain character replacements (e.g., `$` replaced by `S`).
    
2. **Signature Detection**:
    - Each section of the image, assumed to represent a student, contains a subsection for the signature.
    - The white-space percentage in the signature area is computed.
    - Based on a threshold (5% in this code), it's determined whether a signature is present (attendance marked) or not.

### 4. Output

1. **Text Information**:
    - The extracted data (student index, name, and attendance) is structured and saved in XML format under the `Outputs` directory.
    
2. **Signature Saving**:
    - The detected signatures are saved as individual `.jpeg` images under the `Outputs` directory.

--------

##  Modules and Functions

###  Utility Functions

#### `__should_merge_lines(line_a, line_b, rho_distance, theta_distance)`

Determines if two lines should be merged based on their rho and theta values.

#### `resize_to_right_ratio(img, interpolation=cv2.INTER_LINEAR, width=750)`

Resizes the input image to the right ratio, given a specified width.

#### `merge_lines(line_a, line_b)`

Merges two lines and returns their average rho and theta values.

#### `get_merged_line(lines, line_a, rho_distance, degree_distance)`

Returns the merged line for the given lines and parameters.

#### `adaptive_binary_image(img)`

Converts the image to grayscale, blurs it, and then applies adaptive thresholding to generate a binary image.

#### `merge_nearby_lines(lines, rho_distance=30, degree_distance=20)`

Merges lines that are close to each other based on specified rho and degree distances.

#### `draw_lines(lines, img)`

Draws the detected lines on the input image.

### 3.2. Image Processing Functions

#### `sort_by_upper_left_pos(rect_a, rect_b)`

Sorts rectangles based on their top-left position.

#### `get_rotated_sign_sheet_sheet(img, img_adaptive_binary)`

Gets the rotated sign sheet from the image based on contours.

#### `generate_sign_sheet_sheet(img, num_rows_in_grid=19, max_num_cols=20)`

Generates and processes the sign sheet, including rotation, grid detection, and cell detection.

#### `get_sign_sheet_grid(img_binary_sheet)`

Generates a grid on the sign sheet for further cell detection.

#### `__filter_by_dim(val, target_width, target_height)`

Filters bounding rectangles based on dimensions.

#### `getting_the_most_common_area(bounding_rects, cell_resolution)`

Identifies the most common area among the bounding rectangles.

#### `validate_and_find_sign_sheet_cell(cells, bounding_rect)`

Validates and finds the sign sheet cell in the bounding rectangles.

#### `getting_the_sign_sheet_cells_bounding_rects(img_binary_grid, num_rows_in_grid=19, max_num_cols=20)`

Identifies the bounding rectangles of the sign sheet cells.

##  Workflow

1. Load the image.
2. Pre-process the image by resizing and converting to a binary image.
3. Detect and correct orientation to get a rotated sign sheet.
4. Extract the grid from the sign sheet.
5. Detect and process cells within the grid.
6. Return the processed sign sheet and cells' bounding rectangles.

