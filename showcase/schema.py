from rest_framework import serializers


class WeekEntrySerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    cat_id = serializers.IntegerField()
    name = serializers.CharField()
    color = serializers.CharField()
    score = serializers.IntegerField()


class WeekResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    results = WeekEntrySerializer(many=True)
    date_from = serializers.DateField()
    date_to = serializers.DateField()
