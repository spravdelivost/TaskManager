from tkinter import *
from tkinter import messagebox, END
from datetime import datetime
from tkinter import Toplevel, Label, Entry, Button
from tkcalendar import Calendar
import time
import pygame

music_playing = False

def edit_task():
    selected_task_index = task_listbox.curselection()

    if not selected_task_index:
        messagebox.showinfo("Error", "No task selected.")
        return

    task_info = task_listbox.get(selected_task_index[0])

    if ' | Due: ' in task_info:
        task, due_date_str = task_info.split(' | Due: ')
    elif ' | due: ' in task_info:
        task, due_date_str = task_info.split(' | due: ')
    else:
        messagebox.showinfo("Error", "Unexpected task format.")
        return

    try:
        due_date = datetime.strptime(due_date_str, "%m/%d/%y")

        if deadline_has_passed(due_date):
            messagebox.showinfo("Task Edit", f"The deadline for '{task}' has passed. Editing not allowed.")
            return

        edit_top = Toplevel()
        edit_top.title("Edit Task")
        edit_top.geometry("300x150")

        task_entry_edit = Entry(edit_top, font=('Helvetica', 14), relief=SOLID)
        task_entry_edit.insert(0, task)
        task_entry_edit.pack(pady=10)

        def update_task():
            new_task = task_entry_edit.get()
            if new_task:
                task_listbox.delete(selected_task_index)
                task_listbox.insert(selected_task_index, f"{new_task} | Due: {due_date_str}")
                edit_top.destroy()
            else:
                messagebox.showinfo("Error", "Task cannot be empty.")

        confirm_button = Button(edit_top, text="Confirm Edit", command=update_task, bg="#4CAF50", fg="white", relief=FLAT)
        confirm_button.pack(pady=10)

    except ValueError:
        messagebox.showinfo("Invalid Due Date", "Error parsing due date.")


def edit_deadline():
    selected_task_index = task_listbox.curselection()

    if not selected_task_index:
        messagebox.showinfo("Error", "No task selected.")
        return

    refresh_top = Toplevel()
    refresh_top.title("Refresh Deadline")
    refresh_top.geometry("300x150")

    def refresh_deadline():
        new_due_date_str = select_due_date()

        if new_due_date_str:
            try:
                new_due_date = datetime.strptime(new_due_date_str, "%m/%d/%y")
                current_date = datetime.now()

                if new_due_date <= current_date:
                    messagebox.showinfo("Invalid Due Date", "The due date has already passed.")
                else:
                    task_info = task_listbox.get(selected_task_index[0])
                    task, _ = task_info.split(' | Due: ')
                    task_listbox.delete(selected_task_index)
                    task_listbox.insert(selected_task_index, f"{task} | Due: {new_due_date_str}")
                    refresh_top.destroy()

            except ValueError:
                messagebox.showinfo("Invalid Due Date", "Error parsing due date.")

    refresh_button = Button(refresh_top, text="Change Deadline", command=refresh_deadline, bg="#4CAF50", fg="white", relief=FLAT)
    refresh_button.pack(pady=10)


def add_task():
    task = task_entry.get()

    if not task:
        messagebox.showinfo("Error", "Write down the task")
        return

    due_date_str = select_due_date()

    if task and due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, "%m/%d/%y")
            current_date = datetime.now()

            if due_date <= current_date:
                messagebox.showinfo("Invalid Due Date", f"The due date for '{task}' has already passed.")
            else:
                task_listbox.insert(END, f"{task} | Due: {due_date_str}")
                task_entry.delete(0, END)

        except ValueError:
            messagebox.showinfo("Invalid Due Date", "Please select a valid date format (MM/DD/YY).")


def select_due_date():
    def grab_date():
        due_date_str = cal.get_date()
        my_label.config(text="Due date is " + due_date_str)
        top.after(500, lambda: top.destroy())
        top.due_date_str = due_date_str

    top = Toplevel()
    top.title("Calendar")
    top.geometry("300x280")
    top.resizable(False, False)

    cal = Calendar(top, selectmode='day', year=time.localtime().tm_year, month=time.localtime().tm_mon, day=time.localtime().tm_mday)
    cal.pack(pady=10)

    my_button = Button(top, text="Set Date", command=grab_date, bg="#4CAF50", fg="white", relief=FLAT)
    my_button.pack(pady=10)
    my_label = Label(top, text='')
    my_label.pack(pady=10)

    top.wait_window(top)

    return getattr(top, 'due_date_str', None)


