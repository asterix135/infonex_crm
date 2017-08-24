from django.conf.urls import url
from django.contrib.auth.decorators import login_required, permission_required

from . import views

app_name = 'marketing'
urlpatterns = [
    ################
    # Base views
    ################
    url(r'^$', login_required(views.Index.as_view()), name='index'),
    url(r'^upload/$',
        login_required(views.UploadFile.as_view()),
        name='upload'),

    ################
    # Ajax
    ################
    url(r'^add/$',
        login_required(views.Add.as_view()),
        name='add'),
    url(r'^bulk_update/$',
        login_required(views.BulkUpdate.as_view()),
        name='bulk_update'),
    url(r'^delete/$',
        login_required(views.DeletePerson.as_view()),
        name='delete'),
    url(r'^delete_upload/(?P<pk>[0-9]+)/$',
        login_required(views.DeleteUpload.as_view()),
        name='delete_upload'),
    url(r'^download_errors/$',
        login_required(views.DownloadErrors.as_view()),
        name='download_errors'),
    url(r'^field_matcher/(?P<pk>[0-9]+)/$',
        login_required(views.FieldMatcher.as_view()),
        name='field_matcher'),
    url(r'^process_upload/$',
        login_required(views.ProcessUpload.as_view()),
        name='process_upload'),
    url(r'^update/$',
        login_required(views.UpdatePerson.as_view()),
        name='update'),
]
