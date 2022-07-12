from rest_framework import serializers, mixins

from rest_framework.authtoken.models import Token

from .models import Poll, Choice, Vote
from django.contrib.auth.models import User

def yield_instance(model_cls, model_list, **defaults):
    for values in model_list:
        yield model_cls(**values, **defaults)

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        Token.objects.create(user=user)
        return user

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = '__all__'


class ChoiceSerializer(serializers.ModelSerializer):

    voters_count = serializers.SerializerMethodField()
    votes = VoteSerializer(many=True, required=False, partial=True)

    def get_voters_count(self, obj):
        return obj.votes.all().count()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('required', None) == False:
            self.fields['poll'].required = False

    class Meta:
        model = Choice
        fields = '__all__'


class PollSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, required=False)

    class Meta:
        model = Poll
        fields = '__all__'
        read_only_fields = ('created_by',)
    
    def create(self, validated_data):
        choices_data = validated_data.pop('choices', [])
        poll_obj = Poll.objects.create(**validated_data)
        Choice.objects.bulk_create(iter(yield_instance(Choice, choices_data, poll = poll_obj)))
        return poll_obj

    def update(self, instance, validated_data):
        validated_data.pop('choices', [])
        return super().update(instance, validated_data)

    def save(self, **kwargs):
        super().save(**kwargs, created_by = self.context.get("request").user)
