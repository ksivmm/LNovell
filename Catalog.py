import tkinter as tk from tkinter import ttk, messagebox from tkinter import PhotoImage import sqlite3
iclass NovelApp: def init(self, root): self.root = root self.root.title("Novel Catalog") self.create_db() self.create_main_page()

def create_db(self):
    self.conn = sqlite3.connect("novels.db")
    self.cursor = self.conn.cursor()
    self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS novels (
            id INTEGER PRIMARY KEY,
            title TEXT,
            cover TEXT,
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
    self.main_frame = ttk.Frame(self.root)
    self.main_frame.pack(fill="both", expand=True)

    self.catalog_label = ttk.Label(self.main_frame, text="Catalog of Novels")
    self.catalog_label.pack(pady=10)

    self.novel_frame = ttk.Frame(self.main_frame)
    self.novel_frame.pack(fill="both", expand=True)

    self.load_novels()

    self.add_novel_button = ttk.Button(self.main_frame, text="Add Novel", command=self.open_add_novel_page)
    self.add_novel_button.pack(pady=10)

def load_novels(self):
    for widget in self.novel_frame.winfo_children():
        widget.destroy()

    self.cursor.execute("SELECT * FROM novels")
    row_num = 0
    col_num = 0
    for row in self.cursor.fetchall():
        novel_cover = PhotoImage(file=row[2]).subsample(4, 4)  # Resize cover to 161x225
        cover_label = ttk.Label(self.novel_frame, image=novel_cover)
        cover_label.image = novel_cover
        cover_label.grid(row=row_num, column=col_num, padx=5, pady=5)
        cover_label.bind("<Button-1>", lambda e, novel_id=row[0]: self.open_novel_page(novel_id))

        title_label = ttk.Label(self.novel_frame, text=row[1], width=20, anchor="center")
        title_label.grid(row=row_num+1, column=col_num, padx=5, pady=5)

        col_num += 1
        if col_num == 7:
            col_num = 0
            row_num += 2

def open_novel_page(self, novel_id):
    self.main_frame.pack_forget()
    self.novel_frame = ttk.Frame(self.root)
    self.novel_frame.pack(fill="both", expand=True)

    self.cursor.execute("SELECT * FROM novels WHERE id=?", (novel_id,))
    novel = self.cursor.fetchone()

    self.novel_cover = ttk.Label(self.novel_frame, text=novel[2])
    self.novel_cover.pack(pady=10)

    self.novel_description = ttk.Label(self.novel_frame, text=novel[3])
    self.novel_description.pack(pady=10)

    self.chapter_list = ttk.Treeview(self.novel_frame, columns=("Title"), show="headings")
    self.chapter_list.heading("Title", text="Title")
    self.chapter_list.pack(fill="both", expand=True)
    self.chapter_list.bind("<Double-1>", self.open_chapter_page)

    self.cursor.execute("SELECT * FROM chapters WHERE novel_id=?", (novel_id,))
    for row in self.cursor.fetchall():
        self.chapter_list.insert("", "end", values=(row[2],))

    self.add_chapter_button = ttk.Button(self.novel_frame, text="Add Chapter", command=lambda: self.open_add_chapter_page(novel_id))
    self.add_chapter_button.pack(pady=10)

    self.back_button = ttk.Button(self.novel_frame, text="Back", command=self.back_to_main)
    self.back_button.pack(pady=10)

def open_chapter_page(self, event):
    selected_item = self.chapter_list.selection()[0]
    chapter_title = self.chapter_list.item(selected_item, "values")[0]
    self.cursor.execute("SELECT * FROM chapters WHERE title=?", (chapter_title,))
    chapter = self.cursor.fetchone()

    self.novel_frame.pack_forget()
    self.chapter_frame = ttk.Frame(self.root)
    self.chapter_frame.pack(fill="both", expand=True)

    self.chapter_title_label = ttk.Label(self.chapter_frame, text=chapter[2])
    self.chapter_title_label.pack(pady=10)

    self.chapter_content = tk.Text(self.chapter_frame)
    self.chapter_content.pack(fill="both", expand=True)
    self.chapter_content.insert("1.0", chapter[3])

    self.nav_frame = ttk.Frame(self.chapter_frame)
    self.nav_frame.pack(pady=10)

    self.back_button = ttk.Button(self.nav_frame, text="Back", command=self.back_to_novel)
    self.back_button.pack(side="left")

    self.next_button = ttk.Button(self.nav_frame, text="Next", command=self.next_chapter)
    self.next_button.pack(side="left")

def back_to_main(self):
    self.novel_frame.pack_forget()
    self.main_frame.pack(fill="both", expand=True)

def back_to_novel(self):
    self.chapter_frame.pack_forget()
    self.novel_frame.pack(fill="both", expand=True)

def next_chapter(self):
    messagebox.showinfo("Navigation", "This functionality is not implemented yet.")

def open_add_novel_page(self):
    self.main_frame.pack_forget()
    self.add_novel_frame = ttk.Frame(self.root)
    self.add_novel_frame.pack(fill="both", expand=True)

    self.novel_title_label = ttk.Label(self.add_novel_frame, text="Title:")
    self.novel_title_label.pack(pady=10)
    self.novel_title_entry = ttk.Entry(self.add_novel_frame)
    self.novel_title_entry.pack(pady=10)

    self.novel_cover_label = ttk.Label(self.add_novel_frame, text="Cover:")
    self.novel_cover_label.pack(pady=10)
    self.novel_cover_entry = ttk.Entry(self.add_novel_frame)
    self.novel_cover_entry.pack(pady=10)

    self.novel_description_label = ttk.Label(self.add_novel_frame, text="Description:")
    self.novel_description_label.pack(pady=10)
    self.novel_description_entry = ttk.Entry(self.add_novel_frame)
    self.novel_description_entry.pack(pady=10)

    self.add_button = ttk.Button(self.add_novel_frame, text="Add Novel", command=self.add_novel)
    self.add_button.pack(pady=10)

    self.back_button = ttk.Button(self.add_novel_frame, text="Back", command=self.back_to_main_from_add)
    self.back_button.pack(pady=10)

def add_novel(self):
    title = self.novel_title_entry.get()
    cover = self.novel_cover_entry.get()
    description = self.novel_description_entry.get()
    self.cursor.execute("INSERT INTO novels (title, cover, description) VALUES (?, ?, ?)", (title, cover, description))
    self.conn.commit()
    self.back_to_main_from_add()
    self.load_novels()

def back_to_main_from_add(self):
    self.add_novel_frame.pack_forget()
    self.main_frame.pack(fill="both", expand=True)

def open_add_chapter_page(self, novel_id):
    self.novel_frame.pack_forget()
    self.add_chapter_frame = ttk.Frame(self.root)
    self.add_chapter_frame.pack(fill="both", expand=True)

    self.chapter_title_label = ttk.Label(self.add_chapter_frame, text="Chapter Title:")
    self.chapter_title_label.pack(pady=10)
    self.chapter_title_entry = ttk.Entry(self.add_chapter_frame)
    self.chapter_title_entry.pack(pady=10)

    self.chapter_content_label = ttk.Label(self.add_chapter_frame, text="Content:")
    self.chapter_content_label.pack(pady=10)
    self.chapter_content_entry = tk.Text(self.add_chapter_frame)
    self.chapter_content_entry.pack(pady=10)

    self.add_button = ttk.Button(self.add_chapter_frame, text="Add Chapter", command=lambda: self.add_chapter(novel_id))
    self.add_button.pack(pady=10)

    self.back_button = ttk.Button(self.add_chapter_frame, text="Back", command=self.back_to_novel_from_add)
    self.back_button.pack(pady=10)

def add_chapter(self, novel_id):
    title = self.chapter_title_entry.get()
    content = self.chapter_content_entry.get("1.0", "end")
    self.cursor.execute("INSERT INTO chapters (novel_id, title, content) VALUES (?, ?, ?)", (novel_id, title, content))
    self.conn.commit()
    self.back_to_novel_from_add()
    self.load_chapters(novel_id)

def back_to_novel_from_add(self):
    self.add_chapter_frame.pack_forget()
    self.novel_frame.pack(fill="both", expand=True)

def load_chapters(self, novel_id):
    self.chapter_list.delete(*self.chapter_list.get_children())
    self.cursor.execute("SELECT * FROM chapters WHERE novel_id=?", (novel_id,))
    for row in self.cursor.fetchall():
        self.chapter_list.insert("", "end", values=(row[2],))

if name == "main": root = tk.Tk() app = NovelApp(root) root.mainloop()

