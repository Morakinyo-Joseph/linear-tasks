from django.urls import path
from rest_framework.routers import DefaultRouter

from .autofix_demo.views import BoardDigestView, BulkCompleteView, NotifyPreviewView
from .demo_views import BoomView, NoticeView
from .views import TodoViewSet

router = DefaultRouter()
router.register(r"todos", TodoViewSet, basename="todo")

urlpatterns = [
    path("demo/boom/", BoomView.as_view(), name="demo-boom"),
    path("demo/notice/", NoticeView.as_view(), name="demo-notice"),
    # Multi-layer autofix demos (DEBUG only) — views → serializers → services → utils
    path(
        "demo/complex/board-digest/",
        BoardDigestView.as_view(),
        name="demo-complex-board-digest",
    ),
    path(
        "demo/complex/bulk-complete/",
        BulkCompleteView.as_view(),
        name="demo-complex-bulk-complete",
    ),
    path(
        "demo/complex/notify-preview/",
        NotifyPreviewView.as_view(),
        name="demo-complex-notify-preview",
    ),
    *router.urls,
]
