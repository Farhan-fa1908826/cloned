from PIL import Image, ImageDraw
import base64
import random
from io import BytesIO

def decode_base64_image(image_string):
    """Decode a base64 image string into a PIL Image object."""
    image_bytes = base64.b64decode(image_string)
    image = Image.open(BytesIO(image_bytes))
    return image

def encode_image_to_base64(image):
    """Encode a PIL Image object to a base64 string."""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def apply_threshold(image, threshold):
    """Apply thresholding to each color channel of the image."""
    width, height = image.size
    thresholded_image = Image.new("RGB", (width, height))
    for y in range(height):
        for x in range(width):
            pixel = image.getpixel((x, y))
            # Apply threshold to each color channel
            r = 0 if pixel[0] < threshold else 255
            g = 0 if pixel[1] < threshold else 255
            b = 0 if pixel[2] < threshold else 255
            thresholded_image.putpixel((x, y), (r, g, b))
    return thresholded_image

def generate_visual_cryptography_shares(original_image):
    """Generate two shares of a visual cryptography scheme."""
    width, height = original_image.size
    
    # Create share images
    share1 = Image.new("RGB", (width, height), color=(255, 255, 255))  # Initialize with white pixels
    share2 = Image.new("RGB", (width, height), color=(255, 255, 255))  # Initialize with white pixels

    # Create draw objects
    draw1 = ImageDraw.Draw(share1)
    draw2 = ImageDraw.Draw(share2)

    # Randomly assign color channels of each pixel to each share
    for y in range(height):
        for x in range(width):
            pixel = original_image.getpixel((x, y))
            # Split pixel into R, G, and B components
            r, g, b = pixel
            if random.choice([True, False]):  # Randomly choose which share to assign the color channels
                draw1.point((x, y), fill=(r, 255, 255))  # Assign R channel to share 1
                draw2.point((x, y), fill=(255, g, b))    # Assign G and B channels to share 2
            else:
                draw1.point((x, y), fill=(255, g, b))    # Assign G and B channels to share 1
                draw2.point((x, y), fill=(r, 255, 255))  # Assign R channel to share 2

    return share1, share2

def combine_shares_to_recreate_image(share1, share2):
    """Combine two shares to recreate the original image."""
    width, height = share1.size
    combined_image = Image.new("RGB", (width, height), color=(255, 255, 255))  # Initialize with white pixels
    draw = ImageDraw.Draw(combined_image)

    for y in range(height):
        for x in range(width):
            pixel1 = share1.getpixel((x, y))
            pixel2 = share2.getpixel((x, y))
            # Combine color channels from both shares
            r = pixel1[0] if pixel1[0] != 255 else pixel2[0]
            g = pixel1[1] if pixel1[1] != 255 else pixel2[1]
            b = pixel1[2] if pixel1[2] != 255 else pixel2[2]
            draw.point((x, y), fill=(r, g, b))

    return combined_image

# Input the base64-encoded image string
base64_image_string = input("Enter the base64 encoded image string: ")

# Decode the base64 string into a PIL Image object
original_image = decode_base64_image(base64_image_string)

# Apply thresholding to the original image
thresholded_image = apply_threshold(original_image, threshold=100)

# Generate two shares of the visual cryptography scheme
share1, share2 = generate_visual_cryptography_shares(thresholded_image)

# Combine the shares to recreate the original image
recreated_image = combine_shares_to_recreate_image(share1, share2)

# Display the recreated image
recreated_image.show()

# Optional: Save the shares and the recreated image
share1.save("share1.png")
share2.save("share2.png")
recreated_image.save("recreated_image.png")
