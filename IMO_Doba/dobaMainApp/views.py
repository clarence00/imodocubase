from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound, Http404
from .models import Document
from django.http import JsonResponse
from .parseDoc import update_data
from django.shortcuts import get_object_or_404, redirect
from .forms import RenameDocumentForm
from send2trash import send2trash
from django.core.paginator import Paginator
import os


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def doc_update(request):
    # Fetch data from the database or perform any other operations
    update_data(request)
    # Example: Fetch all documents from the database
    documents = Document.objects.all()
    # Render the template

    # Set Up Pagination
    num_paginator = Paginator(Document.objects.all(), 10)
    page = request.GET.get('page')

    documents = num_paginator.get_page(page)
    return render(request, "dobaMainPage/dbview.html", {'documents': documents})


def home(request):

    # Scripts for HOME PAGE to Django Backend
    documents = Document.objects.all()

    return render(request, "dobaMainPage/home.html", {'documents': documents})


def translogs(request):

    # Scripts for TRANSMISSION LOGS to Django Backend

    return render(request, "dobaMainPage/translogs.html", {'documents': documents})


def rep_gen(request):
    error_message = None
    start_date = None
    queryset = None
    end_date = None

    try:

        if request.method == 'POST':
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

            # Perform query to retrieve data based on date range
            queryset = Document.objects.filter(
                date__range=[start_date, end_date])

            # Return response (render report template or return data as JSON/XML)
            return render(request, 'dobaMainPage/repgeny.html', {'queryset': queryset})

    except Exception as e:
        error_message = "An error occurred: " + str(e)
        return render(request, 'dobaMainPage/repgeny.html', {'error_message': error_message})

    return render(request, 'dobaMainPage/repgeny.html', {'queryset': queryset})


def download_document(request, document_id):
    # Retrieve the document object from the database
    document = get_object_or_404(Document, pk=document_id)

    # Get the file content from the document object
    file_path = document.file_path
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(
                fh.read(), content_type='appication/octet-stream')
            response['Content-Disposition'] = 'inline; filename =' + \
                os.path.basename(file_path)
            return response
    raise Http404


def rename_doc(request, document_id):
    document = get_object_or_404(Document, id=document_id)

    if request.method == 'POST':
        form = RenameDocumentForm(request.POST, instance=document)
        if form.is_valid():
            # Save the updated document name
            new_fileName = form.cleaned_data['document_name']
            print(new_fileName)

            old_filePath = document.file_path
            new_filePath = os.path.join(
                os.path.dirname(old_filePath), new_fileName)
            os.rename(old_filePath, new_filePath)
            document.file_path = new_filePath

            document.document_name = new_fileName
            document.save()

            original_document_id = document_id
            document.delete()

            update_data(request)
            return redirect('/dbview')  # Redirect to document detail page
    else:
        # Initialize the form with the document instance
        form = RenameDocumentForm(instance=document)

    return render(request, 'dobaMainPage/rename_doc.html', {'document': document, 'form': form})


def delete_doc(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    file_path = document.file_path

    if request.method == 'POST':
        try:
            print("Deleting " + file_path)
            send2trash(file_path)
            document.delete()
            return redirect('/dbview')

        except:
            HttpResponseNotFound(f"FILE '{file_path}' NOT FOUND")
            return redirect('/dbview')

    return render(request, 'dobaMainPage/delConf.html', {'document': document})


def search_data(request):
    query = request.GET.get("query")
    if query:

        results = Document.objects.filter(
            document_type__icontains=query).order_by('id')

        page = request.GET.get('page', 1)
        num_paginator = Paginator(results, 5)
        results = num_paginator.page(page)

        return render(request, "dobaMainPage/searchPage.html", {'query': query, 'results': results})

    else:
        return render(request, "dobaMainPage/searchPage.html")
