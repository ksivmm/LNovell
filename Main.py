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
        if hasattr(self, "current_frame"):
            self.current_frame.destroy()

        self.current_frame = ttk.Frame(self.root)
        self.current_frame.pack(fill="both", expand=True)

        ttk.Label(self.current_frame, text="Catalog of Novels", font=("Arial", 14)).pack(pady=10)

        self.novel_frame = ttk.Frame(self.current_frame)
        self.novel_frame.pack(fill="both", expand=True)

        self.load_novels()

        ttk.Button(self.current_frame, text="Add Novel", command=self.open_add_novel_page).pack(pady=10)

    def load_novels(self):
        for widget in self.novel_frame.winfo_children():
            widget.destroy()

        self.cursor.execute("SELECT * FROM novels")
        novels = self.cursor.fetchall()

        for i, (novel_id, title, cover_data, _) in enumerate(novels):
            if cover_data:
                image = Image.open(io.BytesIO(cover_data))
                image = image.resize((100, 150), Image.Resampling.LANCZOS)
                novel_cover = ImageTk.PhotoImage(image)
            else:
                novel_cover = None

            cover_label = ttk.Label(self.novel_frame, image=novel_cover)
            cover_label.image = novel_cover
            cover_label.grid(row=i // 5, column=i % 5, padx=5, pady=5)
            cover_label.bind("<Button-1>", lambda e, novel_id=novel_id: self.open_novel_page(novel_id))

            ttk.Label(self.novel_frame, text=title, width=20).grid(row=(i // 5) + 1, column=i % 5, padx=5, pady=5)

    def open_novel_page(self, novel_id):
        self.current_frame.destroy()
        self.current_frame = ttk.Frame(self.root)
        self.current_frame.pack(fill="both", expand=True)

        self.cursor.execute("SELECT * FROM novels WHERE id=?", (novel_id,))
        novel = self.cursor.fetchone()

        title, cover_data, description = novel[1:]

        if cover_data:
            image = Image.open(io.BytesIO(cover_data))
            image = image.resize((200, 300), Image.Resampling.LANCZOS)
            novel_cover = ImageTk.PhotoImage(image)
        else:
            novel_cover = None

        ttk.Label(self.current_frame, image=novel_cover).pack(pady=10)
        ttk.Label(self.current_frame, text=title, font=("Arial", 16)).pack()
        ttk.Label(self.current_frame, text=description).pack()

        ttk.Button(self.current_frame, text="Back", command=self.create_main_page).pack(pady=10)

    def open_add_novel_page(self):
        self.current_frame.destroy()
        self.current_frame = ttk.Frame(self.root)
        self.current_frame.pack(fill="both", expand=True)

        ttk.Label(self.current_frame, text="Add a New Novel", font=("Arial", 14)).pack(pady=10)

        ttk.Label(self.current_frame, text="Title:").pack()
        self.novel_title_entry = ttk.Entry(self.current_frame)
        self.novel_title_entry.pack()

        ttk.Label(self.current_frame, text="Cover:").pack()
        self.upload_button = ttk.Button(self.current_frame, text="Upload Cover", command=self.upload_cover)
        self.upload_button.pack()

        ttk.Label(self.current_frame, text="Description:").pack()
        self.novel_description_entry = ttk.Entry(self.current_frame)
        self.novel_description_entry.pack()

        ttk.Button(self.current_frame, text="Add Novel", command=self.add_novel).pack(pady=10)
        ttk.Button(self.current_frame, text="Back", command=self.create_main_page).pack(pady=10)

        self.cover_data = None

    def upload_cover(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            with open(file_path, "rb") as file:
                self.cover_data = file.read()

    def add_novel(self):
        title = self.novel_title_entry.get()
        description = self.novel_description_entry.get()

        if not title.strip():
            messagebox.showerror("Error", "Title cannot be empty")
            return

        self.cursor.execute("INSERT INTO novels (title, cover, description) VALUES (?, ?, ?)", (title, self.cover_data, description))
        self.conn.commit()
        self.create_main_page()

if __name__ == "__main__":
    root = tk.Tk()
    app = NovelApp(root)
    root.mainloop()
