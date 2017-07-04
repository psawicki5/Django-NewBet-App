def login_cp(request):
    if request.user.is_authenticated():
        action = "/logout/"
        label = "Log out"
    else:
        action = "/login/"
        label = "Log in"
    context = {
        "action": action,
        "label": label
    }
    return context
