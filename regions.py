import os
import cv2
import sys
import numpy as np
import random

MASK_THRESHOLD = 160.0 # Arbitrary value to throw out masks of non-cell areas
MASKING_USE_BORDER = False

input = sys.argv[1]
try:
  os.path.isfile(input)
except FileNotFoundError:
  print("File DNE")

os.makedirs("target", exist_ok=True)

# Load as grayscale
image = cv2.imread(input, cv2.IMREAD_GRAYSCALE)

# Threshold to get a binary image
_, binary_image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY_INV)

# Wrap image in 1px white border for detecting enclosures at the edge
bordered_image = cv2.copyMakeBorder(binary_image[1:-1, 1:-1], 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=255)

processed_image = bordered_image if MASKING_USE_BORDER else binary_image

# Find contours in the binary image
contours, _ = cv2.findContours(processed_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

# Create a mask for each contour
masks = []
for i, contour in enumerate(contours):
    # Create a blank mask
    mask = np.zeros_like(binary_image)
    cv2.drawContours(mask, [contour], -1, 255, -1)  # Fill the contour
    # print(f"{i} | image: {cv2.mean(image, mask=mask)[0]}, mask: {cv2.mean(src=mask)[0]}")
    if MASK_THRESHOLD < cv2.mean(image, mask=mask)[0] and cv2.mean(src=mask)[0] < 255:
      cv2.imwrite(f'target/mask_{i:>03}.png', mask)
      masks.append(mask)

# Visualize contours with unique colors
combined_mask = np.zeros_like(binary_image)
for i, mask in enumerate(masks):
  combined_mask[mask > 0] = random.randint(40, 210)  # Assign a grayscale value

a = cv2.cvtColor(combined_mask, cv2.COLOR_GRAY2BGR)
alpha = np.sum(a, axis=-1) > 0
alpha = np.uint8(alpha * 255)
res = np.dstack((a, alpha))

cv2.imwrite('target/combined.png', res)
