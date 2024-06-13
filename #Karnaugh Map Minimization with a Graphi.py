import tkinter as tk
from itertools import product

class KMapSolver:
    def __init__(self, root):
        self.root = root
        self.root.title("K-Map Solver")
        
        # Number of variables
        self.num_vars_label = tk.Label(root, text="Number of Variables:")
        self.num_vars_label.grid(row=0, column=0)
        
        self.num_vars_entry = tk.Entry(root)
        self.num_vars_entry.grid(row=0, column=1)
        self.num_vars_entry.insert(0, "3")
        
        # Minterms
        self.minterms_label = tk.Label(root, text="Minterms:")
        self.minterms_label.grid(row=1, column=0)
        
        self.minterms_entry = tk.Entry(root)
        self.minterms_entry.grid(row=1, column=1)
        self.minterms_entry.insert(0, "0,2,3,5,6,7")
        
        # Don't Cares
        self.dc_label = tk.Label(root, text="Don't Cares:")
        self.dc_label.grid(row=2, column=0)
        
        self.dc_entry = tk.Entry(root)
        self.dc_entry.grid(row=2, column=1)
        self.dc_entry.insert(0, "1,4")
        
        # Update button
        self.update_button = tk.Button(root, text="Update K-Map", command=self.update_kmap)
        self.update_button.grid(row=3, column=0, columnspan=2)
        
        # Karnaugh Map grid
        self.canvas = tk.Canvas(root, width=500, height=300, bg='white')
        self.canvas.grid(row=4, column=0, columnspan=2)
        
        # Minimized equation display
        self.minimized_eq_label = tk.Label(root, text="Minimized Equation: ")
        self.minimized_eq_label.grid(row=5, column=0, columnspan=2)

    def draw_grid(self, num_vars):
        self.canvas.delete("all")
        cell_size = 100
        num_rows = 2
        num_cols = 4
        
        # Draw the variable labels
        self.canvas.create_text(50, 20, text='BC\\A', font=('Helvetica', 14, 'bold'))
        self.canvas.create_text(150, 20, text='00', font=('Helvetica', 14, 'bold'))
        self.canvas.create_text(250, 20, text='01', font=('Helvetica', 14, 'bold'))
        self.canvas.create_text(350, 20, text='11', font=('Helvetica', 14, 'bold'))
        self.canvas.create_text(450, 20, text='10', font=('Helvetica', 14, 'bold'))
        self.canvas.create_text(20, 100, text='0', font=('Helvetica', 14, 'bold'))
        self.canvas.create_text(20, 200, text='1', font=('Helvetica', 14, 'bold'))
        
        for i in range(num_rows):
            for j in range(num_cols):
                self.canvas.create_rectangle(j * cell_size + 100, (i + 1) * cell_size, (j + 1) * cell_size + 100, (i + 2) * cell_size, outline='black')
                self.canvas.create_text(j * cell_size + 150, (i + 1) * cell_size + 50, text='', font=('Helvetica', 14))

    def get_positions(self, num_vars):
        if num_vars == 2:
            return [((0, 0), 0), ((0, 1), 1), ((1, 0), 2), ((1, 1), 3)]
        elif num_vars == 3:
            return [((0, 0), 0), ((0, 1), 1), ((0, 2), 3), ((0, 3), 2),
                    ((1, 0), 4), ((1, 1), 5), ((1, 2), 7), ((1, 3), 6)]
        elif num_vars == 4:
            return [((0, 0), 0), ((0, 1), 1), ((0, 2), 3), ((0, 3), 2),
                    ((1, 0), 4), ((1, 1), 5), ((1, 2), 7), ((1, 3), 6),
                    ((2, 0), 12), ((2, 1), 13), ((2, 2), 15), ((2, 3), 14),
                    ((3, 0), 8), ((3, 1), 9), ((3, 2), 11), ((3, 3), 10)]

    def update_kmap(self):
        num_vars = int(self.num_vars_entry.get())
        self.draw_grid(num_vars)
        
        minterms = self.minterms_entry.get().split(',')
        minterms = [int(m) for m in minterms if m.isdigit()]
        dontcares = self.dc_entry.get().split(',')
        dontcares = [int(dc) for dc in dontcares if dc.isdigit()]
        
        values = ['0'] * (2 ** num_vars)
        for m in minterms:
            values[m] = '1'
        for dc in dontcares:
            values[dc] = 'X'
        
        colors = {'0': 'black', '1': 'red', 'X': 'grey'}
        
        positions = self.get_positions(num_vars)
        for (i, j), idx in positions:
            value = values[idx]
            self.canvas.create_rectangle(j * 100 + 100, (i + 1) * 100, (j + 1) * 100 + 100, (i + 2) * 100, fill=colors[value], outline='black')
            self.canvas.create_text(j * 100 + 150, (i + 1) * 100 + 50, text=value, fill='white', font=('Helvetica', 14, 'bold'))
        
        self.display_minimized_equation(num_vars, minterms, dontcares)
        self.display_truth_table(num_vars, values)

    def display_minimized_equation(self, num_vars, minterms, dontcares):
        groups = self.find_groups(num_vars, minterms, dontcares)
        equation = self.simplify_groups(groups)
        self.minimized_eq_label.config(text=f"Minimized Equation: {equation}")

    def find_groups(self, num_vars, minterms, dontcares):
        kmap = [''] * (2 ** num_vars)
        for m in minterms:
            kmap[m] = '1'
        for dc in dontcares:
            kmap[dc] = 'X'
        
        groups = []
        for size in [8, 4, 2, 1]:
            for i in range(2 ** num_vars):
                if kmap[i] == '1':
                    group = [i]
                    for j in range(1, size):
                        if i ^ j < len(kmap) and (kmap[i ^ j] == '1' or kmap[i ^ j] == 'X'):
                            group.append(i ^ j)
                    if len(group) == size:
                        groups.append(group)
                        for idx in group:
                            kmap[idx] = 'G'
        
        self.highlight_groups(groups, num_vars)
        
        return groups

    def highlight_groups(self, groups, num_vars):
        cell_size = 100
        positions = self.get_positions(num_vars)
        for group in groups:
            for idx in group:
                (i, j), _ = positions[idx]
                self.canvas.create_rectangle(j * cell_size + 100, (i + 1) * cell_size, (j + 1) * cell_size + 100, (i + 2) * cell_size, outline='yellow', width=3)
    
    def simplify_groups(self, groups):
        terms = []
        for group in groups:
            term = ""
            binary_reps = [format(idx, f'0{len(bin(group[0]))-2}b') for idx in group]
            for i in range(len(binary_reps[0])):
                if all(b[i] == binary_reps[0][i] for b in binary_reps):
                    if binary_reps[0][i] == '1':
                        term += chr(65 + i)
                    else:
                        term += chr(65 + i) + "'"
            terms.append(term)
        return " + ".join(terms)

    def display_truth_table(self, num_vars, values):
        for widget in self.root.grid_slaves():
            if int(widget.grid_info()["row"]) > 5:
                widget.grid_forget()
        
        headers = [f'Var {i}' for i in range(num_vars)] + ['Output']
        colors = ['#ffcccb', '#ccffcc', '#ccccff', '#ffebcc']
        
        for col, header in enumerate(headers):
            label = tk.Label(self.root, text=header, bg=colors[col % len(colors)])
            label.grid(row=6, column=col, sticky='ew')
        
        for row, vals in enumerate(product('01', repeat=num_vars)):
            for col, val in enumerate(vals):
                label = tk.Label(self.root, text=val, bg=colors[col % len(colors)])
                label.grid(row=row + 7, column=col, sticky='ew')
            output = values[int(''.join(vals), 2)]
            label = tk.Label(self.root, text=output, bg=colors[num_vars % len(colors)])
            label.grid(row=row + 7, column=num_vars, sticky='ew')

if __name__ == "__main__":
    root = tk.Tk()
    app = KMapSolver(root)
    root.mainloop()
