from django.urls import path
from . import views
from . import camera3
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home),
    path('Home/', views.home),
    path('trex/', views.trex, name='trex'),
    path('hc/', views.hc, name='hc'),
    path('rps/',views.rps,name='rps'),
    path('tictactoe/', views.tictactoe, name='tictactoe'),
    path('snakegame/', views.snakegame, name='snakegame'),
    path('video_stream', views.video_stream, name='video_stream'),
    path('video_stream2', views.video_stream2, name='video_stream2'),
    path('video_stream3', views.video_stream3, name='video_stream3'),
    path('video_stream4', views.video_stream4, name='video_stream4'),
    path('video_stream5', views.video_stream5, name='video_stream5'),
]
