# Exam Orchestrator Backend

Python Flask backend for the Exam Orchestrator application - an intelligent exam scheduling system.

## Features

- **Exam Management**: Create, update, delete, and list exams
- **Automatic Scheduling**: Intelligent algorithm to schedule exams based on preferences and constraints
- **Department Management**: Organize exams by departments
- **Room Management**: Manage classrooms and computer labs
- **Excel Export**: Export exam schedules to Excel files
- **Settings Management**: Configure exam week dates and other settings
- **RESTful API**: Clean REST API for frontend integration

## Technology Stack

- **Framework**: Flask 3.0.0
- **Database**: MySQL with SQLAlchemy ORM
- **Serialization**: Marshmallow
- **Excel Export**: openpyxl, pandas
- **CORS**: Flask-CORS for frontend integration

## Installation

### Prerequisites

- Python 3.8+
- MySQL 5.7+ or MySQL 8.0+
- pip (Python package manager)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd exam-orchestrator-planner/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Copy example environment file
   cp .env.example .env
   
   # Edit .env file with your database credentials
   ```

5. **Setup MySQL database**
   ```sql
   CREATE DATABASE exam_orchestrator CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'exam_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON exam_orchestrator.* TO 'exam_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

6. **Initialize database**
   ```bash
   python setup_database.py init
   ```

7. **Add sample data (optional)**
   ```bash
   python setup_database.py sample
   ```

## Configuration

Edit the `.env` file with your settings:

```env
# Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=exam_user
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=exam_orchestrator

# Flask Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True

# CORS Configuration
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## Running the Application

### Development Mode

```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Production Mode

```bash
export FLASK_ENV=production
python app.py
```

## API Endpoints

### Health Check
- `GET /api/health` - Health check endpoint
- `GET /api` - API information

### Exams
- `GET /api/exams` - Get all exams
- `POST /api/exams` - Create new exam
- `GET /api/exams/{id}` - Get specific exam
- `PUT /api/exams/{id}` - Update exam
- `DELETE /api/exams/{id}` - Delete exam

### Schedule
- `GET /api/schedule` - Get exam schedule
- `POST /api/schedule/generate` - Generate automatic schedule
- `PUT /api/schedule/{id}` - Update schedule
- `DELETE /api/schedule/{id}` - Delete schedule

### Departments
- `GET /api/departments` - Get all departments
- `POST /api/departments` - Create department
- `GET /api/departments/{id}` - Get specific department
- `PUT /api/departments/{id}` - Update department
- `DELETE /api/departments/{id}` - Delete department

### Settings
- `GET /api/settings` - Get all settings
- `GET /api/settings/{key}` - Get specific setting
- `POST /api/settings` - Create/update setting
- `GET /api/settings/exam-week` - Get exam week settings
- `POST /api/settings/exam-week` - Save exam week settings

### Export
- `GET /api/export/excel` - Export all departments to Excel
- `GET /api/export/excel/{department_id}` - Export specific department
- `GET /api/export/departments-summary` - Get departments summary
- `GET /api/export/preview/{department_id}` - Preview export data

## Database Schema

### Tables

1. **departments** - Department information
2. **rooms** - Classroom and lab information
3. **exams** - Exam details and requirements
4. **exam_schedules** - Scheduled exam times and rooms
5. **settings** - Application settings

### Key Relationships

- Exams belong to departments
- Rooms can belong to departments
- Exam schedules link exams to rooms and time slots

## Scheduling Algorithm

The automatic scheduling system considers:

1. **Exam Requirements**
   - Computer lab requirement
   - Student count vs room capacity
   - Exam duration

2. **Preferences**
   - Instructor preferred dates
   - Department preferences

3. **Constraints**
   - Room availability
   - Time slot conflicts
   - Exam week date range

4. **Optimization**
   - Minimize room changes
   - Prefer department-specific rooms
   - Balance daily exam load

## Database Management

### Initialize Database
```bash
python setup_database.py init
```

### Reset Database (WARNING: Deletes all data)
```bash
python setup_database.py reset
```

### Add Sample Data
```bash
python setup_database.py sample
```

### Show Database Info
```bash
python setup_database.py info
```

## Development

### Project Structure
```
backend/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── database.py           # Database initialization
├── models.py             # SQLAlchemy models
├── requirements.txt      # Python dependencies
├── setup_database.py     # Database setup script
├── routes/               # API route handlers
│   ├── exam_routes.py
│   ├── schedule_routes.py
│   ├── department_routes.py
│   ├── settings_routes.py
│   └── export_routes.py
├── services/             # Business logic services
│   ├── scheduler_service.py
│   └── export_service.py
└── utils/                # Utility functions
    ├── date_utils.py
    └── validation.py
```

### Adding New Features

1. Create new route in `routes/` directory
2. Add business logic in `services/` directory
3. Register blueprint in `app.py`
4. Update database models if needed

## Testing

### Manual Testing
Use tools like Postman or curl to test API endpoints:

```bash
# Health check
curl http://localhost:5000/api/health

# Get all exams
curl http://localhost:5000/api/exams

# Create new exam
curl -X POST http://localhost:5000/api/exams \
  -H "Content-Type: application/json" \
  -d '{"course_name":"Test Course","class_name":"1","instructor":"Test Instructor","student_count":30,"duration":90,"department_id":1}'
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check MySQL service is running
   - Verify database credentials in `.env`
   - Ensure database exists

2. **Import Errors**
   - Activate virtual environment
   - Install all requirements: `pip install -r requirements.txt`

3. **CORS Issues**
   - Check CORS_ORIGINS in `.env`
   - Ensure frontend URL is included

4. **Permission Errors**
   - Check MySQL user permissions
   - Verify file system permissions for uploads

### Logs

The application logs important events to the console. In production, consider using a proper logging system.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
