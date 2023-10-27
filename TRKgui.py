import tkinter

from tkinter import ttk

from tkinter import messagebox

import os

def enter_data():

    accepted = accept_var.get()
    cmdline=""
    

    if accepted=="Accepted":

        # User info

        USB     = USB_entry.get()

        keyfile = keyfile_entry.get()

        prt       = prt_combobox.get()
        setup     = setup_combobox.get()
        ognddb    = ognddb_combobox.get()
        encrypt   = encrypt_combobox.get()
        stealth   = stealth_combobox.get()
        reg       = reg_combobox.get()

        


        print("USB: ", USB, "Keyfile: ", keyfile,"PRT: ", prt)
        print("Setup: ", setup, "OGNDDB:", ognddb, "Encrypt", encrypt, "Stealth:", stealth, "Registration:", reg)
        if USB == "":
           cmdline += " -u USB0"
        else:
           cmdline += " -u "+USB
        if keyfile != "":
           cmdline += " -kf "+keyfile
        if prt == 'Y':
           cmdline += " -p TRUE"
        if setup == 'Y':
           cmdline += " -s TRUE"
        else:
           cmdline += " -s FALSE"
        if ognddb == 'Y':
           cmdline += " -o TRUE"
        else:
           cmdline += " -o FALSE"
        if encrypt == 'Y':
           cmdline += " -n TRUE"
        else:
           cmdline += " -n FALSE"
        if stealth == 'Y':
           cmdline += " -st TRUE"
        else:
           cmdline += " -st FALSE"
        if reg == 'Y':
           cmdline += " -r TRUE"
        else:
           cmdline += " -r FALSE"
        print ("CMD line:", cmdline)


        print("------------------------------------------")

        os.system ("python3 TRKsetup.py "+cmdline)


        print("------------------------------------------")

    else:

        tkinter.messagebox.showwarning(title= "Error", message="You must be ready to connect the IGC/OGN Tracker")



window = tkinter.Tk()
window.geometry("1000x780")

window.title("IGC/OGN Tracker setup")



frame = tkinter.Frame(window)

frame.pack()



# dealing with USB & Keyfile

user_info_frame =tkinter.LabelFrame(frame, text="User Information")

user_info_frame.grid(row= 0, column=0, padx=20, pady=10)



USB_label = tkinter.Label(user_info_frame, text="USB")

USB_label.grid(row=0, column=0)

keyfile_label = tkinter.Label(user_info_frame, text="Keyfile")

keyfile_label.grid(row=0, column=1)



USB_entry = tkinter.Entry(user_info_frame)

keyfile_entry = tkinter.Entry(user_info_frame)

USB_entry.grid(row=1, column=0)

keyfile_entry.grid(row=1, column=1)



prt_label = tkinter.Label(user_info_frame, text="prt")

prt_combobox = ttk.Combobox(user_info_frame, values=["", "Y", "N"])

prt_label.grid(row=0, column=2)

prt_combobox.grid(row=1, column=2)







for widget in user_info_frame.winfo_children():

    widget.grid_configure(padx=10, pady=5)


# dealing with the options

options_frame = tkinter.LabelFrame(frame, text="SETUP Options")

options_frame.grid(row=1, column=0, sticky="news", padx=20, pady=10)


setup_label = tkinter.Label(options_frame, text="setup")

setup_combobox = ttk.Combobox(options_frame, values=["", "Y", "N"])

setup_label.grid(row=0, column=0)

setup_combobox.grid(row=1, column=0)


ognddb_label = tkinter.Label(options_frame, text="OGNDDB")

ognddb_combobox = ttk.Combobox(options_frame, values=["", "Y", "N"])

ognddb_label.grid(row=0, column=1)

ognddb_combobox.grid(row=1, column=1)


encrypt_label = tkinter.Label(options_frame, text="Encrypt")

encrypt_combobox = ttk.Combobox(options_frame, values=["", "Y", "N"])

encrypt_label.grid(row=0, column=2)

encrypt_combobox.grid(row=1, column=2)


stealth_label = tkinter.Label(options_frame, text="Stealth")

stealth_combobox = ttk.Combobox(options_frame, values=["", "Y", "N"])

stealth_label.grid(row=2, column=0)

stealth_combobox.grid(row=3, column=0)


reg_label = tkinter.Label(options_frame, text="Register")

reg_combobox = ttk.Combobox(options_frame, values=["", "Y", "N"])

reg_label.grid(row=2, column=1)

reg_combobox.grid(row=3, column=1)

for widget in options_frame.winfo_children():

    widget.grid_configure(padx=2, pady=2)


# Accept terms

terms_frame = tkinter.LabelFrame(frame, text="Terms & Conditions")

terms_frame.grid(row=2, column=0, sticky="news", padx=20, pady=10)



accept_var = tkinter.StringVar(value="Not Accepted")

terms_check = tkinter.Checkbutton(terms_frame, text= "I have connected the IGC/OGN Tracker.",

                                  variable=accept_var, onvalue="Accepted", offvalue="Not Accepted")

terms_check.grid(row=0, column=0)



# Button

button = tkinter.Button(frame, text="Enter data", command= enter_data)

button.grid(row=3, column=0, sticky="news", padx=20, pady=10)

 

window.mainloop()

