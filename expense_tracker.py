"""
Expense Tracker - Трекер расходов
Автор: Натфуллин Ильназ
Курс: Итоговая аттестация
Дата: 2026
"""

import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker - Трекер расходов | Автор: Натфуллин Ильназ")
        self.root.geometry("900x600")
        
        self.data_file = "expenses.json"
        self.expenses = []
        self.load_expenses()
        
        # Поля ввода
        input_frame = ttk.LabelFrame(root, text="Новый расход", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0)
        self.amount_entry = ttk.Entry(input_frame)
        self.amount_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(input_frame, text="Категория:").grid(row=0, column=2)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, 
                                           values=["Еда", "Транспорт", "Развлечения", "Другое"])
        self.category_combo.grid(row=0, column=3, padx=5)
        
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4)
        self.date_entry = ttk.Entry(input_frame)
        self.date_entry.grid(row=0, column=5, padx=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Button(input_frame, text="Добавить расход", command=self.add_expense).grid(row=0, column=6, padx=10)
        
        # Фильтры
        filter_frame = ttk.LabelFrame(root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Категория:").grid(row=0, column=0)
        self.filter_cat = tk.StringVar(value="Все")
        ttk.Combobox(filter_frame, textvariable=self.filter_cat, 
                     values=["Все", "Еда", "Транспорт", "Развлечения", "Другое"]).grid(row=0, column=1)
        
        ttk.Label(filter_frame, text="Дата от:").grid(row=0, column=2)
        self.date_from = ttk.Entry(filter_frame, width=12)
        self.date_from.grid(row=0, column=3)
        self.date_from.insert(0, "2024-01-01")
        
        ttk.Label(filter_frame, text="до:").grid(row=0, column=4)
        self.date_to = ttk.Entry(filter_frame, width=12)
        self.date_to.grid(row=0, column=5)
        self.date_to.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Button(filter_frame, text="Применить фильтр", command=self.refresh_table).grid(row=0, column=6)
        ttk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter).grid(row=0, column=7)
        
        # Статистика
        stats_frame = ttk.LabelFrame(root, text="Статистика", padding=10)
        stats_frame.pack(fill="x", padx=10, pady=5)
        self.total_label = ttk.Label(stats_frame, text="Общая сумма за период: 0 ₽", font=("Arial", 12, "bold"))
        self.total_label.pack()
        
        # Таблица
        table_frame = ttk.Frame(root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.tree = ttk.Treeview(table_frame, columns=("ID", "Сумма", "Категория", "Дата"), show="headings")
        for col in ("ID", "Сумма", "Категория", "Дата"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопки управления
        btn_frame = ttk.Frame(root)
        btn_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(btn_frame, text="🗑 Удалить выбранный расход", command=self.delete_expense).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="💾 Сохранить в JSON", command=self.save_expenses_to_file).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📂 Загрузить из JSON", command=self.load_expenses_from_file).pack(side="left", padx=5)
        
        self.refresh_table()
    
    def add_expense(self):
        """Добавление нового расхода с валидацией"""
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом!")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число в поле 'Сумма'!")
            return
        
        category = self.category_var.get()
        if not category:
            messagebox.showerror("Ошибка", "Выберите категорию расхода!")
            return
        
        date = self.date_entry.get()
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД\nПример: 2026-01-15")
            return
        
        self.expenses.append({
            "id": len(self.expenses) + 1,
            "amount": amount,
            "category": category,
            "date": date
        })
        self.save_expenses_to_file()
        self.clear_inputs()
        self.refresh_table()
        messagebox.showinfo("Успех", f"Расход на сумму {amount} ₽ добавлен!")
    
    def delete_expense(self):
        """Удаление выбранного расхода"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите расход для удаления!")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот расход?"):
            item = self.tree.item(selected[0])
            exp_id = item['values'][0]
            self.expenses = [e for e in self.expenses if e['id'] != exp_id]
            for i, e in enumerate(self.expenses, 1):
                e['id'] = i
            self.save_expenses_to_file()
            self.refresh_table()
            messagebox.showinfo("Успех", "Расход удалён!")
    
    def refresh_table(self):
        """Обновление таблицы с учётом фильтров"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        filtered = self.expenses
        if self.filter_cat.get() != "Все":
            filtered = [e for e in filtered if e['category'] == self.filter_cat.get()]
        if self.date_from.get():
            filtered = [e for e in filtered if e['date'] >= self.date_from.get()]
        if self.date_to.get():
            filtered = [e for e in filtered if e['date'] <= self.date_to.get()]
        
        total = 0
        for e in filtered:
            self.tree.insert("", "end", values=(e['id'], f"{e['amount']:.2f}", e['category'], e['date']))
            total += e['amount']
        
        self.total_label.config(text=f"Общая сумма за период: {total:.2f} ₽")
    
    def reset_filter(self):
        """Сброс фильтров"""
        self.filter_cat.set("Все")
        self.date_from.delete(0, tk.END)
        self.date_from.insert(0, "2024-01-01")
        self.date_to.delete(0, tk.END)
        self.date_to.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.refresh_table()
        messagebox.showinfo("Информация", "Фильтры сброшены!")
    
    def clear_inputs(self):
        """Очистка полей ввода"""
        self.amount_entry.delete(0, tk.END)
        self.category_var.set("")
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
    
    def load_expenses(self):
        """Загрузка расходов из JSON-файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.expenses = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.expenses = []
    
    def save_expenses_to_file(self):
        """Сохранение расходов в JSON-файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.expenses, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Сохранено", "Данные сохранены в файл expenses.json")
        except IOError as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
    
    def load_expenses_from_file(self):
        """Принудительная загрузка из JSON-файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.expenses = json.load(f)
                self.refresh_table()
                messagebox.showinfo("Успех", "Данные загружены из файла!")
            except (json.JSONDecodeError, IOError) as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
        else:
            messagebox.showwarning("Предупреждение", "Файл expenses.json не найден!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()