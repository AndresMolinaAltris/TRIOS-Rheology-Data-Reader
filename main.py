import tkinter as tk
from rheology_gui import RheologyGUI

def main():
    root = tk.Tk()
    app = RheologyGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()