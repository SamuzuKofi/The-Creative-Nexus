from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'core'

router = DefaultRouter()
router.register(r'portfolios', views.PortfolioViewSet, basename='portfolio')
router.register(r'works', views.CreativeWorkViewSet, basename='creative-work')
router.register(r'collaborations', views.CollaborationViewSet,
                basename='collaboration')
router.register(r'projects', views.ProjectViewSet, basename='project')
router.register(r'notifications', views.NotificationViewSet,
                basename='notification')
router.register(r'ratings', views.RatingViewSet, basename='rating')
router.register(r'mentorship-requests', views.MentorshipRequestViewSet,
                basename='mentorship-request')

urlpatterns = router.urls
