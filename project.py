"""
References and Citations:

Gemini API:
- Learned from: https://ai.google.dev/gemini-api/docs/

System Instructions:
- Learned from: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/system-instruction-introduction#output-format

Dependency Injection:
- Learned from:
https://www.reddit.com/r/Python/comments/195uk6d/do_you_prefer_mock_or_dependency_injection_when/
https://www.geeksforgeeks.org/python/first-class-functions-python/


Usage of iter() and next() learned from::
https://docs.python.org/3/library/functions.html


How to strikethrough:
- Learned from: https://stackoverflow.com/questions/25244454/python-create-strikethrough-strikeout-overstrike-string-type#:~:text=So%20you%20basically%20surround%20the,github.com/ConnerWill/d4b6c776b509add763e17f9f113fd25b

"""

import csv
from datetime import date
import re
import pathlib


import tabulate
import requests
from google import genai
from google.genai import types


class Todo:
    def __init__(self):
        # Variable with all the data of the to-do list inside of it
        self.todo_list_file = []

        # Default values for future editing
        self.priority = "1"
        self.task = "empty"
        self.due_date = 12 / 12 / 9999

        # Creates a new file if there is none
        with open("todo_list.csv", "a+", newline="") as todo_file:
            ...

        # Pass the data into the csv file to a variable to be more easily workable
        with open("todo_list.csv") as todo_file:
            todo_reader = csv.DictReader(todo_file)
            for row in todo_reader:
                self.todo_list_file.append(row)

        # Verifies if the file is empty to write the header
        if not self.todo_list_file:
            with open("todo_list.csv", "w", newline="") as todo_file:
                todo_writer = csv.DictWriter(
                    todo_file, fieldnames=["Priority", "Task", "Due Date", "Status"]
                )
                todo_writer.writeheader()

    # Prints the to-do list as table
    def __str__(self):
        return tabulate.tabulate(self.todo_list_file, headers="keys", tablefmt="grid")

    # Adds a new tasks to the list
    def add(self, user_input=input):
        task = user_input("Add a new task:\n    -Task: ").strip()

        while True:
            due_date = user_input("    -Due date (MM/DD/YYYY): ").strip()

            if date_add := re.search(r"^(\d{2})/(\d{2})/(\d{4})$", due_date):
                try:
                    date(
                        int(date_add.group(3)),
                        int(date_add.group(1)),
                        int(date_add.group(2)),
                    )
                    break
                except ValueError:
                    print("Incorrect date. Try again.")
                    continue

            else:
                print("Wrong format. Try again.")
                continue

        while True:
            priority = user_input("    -Priority (Scale out of 10): ").strip()

            if not priority.isdecimal():
                print(
                    "The input entered was not a number. PLease enter an integer (1-10)."
                )

            elif 1 <= int(priority) <= 10:
                break

            else:
                print("Please enter an integer (1-10)")

        self.todo_list_file.append(
            {
                "Priority": priority,
                "Task": task,
                "Due Date": due_date,
                "Status": "incomplete",
            }
        )

        self.save()

    # Marks and unmark the task as done
    def done(self, user_input=input):
        while True:
            # ANSI codes for crossing out the text
            STRIKETHROUGH = "\x1b[9m"
            RESET = "\x1b[0m"

            number_of_tasks = 0

            print("""Which task you want to mark/unmark as done?
----------------------------------------------""")
            for number, task in enumerate(self.todo_list_file):
                print(f"{number + 1} - {task["Task"]}")
                number_of_tasks += 1

            done_option: str = user_input(
                """----------------------------------------------
Type the number of the desire task: """
            ).strip()

            if not done_option.isdecimal():
                print(f"\nEnter a valid number between 1 and {number_of_tasks}\n")
                continue

            elif int(done_option) < 1 or int(done_option) > number_of_tasks:
                print(f"\nEnter a valid number between 1 and {number_of_tasks}\n")
                continue

            # Verifying if the task is marked as done already
            elif re.search(
                r"^.\[9m(.*).\[0m$", self.todo_list_file[int(done_option) - 1]["Task"]
            ):

                done_option: int = int(done_option)

                for key, value in self.todo_list_file[done_option - 1].items():
                    if key == "Status":
                        break
                    key_match = re.search(
                        r"^.\[9m(.*).\[0m$",
                        self.todo_list_file[int(done_option) - 1][key],
                    )
                    self.todo_list_file[done_option - 1][key] = f"{key_match.group(1)}"

                # Changing status
                self.todo_list_file[done_option - 1]["Status"] = "incomplete"

                self.save()

            else:
                done_option: int = int(done_option)

                # Crossing out each item of the list
                for key, value in self.todo_list_file[done_option - 1].items():
                    self.todo_list_file[done_option - 1][
                        key
                    ] = f"{STRIKETHROUGH}{value}{RESET}"

                # Changing status
                self.todo_list_file[done_option - 1]["Status"] = "done"

                self.save()

            break

    def edit(self, user_input=input):
        while True:

            number_of_tasks = 0

            print("""Which task you want to edit?
----------------------------------------------""")
            for number, task in enumerate(self.todo_list_file):
                print(f"{number + 1} - {task["Task"]}")
                number_of_tasks += 1

            edit_option_main: str = user_input(
                """----------------------------------------------
Type the number of the desire task: """
            ).strip()

            if not edit_option_main.isdecimal():
                print(f"\nEnter a valid number between 1 and {number_of_tasks}\n")
                continue

            elif int(edit_option_main) < 1 or int(edit_option_main) > number_of_tasks:
                print(f"\nEnter a valid number between 1 and {number_of_tasks}\n")
                continue

            else:
                edit_option_main = int(edit_option_main)

                while True:
                    edit_option_second = user_input(EDIT_MENU).strip().lower()
                    match edit_option_second:

                        case "priority":
                            while True:
                                edit_priority = user_input(
                                    "Enter the new priority out of 10: "
                                ).strip()

                                if not edit_priority.isdecimal():
                                    print(
                                        "The input entered was not a number. PLease enter an integer (1-10)."
                                    )

                                elif 1 <= int(edit_priority) <= 10:
                                    break

                                else:
                                    print("Please enter an integer (1-10)")

                            self.todo_list_file[edit_option_main - 1][
                                "Priority"
                            ] = edit_priority

                            self.save()

                        case "task":
                            STRIKETHROUGH = "\x1b[9m"
                            RESET = "\x1b[0m"
                            if edit_task := re.search(
                                r"^.\[9m(.*).\[0m$",
                                self.todo_list_file[edit_option_main - 1]["Task"],
                            ):
                                self.todo_list_file[edit_option_main - 1][
                                    "Task"
                                ] = f"{STRIKETHROUGH}{user_input("What is the new task?: ").strip()}{RESET}"

                            else:
                                self.todo_list_file[edit_option_main - 1]["Task"] = (
                                    user_input("What is the new task?: ").strip()
                                )

                            self.save()

                        case "due date":
                            while True:
                                edit_due_date_input = user_input(
                                    "Enter the new date in (MM/DD/YYYY) format: "
                                ).strip()

                                if edit_due_date := re.search(
                                    r"^(\d{2})/(\d{2})/(\d{4})$", edit_due_date_input
                                ):
                                    try:
                                        date(
                                            int(edit_due_date.group(3)),
                                            int(edit_due_date.group(1)),
                                            int(edit_due_date.group(2)),
                                        )
                                        break
                                    except ValueError:
                                        print("Incorrect date. Try again.")
                                        continue

                                else:
                                    print("Wrong format. Try again.")
                                    continue

                            self.todo_list_file[edit_option_main - 1][
                                "Due Date"
                            ] = edit_due_date_input

                            self.save()

                        case "back":
                            break

                        case _:
                            print("Please type one of the possible options.")
                            continue

            break

    # Deletes one task form the list
    def delete(self, user_input=input):
        while True:
            number_of_tasks = 0
            print("""Which task you want to delete?
Type "back" to go back.
----------------------------------------------""")
            for number, task in enumerate(self.todo_list_file):
                print(f"{number + 1} - {task["Task"]}")
                number_of_tasks += 1

            delete_option: str = (
                user_input("""----------------------------------------------
    Type the number of the desire task: """).strip().lower()
            )

            if delete_option == "back":
                break

            elif not delete_option.isdecimal():
                print(f"\nEnter a valid number between 1 and {number_of_tasks}\n")
                continue

            elif int(delete_option) < 1 or int(delete_option) > number_of_tasks:
                print(f"\nEnter a valid number between 1 and {number_of_tasks}\n")
                continue

            else:
                delete_option = int(delete_option)

                del self.todo_list_file[delete_option - 1]

                self.save()

            break

    # Deletes all tasks
    def clear(self, user_input=input):
        while True:
            clear_option = (
                user_input("Are you sure you want to delete all your tasks? (yes/no): ")
                .strip()
                .lower()
            )
            match clear_option:
                case "yes":
                    self.todo_list_file = []
                    self.save()

                case "no":
                    break

                case _:
                    print('\nType one of the two options: "yes" or "no"\n')
                    continue

            break

    # Writes the current list into a file
    def save(self):
        with open("todo_list.csv", "w", newline="") as todo_file:
            todo_writer = csv.DictWriter(
                todo_file, fieldnames=["Priority", "Task", "Due Date", "Status"]
            )
            todo_writer.writeheader()

            for row in self.todo_list_file:
                todo_writer.writerow(row)


