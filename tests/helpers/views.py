from django.urls import resolve, reverse


class ViewProvider:

    def __init__(self, view_name, app_name='rest_registration'):
        self.view_name = view_name
        self.app_name = app_name
        self._view_url = None
        self._view_func = None

    @property
    def full_view_name(self):
        return '{self.app_name}:{self.view_name}'.format(self=self)

    @property
    def view_url(self):
        if self._view_url is None:
            self._view_url = reverse(self.full_view_name)
        return self._view_url

    def view_func(self, *args, **kwargs):
        if self._view_func is None:
            match = resolve(self.view_url)
            self._view_func = match.func
        return self._view_func(*args, **kwargs)