def remove_task():
    selected_task_index = task_listbox.curselection()

    if not selected_task_index:
        messagebox.showinfo("Error", "No task selected.")
        return

    task_info = task_listbox.get(selected_task_index[0])

    if ' | Due: ' in task_info:
        task, due_date_str = task_info.split(' | Due: ')
    else:
        messagebox.showinfo("Error", "Unexpected task format.")
        return

    try:
        due_date = datetime.strptime(due_date_str, "%m/%d/%y")

        if deadline_has_passed(due_date):
            confirmation = messagebox.askyesno('Task Removal', f"The deadline for '{task}' has passed. Do you still want to delete it?")
            if confirmation:
                task_listbox.delete(selected_task_index[0])
            else:
                messagebox.showinfo("Task Removal", "Deletion of '{task}' canceled.")
        else:
            confirmation = messagebox.askyesno('Alert', f"Do you really want to delete task: {task} ?")
            if confirmation:
                task_listbox.delete(selected_task_index)
            else:
                messagebox.showinfo("Task Removal", "Deletion of '{task}' canceled.")

    except ValueError:
        messagebox.showinfo("Invalid Due Date", "Error parsing due date.")

def deadline_has_passed(due_date):
    current_date = datetime.now()
    return due_date < current_date

def on_enter_key(event):
    add_task()

def on_delete_key(event):
    remove_task()

def check_deadlines():
    current_date = datetime.now()
    for index in range(task_listbox.size()):
        task_info = task_listbox.get(index)
        if ' | Due: ' in task_info:
            task, due_date_str = task_info.split(' | Due: ')
            try:
                due_date = datetime.strptime(due_date_str, "%m/%d/%y")
                if current_date >= due_date:
                    messagebox.showinfo("Deadline Alert", f"The deadline for '{task}' has passed!")
            except ValueError:
                pass
    root.after(60000, check_deadlines)

def toggle_music():
    global music_playing
    if not music_playing:
        play_music()
        music_playing = True
    else:
        stop_music()
        music_playing = False


def play_music():
    global music_playing
    music_playing = True
    pygame.mixer.init()
    pygame.mixer.music.load("minecraft.mp3")
    pygame.mixer.music.play()

def stop_music():
    global music_playing
    if music_playing:
        pygame.mixer.music.stop()
root = Tk()
root.title("Task Manager")
root.geometry('600x600')
root.resizable(width=False, height=False)

frame = Frame(root, bg='#f9f9f9', bd=5)
frame.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.8)

title = Label(frame, text='Task Manager', bg='#f9f9f9', fg='#333', font=('times', 18, 'bold'))
title.pack(pady=10)

task_entry = Entry(frame, bg='#ecf0f1', font=('Helvetica', 16), relief=SOLID)
task_entry.pack(pady=10, padx=10, ipady=5, fill=X)

button_color = "grey"

add_button = Button(frame, text="Add Task", command=add_task, bg=button_color, fg="white", relief=FLAT)
add_button.place(x=10, y=110, width=100, height=40)

remove_button = Button(frame, text="Remove Task", command=remove_task, bg=button_color, fg="white", relief=FLAT)
remove_button.place(x=130, y=110, width=100, height=40)

edit_button = Button(frame, text="Edit Task", command=edit_task, bg=button_color, fg="white", relief=FLAT)
edit_button.place(x=250, y=110, width=100, height=40)

refresh_button = Button(frame, text="Edit Deadline", command=edit_deadline, bg=button_color, fg="white", relief=FLAT)
refresh_button.place(x=370, y=110, width=100, height=40)

task_listbox = Listbox(frame, bg='#ecf0f1', font=('Helvetica', 16), selectbackground='#3498DB', selectmode=SOLID, bd=0)
task_listbox.pack(pady=45, padx=10, fill=BOTH, expand=True)

task_entry.bind('<Return>', on_enter_key)
root.bind('<Delete>', on_delete_key)

check_deadlines()

music_button = Button(root, text="Music", command=toggle_music, bg=button_color, fg="white", relief=FLAT)
music_button.place(relx=0.8, rely=0.92, width=80, height=40)

root.mainloop()
