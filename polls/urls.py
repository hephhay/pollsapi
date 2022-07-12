from posixpath import basename
from django.urls import path
from rest_framework.routers import DefaultRouter

from .apiviews import ChoiceViewset, VoteViewSet, PollViewSet, UserCreate, LoginView


router = DefaultRouter()
router.register('polls', PollViewSet, basename='polls')
router.register(r'polls/(?P<poll>\d+)/choices', ChoiceViewset, basename='choice_set')
router.register(r'polls/(?P<poll>\d+)/choices/(?P<choice>\d+)/vote', VoteViewSet, basename='vote_set')

urlpatterns = [
    path("users/", UserCreate.as_view(), name="user_create"),
    path("login/", LoginView.as_view(), name="login"),
]

urlpatterns += router.urls