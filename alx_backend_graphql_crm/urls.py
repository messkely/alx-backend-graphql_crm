from django.contrib import admin
from django.urls import path, include, re_path
from graphene_django.views import GraphQLView
from crm.schema import schema
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('admin/', admin.site.urls),
    path('crm/', include('crm.urls')),
    re_path(r"graphql", csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema)), name='graphql'),
]