import sys
import tkinter as tk
from gui.menu_window import MenuWindow

def main():
    root = tk.Tk()
    app = MenuWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()