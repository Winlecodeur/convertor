from django.shortcuts import render
import os
import uuid
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from pdf2docx import Converter
from docx2pdf import convert as docx2pdf_convert 
import psutil

def index(request):
    return render (request ,'index.html')

def convert(request):
    if request.method == 'POST'  : 
        upload_file = request.FILES.get('document')
        conversion_type = request.POST.get('conversion_type')
        #Générer un nom de fichier unique
        unique_id= uuid.uuid4().hex
        input_path = os.path.join(settings.MEDIA_ROOT, f"{unique_id}_{upload_file.name}")
        output_filename =  ""
        output_path= ""
        #sauvegarde le fichier download
        with open(input_path, 'wb+') as destination :
            for chunk in upload_file.chunks() : 
                destination.write(chunk)
        try : 
            if conversion_type == 'pdf_to_word' :
                output_filename = f"{unique_id}.docx"
                output_path= os.path.join(settings.MEDIA_ROOT, output_filename)
                #convertir PDF en word 
                cv = Converter(input_path)
                cv.convert(output_path)
                cv.close()
            elif conversion_type == 'word_to_pdf' : 
                output_filename = f"{unique_id}.pdf"
                output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
                #convertit word to PDF
                docx2pdf_convert(input_path,output_path)
                close_word_processes() 
            else :
                return HttpResponse('Type de conversion invalide', status=400)
                #supprimer le fichier d'entrée après conversion
            os.remove(input_path)
            #fournir le lien de téléchargement
            return render (request, 'result.html', {'download_link':os.path.join(settings.MEDIA_URL,output_filename)})
        except Exception as e : 
            #en cas d'erreur , supprimer les fichiers et afficher un message d'erreur
            if os.path.exists(input_path):
                os.remove(input_path)
                if output_path and os.path.exists(output_path):
                    os.remove(output_path)
                    return HttpResponse(f"Erreur lors de la conversion : {str(e)}", status=500)
    return HttpResponseRedirect(reverse('index'))

def close_word_processes():
    """FERMER TOUS LES PROCESSUS MICROSOFT WORD APRES LES CONVERSIONS"""
    for proc in psutil.process_iter(['pid','name']):
        if proc.info['name'] and 'WINWORD' in proc.info['name'].upper():
            try : 
                proc.kill()
            except psutil.NoSuchProcess:  
                pass 