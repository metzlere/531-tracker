"""
Flask application for the 5/3/1 Workout Tracker.

This module defines the routes for setting/viewing training maxes, logging workouts,
viewing history, correcting mistakes, viewing volume history, and generating progress graphs.
"""

from datetime import datetime, date, timedelta
from typing import Any, Dict, List, Optional, Tuple

import plotly.graph_objects as go
from flask import Flask, render_template, request, redirect, url_for, flash, Response

from workout_db import Database


app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Needed for flashing messages

# Instantiate the database
db: Database = Database()


@app.route("/")
def index() -> str:
    """Render the home page."""
    return render_template("index.html")


# -----------------------------------------------------------------------------


@app.route("/set-training-maxes", methods=["GET", "POST"])
def set_training_maxes() -> Response:
    """
    Set training maxes for main lifts.

    GET: Render the form for entering 1RM values.
    POST: Process the submitted form and update the training maxes.
    """
    lifts: List[str] = ["Squat", "Bench Press", "Deadlift", "Press"]

    if request.method == "POST":
        for lift in lifts:
            one_rm_str: Optional[str] = request.form.get(lift)

            if one_rm_str:
                try:
                    one_rm: float = float(one_rm_str)
                    training_max: float = one_rm * 0.9

                    db.set_training_max(lift, one_rm, training_max)

                except ValueError:
                    flash(f"Invalid input for {lift}. Please enter a number.", "error")
                    return redirect(url_for("set_training_maxes"))

        flash("Training maxes updated successfully!", "success")
        return redirect(url_for("index"))

    return render_template("set_training_maxes.html", lifts=lifts)


# -----------------------------------------------------------------------------


@app.route("/view-training-maxes")
def view_training_maxes() -> str:
    """
    View training max history for all lifts.

    Returns:
        Rendered template with training max history.
    """
    tms: List[Any] = db.get_training_max_history()
    return render_template("view_training_maxes.html", tms=tms)


# -----------------------------------------------------------------------------


@app.route("/start-workout", methods=["GET", "POST"])
def start_workout() -> Response:
    """
    Start a workout session by choosing a main lift or accessory work.

    GET: Render the workout selection form.
    POST: Redirect based on user selection.
    """
    lifts: List[str] = ["Squat", "Bench Press", "Deadlift", "Press", "Accessory"]

    if request.method == "POST":
        lift: Optional[str] = request.form.get("lift")
        if lift == "Accessory":
            return redirect(url_for("add_accessory"))
        else:
            return redirect(url_for("perform_workout", lift=lift))

    return render_template("start_workout.html", lifts=lifts)


# -----------------------------------------------------------------------------


@app.route("/perform-workout/<lift>", methods=["GET", "POST"])
def perform_workout(lift: str) -> Response:
    """
    Log a main lift workout based on the selected training max and week scheme.

    Args:
        lift (str): The name of the lift to perform.

    GET: Render the workout form.
    POST: Validate and log the workout.
    """
    tm: Optional[float] = db.get_training_max(lift)
    if tm is None:
        flash("Please set your Training Max first.", "error")
        return redirect(url_for("set_training_maxes"))

    # Define percentages and rep schemes for each week
    percentages: Dict[str, List[float]] = {
        "1": [0.65, 0.75, 0.85],
        "2": [0.70, 0.80, 0.90],
        "3": [0.75, 0.85, 0.95],
    }

    reps_schemes: Dict[str, List[str]] = {
        "1": ["5", "5", "5+"],
        "2": ["3", "3", "3+"],
        "3": ["5", "3", "1+"],
    }

    # Use the week provided in the query string (GET) or default to "1"
    selected_week: str = request.args.get("week", "1")

    if request.method == "POST":
        week: Optional[str] = request.form.get("week")

        if week not in percentages:
            flash("Invalid week selected.", "error")
            return redirect(url_for("perform_workout", lift=lift))

        # Get workout duration
        workout_duration_str: Optional[str] = request.form.get("workout_duration")
        workout_duration: Optional[int] = None
        if workout_duration_str and workout_duration_str != "0":
            try:
                workout_duration = int(workout_duration_str)
            except ValueError:
                pass

        for idx in range(3):
            reps: Optional[str] = request.form.get(f"set_{idx+1}")
            if reps is None or reps == "":
                flash("Please fill in all the set results.", "error")
                return redirect(url_for("perform_workout", lift=lift))

            weight: float = tm * percentages[week][idx]
            db.log_workout(datetime.now().date(), lift, weight, reps, workout_duration)

        flash("Workout logged successfully!", "success")
        return redirect(url_for("add_accessory"))

    return render_template(
        "perform_workout.html",
        lift=lift,
        tm=tm,
        percentages=percentages,
        reps_schemes=reps_schemes,
        selected_week=selected_week,
    )


# -----------------------------------------------------------------------------


