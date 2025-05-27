// API client for Exam Orchestrator backend

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

interface ApiResponse<T> {
  success: boolean;
  message: string;
  data?: T;
}

interface Exam {
  id?: number;
  course_id: number;
  course_name?: string; // Computed from course
  class_name?: string; // Computed from course
  credits?: number; // Computed from course
  instructor: string;
  student_count: number;
  duration: number;
  needs_computer: boolean;
  preferred_dates: string[];
  department_id: number;
  status?: string;
  created_at?: string;
  updated_at?: string;
  department?: Department;
  course?: Course;
  exam_schedules?: ExamSchedule[];
}

interface Course {
  id: number;
  name: string;
  code: string;
  credits: number;
  class_level: number;
  department_id: number;
  is_active: boolean;
  department?: Department;
}

interface Department {
  id: number;
  name: string;
  code: string;
  created_at?: string;
}

interface Room {
  id: number;
  name: string;
  capacity: number;
  has_computer: boolean;
  department_id?: number;
  is_active: boolean;
  department?: Department;
}

interface ExamSchedule {
  id: number;
  exam_id: number;
  room_id: number;
  scheduled_date: string;
  start_time: string;
  end_time: string;
  exam?: Exam;
  room?: Room;
}

interface ExamWeekSettings {
  start_date: string;
  end_date: string;
}

