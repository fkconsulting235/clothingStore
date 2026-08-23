from django.contrib.auth.decorators import login_required, user_passes_test


def staff_required(view_func):
    checked = user_passes_test(lambda u: u.is_active and u.is_staff, login_url='dashboard:login')(view_func)
    return login_required(checked, login_url='dashboard:login')
