# see https://github.com/marazmiki/crispy-forms-decorator/tree/master

from django.forms.widgets import PasswordInput

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Fieldset, Layout
from django_password_eye.widgets import PasswordEyeWidget

# subset of FormHelper-variables
PASSED_PARAMS = [
    'form_method', 'form_action', 'form_id', 'form_class',
    'form_group_wrapper_class',
    'form_tag', 'form_error_title',
    'formset_error_title',
    'include_media'
]


class CrispyFormMixin(object):
    _crispy_handler: FormHelper = None

    def __init__(self, *args, **kwargs):
        super(CrispyFormMixin, self).__init__(*args, **kwargs)

        if not hasattr(self, 'helper'):
            if self._crispy_handler is not None:
                self.helper = FormHelper() if self._crispy_handler is None else self._crispy_handler

        if self.helper.layout is None:
            self.helper.layout = self.get_layout()

        # use PasswordEyeWidget for all password input fields
        for field in self.fields.values():
            if isinstance(field.widget, PasswordInput):
                field.widget = PasswordEyeWidget(independent=True)

    def get_layout(self):
        fieldsets = self.get_fieldsets()

        if not fieldsets:
            return Layout(*[self.normalize_field(f) for f in self.fields.keys()])
        else:
            bits = []
            for fieldset in fieldsets:
                if isinstance(fieldset, Fieldset): bits.append(fieldset)
                
                if isinstance(fieldset, tuple):
                    legend, fields = fieldset
                    fieldset = Fieldset(
                        legend,
                        *[self.normalize_field(f) for f in fields]
                    )
                    bits.append(fieldset)

            return Layout(*bits)

    def get_fieldsets(self):
        return []

    def normalize_field(self, field):
        field_handler = getattr(self, 'render_{}_field'.format(field), None)
        if field_handler is not None: return field_handler()

        return field if isinstance(field, Field) else Field(field)


def crispy(*args, **kwargs):
    """ optional params:
    * helper=FormHelper()
    * form_id='id-exampleForm',
    * form_class ='blueForms',
    * form_method='post',
    * form_action='submit_survey',
    * form_error_title='Shit happened for whole form:',
    * formset_error_title='Shit happened for whole formset:',
    * include_media=True,
    * form_tag=True,
    * extra_inputs=[Submit('submit', 'Submit')]),

    * You can define a render_FIELDNAME_field() method to make crispy render the field as you want, e.G.
        def render_first_name_field(self):
            return HTML('Oops, where is our first name?')
    """

    form_cls = None

    if len(args) == 1 and callable(args[0]):
        form_cls = args[0]

    try:
        crispy_helper = kwargs['helper']
        assert isinstance(crispy_helper, FormHelper)
    except (KeyError, AssertionError):
        crispy_helper = FormHelper()

    for ei in kwargs.pop('extra_inputs', []): crispy_helper.add_input(ei)

    for k in PASSED_PARAMS:
        if k in kwargs: setattr(crispy_helper, k, kwargs[k])
        

    def inner(form_cls):
        if not issubclass(form_cls, CrispyFormMixin):
            form_cls.__bases__ = (CrispyFormMixin, ) + form_cls.__bases__
        form_cls._crispy_handler = crispy_helper
        return form_cls

    return inner(form_cls) if form_cls else inner