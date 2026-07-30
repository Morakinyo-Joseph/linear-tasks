from django.urls import path
from rest_framework.routers import DefaultRouter

from .demo_views import BoomView, NoticeView
from .views import TodoViewSet

router = DefaultRouter()
router.register(r"todos", TodoViewSet, basename="todo")

urlpatterns = [
    path("demo/boom/", BoomView.as_view(), name="demo-boom"),
    path("demo/notice/", NoticeView.as_view(), name="demo-notice"),
    *router.urls,
]
