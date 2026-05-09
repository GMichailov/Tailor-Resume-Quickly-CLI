import shutil
import uuid
from pathlib import Path

from storage import (
    get_resume_by_name,
    get_skill_entry_by_id,
    get_summary_entry_by_id,
    insert_bullet_point,
    insert_bullet_point_group,
    insert_const_data,
    insert_project_entry,
    insert_resume,
    insert_skill_entry,
    insert_summary_entry,
    insert_work_entry,
    list_skill_entries,
    list_summary_entries,
)

from tailor import tailor_resume


def select_primary_action():
    goal = input(
        """
        Enter the number corresponding to what you would like to do.
        1. Upload a previous resume file for this program to edit in-place later.
        2. Update personal information (linkedin, phone number, address, etc)
        3. Add bullet points or information to later be able to insert into your resume.
        4. Drop in a job description and create a tailored resume for this job using AI and ATS.
        > 
        """
    )
    if goal.strip() not in "1234" and len(goal.strip()) != 1:
        return -1
    else:
        return int(goal.strip())


def upload_resume_file():
    file_address = input(
        """
        Input the absolute file address on your device to this resume (this will only create a copy): 
        """
    ).strip()
    resume_path = Path(file_address)
    if not resume_path.is_absolute():
        print("Please provide an absolute file path.\n")
        return
    elif not resume_path.exists() or not resume_path.is_file():
        print("That file does not exist.\n")
        return
    elif resume_path.suffix.lower() != ".docx":
        print("Only .docx resume files are supported right now.\n")
        return
    try:
        with resume_path.open("rb") as resume_file:
            resume_file.read(1)
    except OSError:
        print("That file could not be accessed.\n")
        return

    resume_title = input(
        """
        Enter a title for this resume:
        """
    ).strip()
    if not resume_title:
        print("Resume title cannot be empty.\n")
        return
    existing_resume = get_resume_by_name(resume_title)
    destination_directory = Path("files")
    destination_directory.mkdir(parents=True, exist_ok=True)
    if existing_resume:
        overwrite = input(
            f'A resume named "{resume_title}" already exists. Overwrite it? (y/n): '
        ).strip().lower()

        if overwrite != "y":
            print("Upload cancelled.\n")
            return
        resume_id = existing_resume[0]
    else:
        resume_id = str(uuid.uuid4())
        insert_resume(resume_id, resume_title)
    destination_path = destination_directory / f"{resume_id}.docx"
    try:
        shutil.copy2(resume_path, destination_path)
    except OSError:
        print("Unable to copy the resume into the files directory.\n")
        return
    print(f'Resume "{resume_title}" saved as {destination_path.name}.\n')


def ensure_long_input_file_exists():
    Path("long_input.txt").touch(exist_ok=True)


def read_long_input_text(required=False, empty_error_text="long_input.txt is empty."):
    ensure_long_input_file_exists()
    raw_text = Path("long_input.txt").read_text(encoding="utf-8").strip()
    if not raw_text:
        if required:
            print(f"{empty_error_text}\n")
        return None
    return raw_text


def prompt_long_input_text(prompt_text, required=False, empty_error_text="long_input.txt is empty."):
    input(prompt_text)
    return read_long_input_text(required=required, empty_error_text=empty_error_text)


def normalize_optional_text(value):
    cleaned_value = value.strip()
    if not cleaned_value:
        return None
    return cleaned_value


def prompt_required_text(prompt_text, error_text):
    while True:
        value = input(prompt_text).strip()
        if value:
            return value
        print(f"{error_text}\n")


def update_personal_information():
    name = prompt_required_text(
        """
        Enter your name:
        """,
        "Name is required.",
    )
    email = normalize_optional_text(
        input(
            """
            Enter your email (optional):
            """
        )
    )
    linkedin_url = normalize_optional_text(
        input(
            """
            Enter your LinkedIn URL (optional):
            """
        )
    )
    github_url = normalize_optional_text(
        input(
            """
            Enter your GitHub URL (optional):
            """
        )
    )
    phone_number = normalize_optional_text(
        input(
            """
            Enter your phone number (optional):
            """
        )
    )
    location = normalize_optional_text(
        input(
            """
            Enter your location (optional):
            """
        )
    )
    certifications = prompt_long_input_text(
        """
        Paste certifications into long_input.txt, then press Enter (optional):
        """
    )
    educations = prompt_long_input_text(
        """
        Paste educations into long_input.txt, then press Enter (optional):
        """
    )

    insert_const_data(
        name=name,
        email=email,
        linkedin_url=linkedin_url,
        github_url=github_url,
        phone_number=phone_number,
        location=location,
        certifications=certifications,
        educations=educations,
    )
    print("Personal information saved.\n")


def display_entry_titles(entries):
    for index, entry in enumerate(entries, start=1):
        description = entry[1] if entry[1] else "(no description)"
        print(f"{index}. {description}")
    print("")


