from django.http import HttpResponse

def salutView(request):
    return HttpResponse('Salut les gens')