from rest_framework import serializers

from .models import User, Post, Photo, Car, Site, City, State, BSF, BSF_Options, PCF, VHF, VDF
from django.contrib.auth import update_session_auth_hash

def response(type_, label, data):
    return {'type':type_, 'label': label, 'data': data}

class UserSerializer(serializers.ModelSerializer):
    posts = serializers.HyperlinkedIdentityField(view_name='userpost-list', lookup_field='username')

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'posts', )


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(required=False)
    photos = serializers.HyperlinkedIdentityField(view_name='postphoto-list')
    # author = serializers.HyperlinkedRelatedField(view_name='user-detail', lookup_field='username')

    def get_validation_exclusions(self, *args, **kwargs):
        # Need to exclude `user` since we'll add that later based off the request
        exclusions = super(PostSerializer, self).get_validation_exclusions(*args, **kwargs)
        return exclusions + ['author']

    class Meta:
        model = Post
        fields = '__all__'


class PhotoSerializer(serializers.ModelSerializer):
    image = serializers.ReadOnlyField(source='image.url')

    class Meta:
        model = Photo

class SiteSerializer(serializers.ModelSerializer):


    class Meta:
        model = Site
        fields = ('id', 'site_name', 'url', 'created', 'updated')

class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = '__all__'

class StateSerializer(serializers.ModelSerializer):

    class Meta:
        model = State
        fields = '__all__'

class BuildSheetOptionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = BSF_Options
        fields = '__all__'

    # def to_representation(self, instance):
    #     return instance.value

class BuildSheetSerializer(serializers.ModelSerializer):
    #options = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    #id = BuildSheetOptionsSerializer(many=True)
    # id = BuildSheetOptionsSerializer(required=True)
    options = BuildSheetOptionsSerializer(many=True, read_only=True)

    class Meta:
        model = BSF
        fields = ['id', 'options', 'vin', 'msrp', 'warranty_start', 'model_year', 'model_detail', 'color', 'production_month', 'interior']
    # def to_representation(self, instance):
    #     serialized_data = super(BuildSheetSerializer,  self).to_representation(instance)
    #     print(serialized_data['options'])
    #     data = ''
    #     for option in serialized_data['options']:
    #         data = data + option + ','
    #     serialized_data['options'] = data
    #
    #     return serialized_data
class VDFSerializer(serializers.ModelSerializer):

    class Meta:
        model = VDF
        fields = '__all__'
class VHFSerializer(serializers.ModelSerializer):

    class Meta:
        model = VHF
        fields = '__all__'
class PCFSerializer(serializers.ModelSerializer):
    class Meta:
        model = PCF
        fields = '__all__'
class PCFModelNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = PCF
        fields = ('model_number',)
class CarSerializer(serializers.ModelSerializer):
    site = SiteSerializer(required=True)
    vin = BuildSheetSerializer(required=True)
    pcf = PCFSerializer(required=True)
    vdf = VDFSerializer(required=True)
    vhf = VHFSerializer(required=True)

    class Meta:
        model = Car
        fields = '__all__'

class SearchSerializer(serializers.Serializer):

    def to_representation(self, instance):
        if isinstance(instance, Car):
            serializer = CarSerializer(instance, context=self.context)
            #return response('car', instance.name, serializer.data)
            return serializer.data
        if isinstance(instance, BSF):
            serializer = BuildSheetSerializer(instance, context=self.context)
            #return response('bsf', instance.name, serializer.data)
            return serializer.data