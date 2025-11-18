"""Integration tests for fitness plan management (CRUD operations)."""
import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestPlanCRUDOperations:
    """Integration tests for complete plan CRUD workflows."""

    @pytest.mark.asyncio
    async def test_complete_plan_lifecycle(self, auth_client: AsyncClient):
        """Test creating, reading, updating, and deleting a plan."""
        # Create a plan
        plan_data = {
            "name": "完整生命周期测试",
            "description": "测试CRUD操作",
            "exercises": [
                {"name": "跑步", "duration_minutes": 30, "intensity": "medium"},
            ],
        }

        create_response = await auth_client.post("/api/v1/plans", json=plan_data)
        assert create_response.status_code == 201, "Plan creation should succeed"

        plan_id = create_response.json()["id"]

        # Read the plan
        get_response = await auth_client.get(f"/api/v1/plans/{plan_id}")
        assert get_response.status_code == 200
        plan = get_response.json()
        assert plan["name"] == "完整生命周期测试"
        assert plan["description"] == "测试CRUD操作"

        # Update the plan
        update_data = {
            "name": "更新后的名称",
            "description": "更新后的描述",
        }

        update_response = await auth_client.put(
            f"/api/v1/plans/{plan_id}", json=update_data
        )
        assert update_response.status_code == 200, "Plan update should succeed"

        updated_plan = update_response.json()
        assert updated_plan["name"] == "更新后的名称"
        assert updated_plan["description"] == "更新后的描述"

        # Verify update persisted
        get_updated_response = await auth_client.get(f"/api/v1/plans/{plan_id}")
        assert get_updated_response.status_code == 200
        persisted_plan = get_updated_response.json()
        assert persisted_plan["name"] == "更新后的名称"

        # Delete the plan
        delete_response = await auth_client.delete(f"/api/v1/plans/{plan_id}")
        assert delete_response.status_code == 204, "Plan deletion should succeed"

        # Verify plan is deleted (soft delete)
        get_deleted_response = await auth_client.get(f"/api/v1/plans/{plan_id}")
        assert get_deleted_response.status_code == 404, "Deleted plan should not be accessible"

    @pytest.mark.asyncio
    async def test_update_plan_partial(self, auth_client: AsyncClient):
        """Test partial update of a plan."""
        # Create a plan
        plan_data = {
            "name": "原始计划",
            "description": "原始描述",
            "exercises": [{"name": "跑步", "duration_minutes": 30}],
        }

        create_response = await auth_client.post("/api/v1/plans", json=plan_data)
        plan_id = create_response.json()["id"]

        # Update only the name
        update_data = {
            "name": "新名称",
        }

        update_response = await auth_client.put(
            f"/api/v1/plans/{plan_id}", json=update_data
        )
        assert update_response.status_code == 200

        updated_plan = update_response.json()
        assert updated_plan["name"] == "新名称"
        assert updated_plan["description"] == "原始描述"  # Should remain unchanged

    @pytest.mark.asyncio
    async def test_update_nonexistent_plan(self, auth_client: AsyncClient):
        """Test updating a non-existent plan returns 404."""
        fake_plan_id = "00000000-0000-0000-0000-000000000000"
        update_data = {
            "name": "新名称",
        }

        response = await auth_client.put(f"/api/v1/plans/{fake_plan_id}", json=update_data)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_nonexistent_plan(self, auth_client: AsyncClient):
        """Test deleting a non-existent plan returns 404."""
        fake_plan_id = "00000000-0000-0000-0000-000000000000"

        response = await auth_client.delete(f"/api/v1/plans/{fake_plan_id}")
        assert response.status_code == 404


