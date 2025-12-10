# serializers.py
from rest_framework import serializers
from .models import Manufacturer, ElectricCar, EVReview, ChargingSpecification, EVComparison


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = '__all__'


class ElectricCarSerializer(serializers.ModelSerializer):
    manufacturer = ManufacturerSerializer(read_only=True)
    manufacturer_id = serializers.PrimaryKeyRelatedField(
        queryset=Manufacturer.objects.all(),
        source='manufacturer',
        write_only=True
    )
    battery_efficiency = serializers.SerializerMethodField()
    charging_speed = serializers.SerializerMethodField()
    
    class Meta:
        model = ElectricCar
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
    
    def get_battery_efficiency(self, obj):
        return obj.battery_efficiency
    
    def get_charging_speed(self, obj):
        return obj.charging_speed


class EVReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = EVReview
        fields = '__all__'
        read_only_fields = ['review_date']


class ChargingSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChargingSpecification
        fields = '__all__'


class EVComparisonSerializer(serializers.ModelSerializer):
    cars = ElectricCarSerializer(many=True, read_only=True)
    car_ids = serializers.PrimaryKeyRelatedField(
        queryset=ElectricCar.objects.all(),
        source='cars',
        many=True,
        write_only=True
    )
    
    class Meta:
        model = EVComparison
        fields = '__all__'
        read_only_fields = ['created_at']