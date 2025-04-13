import os
import random
import json
import hashlib
from tkinter import *
from tkinter import messagebox, ttk
from PIL import Image, ImageTk

class Case:
    def __init__(self, name, price, image_path, items):
        self.name = name
        self.price = price
        self.image_path = image_path
        self.items = items
        
    @classmethod
    def load_from_folder(cls, folder_path):
        try:
            # Load case information
            case_txt = os.path.join(folder_path, "case.txt")
            if not os.path.exists(case_txt):
                raise FileNotFoundError(f"File {case_txt} not found")
            
            with open(case_txt, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if len(lines) < 2:
                    raise ValueError("Not enough data in case.txt")
                
                name = lines[0].strip()
                price = float(lines[1].strip())
            
            # Load case image
            image_path = os.path.join(folder_path, "case.png")
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image {image_path} not found")
            
            # Load items
            items_txt = os.path.join(folder_path, "items.txt")
            if not os.path.exists(items_txt):
                raise FileNotFoundError(f"File {items_txt} not found")
            
            items = []
            with open(items_txt, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        item_data = line.strip().split(';')
                        if len(item_data) < 4:
                            continue
                            
                        item_name = item_data[0]
                        skin_name = item_data[1]
                        item_price = float(item_data[2])
                        rarity = item_data[3]
                        sprite_path = os.path.join(folder_path, "sprites", f"{item_name}_{skin_name}.png")
                        
                        if not os.path.exists(sprite_path):
                            sprite_path = None
                        
                        items.append({
                            'item': item_name,
                            'skin': skin_name,
                            'price': item_price,
                            'rarity': rarity,
                            'sprite': sprite_path
                        })
            
            return cls(name, price, image_path, items)
            
        except Exception as e:
            print(f"Error loading case from {folder_path}: {str(e)}")
            return None

class Inventory:
    def __init__(self, file_path):
        self.file_path = file_path
        self.backup_path = file_path + ".bak"
        self.items = []
        self.load()
    
    def calculate_checksum(self, data):
        return hashlib.md5(data.encode('utf-8')).hexdigest()
    
    def load(self):
        if os.path.exists(self.file_path):
            try:
                # Verify file integrity
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = f.read()
                    stored_checksum = data.split('\n')[-1] if '\n' in data else ''
                    clean_data = data.rsplit('\n', 1)[0] if '\n' in data else data
                    
                    if stored_checksum and self.calculate_checksum(clean_data) != stored_checksum:
                        # Try loading from backup
                        if os.path.exists(self.backup_path):
                            with open(self.backup_path, 'r', encoding='utf-8') as backup:
                                data = backup.read()
                                stored_checksum = data.split('\n')[-1] if '\n' in data else ''
                                clean_data = data.rsplit('\n', 1)[0] if '\n' in data else data
                                
                                if stored_checksum and self.calculate_checksum(clean_data) != stored_checksum:
                                    raise ValueError("Invalid checksum in backup file")
                                
                                for line in clean_data.split('\n'):
                                    if line.strip():
                                        self.items.append(json.loads(line.strip()))
                            # Restore main file
                            self.save()
                            return
                        raise ValueError("Invalid checksum in inventory file")
                    
                    # Load main file
                    for line in clean_data.split('\n'):
                        if line.strip():
                            self.items.append(json.loads(line.strip()))
            except Exception as e:
                print(f"Error loading inventory: {str(e)}")
                self.items = []
    
    def save(self):
        try:
            # Create backup
            if os.path.exists(self.file_path):
                os.replace(self.file_path, self.backup_path)
            
            # Save data with checksum
            data = '\n'.join(json.dumps(item, ensure_ascii=False) for item in self.items)
            checksum = self.calculate_checksum(data)
            full_data = f"{data}\n{checksum}"
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(full_data)
        except Exception as e:
            print(f"Error saving inventory: {str(e)}")
            # Try to restore from backup
            if os.path.exists(self.backup_path):
                os.replace(self.backup_path, self.file_path)
    
    def add_item(self, item):
        self.items.append(item)
        self.save()
    
    def remove_item(self, index):
        if 0 <= index < len(self.items):
            item = self.items.pop(index)
            self.save()
            return item
        return None
    
    def remove_items(self, indices):
        # Remove in reverse order to prevent index shifting
        removed_items = []
        for index in sorted(indices, reverse=True):
            if 0 <= index < len(self.items):
                removed_items.append(self.items.pop(index))
        if removed_items:
            self.save()
        return removed_items

class MoneyManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.balance = 0.0
        self.load()
    
    def load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r') as f:
                    self.balance = float(f.read())
            except Exception as e:
                print(f"Error loading balance: {str(e)}")
                self.balance = 1000.0
        else:
            self.balance = 1000.0  # Starting balance
            self.save()
    
    def save(self):
        try:
            with open(self.file_path, 'w') as f:
                f.write(str(self.balance))
        except Exception as e:
            print(f"Error saving balance: {str(e)}")
    
    def add_money(self, amount):
        self.balance += amount
        self.save()
    
    def deduct_money(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False

class CaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CasePy")
        self.root.geometry("1000x700")
        
        # Initialize components
        self.money_manager = MoneyManager("money.txt")
        self.inventory = Inventory("inventory.txt")
        
        # Create cases folder if it doesn't exist
        if not os.path.exists("cases"):
            os.makedirs("cases")
            messagebox.showinfo("Information", "The 'cases' folder has been created. Please add cases to this folder.")
        
        self.cases = self.load_cases("cases")
        
        # Create interface
        self.create_main_menu()
    
    def load_cases(self, cases_folder):
        cases = []
        if not os.path.exists(cases_folder):
            return cases
            
        for case_folder in os.listdir(cases_folder):
            folder_path = os.path.join(cases_folder, case_folder)
            if os.path.isdir(folder_path):
                case = Case.load_from_folder(folder_path)
                if case:
                    cases.append(case)
        return cases
    
    def create_main_menu(self):
        # Clear current interface
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Display balance
        self.balance_label = Label(self.root, text=f"Balance: ${self.money_manager.balance:.2f}", 
                                 font=("Arial", 14))
        self.balance_label.pack(pady=10)
        
        # Menu buttons
        Button(self.root, text="Open Cases", command=self.show_cases, 
              font=("Arial", 12), width=20).pack(pady=5)
        Button(self.root, text="Inventory", command=self.show_inventory, 
              font=("Arial", 12), width=20).pack(pady=5)
        Button(self.root, text="Exit", command=self.root.quit, 
              font=("Arial", 12), width=20).pack(pady=5)
    
    def show_cases(self):
        # Clear current interface
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Back button
        Button(self.root, text="Back", command=self.create_main_menu, 
              font=("Arial", 10)).pack(anchor=NW, padx=10, pady=10)
        
        # Display balance
        self.balance_label = Label(self.root, text=f"Balance: ${self.money_manager.balance:.2f}", 
                                 font=("Arial", 14))
        self.balance_label.pack(pady=10)
        
        # Title
        Label(self.root, text="Available Cases", font=("Arial", 16)).pack(pady=10)
        
        # Frame for cases
        cases_frame = Frame(self.root)
        cases_frame.pack(pady=10)
        
        # Display all cases
        for i, case in enumerate(self.cases):
            case_frame = Frame(cases_frame, bd=2, relief=RAISED, padx=10, pady=10)
            case_frame.grid(row=i//3, column=i%3, padx=10, pady=10)
            
            try:
                img = Image.open(case.image_path)
                img = img.resize((150, 150), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                img_label = Label(case_frame, image=photo)
                img_label.image = photo
                img_label.pack()
                
                Label(case_frame, text=case.name, font=("Arial", 12)).pack()
                Label(case_frame, text=f"${case.price:.2f}", font=("Arial", 10)).pack()
                
                Button(case_frame, text="Open", 
                      command=lambda case_obj=case: self.open_case(case_obj),
                      state=NORMAL if self.money_manager.balance >= case.price else DISABLED).pack()
            except Exception as e:
                print(f"Error loading case image: {str(e)}")
                # Placeholder for missing image
                img = Image.new('RGB', (150, 150), color='gray')
                photo = ImageTk.PhotoImage(img)
                
                img_label = Label(case_frame, image=photo)
                img_label.image = photo
                img_label.pack()
                
                Label(case_frame, text=case.name, font=("Arial", 12)).pack()
                Label(case_frame, text=f"${case.price:.2f}", font=("Arial", 10)).pack()
                
                Button(case_frame, text="Open", 
                      command=lambda case_obj=case: self.open_case(case_obj),
                      state=NORMAL if self.money_manager.balance >= case.price else DISABLED).pack()
    
    def open_case(self, case):
        if not self.money_manager.deduct_money(case.price):
            messagebox.showerror("Error", "Not enough funds!")
            return
        
        self.balance_label.config(text=f"Balance: ${self.money_manager.balance:.2f}")
        self.show_case_opening_animation(case)
    
    def show_case_opening_animation(self, case):
        # Clear current interface
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create main frame for animation
        self.animation_frame = Frame(self.root)
        self.animation_frame.pack(expand=True, fill=BOTH)
        
        # Back button (initially disabled)
        self.back_button = Button(self.animation_frame, text="Back", 
                                command=lambda: self.finish_case_opening(case),
                                state=DISABLED)
        self.back_button.pack(anchor=NW, padx=10, pady=10)
        
        # Display case image
        try:
            img = Image.open(case.image_path)
            img = img.resize((300, 300), Image.LANCZOS)
            self.case_photo = ImageTk.PhotoImage(img)
            self.case_label = Label(self.animation_frame, image=self.case_photo)
            self.case_label.image = self.case_photo
            self.case_label.pack(pady=20)
        except Exception as e:
            print(f"Error loading case image: {str(e)}")
            img = Image.new('RGB', (300, 300), color='gray')
            self.case_photo = ImageTk.PhotoImage(img)
            self.case_label = Label(self.animation_frame, image=self.case_photo)
            self.case_label.image = self.case_photo
            self.case_label.pack(pady=20)
        
        # Status label
        self.status_label = Label(self.animation_frame, text="Opening case...", 
                                font=("Arial", 14))
        self.status_label.pack(pady=10)
        
        # Frame for displaying items
        self.item_frame = Frame(self.animation_frame)
        self.item_frame.pack(pady=20)
        
        # Prepare for animation
        self.animation_items = case.items.copy()
        self.animation_counter = 0
        self.is_animation_running = True
        
        # Start animation
        self.animate_case_opening(case)
    
    def animate_case_opening(self, case):
        if not self.is_animation_running:
            return
        
        if self.animation_counter < 20:
            # Select random item for animation
            item = random.choice(self.animation_items)
            
            # Create new frame for current item
            for widget in self.item_frame.winfo_children():
                widget.destroy()
            
            try:
                if item['sprite'] and os.path.exists(item['sprite']):
                    img = Image.open(item['sprite'])
                else:
                    img = Image.new('RGB', (200, 200), color='darkgray')
                
                img = img.resize((200, 200), Image.LANCZOS)
                self.current_item_photo = ImageTk.PhotoImage(img)
                
                item_label = Label(self.item_frame, image=self.current_item_photo)
                item_label.image = self.current_item_photo
                item_label.pack()
                
            except Exception as e:
                print(f"Error loading item image: {str(e)}")
            
            self.animation_counter += 1
            self.root.after(100 + self.animation_counter * 20, lambda: self.animate_case_opening(case))
        else:
            # Animation complete, show final item
            self.is_animation_running = False
            self.final_item = self.select_item_with_rarity(case.items)
            self.show_final_item(self.final_item)
    
    def select_item_with_rarity(self, items):
        rarity_weights = {
            'common': 50,
            'uncommon': 30,
            'rare': 15,
            'mythical': 4,
            'legendary': 1
        }
        
        weighted_items = []
        for item in items:
            weight = rarity_weights.get(item['rarity'].lower(), 1)
            weighted_items.extend([item] * weight)
        
        return random.choice(weighted_items)
    
    def show_final_item(self, item):
        # Clear item frame
        for widget in self.item_frame.winfo_children():
            widget.destroy()
        
        try:
            if item['sprite'] and os.path.exists(item['sprite']):
                img = Image.open(item['sprite'])
            else:
                img = Image.new('RGB', (300, 300), color='darkgray')
            
            img = img.resize((300, 300), Image.LANCZOS)
            self.final_item_photo = ImageTk.PhotoImage(img)
            
            final_label = Label(self.item_frame, image=self.final_item_photo)
            final_label.image = self.final_item_photo
            final_label.pack()
            
            self.status_label.config(text=f"You received: {item['item']} | {item['skin']}\nPrice: ${item['price']:.2f}\nRarity: {item['rarity']}")
            
            # Add item to inventory
            self.inventory.add_item(item)
            
            # Enable back button
            self.back_button.config(state=NORMAL)
        except Exception as e:
            print(f"Error loading item image: {str(e)}")
    
    def finish_case_opening(self, case):
        # Stop animation if still running
        self.is_animation_running = False
        # Return to main menu
        self.create_main_menu()
    
    def show_inventory(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        Button(self.root, text="Back", command=self.create_main_menu, 
              font=("Arial", 10)).pack(anchor=NW, padx=10, pady=10)
        
        self.balance_label = Label(self.root, text=f"Balance: ${self.money_manager.balance:.2f}", 
                                 font=("Arial", 14))
        self.balance_label.pack(pady=10)
        
        Label(self.root, text="Your Inventory", font=("Arial", 16)).pack(pady=10)
        
        # Frame for bulk actions
        bulk_frame = Frame(self.root)
        bulk_frame.pack(fill=X, padx=10, pady=5)
        
        self.selected_items = []
        Button(bulk_frame, text="Select All", command=self.select_all_items).pack(side=LEFT)
        Button(bulk_frame, text="Deselect All", command=self.deselect_all_items).pack(side=LEFT, padx=5)
        Button(bulk_frame, text="Sell Selected", command=self.sell_selected_items).pack(side=LEFT)
        
        if not self.inventory.items:
            Label(self.root, text="Inventory is empty", font=("Arial", 12)).pack()
            return
        
        canvas = Canvas(self.root)
        scrollbar = Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.item_vars = []
        for i, item in enumerate(self.inventory.items):
            item_frame = Frame(scrollable_frame, bd=2, relief=RAISED, padx=10, pady=10)
            item_frame.pack(fill=X, padx=10, pady=5)
            
            # Checkbox variable
            var = BooleanVar(value=False)
            self.item_vars.append(var)
            
            Checkbutton(item_frame, variable=var, 
                       command=lambda idx=i: self.toggle_item_selection(idx)).grid(row=0, column=0, rowspan=3)
            
            try:
                if item['sprite'] and os.path.exists(item['sprite']):
                    img = Image.open(item['sprite'])
                else:
                    img = Image.new('RGB', (100, 100), color='gray')
                
                img = img.resize((100, 100), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                img_label = Label(item_frame, image=photo)
                img_label.image = photo
                img_label.grid(row=0, column=1, rowspan=3, padx=10)
                
                Label(item_frame, text=f"{item['item']} | {item['skin']}", 
                     font=("Arial", 12)).grid(row=0, column=2, sticky=W)
                Label(item_frame, text=f"Price: ${item['price']:.2f}", 
                     font=("Arial", 10)).grid(row=1, column=2, sticky=W)
                Label(item_frame, text=f"Rarity: {item['rarity']}", 
                     font=("Arial", 10)).grid(row=2, column=2, sticky=W)
                
                Button(item_frame, text="Sell", 
                      command=lambda idx=i: self.sell_item(idx)).grid(row=0, column=3, rowspan=3, padx=10)
            except Exception as e:
                print(f"Error loading inventory item: {str(e)}")
    
    def toggle_item_selection(self, index):
        if 0 <= index < len(self.item_vars):
            if self.item_vars[index].get():
                if index not in self.selected_items:
                    self.selected_items.append(index)
            else:
                if index in self.selected_items:
                    self.selected_items.remove(index)
    
    def select_all_items(self):
        self.selected_items = list(range(len(self.inventory.items)))
        for var in self.item_vars:
            var.set(True)
    
    def deselect_all_items(self):
        self.selected_items = []
        for var in self.item_vars:
            var.set(False)
    
    def sell_selected_items(self):
        if not self.selected_items:
            messagebox.showwarning("Warning", "No items selected!")
            return
        
        total_price = sum(self.inventory.items[i]['price'] for i in self.selected_items)
        if messagebox.askyesno("Confirmation", 
                             f"Are you sure you want to sell {len(self.selected_items)} items for ${total_price:.2f}?"):
            sold_items = self.inventory.remove_items(self.selected_items)
            if sold_items:
                total = sum(item['price'] for item in sold_items)
                self.money_manager.add_money(total)
                self.balance_label.config(text=f"Balance: ${self.money_manager.balance:.2f}")
                messagebox.showinfo("Success", f"Sold {len(sold_items)} items for ${total:.2f}")
                self.show_inventory()  # Refresh interface
    
    def sell_item(self, index):
        item = self.inventory.remove_item(index)
        if item:
            self.money_manager.add_money(item['price'])
            self.balance_label.config(text=f"Balance: ${self.money_manager.balance:.2f}")
            self.show_inventory()
            messagebox.showinfo("Success", f"Item sold for ${item['price']:.2f}")

if __name__ == "__main__":
    root = Tk()
    app = CaseApp(root)
    root.mainloop()
