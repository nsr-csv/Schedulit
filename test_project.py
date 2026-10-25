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

    if re.search(r"^.\[9(.*).\[0m$", todo_list_test.todo_list_file[0]["Task"]):
        assert True

    options_and_input = iter(["done", "1", "back", "exit"])

    todo(todo_list_test, inputs)

    if not re.search(r"^.\[9(.*).\[0m$", todo_list_test.todo_list_file[0]["Task"]):
        assert True


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
