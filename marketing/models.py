from django.db import models

class UploadedFile(models.Model):
    """
    Details on each uploaded file
    """
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey('auth.User',
                                    null=True,
                                    on_delete=models.SET_NULL)
    num_columns = models.IntegerField()


class UploadedRow(models.Model):
    """
    unprocessed rows from uploaded file
    """
    parent_file = models.ForeignKey('UploadedFile', on_delete=models.CASCADE)
    row_is_first = models.BooleanField(default=False)
    row_number = models.IntegerField()
    has_error = models.BooleanField(default=False)
    error_message = models.CharField(max_length=255,
                                     blank=True,
                                     default="")


class UploadedCell(models.Model):
    """
    contents of each cell from uploaded files
    """
    parent_row = models.ForeignKey('UploadedRow', on_delete=models.CASCADE)
    cell_order = models.IntegerField()
    content = models.TextField(blank=True, default="")
