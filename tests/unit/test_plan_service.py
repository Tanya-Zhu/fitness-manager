"""Unit tests for PlanService."""
import pytest
from uuid import uuid4
from src.services.plan_service import PlanService
from src.api.schemas.plan_schemas import FitnessPlanCreate, ExerciseCreate
from src.api.middleware.error_handler import NotFoundException
from src.models.fitness_plan import PlanStatus


@pytest.mark.unit
class TestPlanServiceCreate:
    """Unit tests for creating plans."""

    @pytest.mark.asyncio
    async def test_create_plan_success(self, db_session):
        """Test successful plan creation."""
        service = PlanService(db_session)
        user_id = uuid4()

        plan_data = FitnessPlanCreate(
            name="Test Plan",
            description="Test description",
            exercises=[
                ExerciseCreate(name="Running", duration_minutes=30, intensity="medium"),
                ExerciseCreate(name="Push-ups", repetitions=20, intensity="high"),
            ],
        )

        plan = await service.create_plan(user_id, plan_data)

        assert plan.id is not None
        assert plan.name == "Test Plan"
        assert plan.user_id == user_id
        assert plan.status == PlanStatus.ACTIVE
        assert len(plan.exercises) == 2

    @pytest.mark.asyncio
    async def test_create_plan_with_description_none(self, db_session):
        """Test creating plan without description."""
        service = PlanService(db_session)
        user_id = uuid4()

        plan_data = FitnessPlanCreate(
            name="Minimal Plan",
            exercises=[ExerciseCreate(name="Running", duration_minutes=30)],
        )

        plan = await service.create_plan(user_id, plan_data)

        assert plan.description is None


@pytest.mark.unit
class TestPlanServiceGet:
    """Unit tests for retrieving plans."""

    @pytest.mark.asyncio
    async def test_get_plan_by_id_success(self, db_session):
        """Test getting plan by ID."""
        service = PlanService(db_session)
        user_id = uuid4()

        # Create a plan first
        plan_data = FitnessPlanCreate(
            name="Test Plan",
            exercises=[ExerciseCreate(name="Running", duration_minutes=30)],
        )
        created_plan = await service.create_plan(user_id, plan_data)

        # Retrieve it
        retrieved_plan = await service.get_plan_by_id(user_id, created_plan.id)

        assert retrieved_plan.id == created_plan.id
        assert retrieved_plan.name == "Test Plan"

    @pytest.mark.asyncio
    async def test_get_plan_by_id_not_found(self, db_session):
        """Test getting non-existent plan raises NotFoundException."""
        service = PlanService(db_session)
        user_id = uuid4()
        non_existent_id = uuid4()

        with pytest.raises(NotFoundException):
            await service.get_plan_by_id(user_id, non_existent_id)

    @pytest.mark.asyncio
    async def test_get_plan_wrong_user_not_found(self, db_session):
        """Test getting plan with wrong user ID raises NotFoundException."""
        service = PlanService(db_session)
        owner_id = uuid4()
        other_user_id = uuid4()

        # Create plan with owner
        plan_data = FitnessPlanCreate(
            name="Owner Plan", exercises=[ExerciseCreate(name="Running", duration_minutes=30)]
        )
        created_plan = await service.create_plan(owner_id, plan_data)

        # Try to retrieve with different user
        with pytest.raises(NotFoundException):
            await service.get_plan_by_id(other_user_id, created_plan.id)


@pytest.mark.unit
class TestPlanServiceList:
    """Unit tests for listing plans."""

    @pytest.mark.asyncio
    async def test_get_user_plans_pagination(self, db_session):
        """Test pagination of user plans."""
        service = PlanService(db_session)
        user_id = uuid4()

        # Create 3 plans
        for i in range(3):
            plan_data = FitnessPlanCreate(
                name=f"Plan {i}",
                exercises=[ExerciseCreate(name="Running", duration_minutes=30)],
            )
            await service.create_plan(user_id, plan_data)

        # Get first page (2 items)
        plans, total = await service.get_user_plans(user_id, page=1, page_size=2)

        assert len(plans) == 2
        assert total == 3

        # Get second page (1 item)
        plans_page2, _ = await service.get_user_plans(user_id, page=2, page_size=2)

        assert len(plans_page2) == 1


@pytest.mark.unit
class TestPlanServiceUpdate:
    """Unit tests for updating plans."""

    @pytest.mark.asyncio
    async def test_update_plan_success(self, db_session):
        """Test successful plan update."""
        service = PlanService(db_session)
        user_id = uuid4()

        # Create a plan
        plan_data = FitnessPlanCreate(
            name="Original Name",
            description="Original Description",
            exercises=[ExerciseCreate(name="Running", duration_minutes=30)],
        )
        created_plan = await service.create_plan(user_id, plan_data)

        # Update the plan
        from src.api.schemas.plan_schemas import FitnessPlanUpdate

        update_data = FitnessPlanUpdate(
            name="Updated Name", description="Updated Description"
        )
        updated_plan = await service.update_plan(user_id, created_plan.id, update_data)

        assert updated_plan.name == "Updated Name"
        assert updated_plan.description == "Updated Description"

    @pytest.mark.asyncio
    async def test_update_plan_partial(self, db_session):
        """Test partial plan update."""
        service = PlanService(db_session)
        user_id = uuid4()

        # Create a plan
        plan_data = FitnessPlanCreate(
            name="Original Name",
            description="Original Description",
            exercises=[ExerciseCreate(name="Running", duration_minutes=30)],
        )
        created_plan = await service.create_plan(user_id, plan_data)

        # Update only the name
        from src.api.schemas.plan_schemas import FitnessPlanUpdate

        update_data = FitnessPlanUpdate(name="Updated Name")
        updated_plan = await service.update_plan(user_id, created_plan.id, update_data)

        assert updated_plan.name == "Updated Name"
        assert updated_plan.description == "Original Description"  # Should remain unchanged

    @pytest.mark.asyncio
    async def test_update_plan_not_found(self, db_session):
        """Test updating non-existent plan raises NotFoundException."""
        service = PlanService(db_session)
        user_id = uuid4()
        non_existent_id = uuid4()

        from src.api.schemas.plan_schemas import FitnessPlanUpdate

        update_data = FitnessPlanUpdate(name="Updated Name")

        with pytest.raises(NotFoundException):
            await service.update_plan(user_id, non_existent_id, update_data)


@pytest.mark.unit
class TestPlanServiceDelete:
    """Unit tests for deleting plans."""

    @pytest.mark.asyncio
    async def test_delete_plan_success(self, db_session):
        """Test successful plan deletion."""
        service = PlanService(db_session)
        user_id = uuid4()

        # Create a plan
        plan_data = FitnessPlanCreate(
            name="Test Plan",
            exercises=[ExerciseCreate(name="Running", duration_minutes=30)],
        )
        created_plan = await service.create_plan(user_id, plan_data)

        plan_id = created_plan.id

        # Delete the plan
        await service.delete_plan(user_id, plan_id)

        # Verify plan is soft deleted
        with pytest.raises(NotFoundException):
            await service.get_plan_by_id(user_id, plan_id)

    @pytest.mark.asyncio
    async def test_delete_plan_not_found(self, db_session):
        """Test deleting non-existent plan raises NotFoundException."""
        service = PlanService(db_session)
        user_id = uuid4()
        non_existent_id = uuid4()

        with pytest.raises(NotFoundException):
            await service.delete_plan(user_id, non_existent_id)
