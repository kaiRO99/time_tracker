"""
A time tracker application 
"""
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import Frame, StringVar, CENTER, END
import sqlite3
import ttkbootstrap as ttk
import pandas as pd

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
        cursor.execute("INSERT INTO activity VALUES (?,?,?,?)",newActivity)
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
    start_status.set("enabled")

class home:
    def __init__(self):
        #connect to db
        self.connection = sqlite3.connect("tracker.db")
        self.cursor = self.connection.cursor()

        # create a new db table if it doesn't already exist
        self.cursor.execute("CREATE TABLE IF NOT EXISTS activity (name text, start_time integer, end_time integer, time_delta integer )")

        #? make the app appear in center
        #? make the app stay on top?
        #? make window adaptive?
        # create a window
        self.window = ttk.Window(themename = 'darkly')
        self.window.title('Time Tracker')
        self.window.geometry('600x400')

        # button status
        self.start_status = tk.StringVar(value="disabled")
        self.stop_status = tk.StringVar(value="disabled")
        self.reset_save_status = tk.StringVar(value="disabled")
        self.add_status = tk.StringVar(value="enabled")
        self.delete_status = tk.StringVar(value="disabled")

        self._create_frames()

        # task input
        self.entry_input = tk.StringVar()
        self._create_task_input()
        
        # task label
        self._create_task_label()

        # stopwatch
        self.stopwatch = StopWatch(self.stopwatch_frame)
        self.stopwatch.pack()

        # stopwatch buttons
        self._create_stopwatch_buttons()
        
        # table
        self._create_table()
        
        # delete section
        self.delete_input = tk.StringVar()
        self._create_dropdown()
        self._create_delete_button()
        
        # Bind status updates
        self._bind_status_updates()

        self.window.mainloop()
    
    def _create_frames(self):
        """
        creates and '.pack' frames
        """
        padding = 5
        self.activity_frame = ttk.Frame(master=self.window)#activity frame
        self.stopwatch_frame = ttk.Frame(master=self.window)#stopwatch frame
        self.selected_task_frame = ttk.Frame(master=self.window)#frame for the selected activity
        self.table_frame = ttk.Frame(master = self.window)#frame for table 
        self.delete_frame = ttk.Frame(master=self.window)#frame for the deletion

        self.activity_frame.pack(pady = padding)
        self.selected_task_frame.pack(pady = padding)
        self.stopwatch_frame.pack(pady = padding)
        self.table_frame.pack(pady = padding)
        self.delete_frame.pack(pady = padding)
        
    def _create_task_input(self):
        # selection label 1
        # #for when dropdown is implemented
        # ttk.Label(master = activity_frame, text= 'Select activity:').grid(row=1, column= 0)
        ttk.Label(master = self.activity_frame, text= 'Enter task:').grid(row=1, column= 0)

        """
        not implemented yet/is it even required or useful?
        """
        #set dropdown values
        #TO DO add a "example" text: "select existing"
        # df = pd.read_sql_query('select name from activity group by name', connection)
        # dropdown_values = df['name'].tolist()
        # print(type(dropdown_values))
        #TO DO make it one or the other

        # dropdown selector
        # dropdown_input = tk.StringVar()# the input
        # dropdown = ttk.Combobox(master=activity_frame, width = 25, textvariable= dropdown_input)
        # dropdown['values']=dropdown_values
        # dropdown.grid(column=1, row=1)
        #TO DO call add_name with dropdown_input, make it contidonal
        #TO DO if both dropdown and text are filled and 
        #'add' is clicked, throw an error and clear everything, restarting
        
        # # selection label 2
        # ttk.Label(master = activity_frame, text= 'or enter new activity:').grid(column=2, row=1)

        # entry field
        self.entry = ttk.Entry(master= self.activity_frame, textvariable = self.entry_input)
        self.entry.grid(column=3, row=1)

        # add button
        self.add_button = ttk.Button(
            master =self.activity_frame ,
            text = 'Add', command= self._add,
            cursor='hand2',
            state = self.add_status.get())
        self.add_button.grid(column=4, row=1)
    
    def _bind_status_updates(self):
        """
        traces for buttons 
        """
        self.start_status.trace_add("write", self._update_start)
        self.stop_status.trace_add("write", self._update_stop)
        self.reset_save_status.trace_add("write", self._update_reset_save)
        self.add_status.trace_add("write", self._update_add)
        self.delete_status.trace_add("write", self._update_delete)
    
    def _add(self):
        """
        called when "Add" button clicked. 
        Clears 'newActivity' list, calls add_name, updates label and clears entry 
        """
        newActivity.clear() #make sure it is empty before adding a new one
        add_name(self.entry_input.get(), self.start_status)
        self._update_task_label()
        self.entry.delete(0, END)
        
    def _create_task_label(self):
        """
        "Current task:" label
        """
        ttk.Label(master = self.selected_task_frame, text= 'Current task:').pack(side = 'left')
        self.activity_label = ttk.Label(master = self.selected_task_frame, text = "")
        self.activity_label.pack(side = 'left')
    
    def _update_task_label(self):
        """
        function that changes the label of selected task
        """
        self.activity_label.configure(text= self.entry_input.get())

    def _clear_task_label(self):
        """
        clears the "current task" label 
        """
        self.activity_label.configure(text= "")
    
    def _create_stopwatch_buttons(self):
        """
        cretaes buttons for stopwatch
        """
        self.start_button = ttk.Button(self.stopwatch_frame,
                                text='Start',
                                command= lambda: self.stopwatch.start(self.start_status, self.stop_status, self.add_status),
                                cursor='hand2',
                                state = self.start_status .get())
        self.stop_button = ttk.Button(self.stopwatch_frame,
                                text='Stop',
                                command= lambda: self.stopwatch.stop(self.start_status, self.stop_status, self.reset_save_status),
                                cursor='hand2',
                                state = self.stop_status.get())
        self.reset_button = ttk.Button(self.stopwatch_frame,
                                text='Reset',
                                command= lambda: [self.stopwatch.reset(self.start_status, self.stop_status, self.reset_save_status,self.add_status), self.clear_task_label()],
                                cursor='hand2',
                                state = self.reset_save_status.get())
        self.save_button = ttk.Button(self.stopwatch_frame,
                                text = 'Save',
                                command = lambda: [self.stopwatch.save(self.connection, self.start_status, self.stop_status, self.reset_save_status,self.add_status),
                                                    self.entry_input.set(""), self.refresh_table(),self._clear_task_label(), self._refresh_dropdown()],
                                cursor='hand2',
                                state = self.reset_save_status.get())
        self.start_button.pack(side = 'left')
        self.stop_button.pack(side = 'left')
        self.reset_button.pack(side = 'left')
        self.save_button.pack(side = 'left')
    
    def _create_table(self):
        """
        creates table to display data
        """
        self.table = ttk.Treeview(self.table_frame)
        self.table['columns'] = ('Name', 'Total time')
        self.table.column('#0', width=0, anchor = CENTER, stretch = False)
        for col in self.table['columns']:
            self.table.column(col, width=100, anchor=CENTER)
            self.table.heading(col, text=col.title())
        self.refresh_table()
        self.table.pack()
    
    def refresh_table(self):
        """
        refreshes the table. Also called on initialisation
        """
        for row in self.table.get_children():
            self.table.delete(row)
        table_data = self.cursor.execute("SELECT name, SUM(time_delta) AS total_time FROM activity GROUP BY name")
       
        for name, total_time in table_data:
            hours = total_time // 3600
            minutes = (total_time % 3600) // 60
            seconds = total_time % 60
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.table.insert('', 'end', values=(name, time_str))
            
    def _create_dropdown(self):
        """
        dropdown menu with tasks in db
        """
        self.dropdown = ttk.Combobox(master=self.delete_frame,
                                     width = 25,
                                     textvariable= self.delete_input,
                                     state = 'readonly')
        self._refresh_dropdown()
        self.dropdown.bind('<<ComboboxSelected>>', self._dropbox_changed)
        self.dropdown.pack(side='left')
         
    def _dropbox_changed(self, event=None):
        """
        triggered when the dropdown value changes
        Args:
            event: .bind sends an event object as well
        """
        self.delete_status.set("enabled")
        
    #? add a confirmation pop-up? 
    def _create_delete_button(self):
        """
        button for deleteion of a task 
        """
        self.delete_button = ttk.Button(self.delete_frame,
                                text='Delete',
                                command= lambda: [self._delete_task()],
                                cursor='hand2',
                                state=self.delete_status.get())
        self.delete_button.pack(side='left')
        
    def _delete_task(self):
        """
        deletes a task from the db, refreshes: table, dropdown and button status
        """
        self.cursor.execute("DELETE FROM activity WHERE name = '%s'" %self.delete_input.get())
        self.connection.commit()
        self.refresh_table()
        self._refresh_dropdown()
        self.delete_status.set("disabled")
        self.dropdown.set('')

    def _refresh_dropdown (self):
        """
        refreshes the deleteion dropdown menu when a task is added or deleted. Also called on initialisation
        """
        self.df = pd.read_sql_query('select name from activity group by name', self.connection)
        self.dropdown_values = self.df['name'].tolist()
        self.dropdown['values']=self.dropdown_values
    
    """
    methods to update states of buttons

    Args:
        (*args): extra params passed by the trace_add function
    """
    def _update_start(self, *args):
        new_state = self.start_status.get()
        self.start_button.config(state=new_state)

    def _update_stop(self, *args):
        new_state = self.stop_status.get()
        self.stop_button.config(state=new_state)

    def _update_reset_save(self, *args):
        new_state = self.reset_save_status.get()
        self.reset_button.config(state=new_state)
        self.save_button.config(state=new_state)

    def _update_add(self, *args):
        new_state = self.add_status.get()
        self.add_button.config(state = new_state)
        
    def _update_delete(self, *args):
        new_state = self.delete_status.get()
        self.delete_button.config(state = new_state)
        
if __name__ == '__main__':
    home()