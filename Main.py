import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import io
import random
from datetime import datetime, timedelta

class NovelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Novel Catalog")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.geometry("1200x900")  # Увеличенный размер для большего экрана
        self.root.configure(bg="#000000")  # Черный фон
        self.novels = []  # Временное хранилище для новелл
        self.chapters = {}  # Временное хранилище для глав (по ID новеллы)
        self.create_main_page()

    def on_closing(self):
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
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
        search_query = self.search_entry.get().strip().lower()
        for widget in self.novel_frame.winfo_children():
            widget.destroy()

        novels = [n for n in self.novels if search_query in n['title'].lower()]
        if not search_query:
            novels = self.novels

        row_num, col_num = 0, 0
        style = ttk.Style()
        style.configure("TFrame", background="#000000")
        style.configure("Custom.TFrame", background="#2a2a2a", relief="ridge", borderwidth=2)
        style.configure("TLabel", background="#000000", foreground="white")
        style.configure("TButton", background="#333333", foreground="white")
        style.configure("Rating.TLabel", background="#4a90e2", foreground="white", font=("Arial", 10, "bold"), 
                       borderwidth=1, relief="solid", padding=2, anchor="center")

        for novel in novels:
            if 'cover' in novel and novel['cover']:
                image = Image.open(io.BytesIO(novel['cover']))
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

            title_label = ttk.Label(novel_card, text=novel['title'], foreground="white", background="#2a2a2a", 
                                   font=("Arial", 12, "bold"), wraplength=200, justify="center")
            title_label.pack(pady=2)

            tags = ["В наличии", "Новелла"]
            if random.choice([True, False]):
                tags.append("Корея")
            tags_text = " | ".join(tags)
            tags_label = ttk.Label(novel_card, text=tags_text, foreground="#a0a0a0", background="#2a2a2a", 
                                  font=("Arial", 8), wraplength=200, justify="center")
            tags_label.pack(pady=(0, 5))

            novel_card.bind("<Button-1>", lambda e, nid=novel['id']: self.open_novel_page(nid))

            col_num += 1
            if col_num == 5:
                col_num = 0
                row_num += 1

    def load_novels(self):
        # Пример данных (заменяет базу данных)
        self.novels = [
            {'id': 1, 'title': 'Легендарный механик', 'description': 'Научная фантастика', 
             'cover': self.generate_dummy_cover()},
            {'id': 2, 'title': 'Мастера меча онлайн', 'description': 'Фэнтези', 
             'cover': self.generate_dummy_cover()},
        ]
        self.search_novels()

    def generate_dummy_cover(self):
        # Генерация фиктивной обложки (серое изображение)
        image = Image.new("RGB", (200, 280), "gray")
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()

    def open_novel_page(self, novel_id):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.configure(bg="#000000")  # Черный фон
        novel = next((n for n in self.novels if n['id'] == novel_id), None)

        if novel:
            cover_data = novel['cover']
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

            title_label = ttk.Label(info_frame, text=novel['title'], font=("Arial", 20, "bold"), 
                                   foreground="white", background="#000000")
            title_label.pack(pady=5)

            rating = round(random.uniform(4.0, 5.0), 2) * 1000
            rating_label = ttk.Label(info_frame, text=f"{rating:.0f}", font=("Arial", 14), 
                                    foreground="#4a90e2", background="#000000")
            rating_label.pack(pady=2)

            desc = novel['description'] or "Легендарный механик (Новелла)"
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

            self.chapter_list = ttk.Treeview(chapters_frame, columns=("Title", "Date", "Status"), 
                                            show="headings", height=15, style="Treeview")
            self.chapter_list.heading("Title", text="Название главы")
            self.chapter_list.heading("Date", text="Дата")
            self.chapter_list.heading("Status", text="Статус")
            self.chapter_list.column("Title", width=400)
            self.chapter_list.column("Date", width=150)
            self.chapter_list.column("Status", width=100)
            self.chapter_list.pack(fill="both", expand=True)

            if novel_id in self.chapters:
                for chapter in self.chapters[novel_id]:
                    update_date = chapter.get('update_date', 
                                           (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%d.%m.%Y"))
                    status = random.choice(["Экстра", "Обычная", ""])
                    self.chapter_list.insert("", "end", values=(chapter['title'], update_date, status))

            self.chapter_list.bind("<Double-1>", lambda e: self.open_chapter_page(e))

            nav_frame = ttk.Frame(main_frame, style="TFrame")
            nav_frame.pack(pady=10)
            ttk.Button(self.root, text="Back", command=self.create_main_page, style="TButton").pack(pady=5)
            ttk.Button(self.root, text="Add Chapter", command=lambda: self.open_add_chapter_page(novel_id), 
                      style="TButton").pack(pady=5)

        style = ttk.Style()
        style.configure("TFrame", background="#000000")
        style.configure("Cover.TFrame", background="#000000", relief="flat")
        style.configure("TLabel", background="#000000", foreground="white")
        style.configure("TButton", background="#4a90e2", foreground="white", font=("Arial", 12))
        style.configure("Treeview", background="#2a2a2a", foreground="white", fieldbackground="#2a2a2a")
        style.configure("Treeview.Heading", background="#4a90e2", foreground="white")
        style.configure("TEntry", fieldbackground="#2a2a2a", foreground="white")

    def open_chapter_page(self, event):
        if event:
            selected_item = self.chapter_list.selection()
            if not selected_item:
                return

            chapter_title = self.chapter_list.item(selected_item[0], "values")[0]
            novel_id = next(n['id'] for n in self.novels if n['id'] in self.chapters)
            chapter = next(c for c in self.chapters[novel_id] if c['title'] == chapter_title)
            self.display_chapter((None, novel_id, chapter['title'], chapter['content'], None))
        else:
            if self.chapter_list.get_children():
                novel_id = next(n['id'] for n in self.novels if n['id'] in self.chapters)
                first_chapter = self.chapters[novel_id][0] if self.chapters[novel_id] else None
                if first_chapter:
                    self.display_chapter((None, novel_id, first_chapter['title'], first_chapter['content'], None))

    def display_chapter(self, chapter):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.configure(bg="#000000")  # Черный фон
        _, novel_id, title, content, _ = chapter

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

        # Эмуляция глав (временное решение без базы)
        chapters = self.chapters.get(novel_id, [])
        current_chapter = next((c for c in chapters if c['title'] == title), None)
        if current_chapter:
            chapter_index = chapters.index(current_chapter)
            prev_chapter = chapters[chapter_index - 1] if chapter_index > 0 else None
            next_chapter = chapters[chapter_index + 1] if chapter_index < len(chapters) - 1 else None
        else:
            prev_chapter, next_chapter = None, None

        if prev_chapter:
            ttk.Button(nav_frame, text="Previous", command=lambda: self.display_chapter((
                None, novel_id, prev_chapter['title'], prev_chapter['content'], None)), 
                      style="TButton").pack(side="left", padx=5)

        ttk.Button(nav_frame, text="Back", command=lambda: self.open_novel_page(novel_id), 
                  style="TButton").pack(side="left", padx=5)

        if next_chapter:
            ttk.Button(nav_frame, text="Next", command=lambda: self.display_chapter((
                None, novel_id, next_chapter['title'], next_chapter['content'], None)), 
                      style="TButton").pack(side="left", padx=5)

        # Стили
        style = ttk.Style()
        style.configure("TFrame", background="#000000")
        style.configure("TLabel", background="#000000", foreground="white")
        style.configure("TButton", background="#4a90e2", foreground="white", font=("Arial", 12))
        style.configure("TEntry", fieldbackground="#2a2a2a", foreground="white")

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
        new_novel = {
            'id': len(self.novels) + 1,
            'title': title,
            'description': description,
            'cover': self.cover_data
        }
        self.novels.append(new_novel)
        self.chapters[new_novel['id']] = []  # Инициализация списка глав
        self.create_main_page()

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

        ttk.Label(self.root, text="Update Date (DD.MM.YYYY):", style="TLabel").pack(pady=5)
        self.chapter_date_entry = ttk.Entry(self.root, style="TEntry")
        self.chapter_date_entry.pack(pady=5)

        ttk.Button(self.root, text="Add Chapter", command=lambda: self.add_chapter(novel_id), style="TButton").pack(pady=10)
        ttk.Button(self.root, text="Back", command=lambda: self.open_novel_page(novel_id), style="TButton").pack(pady=10)

    def add_chapter(self, novel_id):
        title = self.chapter_title_entry.get()
        content = self.chapter_content_entry.get("1.0", "end").strip()
        update_date = self.chapter_date_entry.get() or (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%d.%m.%Y")
        if not title:
            messagebox.showerror("Ошибка", "Введите название главы!")
            return
        if not content:
            messagebox.showerror("Ошибка", "Введите содержание главы!")
            return
        if novel_id not in self.chapters:
            self.chapters[novel_id] = []
        self.chapters[novel_id].append({'title': title, 'content': content, 'update_date': update_date})
        self.open_novel_page(novel_id)

if __name__ == "__main__":
    root = tk.Tk()
    app = NovelApp(root)
    root.mainloop()
