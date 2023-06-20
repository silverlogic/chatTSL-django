from rest_framework import fields, serializers

from .types import INPUT_EVENT_TYPE, OUTPUT_EVENT_TYPE


class InputEventSerializer(serializers.Serializer):
    event_type = fields.ChoiceField(INPUT_EVENT_TYPE)
    event_data = fields.JSONField()

    class Meta:
        fields = ["event_type", "event_data"]


class OutputEventSerializer(serializers.Serializer):
    event_type = fields.ChoiceField(OUTPUT_EVENT_TYPE)
    event_data = fields.JSONField()

    class Meta:
        fields = ["event_type", "event_data"]
