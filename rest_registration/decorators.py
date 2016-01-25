import types


def serializer_class_getter(class_getter):

    def decorator(func):
        if not hasattr(func, 'cls'):
            raise Exception('@serializer_class_getter can only decorate'
                            ' @api_view decorated functions')
        apiview = func.cls
        apiview.get_serializer_class = types.MethodType(
            class_getter,
            apiview)
        return func
    return decorator
