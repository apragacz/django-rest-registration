from rest_framework.views import APIView


class APIRegistrationView(APIView):

    def get_serializer_class(self):
        """
        Return the class to use for the serializer.
        """
        raise NotImplementedError()

    def get_output_serializer_class(self):
        """
        Return the class to use for the output serializer.
        Defaults to the result of get_serializer_class() method.
        """
        return self.get_serializer_class()

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input.
        """
        return self._get_serializer(
            self.get_serializer_class(), *args, **kwargs)

    def get_output_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used
        for serializing output.
        """
        return self._get_serializer(
            self.get_output_serializer_class(), *args, **kwargs)

    def _get_serializer(self, serializer_class, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': self.request,
            'view': self
        }