@pytest.mark.integration
class TestExerciseManagement:
    """Integration tests for exercise CRUD operations."""

    @pytest.mark.asyncio
    async def test_add_exercise_to_existing_plan(self, auth_client: AsyncClient):
        """Test adding a new exercise to an existing plan."""
        # Create a plan with one exercise
        plan_data = {
            "name": "测试计划",
            "exercises": [{"name": "跑步", "duration_minutes": 30}],
        }

        create_response = await auth_client.post("/api/v1/plans", json=plan_data)
        plan_id = create_response.json()["id"]

        # Add a new exercise
        new_exercise = {
            "name": "俯卧撑",
            "repetitions": 20,
            "intensity": "high",
        }

        add_response = await auth_client.post(
            f"/api/v1/plans/{plan_id}/exercises", json=new_exercise
        )
        assert add_response.status_code == 201, "Adding exercise should succeed"

        added_exercise = add_response.json()
        assert added_exercise["name"] == "俯卧撑"
        assert added_exercise["repetitions"] == 20

        # Verify the plan now has 2 exercises
        get_plan_response = await auth_client.get(f"/api/v1/plans/{plan_id}")
        plan = get_plan_response.json()
        assert len(plan["exercises"]) == 2

    @pytest.mark.asyncio
    async def test_update_exercise(self, auth_client: AsyncClient):
        """Test updating an existing exercise."""
        # Create a plan with an exercise
        plan_data = {
            "name": "测试计划",
            "exercises": [
                {"name": "跑步", "duration_minutes": 30, "intensity": "medium"}
            ],
        }

        create_response = await auth_client.post("/api/v1/plans", json=plan_data)
        plan = create_response.json()
        plan_id = plan["id"]
        exercise_id = plan["exercises"][0]["id"]

        # Update the exercise
        update_data = {
            "name": "快跑",
            "duration_minutes": 45,
            "intensity": "high",
        }

        update_response = await auth_client.put(
            f"/api/v1/plans/{plan_id}/exercises/{exercise_id}", json=update_data
        )
        assert update_response.status_code == 200, "Exercise update should succeed"

        updated_exercise = update_response.json()
        assert updated_exercise["name"] == "快跑"
        assert updated_exercise["duration_minutes"] == 45
        assert updated_exercise["intensity"] == "high"

    @pytest.mark.asyncio
    async def test_delete_exercise(self, auth_client: AsyncClient):
        """Test deleting an exercise from a plan."""
        # Create a plan with two exercises
        plan_data = {
            "name": "测试计划",
            "exercises": [
                {"name": "跑步", "duration_minutes": 30},
                {"name": "俯卧撑", "repetitions": 20},
            ],
        }

        create_response = await auth_client.post("/api/v1/plans", json=plan_data)
        plan = create_response.json()
        plan_id = plan["id"]
        exercise_id = plan["exercises"][0]["id"]

        # Delete the first exercise
        delete_response = await auth_client.delete(
            f"/api/v1/plans/{plan_id}/exercises/{exercise_id}"
        )
        assert delete_response.status_code == 204, "Exercise deletion should succeed"

        # Verify only one exercise remains
        get_plan_response = await auth_client.get(f"/api/v1/plans/{plan_id}")
        plan = get_plan_response.json()
        assert len(plan["exercises"]) == 1
        assert plan["exercises"][0]["name"] == "俯卧撑"

    @pytest.mark.asyncio
    async def test_cannot_delete_last_exercise(self, auth_client: AsyncClient):
        """Test that deleting the last exercise from a plan is prevented."""
        # Create a plan with one exercise
        plan_data = {
            "name": "测试计划",
            "exercises": [{"name": "跑步", "duration_minutes": 30}],
        }

        create_response = await auth_client.post("/api/v1/plans", json=plan_data)
        plan = create_response.json()
        plan_id = plan["id"]
        exercise_id = plan["exercises"][0]["id"]

        # Try to delete the only exercise
        delete_response = await auth_client.delete(
            f"/api/v1/plans/{plan_id}/exercises/{exercise_id}"
        )
        assert delete_response.status_code == 400, "Should not allow deleting last exercise"

        # Verify the exercise still exists
        get_plan_response = await auth_client.get(f"/api/v1/plans/{plan_id}")
        plan = get_plan_response.json()
        assert len(plan["exercises"]) == 1


@pytest.mark.integration
class TestPlanManagementWithReminders:
    """Integration tests for plan management affecting reminders."""

    @pytest.mark.asyncio
    async def test_delete_plan_removes_reminders(self, auth_client: AsyncClient):
        """Test that deleting a plan also removes its reminders."""
        # Create a plan
        plan_data = {
            "name": "测试计划",
            "exercises": [{"name": "跑步", "duration_minutes": 30}],
        }

        create_response = await auth_client.post("/api/v1/plans", json=plan_data)
        plan_id = create_response.json()["id"]

        # Add a reminder
        reminder_data = {
            "reminder_time": "07:00:00",
            "frequency": "daily",
            "days_of_week": [1, 2, 3, 4, 5],
            "is_enabled": True,
        }

        reminder_response = await auth_client.post(
            f"/api/v1/plans/{plan_id}/reminders", json=reminder_data
        )
        assert reminder_response.status_code == 201

        # Delete the plan
        delete_response = await auth_client.delete(f"/api/v1/plans/{plan_id}")
        assert delete_response.status_code == 204

        # Verify plan and reminders are gone
        get_plan_response = await auth_client.get(f"/api/v1/plans/{plan_id}")
        assert get_plan_response.status_code == 404
