"""
A time tracker application 
"""
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import *
import sqlite3
import ttkbootstrap as ttk

#* global variables
newActivity = []

class StopWatch(Frame):
    def __init__(self, parent = None, **kw):
        Frame.__init__(self, parent, kw)
        self._start = datetime.now()
        self._elapsedtime = 0.0
        self._running = 0
        self.timestr = StringVar()
        self.make_widgets()

    #creates widget
    def make_widgets(self):
        time = ttk.Label(self, textvariable=self.timestr)
        self._set_time(self._elapsedtime)
        time.pack()

    #calculatees elapsed time, updates widget
    def _update(self):
        self._elapsedtime = (datetime.now() - self._start).total_seconds()
        self._set_time(self._elapsedtime)
        self._timer = self.after(50, self._update)

    #format the time
    def _set_time(self, elap):
        minutes = int(elap/60)
        hours = int(minutes/60)
        seconds = int(elap - minutes*60.0)
        self.timestr.set(f'{hours:02d}:{minutes % 60:02d}:{seconds:02d}')

    #start
    def start(self, start_status, stop_status, add_status):
        """
        starts stpowatch, sets status of timers 
        Args:
            start_status (string): flag for start button status.
            stop_status (string): flag for stop button status.
            add_status (string): flag for add button status.
        """
        if not self._running:
            self._start = datetime.now() - timedelta(seconds=self._elapsedtime)
            self._update()
            self._running = 1
            #set the status of buttons
            stop_status.set("enabled")
            start_status.set("disabled")
            add_status.set("disabled")

    #stop
    def stop(self, start_status, stop_status, reset_save_status):
        """
        stops the stopwatch, sets status of some buttons
        Args:
            start_status (string): flag for start button status.
            stop_status (string): flag for stop button status.
            reset_save_status (string): flag for reset and save button status.
        """
        if self._running:
            self.after_cancel(self._timer)
            self._elapsedtime = (datetime.now() - self._start).total_seconds()
            self._set_time(self._elapsedtime)
            self._running = 0
            #set the status of buttons
            start_status.set("enabled")
            reset_save_status.set("enabled")
            stop_status.set("disabled")

    def reset(self, start_status,stop_status, reset_save_status, add_status):
        """
        Resets the newActivity variable, changes button status, resets stopwatch.
        Args:
            start_status (string): flag for start button status.
            stop_status (string): flag for stop button status.
            reset_save_status (string): flag for reset and save button status.
            add_status (string): flag for add button status.
        """
        self._start = datetime.now()
        self._elapsedtime = 0.0
        self._set_time(self._elapsedtime)
        #set the status of buttons
        start_status.set("disabled")
        stop_status.set("disabled")
        reset_save_status.set("disabled")
        add_status.set("enabled")
        newActivity.clear()

    def save(self, connection, start_status, stop_status, reset_save_status, add_status):
        """
        Saves the newActivity list to the db.
        Args:
            connection (connector): connection to sqlite db
            start_status (string): flag for start button status.
            stop_status (string): flag for stop button status.
            reset_save_status (string): flag for reset and save button status.
            add_status (string): flag for add button status.
        """
        cursor = connection.cursor()
        end_time =self._start+timedelta(seconds=self._elapsedtime)
        newActivity.append(int((self._start).strftime("%Y%m%d%H%M%S")))
        newActivity.append(int(end_time.strftime("%Y%m%d%H%M%S")))
        newActivity.append(int(self._elapsedtime))
        cursor.execute("insert into activity values (?,?,?,?)",newActivity)
        connection.commit()
        newActivity.clear()
        self.reset(start_status,stop_status, reset_save_status, add_status)
        #set the status of buttons
        start_status.set("disabled")
        stop_status.set("disabled")
        reset_save_status.set("disabled")
        add_status.set("enabled")

def add_name(name, start_status):
    """
    adds the name of the task, enables the start button

    Args:
        name(string):name to be added.
        start_status(string): flag for start button status
    """
    newActivity.append(name)
    #set the status of buttons
    start_status.set("enabled")

