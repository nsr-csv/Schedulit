from project import Todo
from project import todo
from project import gen
from project import gen_edit

import pytest
import re


def file_exist(file_path):
    try:
        with open(file_path):
            return True

    except:
        return False


todo_list_test = Todo()


def test_todo_add():
    with open("todo_list.csv") as todo_list_reader:
        lines = todo_list_reader.readlines()
        assert lines[0] == "Priority,Task,Due Date,Status\n"

    options_and_input = iter(["add", "TEST", "09/09/9999", "10", "back", "exit"])

    def inputs(_):
        return next(options_and_input)

    todo(todo_list_test, inputs)

    with open("todo_list.csv") as todo_list_reader:
        lines = todo_list_reader.readlines()
        assert lines[-1] == "10,TEST,09/09/9999,incomplete\n"


def test_todo_done():
    options_and_input = iter(["done", "1", "back"])

    def inputs(_):
        return next(options_and_input)

    todo(todo_list_test, inputs)

    assert re.search(r"^.\[9m(.*).\[0m$", todo_list_test.todo_list_file[0]["Task"])
    assert todo_list_test.todo_list_file[0]["Status"] == "done"

    options_and_input = iter(["done", "1", "back", "exit"])

    todo(todo_list_test, inputs)

    assert not re.search(r"^.\[9m(.*).\[0m$", todo_list_test.todo_list_file[0]["Task"])
    assert todo_list_test.todo_list_file[0]["Status"] == "incomplete"


def test_todo_edit():
    options_and_input = iter(
        [
            "edit",
            "1",
            "priority",
            "1",
            "task",
            "Test edit",
            "due date",
            "12/12/9999",
            "back",
            "exit",
        ]
    )

    def inputs(_):
        return next(options_and_input)

    todo(todo_list_test, inputs)

    assert todo_list_test.todo_list_file[0] == {
        "Due Date": "12/12/9999",
        "Priority": "1",
        "Status": "incomplete",
        "Task": "Test edit",
    }


def test_todo_del():
    list_length = len(todo_list_test.todo_list_file)

    options_and_input = iter(["del", str(list_length), "exit"])

    def inputs(_):
        return next(options_and_input)

    todo(todo_list_test, inputs)

    assert len(todo_list_test.todo_list_file) < list_length


def test_todo_clear():
    todo_list_backup = todo_list_test.todo_list_file

    options_and_input = iter(["clear", "yes", "exit"])

    def inputs(_):
        return next(options_and_input)

    todo(todo_list_test, inputs)

    assert todo_list_test.todo_list_file == []

    todo_list_test.todo_list_file = todo_list_backup

    todo_list_test.save()


def test_gen():
    global final_schedule

    options_and_input = iter(["commitments_for_testing.txt", "no", "back", "exit"])

    def inputs(_):
        return next(options_and_input)

    gen(todo_list_test, inputs)

    assert file_exist("final_schedule.txt")

    with open("final_schedule.txt") as file:
        final_schedule = file.readlines()


def test_gen_edit():
    options_and_input = iter(
        [
            "commitments_for_testing.txt",
            "yes",
            "make the last row say 'this_is_a_test'",
            "no",
            "back",
            "exit",
        ]
    )

    def inputs(_):
        return next(options_and_input)

    gen(todo_list_test, inputs)

    with open("final_schedule.txt") as file:
        final_schedule_edited = file.readlines()

    assert final_schedule != final_schedule_edited


def test_todo_completed_priority_edit_and_reopen():
    options_and_input = iter([
        "clear", "yes", "add", "TEST", "01/01/2027", "8",
        "done", "1", "edit", "1", "priority", "5", "back", "exit",
    ])

    def inputs(_):
        return next(options_and_input)

    todo(todo_list_test, inputs)
    assert todo_list_test.todo_list_file[0]["Priority"] == "\x1b[9m5\x1b[0m"
    assert todo_list_test.todo_list_file[0]["Status"] == "done"

    options_and_input = iter(["done", "1", "exit"])
    todo(todo_list_test, inputs)
    assert todo_list_test.todo_list_file[0] == {
        "Priority": "5", "Task": "TEST", "Due Date": "01/01/2027",
        "Status": "incomplete",
    }


def test_todo_completed_date_edit_and_reopen():
    options_and_input = iter([
        "clear", "yes", "add", "TEST", "01/01/2027", "8",
        "done", "1", "edit", "1", "due date", "02/01/2027", "back", "exit",
    ])

    def inputs(_):
        return next(options_and_input)

    todo(todo_list_test, inputs)
    assert todo_list_test.todo_list_file[0]["Due Date"] == "\x1b[9m02/01/2027\x1b[0m"
    assert todo_list_test.todo_list_file[0]["Status"] == "done"

    options_and_input = iter(["done", "1", "exit"])
    todo(todo_list_test, inputs)
    assert todo_list_test.todo_list_file[0] == {
        "Priority": "8", "Task": "TEST", "Due Date": "02/01/2027",
        "Status": "incomplete",
    }


def test_todo_empty_options():
    options_and_input = iter(["clear", "yes", "done", "edit", "del", "exit"])

    def inputs(_):
        return next(options_and_input)

    todo(todo_list_test, inputs)
    assert todo_list_test.todo_list_file == []


def test_todo_back_from_selection():
    options_and_input = iter([
        "clear", "yes", "add", "TEST", "01/01/2027", "8",
        "done", "BACK", "edit", "BACK", "del", "BACK", "exit",
    ])

    def inputs(_):
        return next(options_and_input)

    todo(todo_list_test, inputs)
    assert todo_list_test.todo_list_file[0] == {
        "Priority": "8", "Task": "TEST", "Due Date": "01/01/2027",
        "Status": "incomplete",
    }


def test_todo_reopen_old_edited_task():
    todo_list_test.todo_list_file = [{
        "Priority": "5", "Task": "\x1b[9mTEST\x1b[0m",
        "Due Date": "02/01/2027", "Status": "done",
    }]
    todo_list_test.save()
    options_and_input = iter(["done", "1", "exit"])

    def inputs(_):
        return next(options_and_input)

    todo(todo_list_test, inputs)
    assert todo_list_test.todo_list_file[0] == {
        "Priority": "5", "Task": "TEST", "Due Date": "02/01/2027",
        "Status": "incomplete",
    }
