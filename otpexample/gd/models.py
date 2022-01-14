from django.db import models
#from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
''''
class phoneModel(models.Model):
    Mobile = models.CharField(max_length=10) #PhoneNumberField(unique = True, default=None, null = False, blank = False)
    isVerified = models.BooleanField(blank=False, default=False)
   # counter = models.IntegerField(default=0, blank=False)   # For HOTP Verification

    def __str__(self):
        return str(self.Mobile)
'''
from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User ,on_delete=models.CASCADE)
    mobile = models.CharField(max_length=20)
    otp = models.CharField(max_length=6)

    def __str__(self):
        return str(self.user)

class vedios(models.Model):
    vedio=models.FileField(upload_to='vedios/')
    title=models.CharField(max_length=100)
    category=models.CharField(max_length=50)
    Add_tags=models.CharField(max_length=300)
    skillcategory=models.CharField(max_length=50)
    skills=models.CharField(max_length=500)
    groupskills=models.CharField(max_length=500)
    Targeting_Audience=models.PositiveIntegerField()
    Age_restiction=models.PositiveIntegerField()

    def __str__(self):
        return self.title


#Adding comment, comment_likes adn comment _replies
class Comment(models.Model):
    comment=models.TextField()
    created_on=models.DateTimeField(auto_now_add=True)
    vedio=models.ForeignKey('vedios',blank=True,on_delete=models.CASCADE)
    comment_likes=models.ManyToManyField(User,blank=True ,related_name='comment_likes')
    comment_disllikes=models.ManyToManyField(User,blank=True,related_name='comment_dislkikes')

#this model is used for communityy post comment


publish_choices=(  #this will used for choice in community.
    ('public','public'),
    ('private','private'),
    ('unlist','unlist'),
    
)

class communitypost(models.Model):
    id=models.AutoField(primary_key=True)
    createpost=models.ImageField(upload_to='post/',null=True,verbose_name=" ")
    Title=models.CharField(max_length=50)
    tags=models.CharField(max_length=100)
    publish=models.CharField(max_length=100,choices=publish_choices,default='public')
    post_likes=models.ManyToManyField(User,blank=True,related_name='post_likes')



    def total_post_likes(self):
        return self.post_likes.all().count()
    

    def __str__(self):
        return str(self.Title)
    
    def get_absolute_url(self):
        return reverse('home',args=(str(self.id)))

class community_comment(models.Model):
    id=models.AutoField(primary_key=True)
    post_comment=models.TextField()
    post_created_on=models.DateTimeField(auto_now=True)
    community_post=models.ForeignKey('communitypost',blank=True,on_delete=models.CASCADE)
    parent=models.ForeignKey('self',null=True,blank=True,related_name='replies',on_delete=models.CASCADE)
    likes=models.ManyToManyField(User,blank=True ,related_name='Post_comment_likes')
    comment_disllikes=models.ManyToManyField(User,blank=True,related_name='Post_comment_dislkikes')

    class Meta:
        ordering=['-post_created_on']

    def __str__(self):
        return str

#model for the followers and following
class Support(models.Model):
    user=models.OneToOneField(to=User,on_delete=models.CASCADE)
    private_account=models.BooleanField(default=False)
    followers=models.ManyToManyField('self',blank=True,related_name='user_follower',symmetrical=False)
    following=models.ManyToManyField('self',blank=True,related_name='user_following',symmetrical=False)
    pending_reuqest=models.ManyToManyField('self',blank=True,related_name='pending_request',symmetrical=False)
    blocked_user=models.ManyToManyField('self',blank=True,related_name='block',symmetrical=False)
    created_date=models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.user)
