import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
import os

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Трекер расходов")
        self.root.geometry("800x600")
        
        self.expenses = []
        self.categories = ["еда", "транспорт", "развлечения", "здоровье", "прочее"]
        self.load_data()
        
        self.setup_ui()
        self.refresh_table()
    
    def setup_ui(self):
        # Поля ввода
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=10, padx=10, fill="x")
        
        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, padx=5)
        self.amount_entry = ttk.Entry(input_frame, width=10)
        self.amount_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(input_frame, text="Категория:").grid(row=0, column=2, padx=5)
        self.category_combo = ttk.Combobox(input_frame, values=self.categories, width=12)
        self.category_combo.grid(row=0, column=3, padx=5)
        
        ttk.Label(input_frame, text="Дата (YYYY-MM-DD):").grid(row=0, column=4, padx=5)
        self.date_entry = ttk.Entry(input_frame, width=12)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=0, column=5, padx=5)
        
        ttk.Button(input_frame, text="Добавить расход", command=self.add_expense).grid(row=0, column=6, padx=10)
        
        # Фильтры
        filter_frame = ttk.Frame(self.root)
        filter_frame.pack(pady=5, padx=10, fill="x")
        
        ttk.Label(filter_frame, text="Фильтр по категории:").grid(row=0, column=0)
        self.filter_category = ttk.Combobox(filter_frame, values=["Все"] + self.categories)
        self.filter_category.grid(row=0, column=1, padx=5)
        self.filter_category.set("Все")
        self.filter_category.bind("<<ComboboxSelected>>", self.apply_filters)
        
        ttk.Label(filter_frame, text="С даты:").grid(row=0, column=2, padx=5)
        self.filter_date_start = ttk.Entry(filter_frame, width=12)
        self.filter_date_start.insert(0, (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        self.filter_date_start.grid(row=0, column=3, padx=5)
        
        ttk.Button(filter_frame, text="Применить фильтры", command=self.apply_filters).grid(row=0, column=4, padx=5)
        ttk.Button(filter_frame, text="Подсчет за период", command=self.calculate_period).grid(row=0, column=5, padx=5)
        
        # Таблица
        columns = ("Дата", "Категория", "Сумма")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Итоговая сумма
        self.total_label = ttk.Label(self.root, text="Итого: 0.00 руб.", font=("Arial", 12, "bold"))
        self.total_label.pack(pady=10)
    
    def add_expense(self):
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                raise ValueError("Сумма должна быть положительной")
            
            date_str = self.date_entry.get()
            date = datetime.strptime(date_str, "%Y-%m-%d")
            
            category = self.category_combo.get()
            if not category:
                raise ValueError("Выберите категорию")
            
            expense = {
                "date": date_str,
                "category": category,
                "amount": amount
            }
            self.expenses.append(expense)
            self.save_data()
            self.refresh_table()
            self.clear_inputs()
            
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def clear_inputs(self):
        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.category_combo.set("")
    
    def refresh_table(self, filtered_expenses=None):
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        expenses_to_show = filtered_expenses or self.expenses
        total = sum(exp["amount"] for exp in expenses_to_show)
        self.total_label.config(text=f"Итого: {total:.2f} руб.")
        
        for expense in expenses_to_show:
            self.tree.insert("", "end", values=(expense["date"], expense["category"], f"{expense['amount']:.2f}"))
    
    def apply_filters(self, event=None):
        filtered = self.expenses[:]
        
        # Фильтр по категории
        category = self.filter_category.get()
        if category != "Все":
            filtered = [e for e in filtered if e["category"] == category]
        
        # Фильтр по дате
        try:
            start_date = self.filter_date_start.get()
            if start_date:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                filtered = [e for e in filtered if datetime.strptime(e["date"], "%Y-%m-%d") >= start]
        except ValueError:
            pass
        
        self.refresh_table(filtered)
    
    def calculate_period(self):
        messagebox.showinfo("Подсчет за период", 
                           f"Расходы за выбранный период: {self.total_label.cget('text')}")
    
    def save_data(self):
        with open("expenses.json", "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=2)
    
    def load_data(self):
        if os.path.exists("expenses.json"):
            try:
                with open("expenses.json", "r", encoding="utf-8") as f:
                    self.expenses = json.load(f)
            except:
                self.expenses = []

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()