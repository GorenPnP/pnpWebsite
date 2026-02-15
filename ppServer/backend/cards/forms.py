import uuid

from django import forms
from django.core import validators
from django.core.exceptions import ValidationError

from base.crispy_form_decorator import crispy

from .models import Card, Transaction

def get_card(queryset=Card.objects.filter(active=True), **kwargs):
    try:
        return queryset.get(**kwargs)
    except:
        return None



class CardWidget(forms.MultiWidget):
    def __init__(self, attrs={}, *args, **kwargs):
        self.queryset = kwargs["queryset"]

        choices = [(None, kwargs["empty_label"])] + [(c.__dict__[kwargs["to_field_name"]], c.__str__()) for c in self.queryset]
        widgets = [
            forms.Select(attrs=attrs, choices=choices),
            forms.NumberInput(attrs=attrs.update(placeholder="Karte scannen"))
        ]
        self.has_invalid_choice = False

        super().__init__(widgets, attrs)


    def decompress(self, value):
        if value is None: return [None, None]

        try:
            # is syntactically valid card.pk?
            uuid.UUID(value)
            # then get card by its pk (which is a uuid)
            card = get_card(self.queryset, pk=value)
            return [card, value]
        except:
            # get card by card_id (type of int, not uuid)
            card = get_card(self.queryset, card_id=value)
            return [card, value]


    def value_from_datadict(self, data, files, name) -> Card or None:
        data = super().value_from_datadict(data, files, name)
        card_pk = uuid.UUID(data[0]) if data[0] else None
        card_id = int(data[1]) if data[1] else None
        
        # none given
        if not card_pk and not card_id: return None

        # get card
        card = None
        if   card_pk and not card_id: card = get_card(self.queryset, pk=card_pk)
        elif not card_pk and card_id: card = get_card(self.queryset, card_id=card_id)
        elif card_pk and card_id: card = get_card(self.queryset, pk=card_pk, card_id=card_id)

        # check if they reference a card
        self.has_invalid_choice = card is None
        return card


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

        # widget.has_invalid_choice set in CardWidget.value_from_datadict()
        if self.widget.has_invalid_choice:
            raise ValidationError(self.error_messages["invalid_choice"], code="invalid_choice")

        super().validate(value)

        if self.validate_required and value in validators.EMPTY_VALUES:
            raise ValidationError(self.error_messages["required"], code="required")


    @classmethod
    def get_from_default(cls, original_field, exclude_uuid=None):
        data = original_field.__dict__
        data.pop("_queryset")
        data.pop("widget")

        queryset = Card.objects.prefetch_related("spieler", "char__eigentümer", "account_owner__user").filter(active=True)
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
