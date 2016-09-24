import csv
from io import StringIO
import six

from django.db import models
from django.utils import timezone
from django_smalluuid.models import SmallUUIDField, uuid_default
from model_utils import Choices


class TransactionImport(models.Model):
    STATES = Choices(
        ('pending', 'Pending'),
        ('uploaded', 'Uploaded, ready to import'),
        ('done', 'Import complete'),
    )

    uuid = SmallUUIDField(default=uuid_default(), editable=False)
    timestamp = models.DateTimeField(default=timezone.now, editable=False)
    has_headings = models.BooleanField(default=True, verbose_name='First line of file contains headings')
    file = models.FileField(upload_to='transaction_imports', verbose_name='CSV file to import')
    state = models.CharField(max_length=20, choices=STATES, default='pending')

    def create_columns(self):
        """For each column in file create a TransactionImportColumn"""
        # TODO: Replace with non-CSV-specific reader
        csv_buffer = StringIO(self.file.read().decode())
        reader = csv.reader(csv_buffer)
        headings = six.next(reader)
        try:
            examples = six.next(reader)
        except StopIteration:
            examples = []

        for i, value in enumerate(headings):
            if i >= 20:
                break

            TransactionImportColumn.objects.update_or_create(
                transaction_import=self,
                column_number=i + 1,
                column_heading=value if self.has_headings else '',
                to_field='',
                example=examples[i] if examples else '',
            )

class TransactionImportColumn(models.Model):
    """ Represents a column in an imported file

    Stores information regarding how we map to the data in the column
    to our hordak.StatementLine models.
    """
    TO_FIELDS = Choices(
        ('', '-'),
        ('date', 'Date'),
        ('amount', 'Amount'),
        ('amount_out', 'Amount (money in only)'),
        ('amount_in', 'Amount (money out only)'),
        ('description', 'Description / Notes'),
    )

    transaction_import = models.ForeignKey(TransactionImport, related_name='columns')
    column_number = models.PositiveSmallIntegerField()
    column_heading = models.CharField(max_length=100, default='', blank=True, verbose_name='Column')
    to_field = models.CharField(max_length=20, blank=True, default=None, null=True, choices=TO_FIELDS, verbose_name='Is')
    example = models.CharField(max_length=200, blank=True, default='', null=False)

    class Meta:
        unique_together = (
            ('transaction_import', 'to_field'),
            ('transaction_import', 'column_number'),
        )
        ordering = ['transaction_import', 'column_number']

    def save(self, *args, **kwargs):
        if not self.to_field:
            self.to_field = None
        return super(TransactionImportColumn, self).save(*args, **kwargs)