# Menus here for a cleaner code
MAIN_MENU = """
What do you want to do?
-----------------------------------------------------------------
Type one of the following options:
    "todo" -> to modify or access the To-Do list.
    "gen" -> to generate a personalize schedule for your week.
    "exit" -> to exit the program.
-----------------------------------------------------------------
Type option here: """

TODO_MENU = """
Your To-do list:
----------------------------------------------
Type one of the following options:
    "add" -> to add a new task to the list.
    "done" -> to mark or unmark a task as done.
    "edit" -> to edit a task.
    "del" -> to delete a task.
    "clear" -> to delete all the task.
    "back" -> to go back to the previews menu.
    "exit" -> to exit the program.
----------------------------------------------
Type your option here: """

EDIT_MENU = """
What edits you want to make?
Enter the field you want to edit.
(To exit the edit menu type "back")
-------------------------------
(Priority, Task, Due Date): """


SYSTEM_INSTRUCTIONS_SCHEDULE = """You are a professional weekly schedule maker. Follow these instructions, and base your response on the provided User Input.

Instructions:
- Read through personal commitments and the To-Do list submitted to you.
- Output your response in CSV so that the days are in the column and the time in the rows.
- Take the personal commitments as immutable events and play around with the tasks in the To-Do list as you see them fit.
- Keep it realistic.
- Stick to the facts.
- Do not hallucinate.
- Determine what task should be done first by its priority and due date.
- Do not include extra information, your output should only contain the schedule in the indicated format.
"""


