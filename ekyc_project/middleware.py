def new_middleware(get_response):
    def middleware(request):
        print("BEFORE")
        response = get_response(request)
        print("AFTER")
        return response
    return middleware
