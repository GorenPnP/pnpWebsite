import uuid
from django import forms
from django.core import validators
from django.core.exceptions import ValidationError

from base.crispy_form_decorator import crispy

from .models import Card, Transaction

def get_card(queryset=Card.objects.filter(active=True), **kwargs):
    cards = queryset.filter(**kwargs)
    return cards[0] if cards else None


class CardWidget(forms.MultiWidget):
    def __init__(self, attrs={}, *args, **kwargs):
        self.queryset = kwargs["queryset"]

        choices = [(None, kwargs["empty_label"])] + [(c.__dict__[kwargs["to_field_name"]], c.name) for c in self.queryset]
        widgets = [
            forms.Select(attrs=attrs, choices=choices),
            forms.NumberInput(attrs=attrs.update(placeholder="Karte scannen"))
        ]

        super().__init__(widgets, attrs)


    def decompress(self, value):
        if value is None: return [None, None]

        try:
            # is syntactically valid card_id?
            uuid.UUID(value)
            # then return shit
            card = get_card(self.queryset, id=value)
            return [card if card else None, value]
        except: pass

        card = get_card(self.queryset, card_id=value)
        return [card, card.card_id] if card else [None, None]


    def value_from_datadict(self, data, files, name):
        card, card_id = super().value_from_datadict(data, files, name)
        
        # none given
        if not card and not card_id: return None

        # one given
        if card and not card_id: return card
        if not card and card_id: return get_card(self.queryset, card_id=card_id)

        # both given -> check if they reference the same card 
        card_obj = get_card(self.queryset, id=card)
        return card if card_obj.card_id == int(card_id) else None


class CardField(forms.ModelChoiceField):
    """
    Custom FormField for the Card model. allows selecting Card from Select or scanning via NFC in NumberInput.
    Can be initialized from automatically generated ModelChoiceField for a ForeignKey in a ModelForm with CardField.get_from_default().
    """

    def __init__(self, *args, **kwargs):

        # custom handling of required. Set to False since it will be propagated to all widgets.
        # make sure that exactly one is set (and valid) manually in self.validate(), if self.validate_required is True.
        self.validate_required = kwargs["required"]
        kwargs["required"] = False

        kwargs["widget"] = CardWidget(*args, **kwargs)
        super().__init__(*args, **kwargs)


    def validate(self, value) -> None:
        super().validate(value)

        if self.validate_required and value in validators.EMPTY_VALUES:
            raise ValidationError(self.error_messages["required"], code="required")


    @classmethod
    def get_from_default(cls, original_field, exclude_uuid=None):
        data = original_field.__dict__
        data.pop("_queryset")
        data.pop("widget")

        queryset = Card.objects.filter(active=True)
        if exclude_uuid:
            queryset.exclude(id=exclude_uuid)

        return CardField(
            **data,
            queryset=queryset
        )


@crispy(form_tag=False)
class AdminTransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = ['sender', 'receiver', 'amount', 'reason']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # use custom Multi-Widget Field for Card. Allows scanning via NFC
        self.fields['sender'] = CardField.get_from_default(self.fields['sender'])

        # use custom Multi-Widget Field for Card. Allows scanning via NFC
        self.fields['receiver'] = CardField.get_from_default(self.fields["receiver"])

    def clean(self):
        cleaned_data = super().clean()

        if "sender" in cleaned_data and "receiver" in cleaned_data and cleaned_data["sender"] == cleaned_data["receiver"]:
            raise ValidationError("Sender und Empfänger dürfen nicht gleich sein")
        
        return cleaned_data


@crispy(form_tag=False)
class SpielerTransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = ['amount', 'reason', 'receiver']


    def __init__(self, *args, **kwargs):
        uuid = kwargs.pop('uuid')
        super().__init__(*args, **kwargs)

        # use custom Multi-Widget Field for Card. Allows scanning via NFC
        self.fields['receiver'] = CardField.get_from_default(self.fields["receiver"], uuid)
