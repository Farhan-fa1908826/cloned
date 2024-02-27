"""
Some basic utils 
(previously were in helios module, but making things less interdependent

2010-08-17
"""

import json
import face_recognition as fr
import numpy as np
from PIL import Image, ImageDraw
import base64
import random
from io import BytesIO
from django.dispatch import Signal
from django.core.files.base import ContentFile
from django.contrib.auth import get_user
import face_recognition
import base64
import numpy as np
import cv2
import io
import face_recognition
import base64
import numpy as np
import cv2

def compare_faces(base64_str1, base64_str2):
  try:
      # Decode Base64 strings into image data
      img_data1 = base64.b64decode(base64_str1)
      img_data2 = base64.b64decode(base64_str2)

      # Convert image data into numpy arrays
      nparr1 = np.frombuffer(img_data1, np.uint8)
      nparr2 = np.frombuffer(img_data2, np.uint8)

      # Decode numpy arrays into RGB images
      img1 = cv2.imdecode(nparr1, cv2.IMREAD_COLOR)
      img2 = cv2.imdecode(nparr2, cv2.IMREAD_COLOR)

      # Detect face locations in the images
      face_locations1 = face_recognition.face_locations(img1)
      face_locations2 = face_recognition.face_locations(img2)

      # Check if exactly one face is detected in each image
      if len(face_locations1) == 1 and len(face_locations2) == 1:
          # Encode face encodings for comparison
          face_encodings1 = face_recognition.face_encodings(img1, face_locations1)[0]
          face_encodings2 = face_recognition.face_encodings(img2, face_locations2)[0]

          # Compare the face encodings
          face_distance = face_recognition.face_distance([face_encodings1], face_encodings2)[0]

          # Return the face distance (0 for identical faces, higher values for more dissimilar faces)
          return face_distance

      else:
          print("Error: Could not detect exactly one face in each image.")

  except Exception as e:
      print("Error occurred during face comparison:", e)
      return None
# post_classify_face_signal = Signal()


def decode_base64_image(image_string):
    """Decode a base64 image string into a PIL Image object."""
    image_bytes = base64.b64decode(image_string)
    image = Image.open(BytesIO(image_bytes))
    width, height = image.size
    return image, width, height

def encode_image_to_base64(image):
    """Encode a PIL Image object to a base64 string."""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def generate_visual_cryptography_shares(original_image):
    """Generate two shares of a visual cryptography scheme."""
    width, height = original_image.size
    
    # Create share images
    # share1 = Image.new("RGB", (width * 2, height))
    # share2 = Image.new("RGB", (width * 2, height))

    # draw1 = ImageDraw.Draw(share1)
    # draw2 = ImageDraw.Draw(share2)

    r_list = []
    r_random_list = []
    g_list = []
    g_random_list = []
    b_list = []
    b_random_list = []

    for y in range(height):
        for x in range(width):
            pixel = original_image.getpixel((x, y))
            r,g,b = pixel
            r_random_val = random.randint(1, 1000)
            r_random_list.append(r_random_val)
            g_random_val = random.randint(1, 1000)
            g_random_list.append(g_random_val)
            b_random_val = random.randint(1, 1000)
            b_random_list.append(b_random_val)
            r_list.append(r * r_random_val)
            g_list.append(g * g_random_val)
            b_list.append(b * b_random_val)

            # Generate random value to determine which share gets the pixel
            # random_val = random.randint(0, 1)
            # Assign the pixel to the corresponding share
            # if random_val == 0:
            #     draw1.point((2*x, y), pixel)
            #     draw2.point((2*x+1, y), (255 - pixel[0], 255 - pixel[1], 255 - pixel[2]))  # Invert pixel for share 2
            # else:
            #     draw1.point((2*x, y), (255 - pixel[0], 255 - pixel[1], 255 - pixel[2]))  # Invert pixel for share 1
            #     draw2.point((2*x+1, y), pixel)
    random_val = random.randint(1 , 3)
    if random_val == 1:
        server_list = r_list
        # server_list.append("r")
        client_list1 = g_list
        client_list1.append("g")
        client_list2 = b_list
        client_list2.append("b")
    elif random_val == 2:
        server_list = g_list
        # server_list.append("g")
        client_list1 = r_list 
        client_list1.append("r")  
        client_list2 = b_list
        client_list2.append("b")
    else:
        server_list = b_list
        # server_list.append("b")
        client_list1 = r_list
        client_list1.append("r")
        client_list2 = g_list
        client_list2.append("g")

    return server_list, client_list1, client_list2, r_random_list, g_random_list, b_random_list


