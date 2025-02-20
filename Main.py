import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import sqlite3
import io


class NovelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Novel Catalog")
        self.create_db()
        self.create_main_page()

    def create_db(self):
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

    def create_main_page(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        ttk.Label(self.root, text="Catalog of Novels").pack(pady=10)
        self.novel_frame = ttk.Frame(self.root)
        self.novel_frame.pack(fill="both", expand=True)
        self.load_novels()
        ttk.Button(self.root, text="Add Novel", command=self.open_add_novel_page).pack(pady=10)

    def load_novels(self):
        for widget in self.novel_frame.winfo_children():
            widget.destroy()

        self.cursor.execute("SELECT id, title, cover FROM novels")
        row_num, col_num = 0, 0

        for novel_id, title, cover_data in self.cursor.fetchall():
            if cover_data and isinstance(cover_data, bytes):
                image = Image.open(io.BytesIO(cover_data))
            else:
                image = Image.new("RGB", (161, 225), "gray")

            image = image.resize((161, 225))
            novel_cover = ImageTk.PhotoImage(image)

            cover_label = ttk.Label(self.novel_frame, image=novel_cover)
            cover_label.image = novel_cover
            cover_label.grid(row=row_num, column=col_num, padx=5, pady=5)
            
            # Исправленный обработчик нажатия
            cover_label.bind("<Button-1>", lambda e, novel_id=novel_id: self.open_novel_page(novel_id))

            ttk.Label(self.novel_frame, text=title, width=20, anchor="center").grid(row=row_num+1, column=col_num, padx=5, pady=5)

            col_num += 1
            if col_num == 7:
                col_num = 0
                row_num += 2

    def open_novel_page(self, novel_id):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.cursor.execute("SELECT * FROM novels WHERE id=?", (novel_id,))
        novel = self.cursor.fetchone()

        if novel:
            cover_data = novel[2]
            if cover_data:
                image = Image.open(io.BytesIO(cover_data))
            else:
                image = Image.new("RGB", (161, 225), "gray")

            image = image.resize((161, 225))
            novel_cover = ImageTk.PhotoImage(image)

            ttk.Label(self.root, image=novel_cover).pack(pady=10)
            ttk.Label(self.root, text=novel[1], font=("Arial", 16)).pack()
            ttk.Label(self.root, text=novel[3]).pack()

            self.chapter_list = ttk.Treeview(self.root, columns=("Title"), show="headings")
            self.chapter_list.heading("Title", text="Title")
            self.chapter_list.pack(fill="both", expand=True)
            self.chapter_list.bind("<Double-1>", self.open_chapter_page)

            self.cursor.execute("SELECT * FROM chapters WHERE novel_id=?", (novel_id,))
            for row in self.cursor.fetchall():
                self.chapter_list.insert("", "end", values=(row[2],))

            ttk.Button(self.root, text="Add Chapter", command=lambda: self.open_add_chapter_page(novel_id)).pack(pady=10)
            ttk.Button(self.root, text="Back", command=self.create_main_page).pack(pady=10)

    def open_chapter_page(self, event):
        selected_item = self.chapter_list.selection()
        if not selected_item:
            return

        chapter_title = self.chapter_list.item(selected_item[0], "values")[0]
        self.cursor.execute("SELECT * FROM chapters WHERE title=?", (chapter_title,))
        chapter = self.cursor.fetchone()

        if chapter:
            for widget in self.root.winfo_children():
                widget.destroy()

            ttk.Label(self.root, text=chapter[2], font=("Arial", 16)).pack(pady=10)

            text_widget = tk.Text(self.root)
            text_widget.pack(fill="both", expand=True)
            text_widget.insert("1.0", chapter[3])

            ttk.Button(self.root, text="Back", command=lambda: self.open_novel_page(chapter[1])).pack(pady=10)

    def open_add_novel_page(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        ttk.Label(self.root, text="Title:").pack(pady=5)
        self.novel_title_entry = ttk.Entry(self.root)
        self.novel_title_entry.pack(pady=5)

        ttk.Button(self.root, text="Upload Cover", command=self.upload_cover).pack(pady=5)
        ttk.Label(self.root, text="Description:").pack(pady=5)
        self.novel_description_entry = ttk.Entry(self.root)
        self.novel_description_entry.pack(pady=5)

        ttk.Button(self.root, text="Add Novel", command=self.add_novel).pack(pady=10)
        ttk.Button(self.root, text="Back", command=self.create_main_page).pack(pady=10)

        self.cover_data = None

    def upload_cover(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, "rb") as file:
                self.cover_data = file.read()

    def add_novel(self):
        title = self.novel_title_entry.get()
        description = self.novel_description_entry.get()
        if title and self.cover_data:
            self.cursor.execute("INSERT INTO novels (title, cover, description) VALUES (?, ?, ?)", (title, self.cover_data, description))
            self.conn.commit()
        self.create_main_page()

    def open_add_chapter_page(self, novel_id):
        for widget in self.root.winfo_children():
            widget.destroy()

        ttk.Label(self.root, text="Chapter Title:").pack(pady=10)
        self.chapter_title_entry = ttk.Entry(self.root)
        self.chapter_title_entry.pack(pady=10)

        ttk.Label(self.root, text="Content:").pack(pady=10)
        self.chapter_content_entry = tk.Text(self.root)
        self.chapter_content_entry.pack(pady=10)

        ttk.Button(self.root, text="Add Chapter", command=lambda: self.add_chapter(novel_id)).pack(pady=10)
        ttk.Button(self.root, text="Back", command=lambda: self.open_novel_page(novel_id)).pack(pady=10)

    def add_chapter(self, novel_id):
        title = self.chapter_title_entry.get()
        content = self.chapter_content_entry.get("1.0", "end").strip()
        if title and content:
            self.cursor.execute("INSERT INTO chapters (novel_id, title, content) VALUES (?, ?, ?)", (novel_id, title, content))
            self.conn.commit()
        self.open_novel_page(novel_id)


if __name__ == "__main__":
    root = tk.Tk()
    app = NovelApp(root)
    root.mainloop()