PROMPT_SCHEDULE = """Create carefully a realistic weekly schedule fot a good time management following the tips below and using the information in the document provided
Tips:
- Include regular and personal commitments. Make sure your weekly calendar includes all your regular commitments and personal, such as meals, exercise, bedtimes, meetings, work shifts, etc. This helps you maintain a balanced lifestyle and ensures you don’t overlook important activities.
- Plan breaks. Breaks are essential for maintaining focus and preventing burnout. Make sure your schedule includes breaks; build in planned activities that break up study sessions and help you relax and recharge.
- Overestimate tasks. Allow extra time for tasks, especially at the beginning of the term when you’re learning how long things take. Overestimating ensures you have enough time to complete tasks without feeling rushed.
- Include flex time. Schedule blocks of time that you can use for whatever is needed most. Flex time provides a cushion for when things don’t go as planned, helping you stay on track without feeling overwhelmed. As you get better at estimating how long things take, you can scale back your flex time."""


def main():
    todo_list = Todo()
    while True:
        main_options = input(MAIN_MENU).strip().lower()
        # Selects between the different options of the main menu
        match main_options:
            case "todo":
                if todo(todo_list) == 0:
                    break
                else:
                    print("\n" * 200)  # Clean the terminal
                    continue

            case "gen":
                print("\n" * 200)  # Clean the terminal
                gen(todo_list)
                continue

            case "exit":
                print("\n" * 200)  # Clean the terminal
                print("You have exit the program.\nEnd.\n")
                return

            case _:
                print("\n" * 200)  # Clean the terminal
                print("Please type one of the three possible options.")
                continue


# Menu that manages the todo list
def todo(todo_list, user_input=input):
    while True:
        print("\n" * 200)  # Clean the terminal
        print(f"\n{todo_list}")

        todo_options = user_input(TODO_MENU).strip().lower()
        match todo_options:
            case "add":
                print("\n" * 200)  # Clean the terminal
                todo_list.add(user_input)

            case "done":
                print("\n" * 200)  # Clean the terminal
                todo_list.done(user_input)

            case "edit":
                print("\n" * 200)  # Clean the terminal
                todo_list.edit(user_input)

            case "del":
                print("\n" * 200)  # Clean the terminal
                todo_list.delete(user_input)

            case "clear":
                print("\n" * 200)  # Clean the terminal
                todo_list.clear(user_input)

            case "back":
                print("\n" * 200)  # Clean the terminal
                break

            case "exit":
                print("\n" * 200)  # Clean the terminal
                print("You have exit the program.\nEnd.\n")
                return 0

            case _:
                print("Please type one of the possible options.")
                continue


