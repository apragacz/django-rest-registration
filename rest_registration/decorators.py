import types


def serializer_class_getter(class_getter):

    def _get_serializer_class(self):
        return class_getter()

    def decorator(func):
        if not hasattr(func, 'cls'):
            raise Exception('@serializer_class_getter can only decorate'
                            ' @api_view decorated functions')
        apiview_cls = func.cls
        apiview_cls.get_serializer_class = types.MethodType(
            _get_serializer_class,
            apiview_cls)
        return func
    return decorator
