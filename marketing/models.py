from django.db import models

class UploadedFile(models.Model):
    """
    Details on each uploaded file
    """
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey('auth.User')
    filetype = models.CharField(max_length=10)
    first_row = models.TextField(blank=True, null=True)


class UploadedRow(models.Model):
    """
    unprocessed rows from uploaded file
    """
    parent_file = models.ForeignKey('UploadedFile', on_delete=models.CASCADE)
    row = models.TextField()
