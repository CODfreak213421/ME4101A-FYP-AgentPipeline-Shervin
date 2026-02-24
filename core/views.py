from django.contrib import messages 
from django.shortcuts import redirect, render

# MATLAB integration imports 
from django.conf import settings

from core.tasks import add, psychoacoustics_pipeline

from core.models import datafile, agent_response

from core.forms import UploadedFileForm

# Create your views here.
def home(request):
    form = UploadedFileForm()
    
    if request.method == 'POST':
        form = UploadedFileForm(request.POST, request.FILES)
        if form.is_valid():
            datafile = form.save()
            psychoacoustics_pipeline.delay(datafile.id)
            messages.success(request, 'File uploaded successfully!')
            return redirect('datalog')
        else:
            messages.error(request, 'Error uploading file. Please try again.')
            return render(request, 'core/index.html', {'form': form})

    context = {'form': form}
    
    
    return render(request, 'core/index.html', context=context)

def datalog(request):

    datafiles = datafile.objects.all()

    context = {
        'datafiles': datafiles  
    }

    return render(request, 'core/datalog.html', context=context)