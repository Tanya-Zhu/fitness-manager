/**
 * API调用封装
 */

const API_BASE_URL = window.location.origin;

class API {
    /**
     * 发送HTTP请求
     */
    static async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`;
        const token = localStorage.getItem('access_token');

        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        // 添加认证token
        if (token && !options.skipAuth) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers,
            });

            // 处理401未授权
            if (response.status === 401) {
                localStorage.removeItem('access_token');
                window.location.href = '/login.html';
                return;
            }

            // 处理204 No Content
            if (response.status === 204) {
                return { success: true };
            }

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '请求失败');
            }

            return data;
        } catch (error) {
            console.error('API请求错误:', error);
            throw error;
        }
    }

    // ========== 认证相关 ==========

    static async register(email, password, fullName) {
        return this.request('/api/v1/auth/register', {
            method: 'POST',
            body: JSON.stringify({
                email,
                password,
                full_name: fullName,
            }),
            skipAuth: true,
        });
    }

    static async login(email, password) {
        return this.request('/api/v1/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password }),
            skipAuth: true,
        });
    }

    static async getCurrentUser() {
        return this.request('/api/v1/auth/me');
    }

    // ========== 健身计划相关 ==========

    static async getPlans(page = 1, pageSize = 20, status = null) {
        let url = `/api/v1/plans/?page=${page}&page_size=${pageSize}`;
        if (status) {
            url += `&status=${status}`;
        }
        return this.request(url);
    }

    static async getPlanDetail(planId) {
        return this.request(`/api/v1/plans/${planId}`);
    }

    static async createPlan(planData) {
        return this.request('/api/v1/plans/', {
            method: 'POST',
            body: JSON.stringify(planData),
        });
    }

    static async updatePlan(planId, planData) {
        return this.request(`/api/v1/plans/${planId}`, {
            method: 'PUT',
            body: JSON.stringify(planData),
        });
    }

    static async deletePlan(planId) {
        return this.request(`/api/v1/plans/${planId}`, {
            method: 'DELETE',
        });
    }

    // ========== 锻炼项目相关 ==========

    static async addExercise(planId, exerciseData) {
        return this.request(`/api/v1/plans/${planId}/exercises/`, {
            method: 'POST',
            body: JSON.stringify(exerciseData),
        });
    }

    static async updateExercise(planId, exerciseId, exerciseData) {
        return this.request(`/api/v1/plans/${planId}/exercises/${exerciseId}`, {
            method: 'PUT',
            body: JSON.stringify(exerciseData),
        });
    }

    static async deleteExercise(planId, exerciseId) {
        return this.request(`/api/v1/plans/${planId}/exercises/${exerciseId}`, {
            method: 'DELETE',
        });
    }

    // ========== 提醒相关 ==========

    static async createReminder(planId, reminderData) {
        return this.request(`/api/v1/plans/${planId}/reminders/`, {
            method: 'POST',
            body: JSON.stringify(reminderData),
        });
    }

    static async updateReminder(planId, reminderId, reminderData) {
        return this.request(`/api/v1/plans/${planId}/reminders/${reminderId}`, {
            method: 'PUT',
            body: JSON.stringify(reminderData),
        });
    }

    static async deleteReminder(planId, reminderId) {
        return this.request(`/api/v1/plans/${planId}/reminders/${reminderId}`, {
            method: 'DELETE',
        });
    }

    // ========== 日历导出相关 ==========

    static async exportPlanCalendar(planId) {
        const url = `${API_BASE_URL}/api/v1/plans/${planId}/export/calendar`;
        const token = localStorage.getItem('access_token');

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (!response.ok) {
            throw new Error('导出日历失败');
        }

        // 获取文件名
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'fitness_plan.ics';
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
            if (filenameMatch) {
                filename = filenameMatch[1];
            }
        }

        // 下载文件
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(downloadUrl);
        document.body.removeChild(a);
    }

    // ========== 运动记录相关 ==========

    static async getWorkoutLogs(page = 1, pageSize = 20, startDate = null, endDate = null) {
        let url = `/api/v1/workout-logs/?page=${page}&page_size=${pageSize}`;
        if (startDate) {
            url += `&start_date=${startDate}`;
        }
        if (endDate) {
            url += `&end_date=${endDate}`;
        }
        return this.request(url);
    }

    static async getWorkoutLog(workoutLogId) {
        return this.request(`/api/v1/workout-logs/${workoutLogId}`);
    }

    static async createWorkoutLog(workoutData) {
        return this.request('/api/v1/workout-logs/', {
            method: 'POST',
            body: JSON.stringify(workoutData),
        });
    }

    static async updateWorkoutLog(workoutLogId, workoutData) {
        return this.request(`/api/v1/workout-logs/${workoutLogId}`, {
            method: 'PUT',
            body: JSON.stringify(workoutData),
        });
    }

    static async deleteWorkoutLog(workoutLogId) {
        return this.request(`/api/v1/workout-logs/${workoutLogId}`, {
            method: 'DELETE',
        });
    }

    static async getWorkoutChartData(periodType = 'week', limit = 12) {
        return this.request(`/api/v1/workout-logs/chart-data?period_type=${periodType}&limit=${limit}`);
    }

    // ========== 健身房器械训练相关 ==========

    static async getGymExercises(page = 1, pageSize = 20, startDate = null, endDate = null) {
        let url = `/api/v1/gym-exercises/?page=${page}&page_size=${pageSize}`;
        if (startDate) {
            url += `&start_date=${startDate}`;
        }
        if (endDate) {
            url += `&end_date=${endDate}`;
        }
        return this.request(url);
    }

    static async getGymExercise(exerciseId) {
        return this.request(`/api/v1/gym-exercises/${exerciseId}`);
    }

    static async createGymExercise(exerciseData) {
        return this.request('/api/v1/gym-exercises/', {
            method: 'POST',
            body: JSON.stringify(exerciseData),
        });
    }

    static async updateGymExercise(exerciseId, exerciseData) {
        return this.request(`/api/v1/gym-exercises/${exerciseId}`, {
            method: 'PUT',
            body: JSON.stringify(exerciseData),
        });
    }

    static async deleteGymExercise(exerciseId) {
        return this.request(`/api/v1/gym-exercises/${exerciseId}`, {
            method: 'DELETE',
        });
    }

    static async getExerciseTrends(exerciseName) {
        return this.request(`/api/v1/gym-exercises/trends/${encodeURIComponent(exerciseName)}`);
    }

    static async getExerciseNames() {
        return this.request('/api/v1/gym-exercises/stats/exercise-names');
    }

    // ========== 计划执行记录相关 ==========

    static async getPlanExecutions(page = 1, pageSize = 20, planId = null, startDate = null, endDate = null) {
        let url = `/api/v1/plan-executions/?page=${page}&page_size=${pageSize}`;
        if (planId) {
            url += `&plan_id=${planId}`;
        }
        if (startDate) {
            url += `&start_date=${startDate}`;
        }
        if (endDate) {
            url += `&end_date=${endDate}`;
        }
        return this.request(url);
    }

    static async getPlanExecution(executionId) {
        return this.request(`/api/v1/plan-executions/${executionId}`);
    }

    static async createPlanExecution(executionData) {
        return this.request('/api/v1/plan-executions/', {
            method: 'POST',
            body: JSON.stringify(executionData),
        });
    }

    static async updatePlanExecution(executionId, executionData) {
        return this.request(`/api/v1/plan-executions/${executionId}`, {
            method: 'PUT',
            body: JSON.stringify(executionData),
        });
    }

    static async deletePlanExecution(executionId) {
        return this.request(`/api/v1/plan-executions/${executionId}`, {
            method: 'DELETE',
        });
    }

    // ========== 计划成员和排行榜相关 ==========

    static async invitePlanMember(planId, userEmail) {
        return this.request(`/api/v1/plans/${planId}/members`, {
            method: 'POST',
            body: JSON.stringify({ user_email: userEmail }),
        });
    }

    static async getPlanMembers(planId) {
        return this.request(`/api/v1/plans/${planId}/members`);
    }

    static async getPlanLeaderboard(planId) {
        return this.request(`/api/v1/plans/${planId}/leaderboard`);
    }

    static async removePlanMember(planId, userId) {
        return this.request(`/api/v1/plans/${planId}/members/${userId}`, {
            method: 'DELETE',
        });
    }
}

/**
 * 认证工具类
 */
class Auth {
    static isLoggedIn() {
        return !!localStorage.getItem('access_token');
    }

    static login(token) {
        localStorage.setItem('access_token', token);
    }

    static logout() {
        localStorage.removeItem('access_token');
        window.location.href = '/login.html';
    }

    static requireAuth() {
        if (!this.isLoggedIn()) {
            window.location.href = '/login.html';
            return false;
        }
        return true;
    }
}

/**
 * UI工具类
 */
class UI {
    static showError(message, containerId = 'error-container') {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
                    <span class="block sm:inline">${message}</span>
                </div>
            `;
            setTimeout(() => {
                container.innerHTML = '';
            }, 5000);
        }
    }

    static showSuccess(message, containerId = 'success-container') {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative mb-4" role="alert">
                    <span class="block sm:inline">${message}</span>
                </div>
            `;
            setTimeout(() => {
                container.innerHTML = '';
            }, 3000);
        }
    }

    static showLoading(show = true, containerId = 'loading-container') {
        const container = document.getElementById(containerId);
        if (container) {
            container.style.display = show ? 'block' : 'none';
        }
    }
}