def combine_shares_to_recreate_image(s_list, c1_list, c2_list, width, height, r_random_list, g_random_list, b_random_list):
    """Combine two shares to recreate the original image."""
    # width, height = share1.size
    length = len(s_list) 
    last_c1 = c1_list[len(c1_list) - 1]
    last_c2 = c2_list[len(c2_list) - 1]
    # c1_list.pop()
    # c2_list.pop()
    # print("size of c1 list")
    # print(str(len(c1_list)))
    # combined_tuple = ()
    combined_tuple = ()
    combined_tuples = []

    for i in range(height):
        row_tuples = []
        for j in range(width):
            index = i * width + j
            if last_c1 == "r" and last_c2 == "g":
                combined_tuple = (int(c1_list[index]/r_random_list[index]), int(c2_list[index]/g_random_list[index]), int(s_list[index]/b_random_list[index]))
            elif last_c1 == "r" and last_c2 == "b":
                combined_tuple = (int(c1_list[index]/r_random_list[index]), int(s_list[index]/g_random_list[index]), int(c2_list[index]/b_random_list[index]))
            elif last_c1 == "g" and last_c2 == "b":
                combined_tuple = (int(s_list[index]/r_random_list[index]), int(c1_list[index]/g_random_list[index]), int(c2_list[index]/b_random_list[index]))
            else:
                combined_tuple = (0, 0, 0)  # Default tuple if conditions not met
            row_tuples.append(combined_tuple)
        combined_tuples.append(row_tuples)


    image = Image.new("RGB", (width, height))
    # print(combined_tuples)

    for y in range(height):
        for x in range(width):
            image.putpixel((x, y), combined_tuples[y][x])

    # image.show("Reconstructed Image")  
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes.seek(0)
    base64_image = base64.b64encode(image_bytes.getvalue()).decode()

    return base64_image


## JSON
def to_json(d):
    return json.dumps(d, sort_keys=True)


def from_json(value):
    if value == "" or value is None:
        return None

    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception as e:
            # import ast
            # try:
            #     parsed_value = ast.literal_eval(parsed_value)
            # except Exception as e1:
            raise Exception("value is not JSON parseable, that's bad news") from e

    return value


def JSONFiletoDict(filename):
    with open(filename, 'r') as f:
        content = f.read()
    return from_json(content)




def is_ajax(request):
  return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def get_encoded_faces():
    from profiles.models import Profile
    """
    This function loads all user 
    profile images and encodes their faces
    """
    # Retrieve all user profiles from the database

    qs = Profile.objects.all()

    # Create a dictionary to hold the encoded face for each user
    encoded = {}

    for p in qs:
        # Initialize the encoding variable with None
        encoding = None

        # Load the user's profile image
        face = fr.load_image_file(p.photo.path)

        # Encode the face (if detected)
        face_encodings = fr.face_encodings(face)
        if len(face_encodings) > 0:
            encoding = face_encodings[0]
        else:
            print("No face found in the image")

        # Add the user's encoded face to the dictionary if encoding is not None
        if encoding is not None:
            encoded[p.user.user_id] = encoding

    # Return the dictionary of encoded faces
    return encoded


