from django.shortcuts import render, redirect, get_object_or_404
from .forms import CreateUser, FertilizersForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView
from .models import ImageModel, PodCount, Fertilizer
from .forms import ImageUploadForm, ImageEditForm
import torch
from PIL import Image
import pathlib
import pandas
import numpy as np
import cv2
from django.http import HttpResponseForbidden, JsonResponse
from django.conf import settings
import json
import os
from django.core.files import File
from django.utils.translation import activate
import serial
import random
import time
from django.db.models import Sum 
from pathlib import Path
from .model_yolo import SingletonModel
from urllib.error import HTTPError
import urllib.request

# Create your views here.


# Puerto Serial


# folder_path = Path('C:/Users/jairg/Desktop/CacaoAPP/cacaoApp/model/best.pt')
# model = torch.hub.load('ultralytics/yolov5',  'custom' , path=folder_path, force_reload=True)


# # Gestion de Usuarios
@login_required
def homeView(request):
    users = User.objects.all()
    numberUsers = len(users)
    user_pod_counts = []
    current_user = request.user
    id_user = current_user.id
    print(f'Current User: {current_user}, ID: {current_user.id}') 
    

    for userdata in users:
        images = ImageModel.objects.filter(user_id=userdata)
        total_healthy = sum(image.numHealthy for image in images)
        total_monilia = sum(image.numMonilia for image in images)
        total_pythophora = sum(image.numPythophora for image in images)
        total_pods = total_healthy + total_monilia + total_pythophora
        user_pod_counts.append({
            'id': userdata.id,
            'username': userdata.username,
            'is_superuser': userdata.is_superuser,
            'total_pods': total_pods
        })


    podCounts = PodCount.objects.all()
    print([pod.healthyPod for pod in podCounts])
    totalHealthy = sum(pod.healthyPod for pod in podCounts)    
    totalMonilia = sum(pod.moniliaPod for pod in podCounts)
    totalPythophora = sum(pod.pythophoraPod for pod in podCounts)
    totalMaz = totalMonilia + totalPythophora + totalHealthy
    print(totalMaz)
    print(totalMaz)
    return render(request, 'index.html', {
        # 'usersapp': users, 
        'numberusers': numberUsers,
        'pythoDetects': totalPythophora,
        'moniliaDetects': totalMonilia,
        'healthyDetects': totalHealthy,
        'totalMaz': totalMaz,
        'current_user': current_user,  
        'user_id': id_user,
        'usersapp': user_pod_counts,
    })




