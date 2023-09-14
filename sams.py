import sys

import cv2
import numpy as np
import Image_sheetutills
import easyocr
import utilities
import xml.etree.cElementTree as ET

# Reading Image
print('[ Step 1 ] Reading Image...')

print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(sys.argv))

filename = sys.argv[1]
filename = filename.split(".")[0]
sample = cv2.imread("./Samples/" + sys.argv[1])
print('[ Step 1 ] Image Read Completed!')


def adaptive_binary_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    cv2.imwrite("./Outputs/gray_" + filename + ".jpeg", gray)
    return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 7, 4)


def rotated_sheet(img, img_adaptive_binary):
    contours = external_contours(img_adaptive_binary)
    biggest_contour = biggest_intensity_contour(contours)

    img_raw_sheet = utilities.get_rotated_image_from_contour(img, biggest_contour)
    img_raw_sheet = Image_sheetutills.resize_to_right_ratio(img_raw_sheet)
    img_binary_sheet_rotated = adaptive_binary_image(img_raw_sheet)

    return img_raw_sheet, img_binary_sheet_rotated


def biggest_intensity_contour(contours):
    sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)
    biggest_contour = sorted_contours[0]
    return biggest_contour


def external_contours(img_1_channel):
    contours, _ = cv2.findContours(img_1_channel, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours


# Starting the process
print("[ Step 2 ] Image scaling ...")
scale_percent = 40
width = int(sample.shape[1] * scale_percent / 100)
height = int(sample.shape[0] * scale_percent / 100)
dim = (width, height)

resized = cv2.resize(sample, dim, interpolation=cv2.INTER_AREA)
print("[ Step 2 ] Image Scaling Completed")

#
print("[ Step 3 ] Binarizing, GreyScaling and Rotating the Image...")
binary_image = adaptive_binary_image(resized)

image_with_contours, img_binary_sheet_rotated = rotated_sheet(resized, binary_image)

rotated_image = cv2.rotate(img_binary_sheet_rotated, cv2.ROTATE_90_CLOCKWISE)

shape = rotated_image.shape
new_height = int(shape[1] * 44 / 180)
# 44:180
sub_image = rotated_image[shape[0] - new_height: shape[0], 0: shape[1]]

shape = sub_image.shape
section_height = int(new_height / 6)
print("[ Step 3 ] Completed Binarizing, GreyScaling and Rotating the Image!")

print("[ Step 4 ] Reading Text...")
reader = easyocr.Reader(['en'], gpu=False)

root = ET.Element("nsbm")
doc = ET.SubElement(root, "students")

init_y = 0
for i in range(6):
    print("[ Step 4." + str(i + 1) + ".1 ] Reading Text of Row " + str(i + 1) + "...")
    section = sub_image[0 + section_height * i: section_height * (i + 1), 0: shape[1]]

    sig_section = section[0: section_height, shape[1] - int(shape[1] / 5): shape[1]]
    sig_shape = sig_section.shape
    h = int((sig_shape[0] * 8 / 10) / 2)
    w = int((sig_shape[1] * 8 / 10) / 2)
    x = int(sig_shape[1] / 2) - w
    y = int(sig_shape[0] / 2) - h
    cropped_sig = sig_section[y:y + (h * 2), x:x + (w * 2)]

    section = sub_image[0 + section_height * i: section_height * (i + 1), int(shape[1] / 8): 4 * int(shape[1] / 5)]

    sig_percentage = ((float(np.sum(cropped_sig == 255)) / float(cropped_sig.size)) * 100)
    result = reader.readtext(section, detail=0)
    result[2] = result[2].replace("$", "S")
    data = {
        "index": result[0],
        "name": result[2],
        "attendance": sig_percentage > 5,
    }

    if len(result) > 3:
        data['name'] = result[2] + " " + result[3]
    student = ET.SubElement(doc, "student")
    ET.SubElement(student, "index").text = result[0]
    ET.SubElement(student, "attendance").text = "true" if sig_percentage > 5 else "false"
    print("[ Step 4." + str(i + 1) + ".1 ] Reading Text of Row " + str(i + 1) + " Completed!")

    print("[ Step 4." + str(i + 1) + ".2 ] Saving Captured Signature of Row " + str(i + 1) + "...")
    outputPath = "./Outputs/" + filename + "_" + result[0] + ".jpeg"
    cv2.imwrite(outputPath, cropped_sig)
    print("[ Step 4." + str(i + 1) + ".2 ] Saving Captured Signature of Row " + str(i + 1) + " Completed!")

print("[ Step 4 ] Reading Text Completed!")

print("[ Step 5 ] Saving to XML...")
tree = ET.ElementTree(root)
tree.write("./Outputs/" + filename + "_info.xml")
print("[ Step 5 ] Saving XML Completed!")
