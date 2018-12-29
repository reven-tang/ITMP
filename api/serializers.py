from . import models
from rest_framework import serializers

class MonitorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.MonitorInfo
        fields = ('id', 'ipaddr', 'hostname', 'platform', 'cpucorecount', 'memsize', 'kpi', 'values', 'mtime')