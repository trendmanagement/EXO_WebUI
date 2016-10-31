from django.db import models

from solo.models import SingletonModel


from django.db import models

class SeparatedValuesField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop('token', ',')
        super(SeparatedValuesField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            return
        if isinstance(value, list):
            return value
        return [s.strip() for s in value.splitlines()]

    def get_db_prep_value(self, value, connection, prepared=False):
        if not value:
            return
        assert(isinstance(value, list) or isinstance(value, tuple))
        return self.token.join([s for s in value])

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)



class SiteConfiguration(SingletonModel):
    site_name = models.CharField(max_length=255, default='Site Name')

    maintenance_mode = models.BooleanField(default=False)
    insruments_list = SeparatedValuesField(default=('',))


    def __unicode__(self):
        return u"WebUI Configuration"

    class Meta:
        verbose_name = "WebUI Configuration"
