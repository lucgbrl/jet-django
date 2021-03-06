from django.db import connection, ProgrammingError
from django.utils.translation import ugettext_lazy as _
from django.utils import six
from rest_framework import views, status
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from jet_django.permissions import HasProjectPermissions
from jet_django.serializers.sql import SqlSerializer


class SqlError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Query failed')
    default_code = 'invalid'

    def __init__(self, detail):
        self.detail = {'error': str(detail)}

    def __str__(self):
        return six.text_type(self.detail)


class SqlView(views.APIView):
    pagination_class = None
    authentication_classes = ()
    permission_classes = (HasProjectPermissions,)

    def get(self, request, *args, **kwargs):
        serializer = SqlSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)

        with connection.cursor() as cursor:
            try:
                cursor.execute(serializer.data['query'], serializer.data.get('params', '').split(','))
            except ProgrammingError as e:
                raise SqlError(e)
            rows = cursor.fetchall()

            return Response(rows)
