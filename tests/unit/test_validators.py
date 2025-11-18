"""Unit tests for data validators."""
import pytest
from pydantic import ValidationError
from src.api.schemas.plan_schemas import FitnessPlanCreate, ExerciseCreate


@pytest.mark.unit
class TestPlanValidators:
    """Unit tests for plan validation."""

    def test_plan_name_required(self):
        """Test that plan name is required."""
        with pytest.raises(ValidationError) as exc_info:
            FitnessPlanCreate(exercises=[ExerciseCreate(name="Test", duration_minutes=30)])

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("name",) for e in errors)

    def test_plan_name_too_long(self):
        """Test that plan name cannot exceed 50 characters."""
        with pytest.raises(ValidationError) as exc_info:
            FitnessPlanCreate(
                name="A" * 51, exercises=[ExerciseCreate(name="Test", duration_minutes=30)]
            )

        errors = exc_info.value.errors()
        assert any("name" in str(e["loc"]) for e in errors)

    def test_plan_must_have_exercises(self):
        """Test that plan must have at least one exercise."""
        with pytest.raises(ValidationError) as exc_info:
            FitnessPlanCreate(name="Test Plan", exercises=[])

        errors = exc_info.value.errors()
        assert any("exercises" in str(e["loc"]) for e in errors)


@pytest.mark.unit
class TestExerciseValidators:
    """Unit tests for exercise validation."""

    def test_exercise_name_required(self):
        """Test that exercise name is required."""
        with pytest.raises(ValidationError):
            ExerciseCreate(duration_minutes=30)

    def test_exercise_needs_duration_or_reps(self):
        """Test that exercise needs either duration or repetitions."""
        with pytest.raises(ValidationError) as exc_info:
            ExerciseCreate(name="Test Exercise")

        error_msg = str(exc_info.value)
        assert "duration_minutes or repetitions" in error_msg.lower()

    def test_exercise_can_have_duration_only(self):
        """Test that exercise can have only duration."""
        exercise = ExerciseCreate(name="Running", duration_minutes=30)
        assert exercise.name == "Running"
        assert exercise.duration_minutes == 30
        assert exercise.repetitions is None

    def test_exercise_can_have_reps_only(self):
        """Test that exercise can have only repetitions."""
        exercise = ExerciseCreate(name="Push-ups", repetitions=20)
        assert exercise.name == "Push-ups"
        assert exercise.repetitions == 20
        assert exercise.duration_minutes is None

    def test_exercise_duration_must_be_positive(self):
        """Test that duration must be positive."""
        with pytest.raises(ValidationError) as exc_info:
            ExerciseCreate(name="Test", duration_minutes=0)

        errors = exc_info.value.errors()
        assert any("duration_minutes" in str(e["loc"]) for e in errors)

    def test_exercise_reps_must_be_positive(self):
        """Test that repetitions must be positive."""
        with pytest.raises(ValidationError) as exc_info:
            ExerciseCreate(name="Test", repetitions=-1)

        errors = exc_info.value.errors()
        assert any("repetitions" in str(e["loc"]) for e in errors)