@app.route("/add-accessory", methods=["GET", "POST"])
def add_accessory() -> Response:
    """
    Log an accessory workout session.
    GET: Render the accessory workout form along with accessory workout history.
    POST: Validate and log the accessory workout.
    """
    if request.method == "POST":
        exercise: Optional[str] = request.form.get("exercise")
        body_part: Optional[str] = request.form.get("body_part")
        total_sets_str: Optional[str] = request.form.get("total_sets")

        if not exercise:
            flash("Please provide exercise name.", "error")
            return redirect(url_for("add_accessory"))

        try:
            total_sets = int(total_sets_str) if total_sets_str else 1
            
            # Get workout duration
            workout_duration_str: Optional[str] = request.form.get("workout_duration")
            workout_duration: Optional[int] = None
            if workout_duration_str and workout_duration_str != "0":
                try:
                    workout_duration = int(workout_duration_str)
                except ValueError:
                    pass
            
            # Check if exercise exists in exercises table
            bp: Optional[str] = db.get_exercise_body_part(exercise)
            if bp is None and not body_part:
                flash("New accessory exercise. Please enter the primary body part.", "error")
                return redirect(url_for("add_accessory"))
            elif bp is None:
                db.add_exercise(exercise, body_part)

            # Process each set
            sets_logged = 0
            for set_num in range(1, total_sets + 1):
                weight_str: Optional[str] = request.form.get(f"weight_{set_num}")
                reps_str: Optional[str] = request.form.get(f"reps_{set_num}")
                
                if weight_str and reps_str:
                    try:
                        weight_val: float = float(weight_str)
                        # Only assign workout duration to the first set to avoid duplication
                        set_duration = workout_duration if set_num == 1 else None
                        db.log_workout(datetime.now().date(), exercise, weight_val, reps_str, set_duration)
                        sets_logged += 1
                    except ValueError:
                        flash(f"Invalid weight for set {set_num}. Please enter a number.", "error")
                        return redirect(url_for("add_accessory"))
                else:
                    flash(f"Please provide weight and reps for set {set_num}.", "error")
                    return redirect(url_for("add_accessory"))

            flash(f"{sets_logged} set(s) logged successfully!", "success")

        except ValueError:
            flash("Invalid data provided.", "error")

        return redirect(url_for("add_accessory"))

    # GET: Render the accessory form along with accessory workout history.
    past_exercises: List[str] = db.get_past_accessory_exercises()
    all_records: List[Any] = db.get_workout_history()
    main_lifts: Tuple[str, str, str, str] = ("Squat", "Bench Press", "Deadlift", "Press")
    accessory_history = [r for r in all_records if r[2] not in main_lifts]
    return render_template("add_accessory.html", past_exercises=past_exercises, accessory_history=accessory_history)


# -----------------------------------------------------------------------------


@app.route("/history")
def history() -> str:
    """
    Display the workout history with optional filtering by exercise type and week limit.

    Query Parameters:
        type: Filter by 'main' or 'accessory'
        limit_weeks: Number of weeks to limit the history

    Returns:
        Rendered template with workout records.
    """
    exercise_type: Optional[str] = request.args.get("type")  # 'main' or 'accessory'
    limit_weeks: Optional[int] = request.args.get("limit_weeks", type=int)

    records: List[Any] = db.get_workout_history()  # reverse to show oldest first
    main_lifts: tuple = ("Squat", "Bench Press", "Deadlift", "Press")

    if exercise_type == "main":
        records = [r for r in records if r[2] in main_lifts]
    elif exercise_type == "accessory":
        records = [r for r in records if r[2] not in main_lifts]

    if limit_weeks:
        today: date = date.today()
        start_date = today - timedelta(weeks=limit_weeks)
        records = [
            r for r in records if datetime.strptime(r[1], "%Y-%m-%d").date() >= start_date
        ]

    return render_template("history.html", records=records)


# -----------------------------------------------------------------------------


@app.route("/correct-mistake")
def correct_mistake() -> str:
    """
    Display the workout entries in reverse order to allow corrections.

    Returns:
        Rendered template with a list of workout entries.
    """
    records: List[Any] = db.get_workout_history()
    return render_template("correct_mistake.html", records=records)


# -----------------------------------------------------------------------------


@app.route("/update-entry/<int:entry_id>", methods=["GET", "POST"])
def update_entry(entry_id: int) -> Response:
    """
    Update a specific workout entry.

    Args:
        entry_id (int): The ID of the workout entry to update.

    GET: Render the update form pre-filled with entry details.
    POST: Process the form and update the entry.
    """
    if request.method == "POST":
        new_weight: Optional[str] = request.form.get("new_weight")
        new_reps: Optional[str] = request.form.get("new_reps")

        try:
            new_weight_val: Optional[float] = float(new_weight) if new_weight else None
            new_reps_val: Optional[int] = int(new_reps) if new_reps else None

            db.update_workout_entry_by_id(
                entry_id, new_weight=new_weight_val, new_reps=new_reps_val
            )

            flash("Entry updated successfully!", "success")

        except ValueError:
            flash("Invalid input for weight or reps.", "error")

        return redirect(url_for("correct_mistake"))

    # GET: Fetch the entry details to pre-fill the form
    records: List[Any] = db.get_workout_history()
    entry: Optional[Any] = next((r for r in records if r[0] == entry_id), None)

    if not entry:
        flash("Entry not found.", "error")
        return redirect(url_for("correct_mistake"))

    return render_template("update_entry.html", entry=entry)


