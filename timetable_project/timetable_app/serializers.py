
from rest_framework import serializers
from .models import Course, TimeSlot, Constraint, Timetable, TimetableEntry

class TimeSlotSerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    slot_type_name = serializers.CharField(source='get_slot_type_display', read_only=True)
    
    class Meta:
        model = TimeSlot
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    time_slots = TimeSlotSerializer(many=True, read_only=True)
    
    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ('user',)
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ConstraintSerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    constraint_type_name = serializers.CharField(source='get_constraint_type_display', read_only=True)
    
    class Meta:
        model = Constraint
        fields = '__all__'
        read_only_fields = ('user',)
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class TimetableEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableEntry
        fields = '__all__'

class TimetableSerializer(serializers.ModelSerializer):
    entries = TimetableEntrySerializer(many=True, read_only=True)
    
    class Meta:
        model = Timetable
        fields = '__all__'
        read_only_fields = ('user',)
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)