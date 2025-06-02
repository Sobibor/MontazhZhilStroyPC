import tkinter as tk
from gui import MainApp 
from database import initialize_database

if __name__ == '__main__':
    initialize_database()  
    
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
