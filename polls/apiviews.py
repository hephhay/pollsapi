from rest_framework import viewsets, status, permissions, generics
from rest_framework.views import APIView
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin, CreateModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from django.shortcuts import get_object_or_404

from .models import Poll, Choice, Vote
from .serializers import PollSerializer, ChoiceSerializer, VoteSerializer, UserSerializer

from django.contrib.auth import authenticate


class OwnerPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        self.message = f"Cannot perform {request.method} on {type(obj).__name__}"

        if request.method in permissions.SAFE_METHODS:
            return True

        model_property = getattr(view, 'owner_field', None)

        if model_property:
            return getattr(obj, model_property) == request.user
        return True


class LoginView(APIView):
    permission_classes = ()
    serializer_class = UserSerializer
    
    def post(self, request,):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            return Response({"token": user.auth_token.key})
        else:
            return Response({"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST)

class UserCreate(generics.CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSerializer

class PollViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, OwnerPermission)
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    owner_field = 'created_by'


class ChoiceViewset(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, OwnerPermission)
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer

    def get_queryset(self):
        return self.queryset.filter(poll_id=self.kwargs.get("poll"))

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        request.data.update(poll = kwargs.get('poll'))
        return request

    def check_permissions(self, request):
        super().check_permissions(request)
        poll = get_object_or_404(Poll, id = request.data.get('poll'))
        if request.method not in permissions.SAFE_METHODS and poll.created_by != request.user:
            self.permission_denied(request, message = f"Cannot perform {request.method} on Choice", code = status.HTTP_403_FORBIDDEN)


class VoteViewSet(UpdateModelMixin, CreateModelMixin, DestroyModelMixin, viewsets.GenericViewSet):

    permission_classes = (permissions.IsAuthenticated, OwnerPermission)
    serializer_class = VoteSerializer
    queryset = Vote.objects.all()
    owner_field = 'voted_by'

    def get_queryset(self):
        self.queryset = self.queryset.filter(poll_id = self.kwargs.get('poll'))
        if self.request.method.lower() == 'post':
            return self.queryset
        return self.queryset.filter(choice_id = self.kwargs.get('choice'))

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        if request.method.lower() not in ('put', 'patch'):
            request.data.update(choice = self.kwargs.get('choice'))
        request.data.update(poll = self.kwargs.get('poll'), voted_by = request.user.id)
        return request

    def get_object(self):
        obj = super().get_object()
        if self.request.data.get('choice') not in obj.poll.choices.values_list('id',  flat = True):
            raise NotFound('choice not in poll')

    def create(self, request, *args, **kwargs):
        if self.get_queryset().exists():
            raise PermissionDenied('User can only vote once in a poll')
        return super().create(request, *args, **kwargs)