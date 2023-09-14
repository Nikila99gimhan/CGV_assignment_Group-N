import sys

import cv2
from skimage.metrics import structural_similarity as ssim


def match(path1, path2):
    img1 = cv2.imread(path1)
    img2 = cv2.imread(path2)
    img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    img1 = cv2.resize(img1, (300, 300))
    img2 = cv2.resize(img2, (300, 300))

    similarity_value = "{:.2f}".format(ssim(img1, img2, gaussian_weights=True, sigma=1.2, use_sample_covariance=False) * 100)

    return float(similarity_value)


student_id = sys.argv[1]

path1 = f'./Outputs/1_{student_id}.jpeg'
path2 = f'./Outputs/3_{student_id}.jpeg'
print(path1)
print(path2)
similarity_value = match(path1, path2)
print(similarity_value)
