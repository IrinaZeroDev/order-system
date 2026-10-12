"""Система управления заказами для малого бизнеса (tkinter + SQLite)."""
import sqlite3
import tkinter as tk
from contextlib import closing
from pathlib import Path
from tkinter import messagebox, ttk

# База лежит рядом с программой, откуда бы её ни запускали
DB_PATH = Path(__file__).resolve().parent / 'business_orders.db'

STATUS_NEW = 'Новый'


# Работа с базой данных

def connect(db_path=None):
    """Подключение к базе; closing() закроет его даже при ошибке."""
    return closing(sqlite3.connect(db_path or DB_PATH))


def init_db(db_path=None):
    with connect(db_path) as conn, conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                customer_name TEXT NOT NULL,
                order_details TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """)


def add_order(customer_name, order_details, db_path=None):
    """Добавляет заказ со статусом «Новый» и возвращает его номер.

    Значения передаются через «?», а не f-строкой: так текст из полей
    ввода не может изменить сам SQL-запрос.
    """
    customer_name = customer_name.strip()
    order_details = order_details.strip()
    if not customer_name or not order_details:
        raise ValueError('Заполните имя клиента и детали заказа')
    # «with conn» сам делает commit, если внутри не было ошибки
    with connect(db_path) as conn, conn:
        cursor = conn.execute(
            'INSERT INTO orders (customer_name, order_details, status) '
            'VALUES (?, ?, ?)',
            (customer_name, order_details, STATUS_NEW),
        )
        return cursor.lastrowid


def get_orders(db_path=None):
    with connect(db_path) as conn:
        return conn.execute(
            'SELECT id, customer_name, order_details, status '
            'FROM orders ORDER BY id'
        ).fetchall()


# Интерфейс

COLUMNS = {
    'id': ('№', 50),
    'customer_name': ('Клиент', 160),
    'order_details': ('Детали заказа', 260),
    'status': ('Статус', 100),
}


class OrderApp:
    def __init__(self, root):
        self.root = root
        root.title('Система управления заказами')
        root.minsize(600, 400)

        form = ttk.Frame(root, padding=10)
        form.pack(fill=tk.X)

        ttk.Label(form, text='Имя клиента').grid(row=0, column=0, sticky=tk.W)
        self.customer_name_entry = ttk.Entry(form, width=40)
        self.customer_name_entry.grid(row=0, column=1, sticky=tk.EW, pady=2)

        ttk.Label(form, text='Детали заказа').grid(row=1, column=0,
                                                   sticky=tk.W)
        self.order_details_entry = ttk.Entry(form, width=40)
        self.order_details_entry.grid(row=1, column=1, sticky=tk.EW, pady=2)
        form.columnconfigure(1, weight=1)

        self.buttons = ttk.Frame(root, padding=(10, 0))
        self.buttons.pack(fill=tk.X)
        ttk.Button(self.buttons, text='Добавить заказ',
                   command=self.add_order).pack(side=tk.LEFT)
        # Enter в поле «Детали заказа» тоже добавляет заказ
        self.order_details_entry.bind('<Return>', lambda _: self.add_order())

        self.tree = ttk.Treeview(root, columns=list(COLUMNS),
                                 show='headings')
        for column, (title, width) in COLUMNS.items():
            self.tree.heading(column, text=title)
            self.tree.column(column, width=width,
                             anchor=tk.CENTER if column == 'id' else tk.W)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.customer_name_entry.focus()
        self.view_orders()

    def add_order(self):
        try:
            add_order(self.customer_name_entry.get(),
                      self.order_details_entry.get())
        except ValueError as error:
            messagebox.showwarning('Предупреждение', str(error))
            return
        self.customer_name_entry.delete(0, tk.END)
        self.order_details_entry.delete(0, tk.END)
        self.customer_name_entry.focus()
        self.view_orders()

    def view_orders(self):
        self.tree.delete(*self.tree.get_children())
        for row in get_orders():
            self.tree.insert('', tk.END, values=row)


def main():
    init_db()
    root = tk.Tk()
    OrderApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