# Generates a weekly schedule using a commitments file and the to-do list
def gen(todo_list, user_input=input):
    try:
        with open("final_schedule.txt") as final_schedule_reader:
            for line in final_schedule_reader:
                print(line.rstrip())

    except:
        ...

    while True:
        personal_commitments_path = user_input(
            '\nType the route of the txt file with your personal commitments (type "back" to go back): '
        ).strip()

        if personal_commitments_path.lower() == "back":
            return

        elif not personal_commitments_path.endswith(".txt"):
            print("This is not a txt file.\nTry again.")
            continue

        else:
            personal_commitments = pathlib.Path(personal_commitments_path)

        try:
            personal_commitments_error_handling = personal_commitments.read_bytes()

        except FileNotFoundError:
            print("File not found. Enter another route.")
            continue

        with (
            open(personal_commitments_path) as personal_commitments_file,
            open("todo_list.csv") as todo_file,
        ):
            personal_commitments_reader = personal_commitments_file.readlines()
            todo_reader = todo_file.readlines()

            if any(
                "To-Do list (Ignore this in parenthesis, this is for avoiding duplicates)"
                in line
                for line in personal_commitments_reader
            ):
                # Get the index where the To Do list starts at for not repeating it
                index_personal_commitments = 0
                for line in personal_commitments_reader:
                    if (
                        "To-Do list (Ignore this in parenthesis, this is for avoiding duplicates)"
                        not in line
                    ):
                        index_personal_commitments += 1

                    else:
                        break

                personal_commitments_reader = personal_commitments_reader[
                    : index_personal_commitments - 1
                ]

                personal_commitments_reader.append(
                    "\nTo-Do list (Ignore this in parenthesis, this is for avoiding duplicates)\n"
                )

                for item in todo_reader:
                    personal_commitments_reader.append(item)

                with open(
                    personal_commitments_path, "w"
                ) as personal_commitments_file_plus_todo:
                    personal_commitments_file_plus_todo.writelines(
                        personal_commitments_reader
                    )

            else:
                personal_commitments_reader.append(
                    "\nTo-Do list (Ignore this in parenthesis, this is for avoiding duplicates)\n"
                )

                for item in todo_reader:
                    personal_commitments_reader.append(item)

                with open(
                    personal_commitments_path, "w"
                ) as personal_commitments_file_plus_todo:
                    personal_commitments_file_plus_todo.writelines(
                        personal_commitments_reader
                    )

        gen_edit(personal_commitments, PROMPT_SCHEDULE)

        break

    schedule_data = []

    with open("schedule.txt") as schedule_file:
        schedule_reader = csv.DictReader(schedule_file)
        for row in schedule_reader:
            schedule_data.append(row)

    final_schedule = tabulate.tabulate(schedule_data, headers="keys", tablefmt="grid")

    print("\n" * 200)  # Clean the terminal
    print(f"{final_schedule}\n")

    with open("final_schedule.txt", "w", newline="") as final_schedule_writer:
        final_schedule_writer.write(str(final_schedule))

    while True:
        gen_edit_option = (
            user_input("\nDo you want to edit this schedule? (yes/no): ")
            .strip()
            .lower()
        )

        match gen_edit_option:
            case "yes":
                modification = user_input(
                    "Describe exactly what do you want to change: "
                )

                to_prompt = f"{PROMPT_SCHEDULE}\n{modification}"

                gen_edit(personal_commitments, to_prompt)

                schedule_data = []

                with open("schedule.txt") as schedule_file:
                    schedule_reader = csv.DictReader(schedule_file)
                    for row in schedule_reader:
                        schedule_data.append(row)

                final_schedule = tabulate.tabulate(
                    schedule_data, headers="keys", tablefmt="grid"
                )

                print("\n" * 200)  # Clean the terminal
                print(f"{final_schedule}\n")

                with open(
                    "final_schedule.txt", "w", newline=""
                ) as final_schedule_writer:
                    final_schedule_writer.write(str(final_schedule))

            case "no":
                print("\n" * 200)  # Clean the terminal
                break

            case _:
                print('Wrong input. Please type "yes" or "no".')
                continue


# Uses gemini to generate the schedule and writes it into a file
def gen_edit(personal_commitments, to_prompt):
    while True:
        with open("gemini_api_key.txt", "a+", newline="") as gemini_api_key:
            gemini_api_key.seek(0)
            gemini_api_key_reader = gemini_api_key.readlines()

        try:
            GEMINI_API_KEY = gemini_api_key_reader[0].strip()

        except IndexError:
            GEMINI_API_KEY = "null"

        result = requests.get(
            f"https://generativelanguage.googleapis.com/v1/models?key={GEMINI_API_KEY}"
        )

        if str(result) == "<Response [200]>":
            print("\nThis may take few minutes. Please wait...")
            break

        else:
            print("\nNo valid API.")

            with open("gemini_api_key.txt", "w", newline="") as gemini_api_key:
                GEMINI_API_KEY = input(
                    "What is your API key for gemini-3-flash-preview?: "
                )

                gemini_api_key.write(GEMINI_API_KEY.strip())
            continue

    client = genai.Client(api_key=GEMINI_API_KEY)

    while True:
        try:
            prompt = to_prompt
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTIONS_SCHEDULE
                ),
                contents=[
                    types.Part.from_bytes(
                        data=personal_commitments.read_bytes(),
                        mime_type="text/plain",
                    ),
                    prompt,
                ],
            )

            schedule = response.text

            with open("schedule.txt", "w", newline="") as schedule_file:
                schedule_file.write(schedule)

            break

        except:
            # continue
            ...


if __name__ == "__main__":
    main()
