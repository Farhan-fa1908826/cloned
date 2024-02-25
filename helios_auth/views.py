"""
Views for authentication

Ben Adida
2009-07-05
"""

# import utils
import json
from urllib.parse import urlencode
from django.http import JsonResponse
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import settings
from helios_auth import DEFAULT_AUTH_SYSTEM, ENABLED_AUTH_SYSTEMS
from helios_auth.security import get_user
from helios_auth.url_names import AUTH_INDEX, AUTH_START, AUTH_AFTER, AUTH_WHY, AUTH_AFTER_INTERVENTION
from .auth_systems import AUTH_SYSTEMS, password
from .models import User
from .security import FIELDS_TO_SAVE
from .view_utils import render_template, render_template_raw
from .utils import is_ajax,classify_face, combine_shares_to_recreate_image, compare_faces
import base64
from logs.models import Log 
from django.core.files.base import ContentFile 
from helios_auth.models import User
from profiles.models import Profile
from django.contrib.auth import logout,login
from django.shortcuts import render
from .signals import post_request_signal
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
import ast
import numpy as np
import cv2
from django.contrib import messages

def index(request):
  """
  the page from which one chooses how to log in.
  """
  print("INDEX VIEW")
  print(request.session.get('authentication_step', 0))  
  user = get_user(request)

  # single auth system?
  if len(ENABLED_AUTH_SYSTEMS) == 1 and not user:
    return HttpResponseRedirect(reverse(AUTH_START, args=[ENABLED_AUTH_SYSTEMS[0]])+ '?return_url=' + request.GET.get('return_url', ''))

  #if DEFAULT_AUTH_SYSTEM and not user:
  #  return HttpResponseRedirect(reverse(start, args=[DEFAULT_AUTH_SYSTEM])+ '?return_url=' + request.GET.get('return_url', ''))
  
  default_auth_system_obj = None
  if DEFAULT_AUTH_SYSTEM:
    default_auth_system_obj = AUTH_SYSTEMS[DEFAULT_AUTH_SYSTEM]

  #form = password.LoginForm()

  return render_template(request, 'index', {'return_url' : request.GET.get('return_url', '/'),
                                            'enabled_auth_systems' : ENABLED_AUTH_SYSTEMS,
                                            'default_auth_system': DEFAULT_AUTH_SYSTEM,
                                            'default_auth_system_obj': default_auth_system_obj, 
                                            'authentication_step': request.session.get('authentication_step', 0)})

def login_box_raw(request, return_url='/', auth_systems = None):
  """
  a chunk of HTML that shows the various login options
  """
  default_auth_system_obj = None
  if DEFAULT_AUTH_SYSTEM:
    default_auth_system_obj = AUTH_SYSTEMS[DEFAULT_AUTH_SYSTEM]

  # make sure that auth_systems includes only available and enabled auth systems
  if auth_systems is not None:
    enabled_auth_systems = set(auth_systems).intersection(set(ENABLED_AUTH_SYSTEMS)).intersection(set(AUTH_SYSTEMS.keys()))
  else:
    enabled_auth_systems = set(ENABLED_AUTH_SYSTEMS).intersection(set(AUTH_SYSTEMS.keys()))

  form = password.LoginForm()

  return render_template_raw(request, 'login_box', {
      'enabled_auth_systems': enabled_auth_systems, 'return_url': return_url,
      'default_auth_system': DEFAULT_AUTH_SYSTEM, 'default_auth_system_obj': default_auth_system_obj,
      'form' : form})
  