def classify_face(user, request, response, **kwargs):
    """
    This function takes an image as input and returns the name of the face it contains
    """
    
    response_data = response.content.decode('utf-8')  # Decode the bytes object to a string
    response_dict = json.loads(response_data)  # Parse the JSON string into a Python dictionary
    response_value = response_dict.get('response', None)
    img = response_value
    if user.has_face_image():
        print("USER HAS FACE IMAGE NO NEED TO SAVE ANYTHING")
        # similarity_index = compare_faces(img, base64_str3)
        # if similarity_index is not None:
        #     print("Similarity Index:", similarity_index)
        # else:
        #     print("Error occurred during comparison.")
        # print(user.server_user_face_share)
    else:
        face_image, width, height = decode_base64_image(img)
        server,c1,c2, r_random, g_random, b_random = generate_visual_cryptography_shares(face_image)
        if c1[len(c1) - 1] == "r" and c2[len(c2) - 1] == "g":
            r1_string = ' '.join(map(str, b_random))
            file_path_3 = 'r3.txt'
            with open(file_path_3, 'w') as file:
                file.write(r1_string)
            random_1 = json.dumps(r_random)
            user.random_1 = random_1
            user.save()
            random_2 = json.dumps(g_random)
            user.random_2 = random_2
            user.save()
        elif c1[len(c1) - 1] == "r" and c2[len(c2) - 1] == "b":
            r1_string = ' '.join(map(str, g_random))
            file_path_3 = 'r3.txt'
            with open(file_path_3, 'w') as file:
                file.write(r1_string)
            random_1 = json.dumps(r_random)
            user.random_1 = random_1
            user.save()
            random_2 = json.dumps(b_random)
            user.random_2 = random_2
            user.save()
        elif c1[len(c1) - 1] == "g" and c2[len(c2) - 1] == "b":
            r1_string = ' '.join(map(str, r_random))
            file_path_3 = 'r3.txt'
            with open(file_path_3, 'w') as file:
                file.write(r1_string)
            random_1 = json.dumps(g_random)
            user.random_1 = random_1
            user.save()
            random_2 = json.dumps(b_random)
            user.random_2 = random_2
            user.save()
        server_share_json = json.dumps(server)
        user.server_user_face_share = server_share_json
        user.save()
        c1_string = ' '.join(map(str, c1))
        c2_string = ' '.join(map(str, c2))
        file_path_1 = 'c1.txt'
        file_path_2 = 'c2.txt'
        with open(file_path_1, 'w') as file:
            file.write(c1_string)
        with open(file_path_2, 'w') as file:
            file.write(c2_string)
        print("SAVING USER FACE IMAGE ON CLIENT DEVICE AND IN SERVER")


    # user = get_user(response)
    # user.server_user_face_share.save('server_share.png', ContentFile(server), save=True)

    # combine_shares_to_recreate_image(server,c1,c2, width, height, r_random, g_random, b_random)
    pass
    # from profiles.models import Profile
    # Load all the known faces and their encodings
    # faces = get_encoded_faces()
    # faces_encoded = list(faces.values())
    # known_face_names = list(faces.keys())

    # # Load the input image
    # img = fr.load_image_file(img)
 
    # try:
    #     # Find the locations of all faces in the input image
    #     face_locations = fr.face_locations(img)

    #     # Encode the faces in the input image
    #     unknown_face_encodings = fr.face_encodings(img, face_locations)

    #     # Identify the faces in the input image
    #     face_names = []
    #     for face_encoding in unknown_face_encodings:
    #         # Compare the encoding of the current face to the encodings of all known faces
    #         matches = fr.compare_faces(faces_encoded, face_encoding)

    #         # Find the known face with the closest encoding to the current face
    #         face_distances = fr.face_distance(faces_encoded, face_encoding)
    #         best_match_index = np.argmin(face_distances)

    #         # If the closest known face is a match for the current face, label the face with the known name
    #         if matches[best_match_index]:
    #             name = known_face_names[best_match_index]
    #         else:
    #             name = "Unknown"

    #         face_names.append(name)

    #     # Return the name of the first face in the input image
    #     return face_names[0]
    # except:
    #     # If no faces are found in the input image or an error occurs, return False
    #     return False

def compare_faces(base64_str1, base64_str2):
    try:
        # Decode Base64 strings into image data
        img_data1 = base64.b64decode(base64_str1)
        img_data2 = base64.b64decode(base64_str2)

        # Convert image data into numpy arrays
        nparr1 = np.frombuffer(img_data1, np.uint8)
        nparr2 = np.frombuffer(img_data2, np.uint8)

        # Decode numpy arrays into RGB images
        img1 = cv2.imdecode(nparr1, cv2.IMREAD_COLOR)
        img2 = cv2.imdecode(nparr2, cv2.IMREAD_COLOR)

        # Detect face locations in the images
        face_locations1 = face_recognition.face_locations(img1)
        face_locations2 = face_recognition.face_locations(img2)

        # Check if exactly one face is detected in each image
        if len(face_locations1) == 1 and len(face_locations2) == 1:
            # Encode face encodings for comparison
            face_encodings1 = face_recognition.face_encodings(img1, face_locations1)[0]
            face_encodings2 = face_recognition.face_encodings(img2, face_locations2)[0]

            # Compare the face encodings
            face_distance = face_recognition.face_distance([face_encodings1], face_encodings2)[0]

            # Return the face distance (0 for identical faces, higher values for more dissimilar faces)
            return face_distance

        else:
            print("Error: Could not detect exactly one face in each image.")

    except Exception as e:
        print("Error occurred during face comparison:", e)
        return None