import sqlite3
import os
import tkinter as tk
from tkinter import ttk, Entry
from PIL import Image, ImageTk


class NovelReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Novel Reader")
        self.root.geometry("800x600")
        self.root.configure(bg="#121212")

        self.current_page = None
        self.create_database()
        self.show_main_page()

    def create_database(self):
        conn = sqlite3.connect("novels.db")
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS novels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                cover TEXT,
                rating REAL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chapters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                novel_id INTEGER,
                title TEXT,
                content TEXT,
                FOREIGN KEY(novel_id) REFERENCES novels(id)
            )
        """)

        conn.commit()
        conn.close()

    def show_main_page(self):
        self.clear_window()

        search_frame = tk.Frame(self.root, bg="#121212")
        search_frame.pack(pady=10, padx=10, fill="x")

        search_entry = Entry(search_frame, font=("Arial", 12), bg="#222", fg="white")
        search_entry.pack(side="left", fill="x", expand=True, padx=5)

        search_button = ttk.Button(search_frame, text="Поиск", command=lambda: self.search_novels(search_entry.get()))
        search_button.pack(side="left", padx=5)

        novels_frame = tk.Frame(self.root, bg="#121212")
        novels_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.display_novels(novels_frame)

    def display_novels(self, frame, search_query=None):
        for widget in frame.winfo_children():
            widget.destroy()

        conn = sqlite3.connect("novels.db")
        cursor = conn.cursor()

        if search_query:
            cursor.execute("SELECT id, title, cover FROM novels WHERE title LIKE ?", ('%' + search_query + '%',))
        else:
            cursor.execute("SELECT id, title, cover FROM novels")

        novels = cursor.fetchall()
        conn.close()

        for i, (novel_id, title, cover_path) in enumerate(novels):
            img = Image.open(cover_path)
            img = img.resize((100, 150))
            cover = ImageTk.PhotoImage(img)

            frame_novel = tk.Frame(frame, bg="#121212")
            frame_novel.grid(row=i // 4, column=i % 4, padx=10, pady=10)

            label_cover = tk.Label(frame_novel, image=cover, bg="#121212")
            label_cover.image = cover
            label_cover.pack()

            label_title = tk.Label(frame_novel, text=title[:20], fg="white", bg="#121212", font=("Arial", 10))
            label_title.pack()

            btn_open = ttk.Button(frame_novel, text="Открыть", command=lambda n=novel_id: self.show_novel_page(n))
            btn_open.pack()

    def search_novels(self, query):
        self.display_novels(self.root.winfo_children()[1], query)

    def show_novel_page(self, novel_id):
        self.clear_window()

        conn = sqlite3.connect("novels.db")
        cursor = conn.cursor()
        cursor.execute("SELECT title, cover, rating FROM novels WHERE id=?", (novel_id,))
        novel = cursor.fetchone()

        if not novel:
            conn.close()
            return

        title, cover_path, rating = novel

        frame = tk.Frame(self.root, bg="#121212")
        frame.pack(pady=10)

        img = Image.open(cover_path)
        img = img.resize((150, 200))
        cover = ImageTk.PhotoImage(img)

        cover_label = tk.Label(frame, image=cover, bg="#121212")
        cover_label.image = cover
        cover_label.pack(side="left", padx=10)

        info_frame = tk.Frame(frame, bg="#121212")
        info_frame.pack(side="left", padx=10)

        tk.Label(info_frame, text=title, font=("Arial", 16, "bold"), fg="white", bg="#121212").pack(anchor="w")
        tk.Label(info_frame, text=f"Рейтинг: {rating}", font=("Arial", 12), fg="white", bg="#121212").pack(anchor="w")

        ttk.Button(info_frame, text="Продолжить читать", command=lambda: self.show_chapter_page(novel_id, last=True)).pack(pady=10)

        chapters_frame = tk.Frame(self.root, bg="#121212")
        chapters_frame.pack(fill="both", expand=True, padx=10, pady=10)

        canvas = tk.Canvas(chapters_frame, bg="#121212", highlightthickness=0)
        scrollbar = ttk.Scrollbar(chapters_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#121212")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        cursor.execute("SELECT id, title FROM chapters WHERE novel_id=?", (novel_id,))
        chapters = cursor.fetchall()
        conn.close()

        for chapter_id, chapter_title in chapters:
            ttk.Button(scrollable_frame, text=chapter_title, command=lambda c=chapter_id: self.show_chapter_page(c)).pack(fill="x", pady=2)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def show_chapter_page(self, chapter_id, last=False):
        self.clear_window()

        conn = sqlite3.connect("novels.db")
        cursor = conn.cursor()

        if last:
            cursor.execute("SELECT id, title, content FROM chapters WHERE novel_id=? ORDER BY id DESC LIMIT 1", (chapter_id,))
        else:
            cursor.execute("SELECT id, title, content FROM chapters WHERE id=?", (chapter_id,))

        chapter = cursor.fetchone()
        conn.close()

        if not chapter:
            return

        chapter_id, title, content = chapter

        frame = tk.Frame(self.root, bg="#121212")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(frame, text=title, font=("Arial", 16, "bold"), fg="white", bg="#121212").pack(pady=5)

        text_frame = tk.Frame(frame, bg="#121212")
        text_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(text_frame, bg="#121212", highlightthickness=0)
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=canvas.yview)
        text_container = tk.Frame(canvas, bg="#121212")

        text_container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=text_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        text_label = tk.Label(text_container, text=content, fg="white", bg="#121212", font=("Arial", 12), wraplength=750, justify="left")
        text_label.pack(pady=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()


root = tk.Tk()
app = NovelReaderApp(root)
root.mainloop()
