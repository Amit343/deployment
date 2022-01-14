from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
#import pyotp
from rest_framework.response import Response
from rest_framework.views import APIView
#from .models import phoneModel
import base64
#from phonenumber_field.modelfields import PhoneNumberField
'''
class generateKey:
    @staticmethod
    def returnValue(phone):
        return str(phone) + str(datetime.date(datetime.now())) + "Some Random Secret Key"

# Time after which OTP will expire
EXPIRY_TIME = 50 # seconds

class getPhoneNumberRegistered_TimeBased(APIView):
    # Get to Create a call for OTP
    @staticmethod
    def get(request, phone):
        try:
            Mobile = phoneModel.objects.get(Mobile=phone)  # if Mobile already exists the take this else create New One
        except ObjectDoesNotExist:
            phoneModel.objects.create(
                Mobile=phone,
            )
            Mobile = phoneModel.objects.get(Mobile=phone)  # user Newly created Model
        Mobile.save()  # Save the data
        keygen = generateKey()
        key = base64.b32encode(keygen.returnValue(phone).encode())  # Key is generated
        OTP = pyotp.TOTP(key,interval = EXPIRY_TIME)  # TOTP Model for OTP is created
        print(OTP.now())
        print(Mobile)
        # Using Multi-Threading send the OTP Using Messaging Services like Twilio or Fast2sms
        return Response({"OTP": OTP.now()}, status=200)  # Just for demonstration

    # This Method verifies the OTP
    @staticmethod
    def post(request, phone):
        try:
            Mobile = phoneModel.objects.get(Mobile=phone)
        except ObjectDoesNotExist:
            return Response("User does not exist", status=404)  # False Call

        keygen = generateKey()
        key = base64.b32encode(keygen.returnValue(phone).encode())  # Generating Key
        OTP = pyotp.TOTP(key,interval = EXPIRY_TIME)  # TOTP Model
        if OTP.verify(request.data["otp"]):  # Verifying the OTP
            Mobile.isVerified = True
            Mobile.save()
            return Response("You are authorised", status=200)
     '''   #return Response("OTP is wrong/expired", status=400)


from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Profile ,Comment
import random
from django.http import HttpResponse
import http.client
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.views.generic import View,DetailView,DeleteView
from django.http import HttpResponseRedirect
from .models import communitypost,community_comment
from django.urls.base import reverse_lazy
#from .import View

# Create your views here


def send_otp(mobile , otp):
    print("FUNCTION CALLED")
    conn = http.client.HTTPSConnection("api.msg91.com")
    authkey = settings.AUTH_KEY
    headers = { 'content-type': "application/json" }
    url = "http://control.msg91.com/api/sendotp.php?otp="+otp+"&message="+"Your otp is "+otp +"&mobile="+mobile+"&authkey="+authkey+"&country=91"
    conn.request("GET", url , headers=headers)
    res = conn.getresponse()
    data = res.read()
    print(data)
    return None



def login_attempt(request):
    if request.method == 'POST':
        mobile = request.POST.get('mobile')

        user = Profile.objects.filter(mobile = mobile).first()

        if user is None:
            context = {'message' : 'User not found', 'class' : 'danger' }
            return render(request,'login.html', context)

        otp = str(random.randint(1000, 9999))
        user.otp = otp
        user.save()
        send_otp(mobile , otp)
        request.session['mobile'] = mobile
        return redirect('login_otp')
    return render(request,'login.html')  #here we have to use teemplate name


def login_otp(request):
    mobile = request.session['mobile']
    context = {'mobile':mobile}
    if request.method == 'POST':
        otp = request.POST.get('otp')
        profile = Profile.objects.filter(mobile=mobile).first()

        if otp == profile.otp:
            user = User.objects.get(id = profile.user.id)
            login(request , user)
            return redirect('cart') #here comes our home page
        else:
            context = {'message' : 'Wrong OTP' , 'class' : 'danger','mobile':mobile }
            return render(request,'login_otp.html' , context)

    return render(request,'login_otp.html' , context)





def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('name')
        mobile = request.POST.get('mobile')

        check_user = User.objects.filter(email = email).first()
        check_profile = Profile.objects.filter(mobile = mobile).first()

        if check_user or check_profile:
            context = {'message' : 'User already exists' , 'class' : 'danger' }
            return render(request,'register.html' , context)

        user = User(email = email , first_name = name)
        user.save()
        otp = str(random.randint(1000 , 9999))
        profile = Profile(user = user , mobile=mobile , otp = otp)
        profile.save()
        send_otp(mobile, otp)
        request.session['mobile'] = mobile
        return redirect('otp')
    return render(request,'register.html')

def otp(request):
    mobile = request.session['mobile']
    context = {'mobile':mobile}
    if request.method == 'POST':
        otp = request.POST.get('otp')
        profile = Profile.objects.filter(mobile=mobile).first()

        if otp == profile.otp:
            return redirect('cart')
        else:
            print('Wrong')

            context = {'message' : 'Wrong OTP' , 'class' : 'danger','mobile':mobile }
            return render(request,'otp.html' , context)


    return render(request,'otp.html' , context)

