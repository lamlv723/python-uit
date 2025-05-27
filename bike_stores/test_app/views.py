from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

# Create your views here.
def index(request):
    #########
    # Logic #
    #########

    # Output
    return HttpResponse("Hello world!")

def test_json_res(request):
    #########
    # Logic #
    #########


    # Output
    data = {
        "test": 1
    }

    return JsonResponse(data)