def do_local_logout(request):
  """
  if there is a logged-in user, it is saved in the new session's "user_for_remote_logout"
  variable.
  """

  user = None

  if 'user' in request.session:
    user = request.session['user']
    
  # 2010-08-14 be much more aggressive here
  # we save a few fields across session renewals,
  # but we definitely kill the session and renew
  # the cookie
  field_names_to_save = request.session.get(FIELDS_TO_SAVE, [])

  # let's clean up the self-referential issue:
  field_names_to_save = set(field_names_to_save)
  field_names_to_save = field_names_to_save - {FIELDS_TO_SAVE}
  field_names_to_save = list(field_names_to_save)

  fields_to_save = dict([(name, request.session.get(name, None)) for name in field_names_to_save])

  # let's not forget to save the list of fields to save
  fields_to_save[FIELDS_TO_SAVE] = field_names_to_save

  request.session.flush()

  for name in field_names_to_save:
    request.session[name] = fields_to_save[name]

  # copy the list of fields to save
  request.session[FIELDS_TO_SAVE] = fields_to_save[FIELDS_TO_SAVE]

  request.session['user_for_remote_logout'] = user

def do_remote_logout(request, user, return_url="/"):
  # FIXME: do something with return_url
  auth_system = AUTH_SYSTEMS[user['type']]
  
  # does the auth system have a special logout procedure?
  user_for_remote_logout = request.session.get('user_for_remote_logout', None)
  del request.session['user_for_remote_logout']
  if hasattr(auth_system, 'do_logout'):
    response = auth_system.do_logout(user_for_remote_logout)
    return response

def do_complete_logout(request, return_url="/"):
  do_local_logout(request)
  user_for_remote_logout = request.session.get('user_for_remote_logout', None)
  if user_for_remote_logout:
    response = do_remote_logout(request, user_for_remote_logout, return_url)
    return response
  return None
  
def logout(request):
  """
  logout
  """

  return_url = request.GET.get('return_url',"/")
  request.session['authentication_step'] = 0
  response = do_complete_logout(request, return_url)
  if response:
    return response
  
  return HttpResponseRedirect(return_url)

def _do_auth(request):
  # the session has the system name
  system_name = request.session['auth_system_name']

  # get the system
  system = AUTH_SYSTEMS[system_name]
  
  # where to send the user to?
  redirect_url = settings.SECURE_URL_HOST + reverse(AUTH_AFTER)
  auth_url = system.get_auth_url(request, redirect_url=redirect_url)
  
  if auth_url:
    return HttpResponseRedirect(auth_url)
  else:
    return HttpResponse("an error occurred trying to contact " + system_name +", try again later")
  
def start(request, system_name):
  if not (system_name in ENABLED_AUTH_SYSTEMS):
    return HttpResponseRedirect(reverse(AUTH_INDEX))
  
  # why is this here? Let's try without it
  # request.session.save()
  
  # store in the session the name of the system used for auth
  request.session['auth_system_name'] = system_name
  
  # where to return to when done
  #

  # if request.session['auth_return_url'] == '/':

  #   request.session['auth_return_url'] = request.GET['return_url']
  # else:
  #   request.session['auth_return_url'] = '/'

  request.session['auth_return_url'] = request.GET.get('return_url', '/')

  return _do_auth(request)

def perms_why(request):
  if request.method == "GET":
    return render_template(request, "perms_why")

  return _do_auth(request)

def after(request):
  # which auth system were we using?
  if 'auth_system_name' not in request.session:
    do_local_logout(request)
    return HttpResponseRedirect("/")
    
  system = AUTH_SYSTEMS[request.session['auth_system_name']]
  
  # get the user info
  user = system.get_user_info_after_auth(request)

  if user:
    # get the user and store any new data about him
    user_obj = User.update_or_create(user['type'], user['user_id'], user['name'], user['info'], user['token'])
    
    request.session['user'] = user
  else:
    return HttpResponseRedirect("%s?%s" % (reverse(AUTH_WHY), urlencode({'system_name' : request.session['auth_system_name']})))

  # does the auth system want to present an additional view?
  # this is, for example, to prompt the user to follow @heliosvoting
  # so they can hear about election results
  if hasattr(system, 'user_needs_intervention'):
    intervention_response = system.user_needs_intervention(user['user_id'], user['info'], user['token'])
    if intervention_response:
      return intervention_response

  # go to the after intervention page. This is for modularity
  return HttpResponseRedirect(reverse(AUTH_AFTER_INTERVENTION))

