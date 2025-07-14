from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from rest_framework import status
from django.contrib.auth.hashers import check_password,make_password

#models
from user_app.models import User, UserProfile,Follow

#Send email
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from .utils import generate_token
from django.utils.encoding import force_bytes,force_str
from django.core.mail import EmailMessage
from django.conf import settings

#Generate token
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

#Authentication check
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated,AllowAny

# pagination
from rest_framework.pagination import PageNumberPagination

# cloudinary
import cloudinary.uploader
import mimetypes

from cloudinary.uploader import destroy
from urllib.parse import urlparse

# Create your views here.

class PostPagination(PageNumberPagination):
    page_size = 10

class SignupView(APIView):
    def post(self,request):
        data = request.data
        
        if User.objects.filter(email=data['email']).exists():
            print('User with this email is already exists...')
            return Response({"details":"User with this email is already exists."},status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=data['username']).exists():
            print('User with this username is already exists...')
            return Response({"details":"User with this username is already exists."},status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create(email=data['email'],username=data['username'],password=make_password(data['password']),is_active=False)

        email_subject="Account Activation!"
        # http://127.0.0.1:8000
        message = render_to_string('activate.html',{
            'user':user,
            'domain':'https://shortne-backend.onrender.com',
            'user_id': urlsafe_base64_encode(force_bytes(user.pk)),
            'token':generate_token.make_token(user)
        })

        email=EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[data['email']])
        email.send()

        return Response({"details":"Check your email to activate your account"},status=status.HTTP_200_OK)

    

class ActivateView(APIView):
    def get(Self,request,uidb64,token):
        try:
            pk=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(id=pk)
        except Exception as error:
            user=None
        if user is not None and generate_token.check_token(user,token):
            user.is_active=True
            user.save()
            print("Account activated...!")
            return render(request,'activate_success.html')
        print("Account activation failed...")
        return render(request,'activate_fail.html')
    
class SigninView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):
        email=request.data.get('email')
        password=request.data.get('password')
        print("Email:",email)
        print("Password:",password)
        # user = authenticate(request,username=email,password=password)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            print("email not match")
            return Response({"Error": "Invalid credentials email"}, status=status.HTTP_401_UNAUTHORIZED)
        
        if user.check_password(password):
            refresh_token = RefreshToken.for_user(user)
            access_token = refresh_token.access_token

            return Response({
                'id': user.id,
                'refresh': str(refresh_token),
                'access': str(access_token),
                'username': user.username,
                'is_active': user.is_active
            }, status=status.HTTP_200_OK)

        
        print("password not match")
        return Response({"Error":"Invalid credentials password"},status=status.HTTP_401_UNAUTHORIZED)
    
class SignoutView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self,request):
        refresh_token=request.data.get('refresh')
        if not refresh_token:
            return Response({"details":"refresh token is required"})
        try:
            print("Refresh_token:",refresh_token)
            token=RefreshToken(refresh_token)
            token.blacklist()
            return Response({"details":"Signout Successfull..."},status=status.HTTP_200_OK)
        except Exception  as e:
            return Response({"details":"Invalid Token"},status=status.HTTP_400_BAD_REQUEST)
            
#password update request mail
class PasswordupdaterequestView(APIView):
    def post(self,request):
        data=request.data['email']
        print("Email:",data)
        try:
            user = User.objects.get(email=data)
            email_subject='Password Reset Request'
            reset_link=f"https://shortne-backend.onrender.com/reset-password/{urlsafe_base64_encode(force_bytes(user.pk))}/{generate_token.make_token(user)}"
            message = render_to_string('password_reset_request.html',{
                    'user':user,
                    'domain':reset_link,           
                    })
            email = EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[data])
            email.content_subtype='html'
            email.send()
            return Response({"details":"Please check your email to update new password."})
        except Exception as error:
            print("Reser_Password_Error:-----",error)
            return Response({"Error":"User with this mail is not exist."})

# update password    
class ResetPasswordView(APIView):
    permission_classes=[AllowAny]
    def post(self,request):

        try:
            user_id=request.data['user_id']
            token=request.data['token']
            new_password = request.data['new_password']
            pk=force_str(urlsafe_base64_decode(user_id))
            user = User.objects.get(id=pk)
        except Exception as error:
             user=None
            
        try:
            if user is not None and generate_token.check_token(user,token):
                user.password=(make_password(new_password))
                user.save()
                print("Password reset successfull..")
                return Response({"details":"Password reset successfull...!"})
        except Exception as error:
            print("Error:....",error)
            return Response('password reset fail..')
    
# leo@123
        
