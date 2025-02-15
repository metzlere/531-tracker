# 5/3/1 Workout Tracker

The **5/3/1 Workout Tracker** is a Flask-based web application designed to help you manage and track your strength training workouts based on Jim Wendler's 5/3/1 program. It provides features to set and view training maxes, log both main and accessory workouts, view workout history, correct mistakes, analyze weekly volume by body part, and visualize progress through interactive graphs.

## Features

- **Training Max Management**  
  Set your one-rep max (1RM) for main lifts (Squat, Bench Press, Deadlift, Press) and automatically calculate your training max (90% of 1RM).  
  View a history of your training max updates.

- **Workout Logging**  
  - **Main Lifts:** Log workouts using pre-defined week-based percentage and rep schemes.
  - **Accessory Work:** Log accessory exercises with the option to add new exercises (and specify the primary body part).

- **Workout History & Corrections**  
  Review your entire workout history with filtering options and easily update or delete incorrect entries.

- **Volume History**  
  Analyze your weekly training volume broken down by body part (measured in total sets).

- **Progress Graph**  
  Visualize your progress for any exercise with interactive Plotly graphs, displaying both weight and reps over time.

## Prerequisites

- **Python 3.7+**  
- **SQLite3** (bundled with Python)

## Installation

1. **Clone the Repository:** 

```bash
git clone https://github.com/your-username/531-workout-tracker.git
cd 531-workout-tracker
```

2. **Create and Activate a Virtual Environment (optional but recommended):** 

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. **Install Dependencies:** 

```bash
pip install -r requirements.txt
```

## Running the Application

1. **Start the Flask Server.**

```bash
python app.py
```
or WSGI Server (gunicorn, could use Waitress if on Windows):
```bash
python -m gunicorn -w 1 app:app
```


2. **Access the Application:** 

Open your web browser and navigate to:  
[http://127.0.0.1:5000/](http://127.0.0.1:5000/)


## Directory Structure

```
/
├── .gitignore
├── app.py                     # Main Flask application with all routes
├── requirements.txt           # Python dependencies
├── workout.db                 # SQLite database file (auto-created)
├── workout_db.py              # Database helper class handling all DB operations
├── static/
│   └── styles.css             # Custom CSS styles for the app
└── templates/                 # HTML templates for the application
    ├── add_accessory.html
    ├── base.html
    ├── correct_mistake.html
    ├── history.html
    ├── index.html
    ├── perform_workout.html
    ├── progress_graph.html
    ├── set_training_maxes.html
    ├── start_workout.html
    ├── update_entry.html
    ├── view_training_maxes.html
    └── volume_history.html
```

## License

This project is licensed under the MIT License.

---

*Happy lifting!*
