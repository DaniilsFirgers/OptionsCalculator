from tkinter import ttk
from tkinter import *

BG_COLOR_1 = "#EEDFCC"
BG_COLOR_2 = "#FAEBD7"
BUTTON_COLOR = "#FFF8DC"


class UserInterface:
    """ Creating a pop-up window that allows to select a public company ticker and an option type"""

    def __init__(self):
        self.detect = False
        self.window = Tk()
        self.window.title("Options calculator")
        self.window.config(padx=25, pady=25, bg=BG_COLOR_1)
        self.canvas = Canvas(width=300, height=300, bg="#FAEBD7", highlightthickness=0)
        self.canvas_text = self.canvas.create_text(150,
                                                   150,
                                                   width=280,
                                                   text="Welcome to the options calculator!\n\n"
                                                        "Please select an option type and a company's ticker.",
                                                   fill="black",
                                                   font=("arial", 15, "italic"))
        self.canvas.grid(padx=10, pady=20, row=0, column=0, columnspan=3)

        self.submit_button = Button(highlightthickness=0, bg=BUTTON_COLOR, activebackground=BG_COLOR_1, text="Submit",
                                    command=self.clicked)
        self.submit_button.grid(row=1, column=2)

        self.symbol_list = ["Select", "APPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "FB", "V", "JPM", "PG"]
        self.symbol = StringVar(self.window)
        self.symbol.set(self.symbol_list[0])
        self.drop_down_list_symbols = ttk.OptionMenu(self.window, self.symbol, *self.symbol_list, command=self.number)
        self.drop_down_list_symbols.grid(row=1, column=0)

        self.options_type = ["Select", "Call", "Put"]
        self.option = StringVar(self.window)
        self.option.set(self.options_type[0])
        self.drop_down_list_options = ttk.OptionMenu(self.window, self.option, *self.options_type, command=self.number)
        self.drop_down_list_options.grid(row=1, column=1)

        self.email_yes = IntVar(self.window)
        self.email_checkbutton = Checkbutton(self.window, text="Send results to my email", variable=self.email_yes,
                                             onvalue=1, offvalue=0, width=21, bg=BG_COLOR_1,
                                             activebackground=BG_COLOR_1, command=self.wants_email)
        self.email_checkbutton.grid(row=2, column=0, columnspan=2, pady=10)

        self.email_label = Label(self.window, text="Email address", bg=BG_COLOR_1)
        self.email_label.grid(row=3, column=0)
        self.email_text = Entry(self.window, bg=BG_COLOR_2, state=DISABLED)
        self.email_text.grid(row=3, column=1)
        self.window.mainloop()

    def clicked(self):
        if self.option.get() == "Select" and self.symbol.get() == "Select":
            self.canvas.itemconfig(self.canvas_text, text="Please select an option type and company!")
        elif self.option.get() == "Select":
            self.canvas.itemconfig(self.canvas_text, text="Please select an option type!")
        elif self.symbol.get() == "Select":
            self.canvas.itemconfig(self.canvas_text, text="Please select a company!")
        elif self.email_yes.get() == 1 and self.email_text.get() == "":
            self.canvas.itemconfig(self.canvas_text, text="Please enter an email!")
        elif self.email_yes.get() == 1 and "@" not in self.email_text.get():
            self.canvas.itemconfig(self.canvas_text, text="Please enter a proper email address!")
        else:
            self.detect = True
            self.window.quit()

    def number(self, *args):
        self.canvas.itemconfig(self.canvas_text, text=f"You've selected "
                                                      f"{self.option.get()} option for "
                                                      f"{self.symbol.get()}.\n\nClick submit to calculate the prices!")

    def wants_email(self):
        if self.email_yes.get() == 1:
            self.email_text.config(state=NORMAL)
        else:
            self.email_text.config(state=DISABLED)
