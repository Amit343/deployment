class EachUserSerializer(serializer.ModelSerializer):
    username=serializers.CharField(source='user.username')
    class Meta:
        model=Profilefields=('id','username')
        read_only_fields=('id','username')


class FollowerSerializer(serializers.ModelSerializer):
    followers = EachUserSerializer(many=True, read_only= True)
    following = EachUserSerializer(many=True,read_only=True)
    
    class Meta:
        model = Profile
        fields = ('followers','following')
        read_only_fields = ('followers','following')

class BlockPendinSerializer(serializers.ModelSerializer):
    panding_request = EachUserSerializer(many=True, read_only= True)
    blocked_user = EachUserSerializer(many=True,read_only=True)

    class Meta:
        model = Profile
        fields = ('panding_request','blocked_user')  
        read_only_fields = ('panding_request','blocked_user')