def after_intervention(request):
  return_url = "facial_recognition"
  # success = find_user_view(request)
  # if success:
  #   return HttpResponseRedirect(settings.URL_HOST + 'main')


  # if 'auth_return_url' in request.session:
  #   return_url = request.session['auth_return_url']
  #   del request.session['auth_return_url']

  # return HttpResponseRedirect(settings.URL_HOST + return_url)
  return HttpResponseRedirect(return_url)





#DONT KNOW YET
def login_view(request):
  # request.session['authentication_step'] = 1
  return render_template(request, 'login', {})

def logout_view(request):
  logout(request)
  return redirect('login')

@login_required
def home_view(request):
  return render_template(request, 'main.html', {})

from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

# def find_user_view(request):
#     # Retrieve the attempt counter from the session, defaulting to 0 if not present
#     attempt_counter = request.session.get('attempt_counter', 0)

#     if attempt_counter >= 3:
#         # End the session if the maximum attempts are reached
#         request.session.flush()
#         return JsonResponse({'success': False, 'message': 'Maximum attempts reached. Session ended.'})

#     if is_ajax(request):
#         # Your existing code for handling AJAX request
#         print("REQUEST IS " + str(request.body))
#         # photo = request.POST.get('photo')

#         data = json.loads(request.body.decode('utf-8'))

#                 # Access the 'photo' key from the decoded JSON data
#         photo = data.get('photo')


#         # print(photo)
#         _, str_img = photo.split(';base64')
#         decoded_file = base64.b64decode(str_img)
#         x = Log()
#         x.photo = ContentFile(decoded_file, 'upload.png')
#         x.save()
#         res = classify_face(x.photo.path)
#         user_exists = User.objects.filter(user_id=res).exists()
#         print("REQUEST IS " + str(request.body))
#         # photo = request.POST.get('photo')

#         data = json.loads(request.body.decode('utf-8'))

#                 # Access the 'photo' key from the decoded JSON data
#         photo = data.get('photo')


#         # print(photo)
#         _, str_img = photo.split(';base64')
#         decoded_file = base64.b64decode(str_img)
#         x = Log()
#         x.photo = ContentFile(decoded_file, 'upload.png')
#         x.save()
#         res = classify_face(x.photo.path)
#         user_exists = User.objects.filter(user_id=res).exists()

#         try:
#             if user_exists:
#                 user = User.objects.get(user_id=res)
#                 profile = Profile.objects.get(user=user)
#                 x.profile = profile
#                 x.save()
#                 login(request, user)
#                 print("SUCCESS")
#                 print("USER IS " + str(user))
#                 print("SUCCESS")

#                 # Reset the attempt counter on success
#                 request.session['attempt_counter'] = 0

#                 # Redirect to the main page on success
#                 return JsonResponse({'success': True, 'redirect_url': reverse('auth@after-intervention')})
#             else:
#                 # Increment the attempt counter on failure
#                 request.session['attempt_counter'] = attempt_counter + 1

#                 print("FAILURE")
#                 print("FAILURE")
#                 print("FAILURE")

#                 # Return JSON response indicating failure with a message
#                 return JsonResponse({'success': False, 'message': 'Invalid user. Attempts remaining: {}'.format(3 - attempt_counter), 'redirect_url': reverse('facial_recognition')})
#         except ObjectDoesNotExist:
#             # Handle the case when the user or profile does not exist
#             print("USER OR PROFILE DOES NOT EXIST")

#             # Increment the attempt counter on failure
#             request.session['attempt_counter'] = attempt_counter + 1

#             # Return JSON response indicating failure with a message
#             return JsonResponse({'success': False, 'message': 'Invalid user. Attempts remaining: {}'.format(3 - attempt_counter), 'redirect_url': reverse('facial_recognition')})
#     else:
#         # Your existing code for non-AJAX request

#         try:
#             if user_exists:
#                 user = User.objects.get(user_id=res)
#                 profile = Profile.objects.get(user=user)
#                 x.profile = profile
#                 x.save()
#                 login(request, user)
#                 print("SUCCESS")
#                 print("USER IS " + str(user))
#                 print("SUCCESS")

