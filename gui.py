import sys
import ctypes
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import OptionMenu
from tkinter import StringVar
from tkinter import ttk
from tkinter import PhotoImage
from tkinter import Label
from tkinter.ttk import Progressbar

try:
    def get_scenarios():
        return ['a', 'b', 'c']

    def browse_output():
        global output_directory
        output_directory = filedialog.askdirectory()
        input_scenarioName = dropdownMenu.get()
        if len(input_scenarioName) > 0:
            pathlabel_outputDir.config(text='Output directory: ' + output_directory + '/' + input_scenarioName)
        else:
            pathlabel_outputDir.config(text='Output directory: ' + output_directory)     

    def browse_policy():
        global policy_directory
        policies = filedialog.askopenfilename(filetypes=[('Shapefiles', '*.shp')])
        policy_directory = [x for x in root.tk.splitlist(policies)]

    def browse_depths():
        global depths_directory
        depths = filedialog.askopenfilenames(parent=root, title='Choose spatial depth data')
        depths_directory = [x for x in root.tk.splitlist(depths)]

    def on_field_change(index, value, op):
        try:
            input_scenarioName = dropdownMenu.get()
            check = input_scenarioName in output_directory
            if not check:
                pathlabel_outputDir.config(text='Output directory: ' + output_directory + '/' + input_scenarioName)           
        except:
            pass

    def getTextFields():
        dict = {
            'title': text_title.get("1.0",'end-1c'),
            'meta': text_meta.get("1.0",'end-1c')
        }
        return dict
        
    def busy():
        root.config(cursor="wait")

    def notbusy():
        root.config(cursor="")

    def focus_next_widget(event):
        event.widget.tk_focusNext().focus()
        return("break")

    def run():
        root.geometry(str(root_w)+ 'x' + str(root_h + 50))
        busy()
        inputs = getTextFields()
        inputs.update({'study_region': dropdownMenu.get()})
        inputs.update({'output_directory': output_directory})
        inputs.update({'opt_csv': opt_csv.get()})
        inputs.update({'opt_shp': opt_shp.get()})
        inputs.update({'opt_report': opt_report.get()})
        # input_scenarioName = dropdownMenu.get()
        progress = Progressbar(length = 100, mode = 'indeterminate')
        progress.grid(row=row, pady=(10,0))
        progress['value'] = 0
        root.update_idletasks()
        label_progress = tk.Label(root, text='connecting to database', font='Helvetica 8', bg='#282a36', fg='#f8f8f2', width = 60)
        label_progress.grid(row=14, sticky='N')
        try:
            t0 = time()
            progress['value'] = 50
            label_progress.config(text='importing hazard module')
            root.update_idletasks()
            print('Hazus results available locally at: ' + inputs['output_directory'] +
                '\\' + inputs['study_region'])
            progress.destroy()
            label_progress.destroy()
            notbusy()
            print('Total elasped time: ' + str(time() - t0))
            root.geometry(str(root_w) + 'x' + str(root_h))
            tk.messagebox.showinfo("Hazus", "Success! Output files can be found at: " + inputs['output_directory'] + '/' + inputs['study_region'])
        except:
            try:
                progress.destroy()
                label_progress.destroy()
            except:
                pass
            root.geometry(str(root_w) + 'x' + str(root_h))
            ctypes.windll.user32.MessageBoxW(None, u"Error: " + str(sys.exc_info()[1]), u'Hazus - Message', 0)
            
    # Create app
    root = tk.Tk()

    # App parameters
    root.title('Hazus Utility Generic GUI')
    root_h = 400
    root_w = 460
    root.geometry(str(root_w) + 'x' + str(root_h))
    root.configure(background='#282a36')

    #App icon
    # root.wm_iconbitmap('./assets/images/HazusHIcon.ico')

    # Init dynamic row
    row = 0

    # ttk styles classes
    style = ttk.Style()
    style.configure("BW.TCheckbutton", foreground="#f8f8f2", background="#282a36", side='LEFT')

    # App body
    
    # Input policy directory
    label_dir_policy = tk.Label(root, text='Select the policy point Shapefile:', font='Helvetica 10 bold', bg='#282a36', fg='#f8f8f2')
    label_dir_policy.grid(row=row, column=0, padx=20, pady=(30,0), sticky='W')

    # Input policy directory browse button
    browsebutton_dir_policy = tk.Button(root, text="Browse", command=browse_policy, relief='flat', bg='#44475a', fg='#f8f8f2', cursor="hand2", font='Helvetica 8 bold')
    browsebutton_dir_policy.grid(row=row, column=0, padx=(375, 0), pady=(30,0), sticky='W')
    browsebutton_dir_policy.bind("<Tab>", focus_next_widget)
    row += 1

    # Input depth directory
    label_dir_depths = tk.Label(root, text='Select the directory where the depth files are stored:', font='Helvetica 10 bold', bg='#282a36', fg='#f8f8f2')
    label_dir_depths.grid(row=row, column=0, padx=20, pady=(30,0), sticky='W')

    # Input depth directory browse button
    browsebutton_dir_depths = tk.Button(root, text="Browse", command=browse_depths, relief='flat', bg='#44475a', fg='#f8f8f2', cursor="hand2", font='Helvetica 8 bold')
    browsebutton_dir_depths.grid(row=row, column=0, padx=(375, 0), pady=(30,0), sticky='W')
    browsebutton_dir_depths.bind("<Tab>", focus_next_widget)
    row += 1

    # Output checkbox label
    label_outputMetadata = tk.Label(root, text='Check to export a point Shapefile with depths:', font='Helvetica 10 bold', bg='#282a36', fg='#f8f8f2')
    label_outputMetadata.grid(row=row, column=0, padx=20, pady=(30, 0), sticky='W')
    row += 1

    # Output checkbox options
    xpadl = 370
    opt_shp = tk.IntVar(value=0)
    ttk.Checkbutton(root, text="Shapefile", variable=opt_shp, style='BW.TCheckbutton').grid(row=row, padx=(xpadl,0), sticky='W')
    row += 1

    # Output directory label
    label_outputDir = tk.Label(root, text='Select a directory for the output files:', font='Helvetica 10 bold', bg='#282a36', fg='#f8f8f2')
    label_outputDir.grid(row=row, column=0, padx=20, pady=(30,0), sticky='W')

    # Output directory browse button
    browsebutton_dat = tk.Button(root, text="Browse", command=browsefunc, relief='flat', bg='#44475a', fg='#f8f8f2', cursor="hand2", font='Helvetica 8 bold')
    browsebutton_dat.grid(row=row, column=0, padx=(375, 0), pady=(30,0), sticky='W')
    browsebutton_dat.bind("<Tab>", focus_next_widget)
    row += 1

    # Output directory path label
    pathlabel_outputDir = tk.Label(root, bg='#282a36', fg='#f8f8f2', font='Helvetica 8')
    pathlabel_outputDir.grid(row=row, column=0, pady=(5, 20), padx=30, sticky='W')
    row += 1

    # Run button
    button_run = tk.Button(root, text='Run', width=20, command=run, relief='flat', bg='#6272a4', fg='#f8f8f2', cursor="hand2", font='Helvetica 8 bold')
    button_run.grid(row=row, column=0, padx=160, pady=(10, 10), sticky='W')
    row += 1

    # Run app
    root.mainloop()
except:
    ctypes.windll.user32.MessageBoxW(None, u"Unable to open correctly: " + str(sys.exc_info()[1]), u'Hazus - Message', 0)