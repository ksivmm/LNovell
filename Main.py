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
        self.root.configure(bg="#000000")  # Черный фон
        self.conn = None  # Инициализация соединения с базой
        self.cursor = None
        self.create_db()
        self.create_main_page()

    def create_db(self):
        try:
            self.conn = sqlite3.connect("novels.db")
            self.cursor = self.conn.cursor()
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS novels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    cover BLOB,
                    description TEXT
                )
            """)
            # Упрощенная таблица chapters без update_date
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS chapters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    novel_id INTEGER,
                    title TEXT,
                    content TEXT,
                    FOREIGN KEY (novel_id) REFERENCES novels (id)
                )
            """)
            # Если таблица chapters уже существует с update_date, удаляем эту колонку
            try:
                self.cursor.execute("ALTER TABLE chapters DROP COLUMN update_date")
                self.conn.commit()
            except sqlite3.OperationalError:
                pass  # Колонка уже удалена или не существует
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось создать базу данных: {e}")

    def __del__(self):
        if self.conn:
            self.conn.close()

    def on_closing(self):
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
            if self.conn:
                self.conn.close()
            self.root.destroy()

    def create_main_page(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Заголовок
        ttk.Label(self.root, text="Catalog of Novels", style="TLabel").pack(pady=20)

        # Поле поиска
        search_frame = ttk.Frame(self.root, style="TFrame")
        search_frame.pack(pady=10, padx=10)
        self.search_entry = ttk.Entry(search_frame, style="TEntry", width=40)
        self.search_entry.pack(side="left", padx=5)
        ttk.Button(search_frame, text="Поиск", command=self.search_novels, style="TButton").pack(side="left")

        # Сетка новелл
        self.novel_frame = ttk.Frame(self.root)
        self.novel_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.novel_frame.configure(style="TFrame")
        self.load_novels()
        ttk.Button(self.root, text="Add Novel", command=self.open_add_novel_page, style="TButton").pack(pady=10)

    def search_novels(self):
        search_query = self.search_entry.get().strip()
        for widget in self.novel_frame.winfo_children():
            widget.destroy()

        try:
            if search_query:
                self.cursor.execute("SELECT id, title, cover, description FROM novels WHERE title LIKE ?",
                                   (f"%{search_query}%",))
            else:
                self.cursor.execute("SELECT id, title, cover, description FROM novels")
            
            novels = self.cursor.fetchall()
            row_num, col_num = 0, 0

            style = ttk.Style()
            style.configure("TFrame", background="#000000")
            style.configure("Custom.TFrame", background="#2a2a2a", relief="ridge", borderwidth=2)
            style.configure("TLabel", background="#000000", foreground="white")
            style.configure("TButton", background="#333333", foreground="white")
            style.configure("Rating.TLabel", background="#4a90e2", foreground="white", font=("Arial", 10, "bold"), 
                           borderwidth=1, relief="solid", padding=2, anchor="center")

            for novel_id, title, cover_data, description in novels:
                if cover_data and isinstance(cover_data, bytes):
                    image = Image.open(io.BytesIO(cover_data))
                else:
                    image = Image.new("RGB", (200, 280), "gray")

                image = image.resize((200, 280))
                novel_cover = ImageTk.PhotoImage(image)

                novel_card = ttk.Frame(self.novel_frame, style="Custom.TFrame")
                novel_card.grid(row=row_num, column=col_num, padx=5, pady=5)

                cover_label = ttk.Label(novel_card, image=novel_cover)
                cover_label.image = novel_cover
                cover_label.pack(pady=5)

                rating = round(random.uniform(8.0, 9.9), 1)
                rating_label = ttk.Label(novel_card, text=f"{rating}/10", style="Rating.TLabel", width=5)
                rating_label.pack(pady=(0, 5))

                title_label = ttk.Label(novel_card, text=title, foreground="white", background="#2a2a2a", 
                                       font=("Arial", 12, "bold"), wraplength=200, justify="center")
                title_label.pack(pady=2)

                # Оставляем только "Новелла" как тег
                tags_text = "Новелла"
                tags_label = ttk.Label(novel_card, text=tags_text, foreground="#a0a0a0", background="#2a2a2a", 
                                      font=("Arial", 8), wraplength=200, justify="center")
                tags_label.pack(pady=(0, 5))

                novel_card.bind("<Button-1>", lambda e, nid=novel_id: self.open_novel_page(nid))

                col_num += 1
                if col_num == 5:
                    col_num = 0
                    row_num += 1

        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось выполнить поиск: {e}")

    def load_novels(self):
        self.search_novels()

    def open_novel_page(self, novel_id):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.configure(bg="#000000")  # Черный фон
        try:
            self.cursor.execute("SELECT * FROM novels WHERE id=?", (novel_id,))
            novel = self.cursor.fetchone()

            if novel:
                cover_data = novel[2]
                if cover_data:
                    image = Image.open(io.BytesIO(cover_data))
                else:
                    image = Image.new("RGB", (200, 280), "gray")

                image = image.resize((200, 280))
                novel_cover = ImageTk.PhotoImage(image)

                main_frame = ttk.Frame(self.root, style="TFrame")
                main_frame.pack(fill="both", expand=True, padx=10, pady=10)

                cover_frame = ttk.Frame(main_frame, style="Cover.TFrame", width=200, height=280)
                cover_frame.pack(pady=10)
                cover_label = ttk.Label(cover_frame, image=novel_cover, background="#000000")
                cover_label.image = novel_cover
                cover_label.place(relx=0.5, rely=0.5, anchor="center")

                info_frame = ttk.Frame(main_frame, style="TFrame")
                info_frame.pack(fill="x", pady=5)

                title_label = ttk.Label(info_frame, text=novel[1], font=("Arial", 20, "bold"), 
                                       foreground="white", background="#000000")
                title_label.pack(pady=5)

                rating = round(random.uniform(4.0, 5.0), 2) * 1000
                rating_label = ttk.Label(info_frame, text=f"{rating:.0f}", font=("Arial", 14), 
                                        foreground="#4a90e2", background="#000000")
                rating_label.pack(pady=2)

                desc = novel[3] or "Легендарный механик (Новелла)"
                desc_label = ttk.Label(info_frame, text=desc, font=("Arial", 12), 
                                      foreground="#a0a0a0", background="#000000", wraplength=800)
                desc_label.pack(pady=5)

                action_frame = ttk.Frame(main_frame, style="TFrame")
                action_frame.pack(pady=10)
                ttk.Button(action_frame, text="Читать", command=lambda: self.open_chapter_page(None), 
                          style="TButton", width=10).pack(side="left", padx=5)
                ttk.Button(action_frame, text="Прогресс чтения", style="TButton", width=15).pack(side="left", padx=5)

                chapters_frame = ttk.Frame(main_frame, style="TFrame")
                chapters_frame.pack(fill="both", expand=True, pady=10)

                self.chapter_list = ttk.Treeview(chapters_frame, columns=("Title"), 
                                                show="headings", height=15, style="Treeview")
                self.chapter_list.heading("Title", text="Название главы")
                self.chapter_list.column("Title", width=550)
                self.chapter_list.pack(fill="both", expand=True)

                self.cursor.execute("SELECT id, title FROM chapters WHERE novel_id=?", (novel_id,))
                for chapter_id, title in self.cursor.fetchall():
                    self.chapter_list.insert("", "end", values=(title,))

                self.chapter_list.bind("<Double-1>", lambda e: self.open_chapter_page(e))

                nav_frame = ttk.Frame(main_frame, style="TFrame")
                nav_frame.pack(pady=10)
                ttk.Button(nav_frame, text="Back", command=self.create_main_page, style="TButton").pack(side="left", pady=5)
                ttk.Button(nav_frame, text="Add Chapter", command=lambda: self.open_add_chapter_page(novel_id), 
                          style="TButton").pack(side="left", pady=5)

            style = ttk.Style()
            style.configure("TFrame", background="#000000")
            style.configure("Cover.TFrame", background="#000000", relief="flat")
            style.configure("TLabel", background="#000000", foreground="white")
            style.configure("TButton", background="#4a90e2", foreground="white", font=("Arial", 12))
            style.configure("Treeview", background="#2a2a2a", foreground="white", fieldbackground="#2a2a2a")
            style.configure("Treeview.Heading", background="#4a90e2", foreground="white")
            style.configure("TEntry", fieldbackground="#2a2a2a", foreground="white")

        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть новеллу: {e}")

    def open_chapter_page(self, event):
        if event:
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
        else:
            if self.chapter_list.get_children():
                novel_id = self.cursor.lastrowid  # Предполагаем, что это ID последней добавленной новеллы
                self.cursor.execute("SELECT * FROM chapters WHERE novel_id=? ORDER BY id ASC LIMIT 1", (novel_id,))
                first_chapter = self.cursor.fetchone()
                if first_chapter:
                    self.display_chapter(first_chapter)

    def display_chapter(self, chapter):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.configure(bg="#000000")  # Черный фон
        chapter_id, novel_id, title, content = chapter  # Убрали update_date

        main_frame = ttk.Frame(self.root, style="TFrame")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Заголовок главы
        title_label = ttk.Label(main_frame, text=title, font=("Arial", 18, "bold"), 
                               foreground="white", background="#000000")
        title_label.pack(pady=10)

        # Текст содержания с форматированием
        text_frame = ttk.Frame(main_frame, style="TFrame")
        text_frame.pack(fill="both", expand=True, padx=20, pady=10)

        text_widget = tk.Text(text_frame, wrap="word", bg="#000000", fg="white", font=("Arial", 14), 
                             height=30, width=100, padx=10, pady=10)
        text_widget.pack(fill="both", expand=True)

        # Разбиваем текст на параграфы и форматируем
        paragraphs = content.split("\n\n")  # Разделяем по пустым строкам
        for i, para in enumerate(paragraphs):
            if para.strip():
                if para.startswith("## "):  # Заголовок уровня 2
                    text_widget.insert("end", f"\n{para[3:].strip()}\n", "heading2")
                elif para.startswith("# "):  # Заголовок уровня 1
                    text_widget.insert("end", f"\n{para[2:].strip()}\n", "heading1")
                elif para.startswith("- "):  # Маркированный список
                    text_widget.insert("end", f"• {para[2:].strip()}\n", "bullet")
                else:
                    text_widget.insert("end", f"{para.strip()}\n\n", "normal")

        # Настройка тегов для форматирования
        text_widget.tag_config("normal", foreground="white", justify="center")
        text_widget.tag_config("heading1", foreground="#4a90e2", font=("Arial", 18, "bold"), justify="center")
        text_widget.tag_config("heading2", foreground="#4a90e2", font=("Arial", 16, "bold"), justify="center")
        text_widget.tag_config("bullet", foreground="white", lmargin1=20, lmargin2=20, justify="left")

        text_widget.config(state="disabled")

        # Навигация
        nav_frame = ttk.Frame(main_frame, style="TFrame")
        nav_frame.pack(pady=10)

        prev_chapter = self.get_prev_chapter(chapter_id, novel_id)
        next_chapter = self.get_next_chapter(chapter_id, novel_id)

        if prev_chapter:
            ttk.Button(nav_frame, text="Previous", command=lambda: self.display_chapter(prev_chapter), 
                      style="TButton").pack(side="left", padx=5)

        ttk.Button(nav_frame, text="Back", command=lambda: self.open_novel_page(novel_id), 
                  style="TButton").pack(side="left", padx=5)

        if next_chapter:
            ttk.Button(nav_frame, text="Next", command=lambda: self.display_chapter(next_chapter), 
                      style="TButton").pack(side="left", padx=5)

        # Стили
        style = ttk.Style()
        style.configure("TFrame", background="#000000")
        style.configure("TLabel", background="#000000", foreground="white")
        style.configure("TButton", background="#4a90e2", foreground="white", font=("Arial", 12))
        style.configure("TEntry", fieldbackground="#2a2a2a", foreground="white")

    def get_prev_chapter(self, chapter_id, novel_id):
        self.cursor.execute("SELECT * FROM chapters WHERE novel_id=? AND id < ? ORDER BY id DESC LIMIT 1", 
                           (novel_id, chapter_id))
        return self.cursor.fetchone()

    def get_next_chapter(self, chapter_id, novel_id):
        self.cursor.execute("SELECT * FROM chapters WHERE novel_id=? AND id > ? ORDER BY id ASC LIMIT 1", 
                           (novel_id, chapter_id))
        return self.cursor.fetchone()

    def open_add_novel_page(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.configure(bg="#000000")
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

        self.root.configure(bg="#000000")
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
