from django.shortcuts import render
from django.http import HttpResponse
from django.http.response import StreamingHttpResponse
from gestureGames.camera import VideoCamera
from gestureGames.camera2 import VideoCamera2
from gestureGames.camera3 import VideoCamera3
from gestureGames.camera4 import VideoCamera4
from gestureGames.camera5 import VideoCamera5

# Create your views here.
def home(request):
    return render(request, 'Home.html')

# TReX
def trex(request):
    return render(request, 'trex.html')

def gen2(camera2):
    while True:
        frame2 = camera2.get_frame()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame2 + b'\r\n\r\n')

def video_stream2(request):
    return StreamingHttpResponse(gen2(VideoCamera2()),
                content_type = 'multipart/x-mixed-replace; boundary=frame')


# Tic Tac Toe
def tictactoe(request):
    return render(request, 'tictactoe.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def video_stream(request):
    return StreamingHttpResponse(gen(VideoCamera()),
                    content_type='multipart/x-mixed-replace; boundary=frame')

# Hand Criket 
def hc(request):
    return render(request, 'hc.html')

def gen3(camera3):
    while True:
        frame = camera3.get_frame()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def video_stream3(request):
    return StreamingHttpResponse(gen3(VideoCamera3()),
                content_type = 'multipart/x-mixed-replace; boundary=frame')



# Rock Paper Sicssors
def rps(request):
    return render(request, 'rps.html')

def gen4(camera4):
    while True:
        frame = camera4.get_frame()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def video_stream4(request):
    return StreamingHttpResponse(gen4(VideoCamera4()),
                    content_type='multipart/x-mixed-replace; boundary=frame')


# SnakeGame
def snakegame(request):
    return render(request, 'snakegame.html')

def gen5(camera5):
    while True:
        frame = camera5.get_frame()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def video_stream5(request):
    return StreamingHttpResponse(gen5(VideoCamera5()),
                    content_type='multipart/x-mixed-replace; boundary=frame')