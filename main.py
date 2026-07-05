import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import ollama
import uuid
import json
import os
import re
import subprocess
import time
import urllib.request

# ─── AUTO START OLLAMA ────────────────────────────────
def start_ollama():
    try:
        urllib.request.urlopen("http://localhost:11434")
        print("Ollama already running!")
        return
    except:
        pass
    try:
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        print("Starting Ollama...")
        for i in range(15):
            time.sleep(1)
            try:
                urllib.request.urlopen("http://localhost:11434")
                print("Ollama is ready!")
                return
            except:
                pass
    except FileNotFoundError:
        print("Ollama not found! Please install from https://ollama.com")

start_ollama()

# ─── HISTORY ──────────────────────────────────────────
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chat_history.json")

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"chats": {}, "titles": {}}

def save_history(chats, titles):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump({"chats": chats, "titles": titles}, f, ensure_ascii=False, indent=2)

# ─── EXPORT CV AS PDF ─────────────────────────────────
def export_cv_pdf(cv_text, save_path):
    from fpdf import FPDF

    cv_text = cv_text.encode('ascii', 'ignore').decode('ascii')
    cv_text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', cv_text)
    cv_text = cv_text.replace('***', '').replace('**', '')

    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(18, 18, 18)
    pdf.set_auto_page_break(auto=True, margin=18)

    lines = cv_text.split('\n')
    first_line_idx = next((i for i, l in enumerate(lines) if l.strip()), 0)

    SECTION_KEYWORDS = [
        'PROFESSIONAL SUMMARY', 'SUMMARY', 'WORK EXPERIENCE', 'EXPERIENCE',
        'EDUCATION', 'TECHNICAL SKILLS', 'SKILLS', 'PROJECTS', 'LANGUAGES',
        'CERTIFICATIONS', 'CONTACT', 'NAME & CONTACT'
    ]

    def is_section(line):
        upper = line.upper().strip().replace('##', '').strip()
        return any(upper == kw or upper.startswith(kw) for kw in SECTION_KEYWORDS) or line.startswith('##')

    def safe_line(line):
        words = []
        for w in line.split():
            while len(w) > 55:
                words.append(w[:55])
                w = w[55:]
            words.append(w)
        return ' '.join(words)

    for idx, line in enumerate(lines):
        line = line.strip()
        if not line:
            pdf.ln(1)
            continue
        line = safe_line(line)
        try:
            if idx == first_line_idx:
                pdf.set_font('Helvetica', 'B', 20)
                pdf.set_text_color(15, 15, 15)
                pdf.multi_cell(0, 11, line, align='C')
                pdf.ln(1)
            elif '|' in line or '@' in line:
                pdf.set_font('Helvetica', '', 9)
                pdf.set_text_color(80, 80, 80)
                pdf.multi_cell(0, 5, line, align='C')
            elif line.startswith('http') or 'github.com' in line or 'linkedin.com' in line:
                pdf.set_font('Helvetica', 'I', 9)
                pdf.set_text_color(0, 80, 180)
                pdf.multi_cell(0, 5, line, align='C')
                pdf.set_text_color(30, 30, 30)
            elif is_section(line):
                clean = line.replace('##', '').strip().upper()
                pdf.ln(4)
                pdf.set_font('Helvetica', 'B', 11)
                pdf.set_text_color(30, 90, 60)
                pdf.multi_cell(0, 7, clean)
                pdf.set_draw_color(30, 90, 60)
                pdf.set_line_width(0.5)
                pdf.line(18, pdf.get_y(), 192, pdf.get_y())
                pdf.ln(3)
                pdf.set_text_color(30, 30, 30)
            elif line.startswith('-') or line.startswith('*') or line.startswith('•'):
                pdf.set_font('Helvetica', '', 10)
                pdf.set_text_color(40, 40, 40)
                pdf.multi_cell(0, 6, '  •  ' + line[1:].strip())
                pdf.ln(1)
            else:
                pdf.set_font('Helvetica', '', 10)
                pdf.set_text_color(40, 40, 40)
                pdf.multi_cell(0, 6, line)
                pdf.ln(1)
        except Exception:
            continue

    pdf.output(save_path)

# ─── MODELS ───────────────────────────────────────────
MODELS = [
    "glm-5.2:cloud",
    "minimax-m3:cloud",
    "llama3.2:1b",
    "llama3.2",
    "llama3.1",
    "gemma2",
    "mistral",
    "phi3",
]