def loginView(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username= username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenido {username}')
                return redirect('home-view')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')


    form = AuthenticationForm()   

    form.fields['username'].label = 'Nombre de usuario'
    form.fields['password'].label = 'Contraseña'
    return render(request, 'login.html', {"form":form})


def createUser(request):
    activate('es')
    if request.method == 'POST':
        form = CreateUser(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login-view')
    else:
        form = CreateUser()

    return render(request, 'createUser.html', {'form': form})


@login_required
def deleteUser(request, user_id):
    if request.method == 'POST':
        if request.user.is_superuser:
            usuario = get_object_or_404(User, pk=user_id)
            usuario.delete()
            return redirect('home-view')
        else: 
            return render('error.html')
    else:
        pass



def userProfile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    # user = request.user  
    analizedImage = ImageModel.objects.filter(user_id=user)
    total_healthy = sum(img.numHealthy for img in analizedImage)
    total_monilia = sum(img.numMonilia for img in analizedImage)
    total_pythophora = sum(img.numPythophora for img in analizedImage)

    is_owner = (request.user == user)
    print(is_owner)

    

    
    return render(request, 'userProfile.html', {
        'user': user,
        'analizedImage': analizedImage,
        'total_healthy': total_healthy,
        'total_monilia': total_monilia,
        'total_pythophora': total_pythophora,
        'is_owner': is_owner
    })


def logoutApp(request):
    logout(request)
    return redirect('login-view')




# Secciones
def detectHumidity(request):
    ## Codigo real
    # ser = serial.Serial('COM3', 9600, timeout=1)
    # humidity = get_sensor_data(ser)
    # ser.close()  # Cierra el puerto serial después de leer el dato
    
    # if request.headers.get('x-requested-with') == 'XMLHttpRequest':
    #     return JsonResponse({'humidity': humidity})


    # Pruebas
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        humidity = get_simulated_sensor_data()
        return JsonResponse({'humidity': humidity})
    return render(request, 'humidity.html')
    


def fertilizers(request):
    user = request.user
    fertilizerPosts = Fertilizer.objects.all()

    return render(request, 'fertilizers.html',{
        'user': user,
        'posts': fertilizerPosts,
    })


def postFertilizer(request, id):
    post = get_object_or_404(Fertilizer, id=id)
    user = request.user

    return render(request, 'postFertilizer.html', {
        'post': post,
        'user': user
        
    })


def addFertilizers(request):
    activate('es')
    if request.method == 'POST':
        form = FertilizersForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user_id = request.user
            post.save()
            return redirect('fertilizers')
        
    else:
        form = FertilizersForm()
        return render(request, 'addFertilizers.html',{
            'form': form
        })



def editAddFertilizer(request, id):
    post = get_object_or_404(Fertilizer, id=id)
    if request.user != post.user_id:
        # Puedes redirigir a alguna página o mostrar un mensaje de error
        return render(request, 'error.html', {'message': 'No tienes permisos para editar esta barbería.'})
    
    if request.method == 'POST':
        form = FertilizersForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.user_id = request.user
            post.save()
            return redirect('fertilizers')  
        
    else:
        form = FertilizersForm(instance=post)
        return render(request, 'editFertilizer.html',{
            'form': form
        })

    
def deleteFertilizer(request, id):
    form = get_object_or_404(Fertilizer, id=id)
    if request.user == form.user_id:
        form.delete()
        return redirect('fertilizers')
    else:
        return HttpResponseForbidden('No Tienes permisos para eliminar este Post')



    





class UploadImage(CreateView):
    model = ImageModel 
    template_name = 'addCocoaPhoto.html'
    fields = ["image"]

   


    def post(self, request, *args, **kwargs):
            if request.method == 'POST':
                form = ImageUploadForm(request.POST, request.FILES)
                if form.is_valid():
                    mazorcaimage = form.save(commit=False)
                    mazorcaimage.user_id = request.user
                    try: 
                        imageByIa, mazorcaP, mazorcaM, mazorcaS, detectState = detectCacaoState(mazorcaimage.image) 
                    except HTTPError as e:
                        if e.code == 403:
                            print("Rate limit exceeded. Waiting before retrying...")
                            time.sleep(60)  # Esperar 60 segundos antes de reintentar
                            return detectCacaoState(mazorcaimage.image)
                        else:
                            raise


                    mazorcaimage.numPythophora = mazorcaP
                    mazorcaimage.numMonilia = mazorcaM
                    mazorcaimage.numHealthy = mazorcaS


                    podCount = PodCount.objects.create()

                    # filtrado de Mazorcas
                
                    if mazorcaP >= 1:
                        mazorcaimage.mazorcaState += f'{mazorcaP} M. con Pythophora\n'
                        podCount.pythophoraPod += mazorcaP

                    if mazorcaM >= 1:
                        mazorcaimage.mazorcaState += f'{mazorcaM} M. con Monilia\n'
                        podCount.moniliaPod += mazorcaM

                    if mazorcaS >= 1:
                        mazorcaimage.mazorcaState += f'{mazorcaS} M. Saludable\n'
                        podCount.healthyPod += mazorcaS


                    podCount.save()

                    mazorcaimage.podCount_id = podCount


                    processed_image_path = os.path.join(settings.DETECTION_MEDIA_ROOT, 'mydetect.png')
                    # guarda la imagen analizada
                    imageByIa.save(processed_image_path)
                    processed_image = File(open(processed_image_path, 'rb'))
                    mazorcaimage.imagesDetected.save('mydetect.png', processed_image, save=False)
                    # mazorcaimage.imagesDetected.save()

                    # Asignar la nueva imagen procesada al campo de imagen del modelo
                    mazorcaimage.image.name = 'mydetect.png'

                
                    # agregar otro campo al formulario de imagen
                    mazorcaimage.save()
                    
                    return redirect('user-profile', user_id=request.user.id)
            else:       
                form = ImageUploadForm()
            return render(request, 'addCocoaPhoto.html', {'form': form})
   
            

# class EditUploadImage(UpdateView):
#     model = ImageModel
#     template_name = 'editCocoaPhoto.html'
#     fields = ["image", 'mazorcaState']

#     def post(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         form = ImageUploadForm(request.POST, request.FILES, instance=self.object)
#         if form.is_valid():
#             mazorcaimage = form.save(commit=False)
#             mazorcaimage.user_id = request.user
#             imageByIa, mazorcaP, mazorcaM, mazorcaS, detectState = detectCacaoState(mazorcaimage.image) 

#             mazorcaimage.numPythophora = mazorcaP
#             mazorcaimage.numMonilia = mazorcaM
#             mazorcaimage.numHealthy = mazorcaS

#             podCount = PodCount.objects.create()

#             # Filtrado de Mazorcas
#             if mazorcaP >= 1:
#                 mazorcaimage.mazorcaState += f'{mazorcaP} M. con Pythophora\n'
#                 podCount.pythophoraPod += mazorcaP

#             if mazorcaM >= 1:
#                 mazorcaimage.mazorcaState += f'{mazorcaM} M. con Monilia\n'
#                 podCount.moniliaPod += mazorcaM

#             if mazorcaS >= 1:
#                 mazorcaimage.mazorcaState += f'{mazorcaS} M. Saludable\n'
#                 podCount.healthyPod += mazorcaS

#             podCount.save()
#             mazorcaimage.podCount_id = podCount

#             processed_image_path = os.path.join(settings.DETECTION_MEDIA_ROOT, 'mydetect.png')
#             # Guarda la imagen analizada
#             imageByIa.save(processed_image_path)
#             processed_image = File(open(processed_image_path, 'rb'))
#             mazorcaimage.imagesDetected.save('mydetect.png', processed_image, save=False)

#             # Asignar la nueva imagen procesada al campo de imagen del modelo
#             mazorcaimage.image.name = 'mydetect.png'

#             mazorcaimage.save()
            
#             return redirect('user-profile', user_id=request.user.id)
#         return render(request, self.template_name, {'form': form})

#     def get_object(self, queryset=None):
#         # Asegúrate de obtener el objeto correcto para editar
#         return get_object_or_404(ImageModel, pk=self.kwargs.get('pk'))




class EditUploadImage(UpdateView):
    model = ImageModel
    template_name = 'editCocoaPhoto.html'
    form_class = ImageEditForm

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, request.FILES, instance=self.object)
        if form.is_valid():
            mazorcaimage = form.save(commit=False)
            mazorcaimage.user_id = request.user
            podCount = mazorcaimage.podCount_id

            # Actualizar los valores con los nuevos datos manuales
            podCount.healthyPod = mazorcaimage.numHealthy
            podCount.moniliaPod = mazorcaimage.numMonilia
            podCount.pythophoraPod = mazorcaimage.numPythophora

            podCount.save()
         
            mazorcaimage.save()
            return redirect('user-profile', user_id=request.user.id)
        return render(request, self.template_name, {'form': form})

    def get_object(self, queryset=None):
        # Asegúrate de obtener el objeto correcto para editar
        return get_object_or_404(ImageModel, pk=self.kwargs.get('pk'))


def deleteRegisterC(request, user_id):
    imgToDelete = get_object_or_404(ImageModel, pk=user_id)
    if request.user == imgToDelete.user_id:
        podCount = imgToDelete.podCount_id
        if podCount:
            podCount.healthyPod -= imgToDelete.numHealthy
            podCount.moniliaPod -= imgToDelete.numMonilia
            podCount.pythophoraPod -= imgToDelete.numPythophora
            podCount.save()
        imgToDelete.delete()
        return redirect('user-profile', user_id=request.user.id)
    
    else:
        return HttpResponseForbidden('No tienes permiso de editar estos datos')







def showError(request):
    return render(request, 'error.html')




# funciones


RATE_LIMIT_INTERVAL = 60  # segundos
MAX_RETRIES = 5

def make_request_with_retries(url, retries=MAX_RETRIES):
    for attempt in range(retries):
        try:
            # Realizar la solicitud aquí
            response = urllib.request.urlopen(url)
            return response.read()
        except HTTPError as e:
            if e.code == 403 and attempt < retries - 1:
                print(f"Rate limit exceeded. Waiting before retrying... Attempt {attempt + 1}")
                time.sleep(RATE_LIMIT_INTERVAL)
            else:
                raise

def detectCacaoState(img_path):
    url = 'https://cocoapod.onrender.com/upload-image/'
    response = make_request_with_retries(url)
    # Dependencias de Lectura
    # Windows
    # temp = pathlib.PosixPath   
    # pathlib.PosixPath = pathlib.WindowsPath
    # folder_path = 'C:/Users/jairg/Desktop/CacaoAPP/cacaoApp/model/best.pt'

    # # Linux Deploy

    # folder_path = Path('C:/Users/jairg/Desktop/CacaoAPP/cacaoApp/model/best.pt')
    # model = torch.hub.load('ultralytics/yolov5',  'custom' , path=folder_path, force_reload=True)


    model = SingletonModel()
    img = Image.open(img_path)

    results = model(img)
        # resultados = results.print()
    results.show()
    r_img = results.render() # returns a list with the images as np.array
    img_with_boxes = r_img[0]

    new_img = Image.fromarray(img_with_boxes) # returns


    print(results.pandas().xyxy[0])
        # x0,y0,x1,y1,confi,cla = results.xyxy[0][-1].numpy()
        # print(x0, y0, x1, y1, confi,cla)
    mazorcas = []
    for mazorca in results.xyxy[0]:
        x0, y0, x1, y1, confi, cla = mazorca.numpy()
        mazorcas.append({
                'x0': x0,
                'y0': y0,
                'x1': x1,
                'y1': y1,
                'confianza': confi,
                'clase': cla
            })


    numMazorcaP = 0
    numMazorcaM = 0
    numMazorcaS = 0
    noDetections = True

    for dataMazorca in mazorcas:
            print(dataMazorca['confianza'])
            print(f'clase detectada {dataMazorca["clase"]}')

            if dataMazorca['clase'] == 0:
                print('Mazorcas con Pythophora')
                numMazorcaP += 1
            if dataMazorca["clase"] == 1:
                print('Mazorcas con Monilia')
                numMazorcaM += 1
            if dataMazorca["clase"] == 2:
                print('Mazoca Saludables')
                numMazorcaS += 1

            else: 
                noDetections = False
   
        



    print(mazorcas)
    

    return new_img, numMazorcaP, numMazorcaM, numMazorcaS, noDetections


    


# def get_sensor_data(ser):
#     if ser.in_waiting > 0:
#         serial_data = ser.readline().decode('utf-8').rstrip()
#         return int(serial_data)
#     return None


def get_simulated_sensor_data():
    # Simular un valor de humedad aleatorio entre 300 y 700
    simulated_humidity = random.randint(0, 1023)
    return simulated_humidity