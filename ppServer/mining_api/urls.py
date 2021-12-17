from rest_framework.routers import DefaultRouter

from . import views

app_name = 'mining_api'


router = DefaultRouter()

router.register('material', views.MaterialViews, basename="material")

urlpatterns = router.urls
