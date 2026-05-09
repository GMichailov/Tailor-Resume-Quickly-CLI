from pathlib import Path
import sqlite3


def get_connection():
    return sqlite3.connect("data.sql")


def ensure_required_files_exist():
    database_path = Path("data.sql")
    if not database_path.exists():
        database_path.touch()

    env_path = Path(".env")
    if not env_path.exists():
        env_path.write_text("API_KEY=", encoding="utf-8")

    files_directory = Path("files")
    files_directory.mkdir(exist_ok=True)


def on_startup():
    ensure_required_files_exist()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS resumes (
            id TEXT PRIMARY KEY,
            name TEXT UNIQUE
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS const_data (
            const_data_id INTEGER PRIMARY KEY,
            name TEXT,
            linkedin_url TEXT,
            github_url TEXT,
            phone_number TEXT,
            location TEXT,
            certifications TEXT,
            educations TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS summaries (
            summary_id INTEGER PRIMARY KEY,
            description TEXT, 
            summary TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS skills (
            skills_id INTEGER PRIMARY KEY, 
            description TEXT,
            skills TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS work (
            id TEXT PRIMARY KEY,
            job_title TEXT,
            company TEXT,
            start_date TEXT,
            end_date TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            title TEXT,
            start_date TEXT,
            end_date TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS bullet_point_group (
            id TEXT PRIMARY KEY,
            projects_or_work_id TEXT,
            description TEXT
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS bullet_points (
            id INTEGER PRIMARY KEY,
            bullet_point_group_id TEXT,
            description TEXT,
            positional_order INTEGER
        )
        """
    )
    conn.commit()
    conn.close()


def get_resume_by_name(name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, name
        FROM resumes
        WHERE name = ?
        """,
        (name,),
    )
    row = cursor.fetchone()
    conn.close()
    return row


def insert_resume(resume_id, name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO resumes (id, name)
        VALUES (?, ?)
        """,
        (resume_id, name),
    )
    conn.commit()
    conn.close()


def insert_const_data(
    name,
    linkedin_url=None,
    github_url=None,
    phone_number=None,
    location=None,
    certifications=None,
    educations=None,
):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO const_data (
            name,
            linkedin_url,
            github_url,
            phone_number,
            location,
            certifications,
            educations
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name,
            linkedin_url,
            github_url,
            phone_number,
            location,
            certifications,
            educations,
        ),
    )
    conn.commit()
    conn.close()


def get_latest_const_data():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            const_data_id,
            name,
            linkedin_url,
            github_url,
            phone_number,
            location,
            certifications,
            educations
        FROM const_data
        ORDER BY const_data_id DESC
        LIMIT 1
        """
    )
    row = cursor.fetchone()
    conn.close()
    return row


def list_skill_entries():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT skills_id, description, skills
        FROM skills
        ORDER BY skills_id ASC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_skill_entry_by_id(skills_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT skills_id, description, skills
        FROM skills
        WHERE skills_id = ?
        """,
        (skills_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return row


def insert_skill_entry(description, skills):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO skills (description, skills)
        VALUES (?, ?)
        """,
        (description, skills),
    )
    conn.commit()
    conn.close()


def list_summary_entries():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT summary_id, description, summary
        FROM summaries
        ORDER BY summary_id ASC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_summary_entry_by_id(summary_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT summary_id, description, summary
        FROM summaries
        WHERE summary_id = ?
        """,
        (summary_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return row


def insert_summary_entry(description, summary):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO summaries (description, summary)
        VALUES (?, ?)
        """,
        (description, summary),
    )
    conn.commit()
    conn.close()


def insert_work_entry(work_id, job_title, company, start_date, end_date=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO work (id, job_title, company, start_date, end_date)
        VALUES (?, ?, ?, ?, ?)
        """,
        (work_id, job_title, company, start_date, end_date),
    )
    conn.commit()
    conn.close()


def insert_project_entry(project_id, title, start_date, end_date=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO projects (id, title, start_date, end_date)
        VALUES (?, ?, ?, ?)
        """,
        (project_id, title, start_date, end_date),
    )
    conn.commit()
    conn.close()


def insert_bullet_point_group(group_id, projects_or_work_id, description):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO bullet_point_group (id, projects_or_work_id, description)
        VALUES (?, ?, ?)
        """,
        (group_id, projects_or_work_id, description),
    )
    conn.commit()
    conn.close()


def insert_bullet_point(group_id, description, positional_order):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO bullet_points (bullet_point_group_id, description, positional_order)
        VALUES (?, ?, ?)
        """,
        (group_id, description, positional_order),
    )
    conn.commit()
    conn.close()


def list_work_entries():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, job_title, company, start_date, end_date
        FROM work
        ORDER BY start_date DESC, id ASC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def list_project_entries():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, title, start_date, end_date
        FROM projects
        ORDER BY start_date DESC, id ASC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def list_bullet_point_groups(parent_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, projects_or_work_id, description
        FROM bullet_point_group
        WHERE projects_or_work_id = ?
        ORDER BY id ASC
        """,
        (parent_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def list_bullet_points_for_group(group_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT id, bullet_point_group_id, description, positional_order
        FROM bullet_points
        WHERE bullet_point_group_id = ?
        ORDER BY positional_order ASC, id ASC
        """,
        (group_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_bullet_point(bullet_point_id, description):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE bullet_points
        SET description = ?
        WHERE id = ?
        """,
        (description, bullet_point_id),
    )
    conn.commit()
    conn.close()


def delete_bullet_point(bullet_point_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        DELETE FROM bullet_points
        WHERE id = ?
        """,
        (bullet_point_id,),
    )
    conn.commit()
    conn.close()


def update_resume_name(resume_id, name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE resumes
        SET name = ?
        WHERE id = ?
        """,
        (name, resume_id),
    )
    conn.commit()
    conn.close()


on_startup()