def browse_or_create_text_entries(
    entry_name,
    list_entries_function,
    get_entry_by_id_function,
    insert_entry_function,
    value_label,
):
    while True:
        selection = input(
            f"""
            {entry_name}
            Enter 1 to see previous entries.
            Enter 2 to enter new.
            Enter 0 to go back.
            >
            """
        ).strip()

        if selection == "0":
            return
        elif selection == "1":
            entries = list_entries_function()
            if not entries:
                print(f"No {entry_name.lower()} entries found.\n")
                continue

            display_entry_titles(entries)

            while True:
                inspect_selection = input(
                    """
                    Enter the number of an entry to inspect it.
                    Enter 0 to go back.
                    >
                    """
                ).strip()

                if inspect_selection == "0":
                    break

                if not inspect_selection.isdigit():
                    print("That is not a valid selection.\n")
                    continue

                selected_index = int(inspect_selection)
                if selected_index < 1 or selected_index > len(entries):
                    print("That is not a valid selection.\n")
                    continue

                entry_id = entries[selected_index - 1][0]
                selected_entry = get_entry_by_id_function(entry_id)

                if not selected_entry:
                    print("Unable to find that entry.\n")
                    continue

                description = selected_entry[1] if selected_entry[1] else "(no description)"
                raw_text = selected_entry[2] if selected_entry[2] else ""

                print(f"\nTitle: {description}\n")
                print(f"{value_label}:\n{raw_text}\n")
        elif selection == "2":
            description = input(
                f"""
                Enter a short title/description for this {entry_name[:-1].lower()} entry:
                """
            ).strip()

            raw_text = input(
                f"""
                Paste the raw text for this {entry_name[:-1].lower()} entry:
                """
            ).strip()

            if not raw_text:
                print("Entry text cannot be empty.\n")
                continue

            insert_entry_function(description or None, raw_text)
            print(f"New {entry_name[:-1].lower()} entry saved.\n")
        else:
            print("That is not a valid selection.\n")


def create_bullet_point_groups(parent_id):
    while True:
        selection = input(
            """
            Bullet point groups
            1. Create a new bullet point group
            0. Finish
            >
            """
        ).strip()

        if selection == "0":
            return
        if selection != "1":
            print("That is not a valid selection.\n")
            continue

        description = prompt_required_text(
            """
            Enter a non-empty description for this bullet point group.
            A quality name will make it much easier to tailor later:
            """,
            "Bullet point group description is required.",
        )

        bullet_points = []

        while True:
            bullet_selection = input(
                """
                Bullet points
                1. Add bullet point
                2. Finish this group
                0. Cancel this group
                >
                """
            ).strip()

            if bullet_selection == "0":
                bullet_points = []
                print("Bullet point group cancelled.\n")
                break
            elif bullet_selection == "1":
                bullet_point_text = prompt_required_text(
                    """
                    Enter the bullet point text:
                    """,
                    "Bullet point text is required.",
                )
                bullet_points.append(bullet_point_text)
                print("Bullet point added.\n")
            elif bullet_selection == "2":
                if not bullet_points:
                    print("No bullet points entered. Group not saved.\n")
                    break

                group_id = str(uuid.uuid4())
                insert_bullet_point_group(group_id, parent_id, description)

                for index, bullet_point in enumerate(bullet_points, start=1):
                    insert_bullet_point(group_id, bullet_point, index)

                print("Bullet point group saved.\n")
                break
            else:
                print("That is not a valid selection.\n")


def add_work_entry():
    job_title = prompt_required_text(
        """
        Enter the job title:
        """,
        "Job title is required.",
    )
    company = prompt_required_text(
        """
        Enter the company:
        """,
        "Company is required.",
    )
    start_date = prompt_required_text(
        """
        Enter the start date:
        """,
        "Start date is required.",
    )
    end_date = normalize_optional_text(
        input(
            """
            Enter the end date (optional):
            """
        )
    )

    work_id = str(uuid.uuid4())
    insert_work_entry(work_id, job_title, company, start_date, end_date)
    create_bullet_point_groups(work_id)
    print("Work entry saved.\n")


def add_project_entry():
    title = prompt_required_text(
        """
        Enter the project title:
        """,
        "Project title is required.",
    )
    start_date = prompt_required_text(
        """
        Enter the start date:
        """,
        "Start date is required.",
    )
    end_date = normalize_optional_text(
        input(
            """
            Enter the end date (optional):
            """
        )
    )

    project_id = str(uuid.uuid4())
    insert_project_entry(project_id, title, start_date, end_date)
    create_bullet_point_groups(project_id)
    print("Project entry saved.\n")


def add_custom_information():
    while True:
        selection = input(
            """
            Custom information
            1. Skills
            2. Summaries
            3. Work
            4. Projects
            0. Back
            >
            """
        ).strip()

        if selection == "0":
            return
        elif selection == "1":
            browse_or_create_text_entries(
                entry_name="Skills",
                list_entries_function=list_skill_entries,
                get_entry_by_id_function=get_skill_entry_by_id,
                insert_entry_function=insert_skill_entry,
                value_label="Skills",
            )
        elif selection == "2":
            browse_or_create_text_entries(
                entry_name="Summaries",
                list_entries_function=list_summary_entries,
                get_entry_by_id_function=get_summary_entry_by_id,
                insert_entry_function=insert_summary_entry,
                value_label="Summary",
            )
        elif selection == "3":
            add_work_entry()
        elif selection == "4":
            add_project_entry()
        else:
            print("That is not a valid selection.\n")


def run_cli():
    ensure_long_input_file_exists()

    while True:
        primary_action = select_primary_action()
        if primary_action == 0:
            print("That is not a valid selection.\n")
            continue
        if primary_action == 1:
            upload_resume_file()
        elif primary_action == 2:
            update_personal_information()
        elif primary_action == 3:
            add_custom_information()
        elif primary_action == 4:
            tailor_resume()


if __name__ == "__main__":
    run_cli()