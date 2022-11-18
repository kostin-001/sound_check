from django.shortcuts import render
from django.utils.safestring import mark_safe
from core.main_logic import SoundCheck
from core.recognize import FileRecognizer


DEFAULT_EXT = ["mp3", "wav"]


def index(request):
    return render(request, 'index.html')


def similar_page(request):
    return render(request, 'scanning_done.html')


def do_crawl(request):
    ext = list(filter(None, [request.POST.get('mp3'), request.POST.get('wav')]))
    if len(ext) == 0:
        ext = DEFAULT_EXT

    try:
        sc = SoundCheck()
        sc.fingerprint_directory(path=request.POST.get('dir_path'), extensions=ext)
        return render(request, 'scanning_done.html')
    except Exception as e:
        return render(request, 'index.html', {'param': mark_safe(str(e))})


def add_to_index(request):
    try:
        sc = SoundCheck()
        sc.fingerprint_file(filepath=request.POST.get('file_path'))
        return render(request, 'index.html', {'param': "File added to index"})
    except Exception as e:
        return render(request, 'index.html', {'param': mark_safe(str(e))})


def find_similar(request):
    path = request.POST.get('file_path')
    if path.endswith(tuple(DEFAULT_EXT)):
        sc = SoundCheck()
        songs = sc.recognize(FileRecognizer, path, int(request.POST.get('limit')))
        return render(request, 'scanning_done.html', {'songs_list': songs})
    else:
        return render(request, 'index.html', {'param': mark_safe("Incorrect file")})