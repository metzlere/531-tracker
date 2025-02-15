"""
Database module for the 5/3/1 Workout Tracker.

Provides the Database class to handle all database operations such as creating tables,
logging workouts, updating entries, and retrieving historical data.
"""

import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


class Database:
    """
    A class to handle database operations for storing and managing workout data.
    """

    def __init__(self) -> None:
        """
        Initialize the Database object by connecting to the SQLite database and
        creating necessary tables if they do not exist.
        """
        self.conn: sqlite3.Connection = sqlite3.connect(
            "workout.db", check_same_thread=False
        )
        self.create_tables()

    # -----------------------------------------------------------------------------

    def create_tables(self) -> None:
        """
        Creates tables for training maxes, training max history, workout history, and exercises.
        """
        c = self.conn.cursor()

        c.execute(
            """CREATE TABLE IF NOT EXISTS training_maxes (
                   exercise TEXT PRIMARY KEY, 
                   one_rm REAL, 
                   training_max REAL
               )"""
        )

        c.execute(
            """CREATE TABLE IF NOT EXISTS training_maxes_history (
                   date TEXT, 
                   exercise TEXT, 
                   one_rm REAL, 
                   training_max REAL
               )"""
        )

        c.execute(
            """CREATE TABLE IF NOT EXISTS workout_history (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   date TEXT, 
                   exercise TEXT, 
                   weight REAL, 
                   reps TEXT
               )"""
        )

        c.execute(
            """CREATE TABLE IF NOT EXISTS exercises (
                   exercise TEXT PRIMARY KEY, 
                   body_part TEXT
               )"""
        )

        self.conn.commit()

    # -----------------------------------------------------------------------------

    def set_training_max(self, exercise: str, one_rm: float, training_max: float) -> None:
        """
        Sets or updates the training max for a given exercise.

        Args:
            exercise (str): Name of the exercise.
            one_rm (float): One-repetition maximum.
            training_max (float): Calculated training max (typically 90% of 1RM).
        """
        c = self.conn.cursor()

        c.execute(
            """REPLACE INTO training_maxes (exercise, one_rm, training_max)
               VALUES (?, ?, ?)""",
            (exercise, one_rm, training_max),
        )

        c.execute(
            """INSERT INTO training_maxes_history (date, exercise, one_rm, training_max)
               VALUES (?, ?, ?, ?)""",
            (datetime.now().date(), exercise, one_rm, training_max),
        )

        self.conn.commit()

    # -----------------------------------------------------------------------------

    def get_training_max_history(self) -> List[Tuple[Any, ...]]:
        """
        Retrieves the entire training max history for all exercises.

        Returns:
            A list of tuples containing date, exercise, one_rm, and training_max.
        """
        c = self.conn.cursor()

        c.execute(
            """SELECT date, exercise, one_rm, training_max 
               FROM training_maxes_history 
               ORDER BY date DESC"""
        )

        return c.fetchall()

    # -----------------------------------------------------------------------------

    def get_training_max(self, exercise: str) -> Optional[float]:
        """
        Retrieves the current training max for a specific exercise.

        Args:
            exercise (str): The exercise name.

        Returns:
            The training max as a float if found; otherwise, None.
        """
        c = self.conn.cursor()

        c.execute(
            """SELECT training_max FROM training_maxes WHERE exercise=?""", (exercise,)
        )

        result = c.fetchone()
        return result[0] if result else None

    # -----------------------------------------------------------------------------

    def log_workout(
        self, date_value: Any, exercise: str, weight: float, reps: str
    ) -> None:
        """
        Logs a workout session for the given exercise, weight, and reps.

        Args:
            date_value (Any): The date of the workout.
            exercise (str): The exercise name.
            weight (float): The weight used.
            reps (str): The number of repetitions (as a string).
        """
        c = self.conn.cursor()

        c.execute(
            """INSERT INTO workout_history (date, exercise, weight, reps)
               VALUES (?, ?, ?, ?)""",
            (date_value, exercise, weight, reps),
        )

        self.conn.commit()

    # -----------------------------------------------------------------------------

    def get_workout_history(self) -> List[Tuple[Any, ...]]:
        """
        Retrieves the complete workout history sorted by date in descending order.

        Returns:
            A list of tuples representing workout history records.
        """
        c = self.conn.cursor()

        c.execute(
            """SELECT id, date, exercise, weight, reps 
               FROM workout_history 
               ORDER BY date DESC, id DESC"""
        )

        return c.fetchall()

    # -----------------------------------------------------------------------------

    def get_past_accessory_exercises(self) -> List[str]:
        """
        Retrieves a list of distinct accessory exercises that are not part of the main lifts.

        Returns:
            A list of exercise names.
        """
        c = self.conn.cursor()
        main_lifts: Tuple[str, str, str, str] = ("Squat", "Bench Press", "Deadlift", "Press")

        c.execute(
            """SELECT DISTINCT exercise FROM workout_history
               WHERE exercise NOT IN (?, ?, ?, ?)""",
            main_lifts,
        )

        exercises = [row[0] for row in c.fetchall()]
        return exercises

    # -----------------------------------------------------------------------------

    def update_workout_entry_by_id(
        self, record_id: int, new_weight: Optional[float] = None, new_reps: Optional[int] = None
    ) -> None:
        """
        Updates the weight and/or reps for a specific workout entry.

        Args:
            record_id (int): The ID of the workout entry.
            new_weight (Optional[float]): New weight value.
            new_reps (Optional[int]): New repetitions value.
        """
        c = self.conn.cursor()

        if new_weight is not None and new_reps is not None:
            c.execute(
                """UPDATE workout_history SET weight = ?, reps = ? WHERE id = ?""",
                (new_weight, new_reps, record_id),
            )
        elif new_weight is not None:
            c.execute(
                """UPDATE workout_history SET weight = ? WHERE id = ?""",
                (new_weight, record_id),
            )
        elif new_reps is not None:
            c.execute(
                """UPDATE workout_history SET reps = ? WHERE id = ?""",
                (new_reps, record_id),
            )

        self.conn.commit()

    # -----------------------------------------------------------------------------

    def delete_workout_entry_by_id(self, record_id: int) -> None:
        """
        Deletes a workout entry from the workout_history table based on the specified ID.

        Args:
            record_id (int): The ID of the workout entry to delete.
        """
        c = self.conn.cursor()

        c.execute("""DELETE FROM workout_history WHERE id = ?""", (record_id,))
        self.conn.commit()
        print("Workout entry deleted successfully.")

    # -----------------------------------------------------------------------------

    def get_exercise_body_part(self, exercise: str) -> Optional[str]:
        """
        Retrieves the body part associated with a specific exercise.

        Args:
            exercise (str): The exercise name.

        Returns:
            The body part as a string if found; otherwise, None.
        """
        c = self.conn.cursor()

        c.execute("""SELECT body_part FROM exercises WHERE exercise=?""", (exercise,))
        result = c.fetchone()
        return result[0] if result else None

    # -----------------------------------------------------------------------------

    def add_exercise(self, exercise: str, body_part: str) -> None:
        """
        Adds a new exercise and its associated body part to the exercises table.

        Args:
            exercise (str): The exercise name.
            body_part (str): The primary body part targeted by the exercise.
        """
        c = self.conn.cursor()

        c.execute(
            """INSERT OR REPLACE INTO exercises (exercise, body_part)
               VALUES (?, ?)""",
            (exercise, body_part),
        )

        self.conn.commit()

    # -----------------------------------------------------------------------------

    def get_weekly_volume_by_body_part(self, start_date: str, end_date: str) -> Dict[str, int]:
        """
        Calculates weekly volume by body part within a specified date range,
        measured in total sets per body part.

        Args:
            start_date (str): The start date in ISO format (YYYY-MM-DD).
            end_date (str): The end date in ISO format (YYYY-MM-DD).

        Returns:
            A dictionary mapping body parts to set counts.
        """
        c = self.conn.cursor()

        c.execute(
            """
            SELECT ex.body_part, COUNT(*) as set_count
            FROM workout_history wh
            JOIN exercises ex ON wh.exercise = ex.exercise
            WHERE date(wh.date) BETWEEN ? AND ?
            GROUP BY ex.body_part
            """,
            (start_date, end_date),
        )

        records: List[Tuple[str, int]] = c.fetchall()
        volume_by_body_part: Dict[str, int] = {}

        for body_part, set_count in records:
            volume_by_body_part[body_part] = set_count

        return volume_by_body_part

    # -----------------------------------------------------------------------------

    def get_all_exercises(self) -> List[str]:
        """
        Retrieves a list of all exercises from the workout history.

        Returns:
            A list of distinct exercise names.
        """
        c = self.conn.cursor()

        c.execute("""SELECT DISTINCT exercise FROM workout_history""")
        exercises: List[str] = [row[0] for row in c.fetchall()]
        return exercises

    # -----------------------------------------------------------------------------

    def get_workout_history_by_exercise(self, exercise: str) -> List[Tuple[Any, ...]]:
        """
        Retrieves the workout history for a specific exercise, sorted by date.

        Args:
            exercise (str): The exercise name.

        Returns:
            A list of tuples representing the workout records for the exercise.
        """
        c = self.conn.cursor()

        c.execute(
            """SELECT date, exercise, weight, reps FROM workout_history
               WHERE exercise = ? ORDER BY date""",
            (exercise,),
        )

        return c.fetchall()
