import cv2
import numpy as np

# Load the image as grayscale
image = cv2.imread('line_drawing.bmp', cv2.IMREAD_GRAYSCALE)

# Threshold the image to get a binary image
_, binary_image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY_INV)

# Find contours in the binary image
contours, _ = cv2.findContours(binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

# Create a mask for each contour
masks = []
for i, contour in enumerate(contours):
    # Create a blank mask
    mask = np.zeros_like(binary_image)
    cv2.drawContours(mask, [contour], -1, 255, thickness=-1)  # Fill the contour
    masks.append(mask)

    # Optionally save each mask
    cv2.imwrite(f'target/mask_{i:>03}.png', mask)

# For verification, you might also want to visualize all contours with unique colors
combined_mask = np.zeros_like(binary_image)
for i, mask in enumerate(masks):
    combined_mask[mask > 0] = (i + 1) * 20  # Assign a unique grayscale value

cv2.imwrite('target/combined.png', combined_mask)
