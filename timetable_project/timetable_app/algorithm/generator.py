
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from ..models import Course, TimeSlot, Constraint, Timetable, TimetableEntry

class TimetableGenerator:
    def __init__(self, user_id):
        self.user_id = user_id
        self.courses = Course.objects.filter(user_id=user_id)
        self.constraints = Constraint.objects.filter(user_id=user_id)
    
    def _check_conflicts(self, timeslot1, timeslot2):
        """Check if two timeslots conflict with each other."""
        if timeslot1.day_of_week != timeslot2.day_of_week:
            return False
        
        # Convert to datetime for easier comparison
        t1_start = datetime.combine(datetime.today(), timeslot1.start_time)
        t1_end = datetime.combine(datetime.today(), timeslot1.end_time)
        t2_start = datetime.combine(datetime.today(), timeslot2.start_time)
        t2_end = datetime.combine(datetime.today(), timeslot2.end_time)
        
        # Check for overlap
        return (t1_start < t2_end) and (t1_end > t2_start)
    
    def _violates_constraints(self, timeslot):
        """Check if a timeslot violates any hard constraints."""
        for constraint in self.constraints:
            if constraint.constraint_type != 'required':
                continue
            
            if constraint.day_of_week == timeslot.day_of_week:
                # Convert to datetime for easier comparison
                c_start = datetime.combine(datetime.today(), constraint.start_time)
                c_end = datetime.combine(datetime.today(), constraint.end_time)
                t_start = datetime.combine(datetime.today(), timeslot.start_time)
                t_end = datetime.combine(datetime.today(), timeslot.end_time)
                
                # Check for overlap
                if (t_start < c_end) and (t_end > c_start):
                    return True
        
        return False
    
    def _evaluate_solution(self, solution):
        """Score a solution based on soft constraints."""
        score = 0
        
        # Check preferred times
        preferred_constraints = [c for c in self.constraints if c.constraint_type == 'preferred']
        for timeslot in solution:
            for constraint in preferred_constraints:
                if constraint.day_of_week == timeslot.day_of_week:
                    c_start = datetime.combine(datetime.today(), constraint.start_time)
                    c_end = datetime.combine(datetime.today(), constraint.end_time)
                    t_start = datetime.combine(datetime.today(), timeslot.start_time)
                    t_end = datetime.combine(datetime.today(), timeslot.end_time)
                    
                    if (t_start >= c_start) and (t_end <= c_end):
                        priority_score = {'low': 1, 'medium': 2, 'high': 3}
                        score += priority_score.get(constraint.priority, 1)
        
        # Check avoid times
        avoid_constraints = [c for c in self.constraints if c.constraint_type == 'avoid']
        for timeslot in solution:
            for constraint in avoid_constraints:
                if constraint.day_of_week == timeslot.day_of_week:
                    c_start = datetime.combine(datetime.today(), constraint.start_time)
                    c_end = datetime.combine(datetime.today(), constraint.end_time)
                    t_start = datetime.combine(datetime.today(), timeslot.start_time)
                    t_end = datetime.combine(datetime.today(), timeslot.end_time)
                    
                    if (t_start < c_end) and (t_end > c_start):
                        priority_score = {'low': 1, 'medium': 2, 'high': 3}
                        score -= priority_score.get(constraint.priority, 1)
        
        return score
    
    def _backtrack(self, course_index, current_solution, all_solutions):
        """Recursive backtracking algorithm to find valid timetables."""
        if course_index >= len(self.courses):
            all_solutions.append(list(current_solution))
            return
        
        course = self.courses[course_index]
        timeslots = TimeSlot.objects.filter(course=course)
        
        for timeslot in timeslots:
            # Check if this timeslot conflicts with any already selected ones
            conflict = False
            for selected_slot in current_solution:
                if self._check_conflicts(timeslot, selected_slot):
                    conflict = True
                    break
            
            # Check if this timeslot violates any hard constraints
            if conflict or self._violates_constraints(timeslot):
                continue
            
            # Add this timeslot to the solution and continue
            current_solution.append(timeslot)
            self._backtrack(course_index + 1, current_solution, all_solutions)
            current_solution.pop()  # Backtrack
    
    def generate_timetables(self, max_solutions=5):
        """Generate up to max_solutions timetables."""
        all_solutions = []
        self._backtrack(0, [], all_solutions)
        
        # Score and sort solutions
        scored_solutions = []
        for solution in all_solutions:
            score = self._evaluate_solution(solution)
            scored_solutions.append((score, solution))
        
        scored_solutions.sort(reverse=True)  # Higher scores first
        
        # Return the top N solutions
        return [solution for score, solution in scored_solutions[:max_solutions]]
    
    def create_timetable(self, name, solution):
        """Create a new Timetable with the given solution."""
        timetable = Timetable.objects.create(
            user_id=self.user_id,
            name=name
        )
        
        for timeslot in solution:
            TimetableEntry.objects.create(
                timetable=timetable,
                timeslot=timeslot
            )
        
        return timetable