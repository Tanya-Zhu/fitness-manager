"""Unit tests for ExerciseService."""
import pytest
from uuid import uuid4
from src.services.exercise_service import ExerciseService
from src.services.plan_service import PlanService
from src.api.schemas.plan_schemas import (
    ExerciseCreate,
    ExerciseUpdate,
    FitnessPlanCreate,
)
from src.api.middleware.error_handler import NotFoundException, BusinessRuleViolationException


@pytest.mark.unit
class TestExerciseServiceAdd:
    """Unit tests for adding exercises."""

    @pytest.mark.asyncio
    async def test_add_exercise_success(self, db_session):
        """Test successfully adding an exercise to a plan."""
        plan_service = PlanService(db_session)
        exercise_service = ExerciseService(db_session)
        user_id = uuid4()

        # Create a plan
        plan_data = FitnessPlanCreate(
            name="Test Plan",
            exercises=[ExerciseCreate(name="Running", duration_minutes=30)],
        )
        plan = await plan_service.create_plan(user_id, plan_data)

        # Add a new exercise
        exercise_data = ExerciseCreate(
            name="Push-ups", repetitions=20, intensity="high"
        )
        exercise = await exercise_service.add_exercise(user_id, plan.id, exercise_data)

        assert exercise.id is not None
        assert exercise.name == "Push-ups"
        assert exercise.repetitions == 20
        assert exercise.intensity.value == "high"
        assert exercise.plan_id == plan.id

    @pytest.mark.asyncio
    async def test_add_exercise_plan_not_found(self, db_session):
        """Test adding exercise to non-existent plan raises NotFoundException."""
        exercise_service = ExerciseService(db_session)
        user_id = uuid4()
        non_existent_plan_id = uuid4()

        exercise_data = ExerciseCreate(name="Running", duration_minutes=30)

        with pytest.raises(NotFoundException):
            await exercise_service.add_exercise(
                user_id, non_existent_plan_id, exercise_data
            )


@pytest.mark.unit
class TestExerciseServiceUpdate:
    """Unit tests for updating exercises."""

    @pytest.mark.asyncio
    async def test_update_exercise_success(self, db_session):
        """Test successfully updating an exercise."""
        plan_service = PlanService(db_session)
        exercise_service = ExerciseService(db_session)
        user_id = uuid4()

        # Create a plan with an exercise
        plan_data = FitnessPlanCreate(
            name="Test Plan",
            exercises=[
                ExerciseCreate(
                    name="Running", duration_minutes=30, intensity="medium"
                )
            ],
        )
        plan = await plan_service.create_plan(user_id, plan_data)
        exercise_id = plan.exercises[0].id

        # Update the exercise
        update_data = ExerciseUpdate(
            name="Fast Running", duration_minutes=45, intensity="high"
        )
        updated_exercise = await exercise_service.update_exercise(
            user_id, plan.id, exercise_id, update_data
        )

        assert updated_exercise.name == "Fast Running"
        assert updated_exercise.duration_minutes == 45
        assert updated_exercise.intensity.value == "high"

    @pytest.mark.asyncio
    async def test_update_exercise_partial(self, db_session):
        """Test partial update of an exercise."""
        plan_service = PlanService(db_session)
        exercise_service = ExerciseService(db_session)
        user_id = uuid4()

        # Create a plan with an exercise
        plan_data = FitnessPlanCreate(
            name="Test Plan",
            exercises=[
                ExerciseCreate(
                    name="Running", duration_minutes=30, intensity="medium"
                )
            ],
        )
        plan = await plan_service.create_plan(user_id, plan_data)
        exercise_id = plan.exercises[0].id

        # Update only the intensity
        update_data = ExerciseUpdate(intensity="high")
        updated_exercise = await exercise_service.update_exercise(
            user_id, plan.id, exercise_id, update_data
        )

        # Only intensity should change
        assert updated_exercise.name == "Running"
        assert updated_exercise.duration_minutes == 30
        assert updated_exercise.intensity.value == "high"

    @pytest.mark.asyncio
    async def test_update_exercise_not_found(self, db_session):
        """Test updating non-existent exercise raises NotFoundException."""
        plan_service = PlanService(db_session)
        exercise_service = ExerciseService(db_session)
        user_id = uuid4()

        # Create a plan
        plan_data = FitnessPlanCreate(
            name="Test Plan",
            exercises=[ExerciseCreate(name="Running", duration_minutes=30)],
        )
        plan = await plan_service.create_plan(user_id, plan_data)

        # Try to update non-existent exercise
        non_existent_exercise_id = uuid4()
        update_data = ExerciseUpdate(name="Updated")

        with pytest.raises(NotFoundException):
            await exercise_service.update_exercise(
                user_id, plan.id, non_existent_exercise_id, update_data
            )