interface ScheduleDay {
  date: string;
  timeSlots: ExamSchedule[];
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;

    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
      },
    };

    const config = { ...defaultOptions, ...options };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || `HTTP error! status: ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Health check
  async healthCheck(): Promise<ApiResponse<any>> {
    return this.request('/api/health');
  }

  // Exams API
  async getExams(): Promise<ApiResponse<Exam[]>> {
    return this.request('/api/exams');
  }

  async createExam(exam: Omit<Exam, 'id'>): Promise<ApiResponse<Exam>> {
    return this.request('/api/exams', {
      method: 'POST',
      body: JSON.stringify(exam),
    });
  }

  async getExam(id: number): Promise<ApiResponse<Exam>> {
    return this.request(`/api/exams/${id}`);
  }

  async updateExam(id: number, exam: Partial<Exam>): Promise<ApiResponse<Exam>> {
    return this.request(`/api/exams/${id}`, {
      method: 'PUT',
      body: JSON.stringify(exam),
    });
  }

  async deleteExam(id: number): Promise<ApiResponse<any>> {
    return this.request(`/api/exams/${id}`, {
      method: 'DELETE',
    });
  }

  // Schedule API
  async getSchedule(params?: {
    start_date?: string;
    end_date?: string;
    department_id?: number;
  }): Promise<ApiResponse<ScheduleDay[]>> {
    const queryParams = new URLSearchParams();
    if (params?.start_date) queryParams.append('start_date', params.start_date);
    if (params?.end_date) queryParams.append('end_date', params.end_date);
    if (params?.department_id) queryParams.append('department_id', params.department_id.toString());

    const endpoint = `/api/schedule${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.request(endpoint);
  }

  async generateSchedule(params?: {
    force_regenerate?: boolean;
    department_id?: number;
  }): Promise<ApiResponse<{
    scheduled_count: number;
    failed_count: number;
    failed_exams: any[];
  }>> {
    return this.request('/api/schedule/generate', {
      method: 'POST',
      body: JSON.stringify(params || {}),
    });
  }

  async updateSchedule(id: number, schedule: Partial<ExamSchedule>): Promise<ApiResponse<ExamSchedule>> {
    return this.request(`/api/schedule/${id}`, {
      method: 'PUT',
      body: JSON.stringify(schedule),
    });
  }

  async deleteSchedule(id: number): Promise<ApiResponse<any>> {
    return this.request(`/api/schedule/${id}`, {
      method: 'DELETE',
    });
  }

  // Courses API
  async getCourses(params?: {
    department_id?: number;
    class_level?: number;
  }): Promise<ApiResponse<Course[]>> {
    const queryParams = new URLSearchParams();
    if (params?.department_id) queryParams.append('department_id', params.department_id.toString());
    if (params?.class_level) queryParams.append('class_level', params.class_level.toString());

    const endpoint = `/api/courses${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.request(endpoint);
  }

  async getCoursesByDepartment(departmentId: number, classLevel?: number): Promise<ApiResponse<Course[]>> {
    const queryParams = new URLSearchParams();
    if (classLevel) queryParams.append('class_level', classLevel.toString());

    const endpoint = `/api/courses/by-department/${departmentId}${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.request(endpoint);
  }

  async createCourse(course: Omit<Course, 'id'>): Promise<ApiResponse<Course>> {
    return this.request('/api/courses', {
      method: 'POST',
      body: JSON.stringify(course),
    });
  }

  async getCourse(id: number): Promise<ApiResponse<Course>> {
    return this.request(`/api/courses/${id}`);
  }

  async updateCourse(id: number, course: Partial<Course>): Promise<ApiResponse<Course>> {
    return this.request(`/api/courses/${id}`, {
      method: 'PUT',
      body: JSON.stringify(course),
    });
  }

  async deleteCourse(id: number): Promise<ApiResponse<any>> {
    return this.request(`/api/courses/${id}`, {
      method: 'DELETE',
    });
  }

  // Departments API
  async getDepartments(): Promise<ApiResponse<Department[]>> {
    return this.request('/api/departments');
  }

  async createDepartment(department: Omit<Department, 'id'>): Promise<ApiResponse<Department>> {
    return this.request('/api/departments', {
      method: 'POST',
      body: JSON.stringify(department),
    });
  }

  async getDepartment(id: number): Promise<ApiResponse<Department>> {
    return this.request(`/api/departments/${id}`);
  }

  async updateDepartment(id: number, department: Partial<Department>): Promise<ApiResponse<Department>> {
    return this.request(`/api/departments/${id}`, {
      method: 'PUT',
      body: JSON.stringify(department),
    });
  }

  async deleteDepartment(id: number): Promise<ApiResponse<any>> {
    return this.request(`/api/departments/${id}`, {
      method: 'DELETE',
    });
  }

  // Settings API
  async getExamWeekSettings(): Promise<ApiResponse<ExamWeekSettings>> {
    return this.request('/api/settings/exam-week');
  }

  async saveExamWeekSettings(settings: ExamWeekSettings): Promise<ApiResponse<ExamWeekSettings>> {
    return this.request('/api/settings/exam-week', {
      method: 'POST',
      body: JSON.stringify(settings),
    });
  }

  async getSetting(key: string): Promise<ApiResponse<any>> {
    return this.request(`/api/settings/${key}`);
  }

  async saveSetting(key: string, value: string): Promise<ApiResponse<any>> {
    return this.request('/api/settings', {
      method: 'POST',
      body: JSON.stringify({ key, value }),
    });
  }

  // Export API
  async exportAllDepartments(params?: {
    start_date?: string;
    end_date?: string;
  }): Promise<Blob> {
    const queryParams = new URLSearchParams();
    if (params?.start_date) queryParams.append('start_date', params.start_date);
    if (params?.end_date) queryParams.append('end_date', params.end_date);

    const endpoint = `/api/export/excel${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await fetch(`${this.baseUrl}${endpoint}`);

    if (!response.ok) {
      throw new Error(`Export failed: ${response.statusText}`);
    }

    return response.blob();
  }

  async exportDepartment(departmentId: number, params?: {
    start_date?: string;
    end_date?: string;
  }): Promise<Blob> {
    const queryParams = new URLSearchParams();
    if (params?.start_date) queryParams.append('start_date', params.start_date);
    if (params?.end_date) queryParams.append('end_date', params.end_date);

    const endpoint = `/api/export/excel/${departmentId}${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await fetch(`${this.baseUrl}${endpoint}`);

    if (!response.ok) {
      throw new Error(`Export failed: ${response.statusText}`);
    }

    return response.blob();
  }

  async getDepartmentsSummary(): Promise<ApiResponse<{
    id: number;
    name: string;
    code: string;
    exam_count: number;
    last_update: string;
  }[]>> {
    return this.request('/api/export/departments-summary');
  }

  async previewDepartmentExport(departmentId: number, params?: {
    start_date?: string;
    end_date?: string;
  }): Promise<ApiResponse<any>> {
    const queryParams = new URLSearchParams();
    if (params?.start_date) queryParams.append('start_date', params.start_date);
    if (params?.end_date) queryParams.append('end_date', params.end_date);

    const endpoint = `/api/export/preview/${departmentId}${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.request(endpoint);
  }
}

// Create and export API client instance
export const apiClient = new ApiClient();

// Export types
export type {
    ApiResponse, Course, Department, Exam, ExamSchedule,
    ExamWeekSettings, Room, ScheduleDay
};

// Utility function to download blob as file
export const downloadBlob = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};
