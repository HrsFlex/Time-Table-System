
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Course, TimeSlot, Constraint, Timetable, TimetableEntry
from .serializers import (
    CourseSerializer, TimeSlotSerializer, ConstraintSerializer,
    TimetableSerializer, TimetableEntrySerializer
)
from .algorithm.generator import TimetableGenerator

class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    
    def get_queryset(self):
        return Course.objects.filter(user=self.request.user)

class TimeSlotViewSet(viewsets.ModelViewSet):
    serializer_class = TimeSlotSerializer
    
    def get_queryset(self):
        return TimeSlot.objects.filter(course__user=self.request.user)

class ConstraintViewSet(viewsets.ModelViewSet):
    serializer_class = ConstraintSerializer
    
    def get_queryset(self):
        return Constraint.objects.filter(user=self.request.user)

class TimetableViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableSerializer
    
    def get_queryset(self):
        return Timetable.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        name = request.data.get('name', 'Generated Timetable')
        max_solutions = int(request.data.get('max_solutions', 5))
        
        generator = TimetableGenerator(request.user.id)
        solutions = generator.generate_timetables(max_solutions)
        
        if not solutions:
            return Response(
                {"error": "No valid timetables could be generated with your constraints."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the first solution by default
        timetable = generator.create_timetable(name, solutions[0])
        
        # Return all generated solutions with scores
        return Response({
            "timetable_id": timetable.id,
            "message": f"Generated {len(solutions)} timetables.",
            "selected": TimetableSerializer(timetable).data
        })
    
    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        timetable = self.get_object()
        format_type = request.query_params.get('format', 'json')
        
        if format_type == 'json':
            return Response(TimetableSerializer(timetable).data)
        elif format_type == 'pdf':
            # In a real implementation, generate PDF using a library
            return Response({"message": "PDF export not implemented in this example"})
        elif format_type == 'ical':
            # In a real implementation, generate iCal using a library
            return Response({"message": "iCal export not implemented in this example"})
        else:
            return Response(
                {"error": f"Unsupported format: {format_type}"},
                status=status.HTTP_400_BAD_REQUEST
            )

class TimetableEntryViewSet(viewsets.ModelViewSet):
    serializer_class = TimetableEntrySerializer
    
    def get_queryset(self):
        return TimetableEntry.objects.filter(timetable__user=self.request.user)