#resend otp function

def resend_otp(request):
    mobile = request.session['mobile']
    context = {'mobile':mobile}
    attempt=0
    if request.method == 'POST':
        otp = request.POST.get('otp')
        profile = Profile.objects.filter(mobile=mobile).first()
        attempt+=1

        if attempt<3:
            if otp == profile.otp:
                return redirect('cart')
            else:
                print('Wrong')
        else:
            return HttpResponse('ca;t send otp')

            context = {'message' : 'Wrong OTP' , 'class' : 'danger','mobile':mobile }
            return render(request,'otp.html' , context)


    return render(request,'otp.html' , context)


#  Adding the function comment likes and comment_dislikes

class Addcomment_likes(LoginRequiredMixin,View):
    def vedio_comment(self,request, id,pk,*args,**kwargs): #id is vedio id ,pk is comment id
        comment=Comment.objects.get(pk=pk)
        is_dislike=False
        for dislike in comment.dislikes.all():
            if dislike == request.user:
                is_dislike=True
                break

        if is_dislike:
            comment.dislikes.remove(request.user)

        is_like=False
        for like in comment.like.all():
            if like==request.user:
                is_like=True
                break

        if not is_like:
            comment.likes.add(request.user)

        if is_like:
            comment.likes.remove(request.user)


        next= request.POST.get('next','/')
        return HttpResponseRedirect(next)


#Add the function comment_dislikes
class Add_dislikecomment(LoginRequiredMixin,View):
    def vedio_comment(self,request,id,pk,*awargs,**kwargs):
        comment=Comment.objects.get(pk=pk)

        is_like=False
        for like in comment.likes.all():
            if like==request.user:
                is_like=True
                break

        if is_like:
            comment.likes.remove(request.user)

        is_dislike=False

        for dislike in comment.dislikes.all():
            if dislike==request.user:
                is_dislike=True
                break

        if not is_dislike:
            comment.dislikes.add(request.user)

        if is_dislike:
            comment.dislikes.remove(request.user)

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)

#function for the  community post like:
def community_post_like(request,pk): #this funciton will be add the use in our database who like the vedio
    commmunity_post= get_object_or_404(communitypost,id.request.Post.get('id'))
    community_post_like.post_likes.add(request,User)
    return HttpResponse(reverse('template_name',arg=[str(pk)]))


def post_likes(request): #this function will be display the user who liked vedio.
    comm_post= get_object_or_404(communitypost,id.request.Post.get('id'))
    comm_post_like=comm_post.likes.all()
    context=({'comm_post_like':comm_post_like})
    return render(request,'template_name',context)

class communitylikeview(DetailView):
    model=communitypost
    template_name='templatename'# here we have to add the template name where you want to render this function
    def get_context_data(self,**kwargs):
        context=super(communitylikeview).get_context_data(**kwargs)
        stuff=get_object_or_404(communitypost,id=self.kwaargs['pk'])
        total_likes=stuff.total_post_likes()
        context={'total_likes':total_likes}
        return context


class designAPIView(APIView):
    def get(self,request):
        alldesign=design.objects.all().values()
        return Response({'list_of_design':alldesign})


    def post(self,request):
        design.objects.create(static=request.data['static'])

        file=design.objects.all().filter(static=request.data['static']).values()
        return Response({'design':file})



#function for the post of community_comment 
def post_comment(self):
    post=get_object_or_404(communitypost,slug=createpost)
    community_comment=post.commmunity_comment.filter(active=True,parent_isnull=True)

    if request.method=='POST':
        community_comment=community_comment(data=request.POST)
        if community_comment_form.is_valid():
            parent_obj=None
            try:
                parent_id=int(reuqest.post.get('parent_id'))
            except:
                parent_id=None
            if parent_id:
                parent_obj=community_comment.objects.get(id=parent_id)
                if parent_obj:
                    reply_comment=community_comment_form.save(commit=False)
                    reply_comment.parent=parent_obj
            new_comment=community_comment_form.save(commit=False)
            new_comment.post=post
            new_comment.save()
            return HttpResponseRedirect(post.get_absolute_url)
    else:
        comment_form=community_comment_form
        context={
            'post':post,
            'community_comment':community_comment,
            'community_comment_form':community_commment_form
        }

    return render (request, 'templatename',context)


#this function to delete the comment
class deletecommuniytcommentview(DeleteView):
    model=community_comment
    template=''
    success=reverse_lazy('template')



#Add the comment likes and dislikes
class Addcommunitycommentlikes(LoginRequiredMixin,View):
    def comment_likes_detail(sel,request,id,pk,*args,**kwargs):
        comment=community_comment.objects.get(pk=pk)
        is_dislike=False
        for dislike in comment.dislikes.all():
            if dislike ==request.user:
                is_dislike=True
                break
        
        if is_dislike:
            comment.dislikess.remove(request.user)

        is_like=False
        for like in comment.likes.all():
            if like==request.user:
                is_like=True
                break

        if not is_like:
            comment.ikes.add(request.user)

        if is_like:
            comment.likes.remove(request.user)

        next=request.POST.get('next','/')
        return HttpResponseRedirect(next)