def home_window():
    """
    function to build the app
    """
    #*connect to db
    connection = sqlite3.connect("tracker.db")
    cursor = connection.cursor()

    #* create a new table if it doesn't already exist
    cursor.execute("create table if not exists activity (name text, start_time integer, end_time integer, time_delta integer )")

    #TODO make the app appear in center
    #TODO make the app stay on top?
    #TODO make window adaptive?
    #* create a window
    window = ttk.Window(themename = 'darkly')
    window.title('Time Tracker')
    window.geometry('600x300')

    #* button status
    start_status = tk.StringVar(value="disabled")
    stop_status = tk.StringVar(value="disabled")
    reset_save_status = tk.StringVar(value="disabled")
    #TODO enable only if dropdown or entry filled?
    add_status = tk.StringVar(value="enabled")

    #* frames
    activity_frame = ttk.Frame(master=window)#activity frame
    stopwatch_frame = ttk.Frame(master=window)#stopwatch frame
    selected_activity_frame = ttk.Frame(master=window)#frame for the selected activity
    activity_frame.pack()
    selected_activity_frame.pack()
    stopwatch_frame.pack()

    #* selection label 1
    # #for when dropdown is implemented
    # ttk.Label(master = activity_frame, text= 'Select activity:').grid(row=1, column= 0)
    ttk.Label(master = activity_frame, text= 'Enter task:').grid(row=1, column= 0)

    #!not implemented yet
    #*set dropdown values
    #TODO add a "example" text: "select existing"
    # df = pd.read_sql_query('select name from activity group by name', connection)
    # dropdown_values = df['name'].tolist()
    # print(type(dropdown_values))
    #TODO make it one or the other


    #* dropdown selector
    # dropdown_input = tk.StringVar()# the input
    # dropdown = ttk.Combobox(master=activity_frame, width = 25, textvariable= dropdown_input)
    # dropdown['values']=dropdown_values
    # dropdown.grid(column=1, row=1)
    #TODO call add_name with dropdown_input, make it contidonal
    #TODO if both dropdown and text are filled and 
    #'add' is clicked, throw an error and clear everything, restarting
    # #* selection label 2
    # ttk.Label(master = activity_frame, text= 'or enter new activity:').grid(column=2, row=1)

    #* entry field
    entry_input = tk.StringVar()
    entry = ttk.Entry(master= activity_frame, textvariable = entry_input)
    entry.grid(column=3, row=1)

    #* add button
    add_button = ttk.Button(
        master =activity_frame ,
        text = 'add', command= lambda: [add_name(entry_input.get(),
                                                 start_status),
                                                 update_activity_label(),
                                                 entry.delete(0,END)],
        cursor='hand2',
        state = add_status.get())
    add_button.grid(column=4, row=1)

    #TODO include a change button that clears the entries and resets the dropdown and textbox
    # make it so while the timer is running, the add button and change button are inactive.
    # currently the reset button clears everyting because there's no way to separate these currently.
    # clear_activity_label()
    # entry.delete(0,END)
    # newActivity.clear()

    #* selected label
    ttk.Label(master = selected_activity_frame, text= 'Current task:').pack(side = 'left')
    activity_label = ttk.Label(master = selected_activity_frame, text = "__")
    activity_label.pack(side = 'left')

    #function that changes the label of selected task
    def update_activity_label():
        activity_label.configure(text= entry_input.get())
    #function that clears label of selected task
    def clear_activity_label():
        activity_label.configure(text= "__")

    #* stopwatch
    stopwatch = StopWatch(stopwatch_frame)
    stopwatch.pack()

    #* stopwatch buttons
    start_button = ttk.Button(stopwatch_frame,
                              text='Start',
                              command= lambda: stopwatch.start(start_status, stop_status, add_status),
                              cursor='hand2',
                              state = start_status .get())
    stop_button = ttk.Button(stopwatch_frame,
                             text='Stop',
                             command= lambda: stopwatch.stop(start_status, stop_status, reset_save_status),
                             cursor='hand2',
                             state = stop_status.get())
    reset_button = ttk.Button(stopwatch_frame,
                              text='Reset',
                              command= lambda: [stopwatch.reset(start_status, stop_status, reset_save_status,add_status), clear_activity_label()],
                              cursor='hand2',
                              state = reset_save_status.get())
    save_button = ttk.Button(stopwatch_frame,
                             text = 'Save',
                             command = lambda: [stopwatch.save(connection, start_status, stop_status, reset_save_status,add_status),
                                                entry_input.set(""), refresh_table()],
                             cursor='hand2',
                             state = reset_save_status.get())

    start_button.pack(side = 'left')
    stop_button.pack(side = 'left')
    reset_button.pack(side = 'left')
    save_button.pack(side = 'left')

    #TODO once the start is clicked, the add is unuseable

    #* query to get total time/name
    table_data = cursor.execute("select name, SUM(time_delta) as total_time from activity group by name")

    #* table to display data
    table = ttk.Treeview(window)
    table['columns'] = ('Name', 'Total time')
    table.column('#0', width=0, anchor = CENTER, stretch = False)
    for col in table['columns']:
        table.column(col, width=100, anchor=CENTER)
        table.heading(col, text=col.title())
    for name, total_time in table_data:
        hours = total_time // 3600
        minutes = (total_time % 3600) // 60
        seconds = total_time % 60
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        table.insert('', 'end', values=(name, time_str))
    table.pack()

    def refresh_table():
        #clear table
        for row in table.get_children():
            table.delete(row)
        #get updated data
        updated_table_data = cursor.execute("select name, SUM(time_delta) as total_time from activity group by name")
        #set updated data
        for name, total_time in updated_table_data:
            hours = total_time // 3600
            minutes = (total_time % 3600) // 60
            seconds = total_time % 60
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            table.insert('', 'end', values=(name, time_str))
            # table.insert('', 'end',values=item)

    #* functions to change the active state of buttons
    #the *args are extra params passed by the trace_add function
    def update_start(*args):
        new_state = start_status.get()
        start_button.config(state=new_state)

    def update_stop(*args):
        new_state = stop_status.get()
        stop_button.config(state=new_state)

    def update_reset_save(*args):
        new_state = reset_save_status.get()
        reset_button.config(state=new_state)
        save_button.config(state=new_state)

    def update_add(*args):
        new_state = add_status.get()
        add_button.config(state = new_state)

    #* traces
    start_status.trace_add("write", update_start)
    stop_status.trace_add("write", update_stop)
    reset_save_status.trace_add("write", update_reset_save)
    add_status.trace_add("write", update_add)

    # #* prints db
    # for row in cursor.execute("select * from activity"):
    #     print(row)

    #* commit and close db
    connection.commit()
    connection.close()
    return window

if __name__ == '__main__':
    window = home_window()
    window.mainloop()

#54 min
