import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import sqlite3
import io
import random

class NovelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Novel Catalog")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.geometry("1200x900")  # Увеличенный размер для большего экрана
        self.root.configure(bg="#1a1a1a")  # Темный фон
        self.create_db()
        self.create_main_page()

    def create_db(self):
        try:
            self.conn = sqlite3.connect("novels.db")
            self.cursor = self.conn.cursor()
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS novels (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    cover BLOB,
                    description TEXT
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS chapters (
                    id INTEGER PRIMARY KEY,
                    novel_id INTEGER,
                    title TEXT,
                    content TEXT,
                    FOREIGN KEY (novel_id) REFERENCES novels (id)
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось создать базу данных: {e}")

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

    def on_closing(self):
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
            self.conn.close()
            self.root.destroy()

    def create_main_page(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        ttk.Label(self.root, text="Catalog of Novels", style="TLabel").pack(pady=20)
        self.novel_frame = ttk.Frame(self.root)
        self.novel_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.novel_frame.configure(style="TFrame")
        self.load_novels()
        ttk.Button(self.root, text="Add Novel", command=self.open_add_novel_page, style="TButton").pack(pady=10)

    def load_novels(self):
        for widget in self.novel_frame.winfo_children():
            widget.destroy()

        try:
            self.cursor.execute("SELECT id, title, cover, description FROM novels")
            novels = self.cursor.fetchall()
            row_num, col_num = 0, 0

            # Настройка стилей для темной темы и карточек
            style = ttk.Style()
            style.configure("TFrame", background="#1a1a1a")
            style.configure("Custom.TFrame", background="#2a2a2a", relief="ridge", borderwidth=2)
            style.configure("TLabel", background="#1a1a1a", foreground="white")
            style.configure("TButton", background="#333333", foreground="white")
            style.configure("Rating.TLabel", background="#4a90e2", foreground="white", font=("Arial", 10, "bold"), 
                          borderwidth=1, relief="solid", padding=2, anchor="center")

            for novel_id, title, cover_data, description in novels:
                # Загрузка или создание изображения обложки
                if cover_data and isinstance(cover_data, bytes):
                    image = Image.open(io.BytesIO(cover_data))
                else:
                    image = Image.new("RGB", (200, 280), "gray")  # Размер как на скриншоте

                image = image.resize((200, 280))
                novel_cover = ImageTk.PhotoImage(image)

                # Фрейм для карточки новеллы
                novel_card = ttk.Frame(self.novel_frame, style="Custom.TFrame")
                novel_card.grid(row=row_num, column=col_num, padx=5, pady=5)

                # Обложка
                cover_label = ttk.Label(novel_card, image=novel_cover)
                cover_label.image = novel_cover
                cover_label.pack(pady=5)

                # Рейтинг (случайный, можно заменить на данные из базы)
                rating = round(random.uniform(8.0, 9.9), 1)
                rating_label = ttk.Label(novel_card, text=f"{rating}/10", style="Rating.TLabel", width=5)
                rating_label.pack(pady=(0, 5))

                # Название
                title_label = ttk.Label(novel_card, text=title, foreground="white", background="#2a2a2a", 
                                       font=("Arial", 12, "bold"), wraplength=200, justify="center")
                title_label.pack(pady=2)

                # Теги (например, "В наличии", "Новелла", "Корея")
                tags = ["В наличии", "Новелла"]
                if random.choice([True, False]):  # Случайно добавляем "Корея"
                    tags.append("Корея")
                tags_text = " | ".join(tags)
                tags_label = ttk.Label(novel_card, text=tags_text, foreground="#a0a0a0", background="#2a2a2a", 
                                      font=("Arial", 8), wraplength=200, justify="center")
                tags_label.pack(pady=(0, 5))

                # Привязка клика к открытию страницы новеллы
                novel_card.bind("<Button-1>", lambda e, nid=novel_id: self.open_novel_page(nid))

                col_num += 1
                if col_num == 5:  # 5 колонок, как на скриншоте
                    col_num = 0
                    row_num += 1

        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить новеллы: {e}")

    def open_novel_page(self, novel_id):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.configure(bg="#1a1a1a")
        try:
            self.cursor.execute("SELECT * FROM novels WHERE id=?", (novel_id,))
            novel = self.cursor.fetchone()

            if novel:
                cover_data = novel[2]
                if cover_data:
                    image = Image.open(io.BytesIO(cover_data))
                else:
                    image = Image.new("RGB", (200, 280), "gray")  # Согласуем размер с главной страницей

                image = image.resize((200, 280))
                novel_cover = ImageTk.PhotoImage(image)

                ttk.Label(self.root, image=novel_cover, style="TLabel").pack(pady=10)
                ttk.Label(self.root, text=novel[1], font=("Arial", 16), style="TLabel").pack()
                ttk.Label(self.root, text=novel[3], style="TLabel").pack()

                self.chapter_list = ttk.Treeview(self.root, columns=("Title"), show="headings", style="Treeview")
                self.chapter_list.heading("Title", text="Title")
                self.chapter_list.pack(fill="both", expand=True)
                self.chapter_list.bind("<Double-1>", self.open_chapter_page)

                self.cursor.execute("SELECT * FROM chapters WHERE novel_id=?", (novel_id,))
                for row in self.cursor.fetchall():
                    self.chapter_list.insert("", "end", values=(row[2],))

                ttk.Button(self.root, text="Add Chapter", command=lambda: self.open_add_chapter_page(novel_id), style="TButton").pack(pady=10)
                ttk.Button(self.root, text="Back", command=self.create_main_page, style="TButton").pack(pady=10)
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть новеллу: {e}")

    def open_chapter_page(self, event):
        selected_item = self.chapter_list.selection()
        if not selected_item:
            return

        chapter_title = self.chapter_list.item(selected_item[0], "values")[0]
        try:
            self.cursor.execute("SELECT * FROM chapters WHERE title=?", (chapter_title,))
            chapter = self.cursor.fetchone()

            if chapter:
                self.display_chapter(chapter)
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть главу: {e}")

    def display_chapter(self, chapter):
        for widget in self.root.winfo_children():
            widget.destroy()

        chapter_id, novel_id, title, content = chapter

        self.root.configure(bg="#1a1a1a")
        ttk.Label(self.root, text=title, font=("Arial", 16), style="TLabel").pack(pady=10)

        text_widget = tk.Text(self.root, wrap="word", bg="#2a2a2a", fg="white")
        text_widget.pack(fill="both", expand=True)
        text_widget.insert("1.0", content)
        text_widget.config(state="disabled")

        nav_frame = ttk.Frame(self.root, style="TFrame")
        nav_frame.pack(pady=10)

        prev_chapter = self.get_prev_chapter(chapter_id, novel_id)
        next_chapter = self.get_next_chapter(chapter_id, novel_id)

        if prev_chapter:
            ttk.Button(nav_frame, text="Previous", command=lambda: self.display_chapter(prev_chapter), style="TButton").pack(side="left", padx=5)

        ttk.Button(nav_frame, text="Back", command=lambda: self.open_novel_page(novel_id), style="TButton").pack(side="left", padx=5)

        if next_chapter:
            ttk.Button(nav_frame, text="Next", command=lambda: self.display_chapter(next_chapter), style="TButton").pack(side="left", padx=5)

    def get_prev_chapter(self, chapter_id, novel_id):
        self.cursor.execute("SELECT * FROM chapters WHERE novel_id=? AND id < ? ORDER BY id DESC LIMIT 1", (novel_id, chapter_id))
        return self.cursor.fetchone()

    def get_next_chapter(self, chapter_id, novel_id):
        self.cursor.execute("SELECT * FROM chapters WHERE novel_id=? AND id > ? ORDER BY id ASC LIMIT 1", (novel_id, chapter_id))
        return self.cursor.fetchone()

    def open_add_novel_page(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.configure(bg="#1a1a1a")
        ttk.Label(self.root, text="Title:", style="TLabel").pack(pady=5)
        self.novel_title_entry = ttk.Entry(self.root, style="TEntry")
        self.novel_title_entry.pack(pady=5)

        ttk.Button(self.root, text="Upload Cover", command=self.upload_cover, style="TButton").pack(pady=5)
        ttk.Label(self.root, text="Description:", style="TLabel").pack(pady=5)
        self.novel_description_entry = tk.Text(self.root, height=5, width=40, bg="#2a2a2a", fg="white")
        self.novel_description_entry.pack(pady=5)

        ttk.Button(self.root, text="Add Novel", command=self.add_novel, style="TButton").pack(pady=10)
        ttk.Button(self.root, text="Back", command=self.create_main_page, style="TButton").pack(pady=10)

        self.cover_data = None

    def upload_cover(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if file_path:
            try:
                with open(file_path, "rb") as file:
                    self.cover_data = file.read()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить обложку: {e}")

    def add_novel(self):
        title = self.novel_title_entry.get()
        description = self.novel_description_entry.get("1.0", "end").strip()
        if not title:
            messagebox.showerror("Ошибка", "Введите название новеллы!")
            return
        if not self.cover_data:
            messagebox.showerror("Ошибка", "Загрузите обложку!")
            return
        try:
            self.cursor.execute("INSERT INTO novels (title, cover, description) VALUES (?, ?, ?)",
                               (title, self.cover_data, description))
            self.conn.commit()
            self.create_main_page()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка базы данных", f"Не удалось добавить новеллу: {e}")

    def open_add_chapter_page(self, novel_id):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.configure(bg="#1a1a1a")
        ttk.Label(self.root, text="Chapter Title:", style="TLabel").pack(pady=10)
        self.chapter_title_entry = ttk.Entry(self.root, style="TEntry")
        self.chapter_title_entry.pack(pady=10)

        ttk.Label(self.root, text="Content:", style="TLabel").pack(pady=10)
        self.chapter_content_entry = tk.Text(self.root, bg="#2a2a2a", fg="white")
        self.chapter_content_entry.pack(pady=10)

        ttk.Button(self.root, text="Add Chapter", command=lambda: self.add_chapter(novel_id), style="TButton").pack(pady=10)
        ttk.Button(self.root, text="Back", command=lambda: self.open_novel_page(novel_id), style="TButton").pack(pady=10)

    def add_chapter(self, novel_id):
        title = self.chapter_title_entry.get()
        content = self.chapter_content_entry.get("1.0", "end").strip()
        if not title:
            messagebox.showerror("Ошибка", "Введите название главы!")
            return
        if not content:
            messagebox.showerror("Ошибка", "Введите содержание главы!")
            return
        try:
            self.cursor.execute("INSERT INTO chapters (novel_id, title, content) VALUES (?, ?, ?)",
                               (novel_id, title, content))
            self.conn.commit()
            self.open_novel_page(novel_id)
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка базы данных", f"Не удалось добавить главу: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NovelApp(root)
    root.mainloop()
