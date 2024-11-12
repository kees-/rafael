import cv2
import numpy as np

# Load as grayscale
image = cv2.imread('tougher.bmp', cv2.IMREAD_GRAYSCALE)

# Threshold to get a binary image
_, binary_image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY_INV)

# Find contours in the binary image
contours, _ = cv2.findContours(binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

# Create a mask for each contour
masks = []
mask_threshold = 170.0
for i, contour in enumerate(contours):
    # Create a blank mask
    mask = np.zeros_like(binary_image)
    cv2.drawContours(mask, [contour], -1, 255, -1)  # Fill the contour
    if cv2.mean(image, mask=mask)[0] > mask_threshold:
      cv2.imwrite(f'target/mask_{i:>03}.png', mask)
      masks.append(mask)

# Visualize contours with unique colors
combined_mask = np.zeros_like(binary_image)
for i, mask in enumerate(masks):
  combined_mask[mask > 0] = 128  # Assign a grayscale value

cv2.imwrite('target/combined.png', combined_mask)
