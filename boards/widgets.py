from django_select2 import forms as s2forms
from .models import Tag

class TagSelect2Widget(s2forms.ModelSelect2TagWidget):
    queryset = Tag.objects.all()
    search_fields = ["name__icontains"]

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def value_from_datadict(self, data, files, name):
        values = super().value_from_datadict(data, files, name)
        pks = []
        for v in values:
            if str(v).isdigit():
                pks.append(str(v))
            else:
                obj, created = Tag.objects.get_or_create(
                    creator=self.request,
                    name=v
                )
                pks.append(str(obj.pk))
        return pks