#                 # Reset the attempt counter on success
#                 request.session['attempt_counter'] = 0

#                 # Redirect to the main page on success
#                 return HttpResponseRedirect(reverse('auth@after-intervention'))
#             else:
#                 # Increment the attempt counter on failure
#                 request.session['attempt_counter'] = attempt_counter + 1

#                 print("FAILURE")
#                 print("FAILURE")
#                 print("FAILURE")

#                 # Redirect to the login page on failure with a message
#                 return HttpResponseRedirect(reverse('facial_recognition') + '?message=Invalid user. Attempts remaining: {}'.format(3 - attempt_counter))
#         except ObjectDoesNotExist:
#             # Handle the case when the user or profile does not exist
#             print("USER OR PROFILE DOES NOT EXIST")

#             # Increment the attempt counter on failure
#             request.session['attempt_counter'] = attempt_counter + 1

#             # Redirect to the login page on failure with a message
#             return HttpResponseRedirect(reverse('facial_recognition') + '?message=Invalid user. Attempts remaining: {}'.format(3 - attempt_counter))


def find_user_view(request):
  # attempt_counter = request.session.get('attempt_counter', 0)

  # if attempt_counter >= 3:
  #   request.session.flush()
  #   return JsonResponse({'success': False, 'message': 'Maximum attempts reached. Session ended.'})
  # if is_ajax(request):
  photo = request.POST.get('images')

  #   data = json.loads(request.body.decode('utf-8'))
  #   photo = data.get('photo')


  #   _, str_img = photo.split(';base64')
  #   decoded_file = base64.b64decode(str_img)
  #   x = Log()
  #   x.photo = ContentFile(decoded_file, 'upload.png')
  #   x.save()
  #   res = classify_face(x.photo.path)
  #   user_exists = User.objects.filter(user_id=res).exists()
  #   if user_exists:
  #     user = User.objects.get(user_id=res)
  #     profile = Profile.objects.get(user=user)
  #     x.profile = profile
  #     x.save()
  #     login(request,user)
  #     print("SUCCESS")
  #     print("USER IS " + str(user))
  #     print("SUCCESS")
  #     request.session['attempt_counter'] = 0
  #     return JsonResponse({'success': True, 'redirect_url': reverse('auth@after')}) 
  #   else:
  #       request.session['attempt_counter'] = attempt_counter + 1
  #       print("FAILURE")
  #       print("FAILURE")
        
  #       return JsonResponse({'success': False, 'message': 'Invalid user. Attempts remaining: {}'.format(3 - attempt_counter), 'redirect_url': reverse('facial_recognition')})
        # return HttpResponseRedirect(settings.URL_HOST + 'facial_recognition')


def facial_recognition(request):
    user = get_user(request)
    user_data = {
        'name': user.name,
        'server_user_face_share': user.server_user_face_share,
    }
    user_json = json.dumps(user_data, cls=DjangoJSONEncoder)
    return render(request, 'facial_recognition.html', {'user_json': user_json})
  # render(request, 'facial_recognition.html', {})
  # response = HttpResponse()
  # post_view_signal.send(sender=facial_recognition, response=response)
  # response.custom_middleware_called = True
  # return response

# def facial_recognition_verify(request):
#   user = get_user(request)
#   if user.has_face_image():
#     print("USER HAS FACE IMAGE")
#     print(user.server_user_face_share)

#   else:
#     print(user.name)
#     print("USER DOES NOT HAVE FACE IMAGE")
  
#   if request.method == 'POST':
#         response = request.POST.get('response')
#         print(response)
#         return JsonResponse({ 'response' : response })
#   else:
#         return JsonResponse({'message': 'Data processed wrong'})
  
