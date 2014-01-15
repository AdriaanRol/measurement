import json
import Tkinter as tk
import ttk
from pprint import pprint as pprint

# opt_name: (from_, to, increment)
IntOptions = {
    'age': (1.0, 200.0, 1.0),
}

def close_ed(parent, edwin):
    parent.focus_set()
    edwin.destroy()

def set_cell(edwin, w, tvar):
    value = tvar.get()
    w.item(w.focus(), values=(value,))
    close_ed(w, edwin)

def edit_cell(e):
    w = e.widget
    if w and len(w.item(w.focus(), 'values')) > 0:
        edwin = tk.Toplevel(e.widget)
        edwin.protocol("WM_DELETE_WINDOW", lambda: close_ed(w, edwin))
        edwin.grab_set()
        edwin.overrideredirect(1)
        opt_name = w.focus()
        (x, y, width, height) = w.bbox(opt_name, 'Values')
        edwin.geometry('%dx%d+%d+%d' % (width, height, w.winfo_rootx() + x, w.winfo_rooty() + y))
        value = w.item(opt_name, 'values')[0]
        tvar = tk.StringVar()
        tvar.set(str(value))
        ed = None
        if opt_name in IntOptions:
            constraints = IntOptions[opt_name]
            ed = tk.Spinbox(edwin, from_=constraints[0], to=constraints[1],
                increment=constraints[2], textvariable=tvar)
        else:
            ed = tk.Entry(edwin, textvariable=tvar)
        if ed:
            ed.config(background='LightYellow')
            #ed.grid(column=0, row=0, sticky=(tk.N, tk.S, tk.W, tk.E))
            ed.pack()
            ed.focus_set()
        edwin.bind('<Return>', lambda e: set_cell(edwin, w, tvar))
        edwin.bind('<Escape>', lambda e: close_ed(w, edwin))

def JSONTree(Tree, Parent, Dictionery, TagList=[]):
    for key in Dictionery :
        if isinstance(Dictionery[key], dict):
            Tree.insert(Parent, 'end', key, text=key)
            TagList.append(key)
            JSONTree(Tree, key, Dictionery[key], TagList)
            pprint(TagList)
        elif isinstance(Dictionery[key], list):
            Tree.insert(Parent, 'end', key, text=key) # Still working on this
        else:
            if Dictionery[key]==None:
                Tree.insert(Parent, 'end', key, text=key, value='None')
            else:
                Tree.insert(Parent, 'end', key, text=key, value=Dictionery[key])

if __name__ == "__main__" :
    # Setup the root UI
    root = tk.Tk()
    root.title("JSON editor")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    # Setup Data
    Data = qt.cfgman['protocols']['AdwinSSRO']
    # Setup the Frames
    TreeFrame = ttk.Frame(root, padding="3")
    TreeFrame.grid(row=0, column=0, sticky=tk.NSEW)
    # Setup the Tree
    tree = ttk.Treeview(TreeFrame, columns=('Values'))
    tree.column('Values', width=100, anchor='center')
    tree.heading('Values', text='Values')
    tree.bind('<Double-1>', edit_cell)
    tree.bind('<Return>', edit_cell)
    JSONTree(tree, '', Data)
    tree.pack(fill=tk.BOTH, expand=1)
    # Limit windows minimum dimensions
    root.update_idletasks()
    root.minsize(root.winfo_reqwidth(), root.winfo_reqheight())
    root.mainloop()