# -----------------------------------------------------------------------------


@app.route("/delete-entry/<int:entry_id>", methods=["POST"])
def delete_entry(entry_id: int) -> Response:
    """
    Delete a workout entry by its ID.

    Args:
        entry_id (int): The ID of the workout entry to delete.
    """
    db.delete_workout_entry_by_id(entry_id)
    flash("Entry deleted successfully.", "success")
    return redirect(url_for("correct_mistake"))


# -----------------------------------------------------------------------------


@app.route("/volume-history")
def volume_history() -> str:
    """
    View weekly volume history broken down by body part.

    Returns:
        Rendered template with weekly volume data.
    """
    today: date = date.today()

    # Get the most recent Monday
    monday: date = today - timedelta(days=today.weekday())
    weeks: List[Dict[str, Any]] = []

    for i in range(4):
        start_date: date = monday - timedelta(weeks=i)
        end_date: date = start_date + timedelta(days=6)
        volume: Dict[str, int] = db.get_weekly_volume_by_body_part(
            start_date.isoformat(), end_date.isoformat()
        )

        weeks.append(
            {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "volume": volume,
            }
        )

    return render_template("volume_history.html", weeks=weeks)


# -----------------------------------------------------------------------------


@app.route("/progress-graph", methods=["GET", "POST"])
def progress_graph() -> str:
    """
    Generate and display a progress graph for a selected exercise using Plotly.

    GET: Render the form to select an exercise.
    POST: Generate the graph for the selected exercise.
    """
    graph_html: Optional[str] = None
    exercises: List[str] = db.get_all_exercises()
    selected_exercise: Optional[str] = None

    if request.method == "POST":
        selected_exercise = request.form.get("exercise")
        if not selected_exercise:
            flash("Please select an exercise.", "error")
            return redirect(url_for("progress_graph"))

        # Get workout history for the selected exercise
        records: List[Any] = db.get_workout_history_by_exercise(selected_exercise)
        if not records:
            flash("No data available for this exercise.", "error")
            return redirect(url_for("progress_graph"))

        # Group records by date and choose the entry with the maximum weight for each date
        date_weight_reps: Dict[str, List[Any]] = {}

        for record in records:
            date_str, exercise, weight, reps = record
            dt: str = date_str

            try:
                reps_val: int = int(reps)
            except ValueError:
                continue

            if dt in date_weight_reps:
                date_weight_reps[dt].append((weight, reps_val))
            else:
                date_weight_reps[dt] = [(weight, reps_val)]

        if not date_weight_reps:
            flash("No valid data available for plotting.", "error")
            return redirect(url_for("progress_graph"))

        # Sort dates and select max entry per date
        dates: List[str] = sorted(date_weight_reps.keys())
        weights: List[float] = []
        reps_list: List[int] = []

        for dt in dates:
            max_entry = max(date_weight_reps[dt], key=lambda x: x[0])
            weights.append(max_entry[0])
            reps_list.append(max_entry[1])

        # Create a Plotly figure with two traces
        fig: go.Figure = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=dates,
                y=weights,
                mode="lines+markers",
                name="Weight",
                line=dict(color="blue"),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=dates,
                y=reps_list,
                mode="lines+markers",
                name="Reps",
                yaxis="y2",
                line=dict(color="red"),
            )
        )

        fig.update_layout(
            title=f"Progress for {selected_exercise}",
            xaxis_title="Date",
            yaxis=dict(
                title={"text": "Weight", "font": {"color": "blue"}},
                tickfont={"color": "blue"},
            ),
            yaxis2=dict(
                title={"text": "Reps", "font": {"color": "red"}},
                tickfont={"color": "red"},
                overlaying="y",
                side="right",
            ),
            legend=dict(x=0, y=1.1, orientation="h"),
            margin=dict(l=40, r=40, t=80, b=40),
        )

        # Convert the Plotly figure to an HTML snippet (without full HTML tags)
        graph_html = fig.to_html(full_html=False, include_plotlyjs=True)

    return render_template(
        "progress_graph.html",
        exercises=exercises,
        graph_html=graph_html,
        selected_exercise=selected_exercise,
    )


# -----------------------------------------------------------------------------


if __name__ == "__main__":
    app.run(debug=True)