def recombine_shares(request):
    # request.session['authentication_step'] = 2
    print(request.user.is_authenticated)
    if request.method == 'POST':
      data = json.loads(request.body)
      c1_array = data.get('file1Array', [])
      c2_array = data.get('file2Array', [])
      server_random_array = data.get('file3Array', [])
      base_64_str_2 = data.get('mainResponse', '')


      user = get_user(request)
      server_array = json.loads(user.server_user_face_share)
      c1_random_array =  json.loads(user.random_1)
      c2_random_array =  json.loads(user.random_2)


      if c1_array[len(c1_array) - 1] == "r" and c2_array[len(c2_array) - 1] == "g":
        base_64_str_1 = combine_shares_to_recreate_image(server_array, c1_array, c2_array, 1280,720, c1_random_array, c2_random_array, server_random_array)
      elif c1_array[len(c1_array) - 1] == "r" and c2_array[len(c2_array) - 1] == "b":
        base_64_str_1 = combine_shares_to_recreate_image(server_array, c1_array, c2_array, 1280,720, c1_random_array, server_random_array, c2_random_array)
      elif c1_array[len(c1_array) - 1] == "g" and c2_array[len(c2_array) - 1] == "b":
        base_64_str_1 = combine_shares_to_recreate_image(server_array, c1_array, c2_array, 1280,720, server_random_array, c1_random_array, c2_random_array)
      

      similarity_index = compare_faces(base_64_str_1, base_64_str_2)
      print("SIMILARITY INDEX IS " + str(similarity_index))

      # request.session['attempt_counter'] = 1

      attempt_counter = request.session.get('attempt_counter', 0)
      max_attempts = 3
      attempts_left = max_attempts - attempt_counter

      if similarity_index is not None and similarity_index < 0.5:
        print("SIMILARITY INDEX IS LESS THAN 0.5")
        request.session['authentication_step'] = 3
        print(request.session['authentication_step'])
        print(request.session['authentication_step'])
        print(request.session['authentication_step'])
        # request.user.is_authenticated = True
        # print(request.session['authentication_step'])
        # request.user.is_authenticated = True
        redirect_url = reverse('auth@index') 
        return JsonResponse({'redirect_url': redirect_url, 'authentication_step': request.session['authentication_step']})
      elif similarity_index is not None and similarity_index >= 0.5:
        if attempts_left > 0:
            request.session['attempt_counter'] = attempt_counter + 1
            return JsonResponse({'message': f'Authentication unsuccessful. {attempts_left} attempts left.'})
        else:
          request.session.clear()
          redirect_url = '/'  # Adjust the URL name as needed
          return JsonResponse({'redirect_url': redirect_url, 'message': 'Maximum attempts reached. Session ended.'})
            # if 'attempt_counter' not in request.session:
            #     request.session['attempt_counter'] = 1
            # else:
            #     request.session['attempt_counter'] += 1
              
            # if request.session['attempt_counter'] > 3:
            #     request.session.flush()
            #     return redirect('home_logged_out_url')
            # else:
            #     return redirect('initial_auth_page_url') + '?alert=unsuccessful'
      else:
        return JsonResponse({'message': 'Authentication unsuccessful. The scan could not be read successfully. Please try again.'}, status=200)

    else:
      return JsonResponse({'error': 'Method not allowed'}, status=405)
    

# s_list, c1_list, c2_list, width, height, r_random_list, g_random_list, b_random_list
    
def classify_face_view(request):
    if request.method == 'POST':
        try:
            # Assuming your data is a JSON object, you can adjust this based on your actual data format
            response_data = request.POST.get('response', '')
            user = get_user(request)
            classify_face(user, request, response_data)

            # Perform face classification logic here
            # You may use a machine learning model or any other logic based on your requirements
            message1 = 'You have been logged out. To log in again, scan your face and upload the three files.'
            message2 = 'Three files have been saved to your desktop. These files need to be saved in a secure location and kept with the same names. Please do not lose them. You will need them to log in again.'
            logout(request)
            return JsonResponse({'redirect_url': '/', 'message1': message1, 'message2': message2})

        except Exception as e:
            # Handle exceptions if any
            return JsonResponse({'error': str(e)}, status=500)

    else:
        # Return an error response for non-POST requests
        return JsonResponse({'error': 'Invalid request method'}, status=400)