class UserProfileView(APIView):
    def get(self,request):
        try:
            username = request.query_params.get('username')
            user = User.objects.get(username=username)
            print("USER:",user)
            profile = UserProfile.objects.get(user = user)
            print("User:",profile)
            serializer = UserProfileSerializer(profile).data
            return Response(serializer)
        
        except User.DoesNotExist:
            return Response({"details": "User does not exist."}, status=404)
        except UserProfile.DoesNotExist:
            return Response({"details": "UserProfile does not exist."}, status=404)
        except Exception as error:
            print("Error:",error)
            return Response({"details": str(error)}, status=500)

class FollowView(APIView):
    permission_classes=[IsAuthenticated]

    def post(self,request):
        following = request.data.get('follow')
        print("Following:",following)
        following = User.objects.get(username=following)
        print("Following_obj:",following)

        try:
            follow = Follow.objects.create(follower=request.user,following=following)
            return Response({"details":"Followed Successfully...!"})
        except Exception as error:
            print("Follow====Error:",error)
            return Response({"details":str(error)})
        
class UnfollowView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self,request):
        try:
            unfollow = request.query_params.get('unfollow')
            following = User.objects.get(username=unfollow)
            follow_intance = Follow.objects.get(follower=request.user,following=following)
            follow_intance.delete()
            return Response({"details":"Unfollowed Successfully...!"})
        
        except Exception as error:
            return Response({"details":str(error)})
        
class FollowStatusView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        try:
            target_user = request.query_params.get('username')
            following =  User.objects.get(username=target_user)
            is_following = Follow.objects.filter(follower=request.user,following=following).exists()
            return Response({"details":is_following})
        except Exception as error:
            return Response({"details":str(error)})
        

class FollowersView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        try:
            print("USER:",request.user)
            # user=User.objects.get(username=request.user)
            user=request.user
            followers = Follow.objects.filter(following=user).values_list('follower',flat=True)
            following = Follow.objects.filter(follower=user).values_list('following',flat=True)
            followers_profile = UserProfile.objects.filter(user__id__in=followers).exclude(user__id__in=following)
            serializer = UserProfileSerializer(followers_profile,many=True)
            # print("Followers:",serializer.data)
            return Response({"details":serializer.data})
        except Exception as error:
            print("Followers Error:",error)
            return Response({"details": str(error)})
        
class FriendslistView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        try:
            user =request.user
            followers = Follow.objects.filter(following=user).values_list('follower',flat=True)
            following = Follow.objects.filter(follower=user).values_list('following',flat=True)
            mutual_ids = set(followers).intersection(set(following))
            friends_profile = UserProfile.objects.filter(user__id__in=mutual_ids)
            serializer = UserProfileSerializer(friends_profile,many=True)
            return Response({"details":serializer.data})
        except Exception as error:
            print("Error:",error)
            return Response({"details":str(error)})
        
# Edit userinfo

import os

def extract_cloudinary_public_id(url):
    
    try:
        parsed = urlparse(url)
        parts = parsed.path.strip('/').split('/')

        if 'upload' in parts:
            upload_index = parts.index('upload')
            # everything after 'upload/' is version and public_id
            public_id_with_ext = "/".join(parts[upload_index + 1:])  # v1751713680/filename.jpg
            filename = os.path.basename(public_id_with_ext)
            public_id = filename.rsplit('.', 1)[0]  # remove .jpg or .mp4
            print("Actual public_id sent to Cloudinary destroy:", public_id)

            return public_id
        return None
    except Exception as e:
        print("Error extracting public ID:", e)
        return None, None



class EditUserinfoView(APIView):
    permission_classes=[IsAuthenticated]
    def patch(self,request):
        try:
            user =request.user
            image = request.FILES.get('image') or request.data.get('image')
            bio=request.data.get('bio')
            link=request.data.get('link')

            userprofile=UserProfile.objects.get(user=user)


            if image:
                mime_type, _ = mimetypes.guess_type(image.name)

                if mime_type and mime_type.startswith("image"):
                        old_url = userprofile.image
                        public_id =extract_cloudinary_public_id(old_url)
                    
                        if public_id:
                            destroy(public_id, resource_type="image")

                        upload_result = cloudinary.uploader.upload(image, resource_type='auto')
                        cloudinary_url = upload_result.get('secure_url')
                        userprofile.image = cloudinary_url
                else:
                    return Response({"details": "Invalid image file."}, status=400)
                
            if bio is not None:
                userprofile.bio=bio
            if link is not None:
                userprofile.link=link
                
            print("Image:", image)


            userprofile.save()
            serializer=UserProfileSerializer(userprofile)
            print("Profile updated successfully...!")

            return Response({"details":"Profile updated successfully...!",
                             "profileinfo":serializer.data})
        except Exception as e:
            return Response({"details":str(e)})
