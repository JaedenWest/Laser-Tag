from tkinter import *
from tkinter import font

root = Tk()

# Two lists of tuples of what was entered in StringVars
red_team = [(StringVar(), StringVar()) for _ in range(20)]
green_team = [(StringVar(), StringVar()) for _ in range(20)]

# Title
label = Label(root, text="Edit Current Game", font=font.Font(weight=font.BOLD, size=18))
label.grid(column=0, columnspan=2, row=0, pady=10)

# Red team entry
red_team_frame = Frame(root, background="red", borderwidth=1)
red_team_frame.grid(column=0, row=1, padx=5)
red_team_label = Label(red_team_frame, text="RED TEAM").grid(row=0)

red_team_entry_frame = Frame(red_team_frame)
red_team_entry_frame.grid(column=0, row=1)

for i in range(20):
    Label(red_team_entry_frame, text=i).grid(column=0, row=i)
    Entry(red_team_entry_frame, borderwidth=1, width=10, textvariable=red_team[i][0]).grid(column=1, row=i)
    Entry(red_team_entry_frame, borderwidth=1, textvariable=red_team[i][1]).grid(column=2, row=i)

# Green team entry
green_team_frame = Frame(root, background="green", borderwidth=1)
green_team_frame.grid(column=1, row=1, padx=5)
green_team_label = Label(green_team_frame, text="GREEN TEAM").grid(row=0)

green_team_entry_frame = Frame(green_team_frame)
green_team_entry_frame.grid(row=1)

for i in range(20):
    Label(green_team_entry_frame, text=i).grid(column=0, row=i)
    Entry(green_team_entry_frame, borderwidth=1, width=10, textvariable=green_team[i][0]).grid(column=1, row=i)
    Entry(green_team_entry_frame, borderwidth=1, textvariable=green_team[i][1]).grid(column=2, row=i)

# # Game mode
# game_mode_label = Label(root, text="Game Mode: Standard public mode").grid(columnspan=2, row=2)

# Controls
controls_frame = Frame(root)
controls_frame.grid(columnspan=2, row=3, pady=5)
controls = ["F3\nStart\nGame", "F12\nClear\nGame"]
for index, value in enumerate(controls):
    if value:
        Label(controls_frame,
              text=value,
              relief="ridge",
              borderwidth=1,
              padx=10,
              anchor="center").grid(row=0, column=index)

# Data and controls
def play(_):
    print("Red Team")
    for player in red_team:
        print(player[0].get(), player[1].get())
    
    print("\nGreen Team")
    for player in green_team:
        print(player[0].get(), player[1].get())

def clear(_):
    for player in red_team:
        player[0].set("")
        player[1].set("")
    
    for player in green_team:
        player[0].set("")
        player[1].set("")

root.bind("<F3>", play)
root.bind("<F12>", clear)

root.mainloop()