#this function for community postcomment dislike

class Add_community_post_dislikecomment(LoginRequiredMixin,View):
    def community_comment(self,request,id,pk,*awargs,**kwargs):
        comment=community_comment.objects.get(pk=pk)

        is_like=False
        for like in commentlikes.all():
            if like==request.user:
                is_like=True
                break
        
        if is_like:
            comment.likes.remove(request.user)

        is_dislike=False
        for dislike in comment.dislike.all():
            if dislike==request.user:
                is_dislike=True
                break

        if not is_dislike:
            comment.dislikes.add(reuqest.user)

        if is_dislike:
            comment.dislike.remove(request.user)

        next=request.POST.get('next','/')
        return HttpResponseRedirect(next)





#this is api for the project
class videoAPIView(APIView):
    def get(self,request): # it is used for get ther vedio through the api.
        allvideos=videos.objects.all().values()
        return Response({'list_of_vedios':allvideos})
    
    def post(self,request): # it is used for posting the vedio through the api.
        videos.objects.create(VideoFile=request.data['VideoFile'])#id=request.data['id'],
        #VideoTitle=request.data['VideoTitle'],
       # VideoFile=request.data['VideoFile'],
       # like=request.data['like'],
        #published_date=request.data['published_date'],
        #comments=request.data['comments'],
        #active_earn=request.data['active_earn'],
        # views=request.data['views'],
        # supported=request.data['supported'],
        # code_mode=request.data['code_mode']
        
        allvideos=videos.objects.all().filter(VideoFile=request.data['VideoFile']).values()
        return Response({'videos':allvideos})


#function for the follow ,unfollow and pending request and private account

class followUnfollow(APIView):
    permission_classes=[IsAuthenticated]

    def current_profile(self,pk):
        try:
            return Support.objects.get(user=self.request.user)
        except Support.DoesNotExist:
            raise Http404
    
    def other_profile(self,pk):
        pk=request.data.get('id')  #here pk is opposite user,s profile ID
        req_type= request.data.get('type')
        current_profile=self.current_profile()
        other_profile=self.other_profile(pk)

        if req_type=='follow':
            if other_profile.private_account:
                other_profile.pending_request.add(current_profile)
                return Response({'Requested':'Follow request has been send !!'},status=status.HTTP_200_0k)

            else:
                if other_profile.blocked_user.filter(id=current_profile).exists():
                    return Response({'Following Fail':"you cannot follow this profilebecuase your id blocked by this user "},status=status.HTTP_400_BAD_REQUEST)
                current_profile.following.add(other_profile)
                other_profile.followers.add(current_profile)
                return Response({"Following":"Following success"},status=status.HTTP_200_0k)

        elif req_type =='accept':
            current_profile.followers.add(other_profile)
            other_profile.following.add(current_profile)
            current_profile.pending_request.remove(other_profile)
            return Response({'Accepted':"Follow request accept successfully"},status=status.HTTP_200_0k)

        elif req_type=='decline':
            current_profile.pending_request.remove(other_profile)
            return Response({'Decline':'follow request successfully declined !!'},status=status.HTTP_200_0k)

        elif  req_type=='unfollow':
            current_profile.following.remove(other_profile)
            other_profile.followers.remove(current_profile)
            return Response({'unfollow':"unfollow success"},status=status.HTTP_200_0k)

        elif req_type=='remove':
            current_profile.followers.remove(other_profile)
            other_profile.following.remove(current_profile)
            return Response({'Remove Success':'Successfully removed your follower',status=status.HTTP_200_0k})

#here we fetch the data followers,following detail and blocked user
def patch(self,request,format=None):
    req_type=request.data.get('type')

    if req_type=="follow detail":
        serializer=FollowerSerializer(self.current_profile())
        return Response({'data':serializer.data},status=status.HTTP_200_0k)

    elif req_type=='block_pending':
        serializer=BlockPendingSerializer(self.current_profile())
        pf=list(Support.objects.filter(pending_request=self.current_profile().id).values('id','user_username'))
        return Response({'data':serializer.data,'sended Request':pf},status=status.HTTP_200_0k)


#you can block and unblock
def put(self,request,format=None):
    pk=request.data.get('id')
    req_type=request.data.get('type')

    if req_type =='block':
        self.current_profile().blocked_user.add(self.other_profile(pk))
        return Response({'Blocked':'This user blocked successfully '},status=status.HTTP_200_0k)

    elif req_type =='unblock':
        self.current_profile().blocked_user.remove(self.other_profile(pk))
        return Response({'unblocked':"this user unblocked successfully"},status=status.HTTP_200_0k)









