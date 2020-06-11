def run_gui():

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
        from modules import functions
    except:
        import functions

    try:

        def browse_output():
            global output_directory
            output_directory = filedialog.askdirectory()
            pathlabel_outputDir.config(text=output_directory)
            print(output_directory)

        def browse_policy():
            global policy_directory
            policies = filedialog.askopenfilename(
                filetypes=[('Shapefiles', '*.shp')])
            policy_directory = [x for x in root.tk.splitlist(policies)][0]
            pathlabel_policy.config(text=policy_directory)
            print(policy_directory)

        def browse_depths():
            global depths_directory
            depths = filedialog.askopenfilenames(
                parent=root, title='Choose spatial depth data')
            depths_directory = [x for x in root.tk.splitlist(depths)]
            text = str(len(depths_directory)) + ' depth files selected' if len(
                depths_directory) > 1 else str(len(depths_directory)) + ' depth file selected'
            pathlabel_depth.config(text=text)
            print(depths_directory)

        def busy():
            root.config(cursor="wait")

        def notbusy():
            root.config(cursor="")

        def focus_next_widget(event):
            event.widget.tk_focusNext().focus()
            return("break")

        def run():
            try:
                functions.AnalyzeNFIP(
                    depths_directory, policy_directory, output_directory, export_shapefile=opt_shp.get())
            except:
                ctypes.windll.user32.MessageBoxW(
                    None, u"Error: " + str(sys.exc_info()[1]), u'Hazus - Message', 0)

        # Create app
        root = tk.Tk()

        # App parameters
        root.title('NFIP Exposure Analysis Tool')
        root_h = 400
        root_w = 460
        root.geometry(str(root_w) + 'x' + str(root_h))
        windowWidth = root.winfo_reqwidth()
        windowHeight = root.winfo_reqheight()
        # Gets both half the screen width/height and window width/height
        positionRight = int(root.winfo_screenwidth()/2 - windowWidth/2)
        positionDown = int(root.winfo_screenheight()/3 - windowHeight/2)
        # Positions the window in the center of the page.
        root.geometry("+{}+{}".format(positionRight, positionDown))
        root.configure(background='#282a36')

        # App icon
        # root.wm_iconbitmap('./assets/images/HazusHIcon.ico')

        # Init dynamic row
        row = 0

        # ttk styles classes
        style = ttk.Style()
        style.configure("BW.TCheckbutton", foreground="#f8f8f2",
                        background="#282a36", side='LEFT')

        # App body

        # Input policy directory
        label_dir_policy = tk.Label(root, text='Select the policy point Shapefile:',
                                    font='Helvetica 10 bold', bg='#282a36', fg='#f8f8f2')
        label_dir_policy.grid(row=row, column=0, padx=20,
                              pady=(30, 0), sticky='W')

        # Input policy directory browse button
        browsebutton_dir_policy = tk.Button(root, text="Browse", command=browse_policy,
                                            relief='flat', bg='#44475a', fg='#f8f8f2', cursor="hand2", font='Helvetica 8 bold')
        browsebutton_dir_policy.grid(
            row=row, column=0, padx=(375, 0), pady=(30, 0), sticky='W')
        browsebutton_dir_policy.bind("<Tab>", focus_next_widget)
        row += 1

        # Input policy path label
        pathlabel_policy = tk.Label(
            root, bg='#282a36', fg='#f8f8f2', font='Helvetica 8')
        pathlabel_policy.grid(
            row=row, column=0, pady=(5, 0), padx=30, sticky='W')
        row += 1

        # Input depth directory
        label_dir_depths = tk.Label(
            root, text='Select all depth files:', font='Helvetica 10 bold', bg='#282a36', fg='#f8f8f2')
        label_dir_depths.grid(row=row, column=0, padx=20,
                              pady=(30, 0), sticky='W')

        # Input depth directory browse button
        browsebutton_dir_depths = tk.Button(root, text="Browse", command=browse_depths,
                                            relief='flat', bg='#44475a', fg='#f8f8f2', cursor="hand2", font='Helvetica 8 bold')
        browsebutton_dir_depths.grid(
            row=row, column=0, padx=(375, 0), pady=(30, 0), sticky='W')
        browsebutton_dir_depths.bind("<Tab>", focus_next_widget)
        row += 1

        # Input depth path label
        pathlabel_depth = tk.Label(
            root, bg='#282a36', fg='#f8f8f2', font='Helvetica 8')
        pathlabel_depth.grid(
            row=row, column=0, pady=(5, 0), padx=30, sticky='W')
        row += 1

        # Output checkbox label
        label_outputMetadata = tk.Label(
            root, text='Check to export the spatial data:', font='Helvetica 10 bold', bg='#282a36', fg='#f8f8f2')
        label_outputMetadata.grid(
            row=row, column=0, padx=20, pady=(20, 0), sticky='W')
        row += 1

        # Output checkbox options
        xpadl = 370
        opt_shp = tk.IntVar(value=0)
        ttk.Checkbutton(root, text="Shapefile", variable=opt_shp, style='BW.TCheckbutton').grid(
            row=row, padx=(xpadl, 0), sticky='W')
        row += 1

        # Output directory label
        label_outputDir = tk.Label(root, text='Select a directory for the output files:',
                                   font='Helvetica 10 bold', bg='#282a36', fg='#f8f8f2')
        label_outputDir.grid(row=row, column=0, padx=20,
                             pady=(30, 0), sticky='W')

        # Output directory browse button
        browsebutton_dat = tk.Button(root, text="Browse", command=browse_output, relief='flat',
                                     bg='#44475a', fg='#f8f8f2', cursor="hand2", font='Helvetica 8 bold')
        browsebutton_dat.grid(row=row, column=0, padx=(
            375, 0), pady=(30, 0), sticky='W')
        browsebutton_dat.bind("<Tab>", focus_next_widget)
        row += 1

        # Output directory path label
        pathlabel_outputDir = tk.Label(
            root, bg='#282a36', fg='#f8f8f2', font='Helvetica 8')
        pathlabel_outputDir.grid(
            row=row, column=0, pady=(5, 20), padx=30, sticky='W')
        row += 1

        # Run button
        button_run = tk.Button(root, text='Run', width=20, command=run, relief='flat',
                               bg='#6272a4', fg='#f8f8f2', cursor="hand2", font='Helvetica 8 bold')
        button_run.grid(row=row, column=0, padx=160, pady=(10, 10), sticky='W')
        row += 1

        # Run app
        root.mainloop()
    except:
        ctypes.windll.user32.MessageBoxW(
            None, u"Unable to open correctly: " + str(sys.exc_info()[1]), u'Hazus - Message', 0)


run_gui()
