# Schedulit

## Video Demo
https://youtu.be/e-atTXHhGZM

## Description

**Schedulit** is a terminal-based productivity and time-management application built to help users deal with disorganization, procrastination, and low productivity.

At its core, Schedulit works as a digital to-do list where users can keep track of their responsibilities. Its main feature, however, is that it can combine the user’s task list with their fixed personal commitments and send that information to the **Gemini 3 Flash** AI model to automatically generate an optimized weekly schedule.

When the user runs `python project.py`, the program opens a terminal menu with three main options: `todo`, `gen`, and `exit`.

The `todo` menu works as a complete task manager. It allows the user to:

- add tasks with due dates and priority levels from 1 to 10
- mark tasks as done
- edit tasks
- delete tasks
- clear the entire list

When a task is marked as done, it is visually crossed out using ANSI formatting in the terminal.

The `gen` menu is responsible for schedule generation. It asks the user for a `.txt` file containing their fixed personal commitments. Then, the program appends the current to-do list to that file and sends the combined information to Gemini. After the schedule is generated, the program displays it in a clean table and asks the user whether they want to make any manual modifications. If the user wants changes, the schedule is regenerated with the new instructions.

---

## Project Structure and Files

This project uses a simple file-based architecture to manage data and program state without needing a full SQL database.

### `project.py`
The main application file. It contains the core logic of the program, including the menus, the to-do list system, and the AI integration.

### `test_project.py`
Contains `pytest` tests that verify the main user-facing workflows, such as adding, editing, deleting, and clearing tasks, as well as checking whether files are created and written correctly.

### `todo_list.csv`
This file acts as the database for the user’s tasks. The program automatically creates and updates it as the user interacts with the `todo` menu.

### `schedule.txt`
A temporary file that stores the raw CSV-formatted response returned directly by the Gemini API.

### `final_schedule.txt`
A formatted and tabulated version of the generated schedule. This makes it easier to print the schedule in the terminal and also allows the user to open or print it outside the program.

### `gemini_api_key.txt`
Stores the user’s Gemini API key.

### `requirements.txt`
Lists the external libraries needed to run the project, including:

- `tabulate`
- `google-genai`
- `requests`

---

## Core Functions and Data Flow

The logic in `project.py` is organized into a main function, several custom functions, and a `Todo` class.

### `main()`
This function starts the program, initializes the `Todo` object, loads the CSV data into memory, and routes the user to the corresponding menu.

### `todo(todo_list)`
This function controls the to-do list interface. It calls methods from the `Todo` class such as `add()`, `done()`, `edit()`, and `delete()`.

Every time the user makes a change, the program calls `save()` to immediately write the updated in-memory list back to `todo_list.csv`.

### `gen(todo_list)`
This function handles schedule generation. Instead of passing a Python list directly to the AI, it opens `todo_list.csv`, reads its contents from disk, and appends that text to the user’s personal commitments `.txt` file. This creates one combined document containing both fixed commitments and pending tasks.

### `gen_edit(personal_commitments, to_prompt)`
This function handles the Gemini API interaction.

It first validates the API key using `requests.get`. If the key is valid, it sends the following to Gemini:

- a system instruction
- the scheduling prompt
- the combined commitments-and-tasks document as bytes

Then, it writes Gemini’s response to `schedule.txt`.

Back in `gen()`, that raw output is read, formatted using `tabulate`, printed to the terminal, and saved to `final_schedule.txt`.

---

## Design Decisions and Challenges

One of the first design decisions I had to make was how to store the user’s data.

I chose to use `.csv` and `.txt` files instead of a database like SQLite. Since the amount of data in this project is relatively small, plain text files were a simpler, faster, and more transparent solution. They also made it easier for me to inspect and debug the data while developing the project.

Another important design decision was separating the schedule output into two files:

- `schedule.txt` for the raw AI output
- `final_schedule.txt` for the formatted version

I chose this approach so the program would not need to re-parse and reformat the same schedule every time it had to be displayed.

I also decided to store the API key in `gemini_api_key.txt` instead of hardcoding it. This makes the project more portable and secure, since any user can run the application with their own credentials.

The most difficult parts of this project were handling continuous file I/O and integrating the Gemini API.

Because the program constantly reads from and writes to files, I had to be very careful with how data moved through the program. I improved this part by reviewing the CS50P lectures on file I/O and applying those concepts carefully.

The Gemini integration was also a major challenge. Making the API accept file attachments together with custom prompts and system instructions required a lot of documentation reading, experimentation, and trial and error until I got the request format working correctly.

---

## Testing and Future Improvements

At the moment, `test_project.py` mainly tests the **happy paths** of the program. It checks that tasks can be processed correctly and that files are written properly.

In the future, I would like to expand the tests to include invalid-input cases, such as:

- incorrect date formats
- impossible dates
- invalid priority values
- network failure simulations

One known limitation is that if the internet connection is lost during API key validation, the program may crash. Also, if Gemini fails during schedule generation, the program may keep looping without showing a clear error message.

I would also like to add a **graphical user interface (GUI)** and make Schedulit generate **three different weekly schedule options at once**, so the user can choose the one that fits their personal working style best.
