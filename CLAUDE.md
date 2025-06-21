# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based web application for tracking 5/3/1 strength training workouts. The application follows Jim Wendler's 5/3/1 program methodology, allowing users to manage training maxes, log main lifts and accessory work, view workout history, and analyze progress.

## Commands

### Running the Application
```bash
python app.py
```

### Production Server
```bash
python -m gunicorn -w 1 app:app
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

## Architecture

### Core Components
- **app.py**: Main Flask application containing all routes and business logic
- **workout_db.py**: Database abstraction layer using SQLite, handles all database operations
- **workout.db**: SQLite database file (auto-created on first run)

### Database Schema
The application uses four main tables:
- `training_maxes`: Current training maxes for main lifts
- `training_maxes_history`: Historical record of training max changes
- `workout_history`: Complete log of all workout sets with optional duration tracking
- `exercises`: Exercise definitions with associated body parts

### Key Features
- **5/3/1 Program Implementation**: Follows standard percentage schemes (Week 1: 65/75/85%, Week 2: 70/80/90%, Week 3: 75/85/95%)
- **Main Lifts**: Squat, Bench Press, Deadlift, Press with calculated training maxes (90% of 1RM)
- **Accessory Work**: Flexible logging system with automatic body part classification
- **Multiple Sets Support**: Can log multiple sets per exercise with individual weight/rep tracking
- **Workout Duration**: Optional timer functionality for tracking workout length
- **Progress Visualization**: Plotly-based graphs showing weight and rep progression over time
- **Volume Analysis**: Weekly volume tracking by body part (measured in total sets)

### Flask Route Structure
- `/`: Home page
- `/set-training-maxes`: Manage 1RM and training maxes
- `/start-workout`: Workout selection interface
- `/perform-workout/<lift>`: Main lift logging with week-based percentages
- `/add-accessory`: Accessory exercise logging with multi-set support
- `/history`: Workout history with filtering options
- `/correct-mistake`: Edit/delete workout entries
- `/volume-history`: Weekly volume analysis by body part
- `/progress-graph`: Exercise progress visualization

### Data Flow
1. Users set training maxes based on 1RM
2. Main lift workouts use predetermined percentage calculations
3. All workout data is stored with timestamps and optional duration
4. Historical data powers progress graphs and volume analysis
5. Exercise body part mapping enables volume tracking by muscle group

## Development Guidelines

### Code Style
- Follow clean, idiomatic Python code practices
- Use clear and logical project architecture
- Maintain modular, extensible components for future scaling
- Prioritize clarity, simplicity, and maintainability over complex abstractions

### Documentation Standards
- **Module-level docstrings**: Explain purpose and context of each file
- **Function-level docstrings**: Use consistent format with Args and Returns sections
- **Type hints**: Required for all function arguments and return values
- **Block comments**: Describe key logic sections
- **Inline comments**: Only where necessary for clarity