@pytest.mark.unit
class TestExerciseServiceDelete:
    """Unit tests for deleting exercises."""

    @pytest.mark.asyncio
    async def test_delete_exercise_success(self, db_session):
        """Test successfully deleting an exercise."""
        plan_service = PlanService(db_session)
        exercise_service = ExerciseService(db_session)
        user_id = uuid4()

        # Create a plan with two exercises
        plan_data = FitnessPlanCreate(
            name="Test Plan",
            exercises=[
                ExerciseCreate(name="Running", duration_minutes=30),
                ExerciseCreate(name="Push-ups", repetitions=20),
            ],
        )
        plan = await plan_service.create_plan(user_id, plan_data)
        exercise_id = plan.exercises[0].id

        # Delete the first exercise
        await exercise_service.delete_exercise(user_id, plan.id, exercise_id)

        # Verify exercise is deleted
        with pytest.raises(NotFoundException):
            await exercise_service.get_exercise_by_id(user_id, plan.id, exercise_id)

    @pytest.mark.asyncio
    async def test_cannot_delete_last_exercise(self, db_session):
        """Test that deleting the last exercise raises BusinessRuleViolationException."""
        plan_service = PlanService(db_session)
        exercise_service = ExerciseService(db_session)
        user_id = uuid4()

        # Create a plan with one exercise
        plan_data = FitnessPlanCreate(
            name="Test Plan",
            exercises=[ExerciseCreate(name="Running", duration_minutes=30)],
        )
        plan = await plan_service.create_plan(user_id, plan_data)
        exercise_id = plan.exercises[0].id

        # Try to delete the only exercise
        with pytest.raises(BusinessRuleViolationException):
            await exercise_service.delete_exercise(user_id, plan.id, exercise_id)

    @pytest.mark.asyncio
    async def test_delete_exercise_not_found(self, db_session):
        """Test deleting non-existent exercise raises NotFoundException."""
        plan_service = PlanService(db_session)
        exercise_service = ExerciseService(db_session)
        user_id = uuid4()

        # Create a plan
        plan_data = FitnessPlanCreate(
            name="Test Plan",
            exercises=[ExerciseCreate(name="Running", duration_minutes=30)],
        )
        plan = await plan_service.create_plan(user_id, plan_data)

        # Try to delete non-existent exercise
        non_existent_exercise_id = uuid4()

        with pytest.raises(NotFoundException):
            await exercise_service.delete_exercise(
                user_id, plan.id, non_existent_exercise_id
            )


@pytest.mark.unit
class TestExerciseServiceGet:
    """Unit tests for getting exercises."""

    @pytest.mark.asyncio
    async def test_get_exercise_by_id_success(self, db_session):
        """Test successfully getting an exercise by ID."""
        plan_service = PlanService(db_session)
        exercise_service = ExerciseService(db_session)
        user_id = uuid4()

        # Create a plan with an exercise
        plan_data = FitnessPlanCreate(
            name="Test Plan",
            exercises=[
                ExerciseCreate(
                    name="Running", duration_minutes=30, intensity="medium"
                )
            ],
        )
        plan = await plan_service.create_plan(user_id, plan_data)
        exercise_id = plan.exercises[0].id

        # Get the exercise
        exercise = await exercise_service.get_exercise_by_id(
            user_id, plan.id, exercise_id
        )

        assert exercise.id == exercise_id
        assert exercise.name == "Running"
        assert exercise.duration_minutes == 30

    @pytest.mark.asyncio
    async def test_get_exercise_not_found(self, db_session):
        """Test getting non-existent exercise raises NotFoundException."""
        plan_service = PlanService(db_session)
        exercise_service = ExerciseService(db_session)
        user_id = uuid4()

        # Create a plan
        plan_data = FitnessPlanCreate(
            name="Test Plan",
            exercises=[ExerciseCreate(name="Running", duration_minutes=30)],
        )
        plan = await plan_service.create_plan(user_id, plan_data)

        # Try to get non-existent exercise
        non_existent_exercise_id = uuid4()

        with pytest.raises(NotFoundException):
            await exercise_service.get_exercise_by_id(
                user_id, plan.id, non_existent_exercise_id
            )
