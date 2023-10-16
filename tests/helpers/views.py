from django.urls import resolve, reverse


class ViewProvider:

    def __init__(self, view_name, app_name='rest_registration', view_cls=None):
        self.view_name = view_name
        self.app_name = app_name
        self.view_cls = view_cls
        self._view_url = None
        self._view_func = None

    @property
    def full_view_name(self) -> str:
        return f"{self.app_name}:{self.view_name}"

    @property
    def view_url(self) -> str:
        if self._view_url is None:
            self._view_url = reverse(self.full_view_name)
        return self._view_url

    def get_view_func(self):
        if self.view_cls:
            return self.view_cls.as_view()
        if self._view_func is None:
            match = resolve(self.view_url)
            self._view_func = match.func
        return self._view_func

    def view_func(self, request, *args, **kwargs):
        view_f = self.get_view_func()
        return view_f(request, *args, **kwargs)