# ─── COLORS ───────────────────────────────────────────
BG_DARK      = "#0f0f0f"
BG_SIDEBAR   = "#171717"
BG_MSG_AI    = "#1a1a1a"
BG_MSG_USER  = "#1e3a2f"
BG_INPUT     = "#1a1a1a"
BG_BTN       = "#2f2f2f"
BG_BTN_HOVER = "#3a3a3a"
BG_ACTIVE    = "#2f2f2f"
BG_SEND      = "#2a7a4a"
BG_UPLOAD    = "#1a2e3a"
BG_EXPORT    = "#2a4a7a"
BG_SWITCH    = "#2a1a3a"

TEXT_PRIMARY   = "#ececec"
TEXT_SECONDARY = "#888888"
TEXT_AI        = "#dddddd"
TEXT_USER      = "#e0ffe8"
TEXT_TITLE     = "#ffffff"

BORDER     = "#2a2a2a"
FONT_TITLE = ("Segoe UI", 14, "bold")
FONT_SMALL = ("Segoe UI", 10)
FONT_MSG   = ("Segoe UI", 11)


class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AnikaAI — CV Builder")
        self.root.geometry("980x680")
        self.root.minsize(700, 500)
        self.root.configure(bg=BG_DARK)

        data = load_history()
        self.chats = data["chats"]
        self.chat_titles = data["titles"]
        self.active_chat = None
        self.loading = False
        self.selected_model = tk.StringVar(value=MODELS[0])
        self.last_cv_text = ""
        self.stream_buffer = ""

        # File management
        self.uploaded_text = ""
        self.auto_loaded_file = None
        self.uploaded_file_text = ""
        self.uploaded_filename = ""
        self.using_file = tk.StringVar(value="No file loaded")

        # Auto-load project info txt
        self.auto_load_txt()

        self.build_ui()

        if self.chat_titles:
            self.refresh_chat_list()
            last_id = list(self.chat_titles.keys())[-1]
            self.select_chat(last_id)

    def auto_load_txt(self):
        folder = os.path.dirname(os.path.abspath(__file__))
        for fname in os.listdir(folder):
            if fname.endswith(".txt"):
                try:
                    with open(os.path.join(folder, fname), "r", encoding="utf-8") as f:
                        self.uploaded_text = f.read()
                    self.auto_loaded_file = fname
                    self.using_file.set(f"📌 Using: {fname}")
                    return
                except:
                    pass

    # ─── BUILD UI ─────────────────────────────────────
    def build_ui(self):
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.build_sidebar()
        self.build_main()

    # ─── SIDEBAR ──────────────────────────────────────
    def build_sidebar(self):
        self.sidebar = tk.Frame(self.root, bg=BG_SIDEBAR, width=240)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)
        self.sidebar.columnconfigure(0, weight=1)
        self.sidebar.rowconfigure(10, weight=1)

        # Title
        tk.Label(
            self.sidebar, text="✦ AnikaAI",
            bg=BG_SIDEBAR, fg=TEXT_TITLE,
            font=FONT_TITLE, anchor="w",
            padx=14, pady=14
        ).grid(row=0, column=0, sticky="ew")

        # New Chat
        tk.Button(
            self.sidebar, text="＋  New Chat",
            bg=BG_BTN, fg=TEXT_PRIMARY,
            font=FONT_SMALL, bd=0, cursor="hand2",
            anchor="w", padx=14, pady=8,
            activebackground=BG_BTN_HOVER,
            activeforeground=TEXT_PRIMARY,
            command=self.new_chat
        ).grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 4))

        # Divider
        tk.Frame(self.sidebar, bg=BORDER, height=1).grid(
            row=2, column=0, sticky="ew", padx=10, pady=(0, 6)
        )

        # File section label
        tk.Label(
            self.sidebar, text="FILES",
            bg=BG_SIDEBAR, fg=TEXT_SECONDARY,
            font=("Segoe UI", 8), anchor="w",
            padx=14
        ).grid(row=3, column=0, sticky="ew")

        # Upload button
        tk.Button(
            self.sidebar, text="📄  Upload TXT File",
            bg=BG_UPLOAD, fg="#7fcfff",
            font=FONT_SMALL, bd=0, cursor="hand2",
            anchor="w", padx=14, pady=8,
            activebackground="#1e3a4a",
            activeforeground="#7fcfff",
            command=self.upload_file
        ).grid(row=4, column=0, sticky="ew", padx=10, pady=(2, 2))

        # Switch file button
        tk.Button(
            self.sidebar, text="🔄  Switch File",
            bg=BG_SWITCH, fg="#cf9fff",
            font=FONT_SMALL, bd=0, cursor="hand2",
            anchor="w", padx=14, pady=8,
            activebackground="#3a1a5a",
            activeforeground="#cf9fff",
            command=self.switch_file
        ).grid(row=5, column=0, sticky="ew", padx=10, pady=(0, 4))

        # Active file indicator
        self.active_file_label = tk.Label(
            self.sidebar,
            textvariable=self.using_file,
            bg=BG_SIDEBAR, fg="#7fcfff",
            font=("Segoe UI", 8), anchor="w",
            padx=14, wraplength=200
        )
        self.active_file_label.grid(row=6, column=0, sticky="ew", pady=(0, 6))

        # Divider
        tk.Frame(self.sidebar, bg=BORDER, height=1).grid(
            row=7, column=0, sticky="ew", padx=10, pady=(0, 6)
        )

        # Export button
        tk.Button(
            self.sidebar, text="📥  Export CV as PDF",
            bg=BG_EXPORT, fg="#7fcfff",
            font=FONT_SMALL, bd=0, cursor="hand2",
            anchor="w", padx=14, pady=8,
            activebackground="#1e2e4a",
            activeforeground="#aaccff",
            command=self.export_cv
        ).grid(row=8, column=0, sticky="ew", padx=10, pady=(0, 6))

        # Model label + dropdown
        tk.Label(
            self.sidebar, text="Model",
            bg=BG_SIDEBAR, fg=TEXT_SECONDARY,
            font=("Segoe UI", 9), anchor="w", padx=14
        ).grid(row=9, column=0, sticky="ew", pady=(4, 2))

        model_menu = tk.OptionMenu(self.sidebar, self.selected_model, *MODELS)
        model_menu.config(
            bg=BG_BTN, fg=TEXT_PRIMARY,
            activebackground=BG_BTN_HOVER,
            activeforeground=TEXT_PRIMARY,
            highlightthickness=0, bd=0,
            font=FONT_SMALL, cursor="hand2"
        )
        model_menu["menu"].config(
            bg=BG_BTN, fg=TEXT_PRIMARY,
            activebackground=BG_ACTIVE,
            activeforeground=TEXT_PRIMARY,
            font=FONT_SMALL
        )
        model_menu.grid(row=9, column=0, sticky="ew", padx=10, pady=(22, 6))

        # Divider
        tk.Frame(self.sidebar, bg=BORDER, height=1).grid(
            row=9, column=0, sticky="sew", padx=10, pady=(0, 4)
        )

        # Chat list
        list_frame = tk.Frame(self.sidebar, bg=BG_SIDEBAR)
        list_frame.grid(row=10, column=0, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)

        self.chat_list_canvas = tk.Canvas(
            list_frame, bg=BG_SIDEBAR, bd=0, highlightthickness=0
        )
        self.chat_list_inner = tk.Frame(self.chat_list_canvas, bg=BG_SIDEBAR)

        self.chat_list_inner.bind(
            "<Configure>",
            lambda e: self.chat_list_canvas.configure(
                scrollregion=self.chat_list_canvas.bbox("all")
            )
        )
        self.chat_list_canvas.create_window((0, 0), window=self.chat_list_inner, anchor="nw")
        self.chat_list_canvas.pack(side="left", fill="both", expand=True)

    # ─── MAIN AREA ────────────────────────────────────
    def build_main(self):
        main_frame = tk.Frame(self.root, bg=BG_DARK)
        main_frame.grid(row=0, column=1, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        self.header_label = tk.Label(
            main_frame,
            text="Ask anything about your CV or type 'Create my CV'",
            bg=BG_DARK, fg=TEXT_SECONDARY,
            font=FONT_SMALL, anchor="w",
            padx=20, pady=12
        )
        self.header_label.grid(row=0, column=0, sticky="ew")
        tk.Frame(main_frame, bg=BORDER, height=1).grid(row=0, column=0, sticky="sew")

        # Messages
        self.msg_frame = tk.Frame(main_frame, bg=BG_DARK)
        self.msg_frame.grid(row=1, column=0, sticky="nsew")
        self.msg_frame.columnconfigure(0, weight=1)
        self.msg_frame.rowconfigure(0, weight=1)

        self.msg_canvas = tk.Canvas(
            self.msg_frame, bg=BG_DARK, bd=0, highlightthickness=0
        )
        msg_scroll = tk.Scrollbar(
            self.msg_frame, orient="vertical", command=self.msg_canvas.yview
        )
        self.msg_inner = tk.Frame(self.msg_canvas, bg=BG_DARK)

        self.msg_inner.bind(
            "<Configure>",
            lambda e: self.msg_canvas.configure(
                scrollregion=self.msg_canvas.bbox("all")
            )
        )
        self.msg_canvas.create_window((0, 0), window=self.msg_inner, anchor="nw")
        self.msg_canvas.configure(yscrollcommand=msg_scroll.set)
        self.msg_canvas.pack(side="left", fill="both", expand=True)
        msg_scroll.pack(side="right", fill="y")

        self.empty_label = tk.Label(
            self.msg_inner,
            text="✦ CV Assistant\n\n• Ask questions about your CV\n• Type 'Create my CV' to generate\n• Switch between files in sidebar\n• Export as PDF anytime",
            bg=BG_DARK, fg="#2a2a2a",
            font=("Segoe UI", 13, "bold"),
            justify="center"
        )
        self.empty_label.pack(expand=True, pady=120)

        # Input
        input_frame = tk.Frame(main_frame, bg=BG_DARK, pady=14, padx=20)
        input_frame.grid(row=2, column=0, sticky="ew")
        input_frame.columnconfigure(0, weight=1)

        box = tk.Frame(
            input_frame, bg=BG_INPUT,
            highlightbackground=BORDER,
            highlightthickness=1, bd=0
        )
        box.grid(row=0, column=0, sticky="ew")
        box.columnconfigure(0, weight=1)

        self.input_box = tk.Text(
            box, height=2, font=FONT_MSG,
            bg=BG_INPUT, fg=TEXT_PRIMARY,
            insertbackground=TEXT_PRIMARY,
            bd=0, padx=12, pady=10,
            wrap="word", relief="flat"
        )
        self.input_box.grid(row=0, column=0, sticky="ew")
        self.input_box.bind("<Return>", self.on_enter)
        self.input_box.bind("<Shift-Return>", lambda e: None)

        placeholder = "Ask anything about your CV..."
        self.input_box.insert("1.0", placeholder)
        self.input_box.config(fg="#555555")
        self.input_box.bind("<FocusIn>",  lambda e: self.clear_placeholder(e, placeholder))
        self.input_box.bind("<FocusOut>", lambda e: self.add_placeholder(e, placeholder))

        self.send_btn = tk.Button(
            box, text="↑",
            bg=BG_SEND, fg="white",
            font=("Segoe UI", 13, "bold"),
            bd=0, cursor="hand2",
            padx=12, pady=6,
            activebackground="#338a58",
            activeforeground="white",
            command=self.send_message
        )
        self.send_btn.grid(row=0, column=1, padx=(0, 6), pady=6)

        self.model_indicator = tk.Label(
            input_frame,
            textvariable=self.selected_model,
            bg=BG_DARK, fg="#333",
            font=("Segoe UI", 9)
        )
        self.model_indicator.grid(row=1, column=0, pady=(4, 0))

    # ─── PLACEHOLDER ──────────────────────────────────
    def clear_placeholder(self, e, placeholder):
        if self.input_box.get("1.0", "end-1c") == placeholder:
            self.input_box.delete("1.0", "end")
            self.input_box.config(fg=TEXT_PRIMARY)

    def add_placeholder(self, e, placeholder):
        if not self.input_box.get("1.0", "end-1c").strip():
            self.input_box.insert("1.0", placeholder)
            self.input_box.config(fg="#555555")

    # ─── FILE UPLOAD ──────────────────────────────────
    def upload_file(self):
        filepath = filedialog.askopenfilename(
            title="Select your info file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not filepath:
            return
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                self.uploaded_file_text = f.read()
                self.uploaded_text = self.uploaded_file_text
            self.uploaded_filename = os.path.basename(filepath)
            self.using_file.set(f"📌 Using: {self.uploaded_filename}")
            if not self.active_chat:
                self.new_chat()
            else:
                # Reset system prompt for new file
                self.reset_system_prompt()
            self.render_system_msg(f"📄 Loaded: {self.uploaded_filename}\n\nAsk me anything about this CV!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file:\n{str(e)}")

    # ─── SWITCH FILE ──────────────────────────────────
    def switch_file(self):
        folder = os.path.dirname(os.path.abspath(__file__))
        project_file = os.path.join(folder, self.auto_loaded_file) if self.auto_loaded_file else None

        # If no uploaded file yet
        if not self.uploaded_file_text:
            messagebox.showwarning("No Uploaded File", "Please upload a file first using the Upload button!")
            return

        # Toggle between project file and uploaded file
        if self.uploaded_text == self.uploaded_file_text:
            # Switch to project info file
            if project_file and os.path.exists(project_file):
                with open(project_file, "r", encoding="utf-8") as f:
                    self.uploaded_text = f.read()
                self.using_file.set(f"📌 Using: {self.auto_loaded_file}")
                self.reset_system_prompt()
                self.render_system_msg(f"🔄 Switched to: {self.auto_loaded_file}")
            else:
                messagebox.showwarning("No Project File", "No project info.txt found in folder!")
        else:
            # Switch to uploaded file
            self.uploaded_text = self.uploaded_file_text
            self.using_file.set(f"📌 Using: {self.uploaded_filename}")
            self.reset_system_prompt()
            self.render_system_msg(f"🔄 Switched to: {self.uploaded_filename}")

    def reset_system_prompt(self):
        """Remove system prompt from current chat so it refreshes with new file"""
        if self.active_chat and self.active_chat in self.chats:
            self.chats[self.active_chat] = [
                m for m in self.chats[self.active_chat]
                if m.get("role") != "system"
            ]

    # ─── EXPORT CV ────────────────────────────────────
    def export_cv(self):
        if not self.last_cv_text:
            messagebox.showwarning("No CV", "Please generate a CV first by typing 'Create my CV'!")
            return
        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile="My_CV.pdf",
            title="Save CV as PDF"
        )
        if not save_path:
            return
        try:
            export_cv_pdf(self.last_cv_text, save_path)
            messagebox.showinfo("Success!", f"CV saved to:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    # ─── CHAT MANAGEMENT ──────────────────────────────
    def new_chat(self):
        chat_id = str(uuid.uuid4())
        self.chats[chat_id] = []
        self.chat_titles[chat_id] = "New Chat"
        self.active_chat = chat_id
        save_history(self.chats, self.chat_titles)
        self.refresh_chat_list()
        self.clear_messages()
        self.header_label.config(text="Ask anything about your CV or type 'Create my CV'")

    def refresh_chat_list(self):
        for w in self.chat_list_inner.winfo_children():
            w.destroy()

        for cid, title in reversed(list(self.chat_titles.items())):
            is_active = cid == self.active_chat
            row = tk.Frame(
                self.chat_list_inner,
                bg=BG_ACTIVE if is_active else BG_SIDEBAR,
                cursor="hand2"
            )
            row.pack(fill="x", padx=8, pady=2)

            lbl = tk.Label(
                row, text=title,
                bg=BG_ACTIVE if is_active else BG_SIDEBAR,
                fg=TEXT_TITLE if is_active else TEXT_SECONDARY,
                font=FONT_SMALL, anchor="w",
                padx=10, pady=8, cursor="hand2"
            )
            lbl.pack(side="left", fill="x", expand=True)

            del_btn = tk.Button(
                row, text="✕",
                bg=BG_ACTIVE if is_active else BG_SIDEBAR,
                fg="#555", font=("Segoe UI", 9),
                bd=0, cursor="hand2", padx=6,
                activebackground=BG_BTN_HOVER,
                activeforeground="#e55",
                command=lambda c=cid: self.delete_chat(c)
            )
            del_btn.pack(side="right", pady=4)

            row.bind("<Button-1>", lambda e, c=cid: self.select_chat(c))
            lbl.bind("<Button-1>", lambda e, c=cid: self.select_chat(c))

    def select_chat(self, chat_id):
        self.active_chat = chat_id
        self.refresh_chat_list()
        self.clear_messages()
        self.header_label.config(text=self.chat_titles.get(chat_id, "Chat"))
        for msg in self.chats.get(chat_id, []):
            if msg["role"] != "system":
                self.render_message(msg["role"], msg["content"])

    def delete_chat(self, chat_id):
        self.chats.pop(chat_id, None)
        self.chat_titles.pop(chat_id, None)
        save_history(self.chats, self.chat_titles)
        if self.active_chat == chat_id:
            self.active_chat = None
            self.clear_messages()
            self.header_label.config(text="Ask anything about your CV or type 'Create my CV'")
        self.refresh_chat_list()

    # ─── MESSAGES ─────────────────────────────────────
    def clear_messages(self):
        for w in self.msg_inner.winfo_children():
            w.destroy()
        self.empty_label = tk.Label(
            self.msg_inner,
            text="✦ CV Assistant\n\n• Ask questions about your CV\n• Type 'Create my CV' to generate\n• Switch between files in sidebar\n• Export as PDF anytime",
            bg=BG_DARK, fg="#2a2a2a",
            font=("Segoe UI", 13, "bold"),
            justify="center"
        )
        self.empty_label.pack(expand=True, pady=120)

    def render_system_msg(self, content):
        if hasattr(self, "empty_label") and self.empty_label.winfo_exists():
            self.empty_label.destroy()
        outer = tk.Frame(self.msg_inner, bg=BG_DARK, pady=4)
        outer.pack(fill="x", padx=24)
        tk.Label(
            outer, text=content,
            bg="#1a2a1a", fg="#7fcfff",
            font=("Segoe UI", 10),
            padx=14, pady=8,
            justify="left", anchor="w",
            wraplength=600
        ).pack(fill="x")
        self.msg_canvas.update_idletasks()
        self.msg_canvas.yview_moveto(1.0)

    def render_message(self, role, content):
        if hasattr(self, "empty_label") and self.empty_label.winfo_exists():
            self.empty_label.destroy()

        is_user = role == "user"
        outer = tk.Frame(self.msg_inner, bg=BG_DARK, pady=6)
        outer.pack(fill="x", padx=24)
        inner = tk.Frame(outer, bg=BG_DARK)
        inner.pack(anchor="e" if is_user else "w")

        tk.Label(
            inner,
            text="A" if is_user else "AI",
            bg="#1a2e1a" if is_user else "#1a1a2e",
            fg="#7fff9f" if is_user else "#7c9fff",
            font=("Segoe UI", 9, "bold"),
            width=3, height=1
        ).pack(side="right" if is_user else "left")

        bubble = tk.Text(
            inner, font=FONT_MSG,
            bg=BG_MSG_USER if is_user else BG_MSG_AI,
            fg=TEXT_USER if is_user else TEXT_AI,
            bd=0, padx=12, pady=10,
            wrap="word", relief="flat",
            width=60, height=1,
            cursor="arrow", state="normal"
        )
        bubble.insert("1.0", content)
        bubble.config(state="disabled")
        lines = int(bubble.index("end-1c").split(".")[0])
        bubble.config(height=max(lines, 1))
        bubble.pack(side="right" if is_user else "left", padx=(0, 8) if is_user else (8, 0))

        self.msg_canvas.update_idletasks()
        self.msg_canvas.yview_moveto(1.0)
        return bubble

    def create_stream_bubble(self):
        if hasattr(self, "empty_label") and self.empty_label.winfo_exists():
            self.empty_label.destroy()
        outer = tk.Frame(self.msg_inner, bg=BG_DARK, pady=6)
        outer.pack(fill="x", padx=24)
        inner = tk.Frame(outer, bg=BG_DARK)
        inner.pack(anchor="w")
        tk.Label(
            inner, text="AI",
            bg="#1a1a2e", fg="#7c9fff",
            font=("Segoe UI", 9, "bold"),
            width=3, height=1
        ).pack(side="left")
        bubble = tk.Text(
            inner, font=FONT_MSG,
            bg=BG_MSG_AI, fg=TEXT_AI,
            bd=0, padx=12, pady=10,
            wrap="word", relief="flat",
            width=60, height=1,
            cursor="arrow", state="normal"
        )
        bubble.pack(side="left", padx=(8, 0))
        return bubble

    def update_stream_bubble(self, bubble, text):
        bubble.config(state="normal")
        bubble.delete("1.0", "end")
        bubble.insert("1.0", text)
        lines = int(bubble.index("end-1c").split(".")[0])
        bubble.config(height=max(lines, 1), state="disabled")
        self.msg_canvas.update_idletasks()
        self.msg_canvas.yview_moveto(1.0)

    def show_typing(self):
        self.typing_frame = tk.Frame(self.msg_inner, bg=BG_DARK, pady=6)
        self.typing_frame.pack(fill="x", padx=24, anchor="w")
        inner = tk.Frame(self.typing_frame, bg=BG_DARK)
        inner.pack(anchor="w")
        tk.Label(inner, text="AI", bg="#1a1a2e", fg="#7c9fff",
                 font=("Segoe UI", 9, "bold"), width=3).pack(side="left")
        tk.Label(inner, text="  ● ● ●", bg=BG_MSG_AI, fg="#444",
                 font=("Segoe UI", 12), padx=12, pady=10).pack(side="left", padx=(8, 0))
        self.msg_canvas.yview_moveto(1.0)

    def hide_typing(self):
        if hasattr(self, "typing_frame") and self.typing_frame.winfo_exists():
            self.typing_frame.destroy()

    # ─── SEND MESSAGE ─────────────────────────────────
    def on_enter(self, e):
        if not e.state & 0x1:
            self.send_message()
            return "break"

    def send_message(self):
        if self.loading:
            return

        placeholder = "Ask anything about your CV..."
        text = self.input_box.get("1.0", "end-1c").strip()
        if not text or text == placeholder:
            return

        if not self.active_chat:
            self.new_chat()

        self.input_box.delete("1.0", "end")

        if not self.chats[self.active_chat]:
            title = text[:30] + ("..." if len(text) > 30 else "")
            self.chat_titles[self.active_chat] = title
            self.header_label.config(text=title)
            self.refresh_chat_list()

        # Inject system prompt once per chat
        if self.uploaded_text:
            if not any(m.get("role") == "system" for m in self.chats[self.active_chat]):
                self.chats[self.active_chat].insert(0, {
                    "role": "system",
                    "content": (
                        "You are a personal career assistant. "
                        "The user's personal information is stored below.\n\n"
                        "RULES:\n"
                        "1. If the user says 'create my cv' or 'generate cv' or 'make cv' — "
                        "generate a full professional CV with sections: "
                        "Name & Contact, Professional Summary, Work Experience, "
                        "Education, Technical Skills, Projects.\n"
                        "2. For ALL other questions — answer SHORT and DIRECTLY. "
                        "Never show the full CV. Never quote the CV text. "
                        "Just answer the specific question naturally.\n"
                        "Example: 'What is my name?' → 'Your name is Anika.'\n"
                        "Example: 'What are my skills?' → 'Your skills include Python, FastAPI, React, and PostgreSQL.'\n\n"
                        f"--- USER'S PERSONAL INFORMATION ---\n{self.uploaded_text}\n--- END ---"
                    )
                })

        self.chats[self.active_chat].append({"role": "user", "content": text})
        save_history(self.chats, self.chat_titles)

        self.render_message("user", text)
        self.show_typing()
        self.loading = True
        self.send_btn.config(state="disabled")

        threading.Thread(target=self.get_reply_stream, daemon=True).start()

    # ─── STREAMING REPLY ──────────────────────────────
    def get_reply_stream(self):
        try:
            self.stream_buffer = ""
            self.root.after(0, self.hide_typing)
            stream_bubble = [None]

            def init_bubble():
                stream_bubble[0] = self.create_stream_bubble()

            self.root.after(10, init_bubble)
            time.sleep(0.05)

            stream = ollama.chat(
                model=self.selected_model.get(),
                messages=self.chats[self.active_chat],
                stream=True,
                options={
                    "num_predict": 800,
                    "temperature": 0.7,
                }
            )

            for chunk in stream:
                token = chunk['message']['content']
                self.stream_buffer += token
                if stream_bubble[0]:
                    buf = self.stream_buffer
                    bubble = stream_bubble[0]
                    self.root.after(0, lambda b=bubble, t=buf: self.update_stream_bubble(b, t))

            reply = self.stream_buffer
            self.chats[self.active_chat].append({"role": "assistant", "content": reply})
            self.last_cv_text = reply
            save_history(self.chats, self.chat_titles)

        except Exception as e:
            reply = (
                f"Error: {str(e)}\n\n"
                f"Make sure Ollama is running!\n"
                f"Run: ollama pull {self.selected_model.get()}"
            )
            self.root.after(0, self.hide_typing)
            self.root.after(0, lambda: self.render_message("assistant", reply))

        self.root.after(0, self.on_stream_done)

    def on_stream_done(self):
        self.loading = False
        self.send_btn.config(state="normal")


# ─── RUN ──────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()