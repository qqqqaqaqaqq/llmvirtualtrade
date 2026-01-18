import os
import sys
import tkinter as tk

if getattr(sys, "frozen", False):
    # PyInstaller 같은 EXE로 패키징 시
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(__file__)

ENV_PATH = os.path.join(BASE_DIR, ".env")

# ===== .env 입력 =====
def read_env():
    values = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and "=" in line and not line.startswith("#"):
                    key, val = line.split("=", 1)
                    values[key.strip()] = val.strip()
    return values

def create_env_with_input():
    root = tk.Tk()
    root.title(".env 입력")
    root.geometry("400x300")
    root.resizable(False, False)

    entries = {}
    labels = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME", "DB_PORT"]

    # 기존 .env 값 읽기
    existing_values = read_env()

    # ===== 경고 메시지 라벨 =====
    message_label = tk.Label(root, text="", fg="red", font=("Arial", 10))
    message_label.place(x=20, y=270, width=360, height=20)

    def shake_window():
        x, y = root.winfo_x(), root.winfo_y()
        for _ in range(3):
            for dx in (-5, 5, -3, 3, 0):
                root.geometry(f"+{x + dx}+{y}")
                root.update()
                root.after(30)

    def submit():
        values = {}
        empty = False
        for label in labels:
            val = entries[label].get().strip()
            if not val:
                empty = True
                break
            values[label] = val

        if empty:
            shake_window()
            message_label.config(text="⚠ 모든 칸을 입력해주세요!")
            return
        else:
            message_label.config(text="")

        env_content = f"""# DB
DB_HOST={values['DB_HOST']}
DB_USER={values['DB_USER']}
DB_PASSWORD={values['DB_PASSWORD']}
DB_NAME={values['DB_NAME']}
DB_PORT={values['DB_PORT']}

"""
        with open(ENV_PATH, "w", encoding="utf-8") as f:
            f.write(env_content)

        print(f"[INFO] .env 파일 생성 완료: {ENV_PATH}")
        root.destroy()

    # ===== 폼 만들기 =====
    for i, label in enumerate(labels):
        tk.Label(root, text=label + ":", anchor="w").place(x=20, y=20 + i * 35, width=120, height=25)
        # 기존 값이 있으면 초기값으로 넣기
        entry_value = existing_values.get(label, "")
        entry = tk.Entry(root, width=30, show="*" if label in ["DB_PASSWORD"] else "")
        entry.insert(0, entry_value)
        entry.place(x=150, y=20 + i * 35, width=220, height=25)
        entries[label] = entry

    submit_btn = tk.Button(root, text="생성", command=submit)
    submit_btn.place(x=160, y=240, width=80, height=30)

    root.mainloop()
    
# ===== .env 체크 =====
if not os.path.exists(ENV_PATH):
    create_env_with_input()

from tkinter import ttk, messagebox, font

from PIL import Image, ImageDraw
import pystray

from app import main
from app.repositories.DBController import (
    user_insert, init_trade_insert, delete_trade_insert
)
from app.db.session import SessionLocal
from app.models.user import UserInformation
from app.core.globals import RUNNING_THREADS

from app.component.userform import UserForm


# ================= THEME =================
DARK = {
    "bg": "#121212",
    "panel": "#1e1e1e",
    "fg": "#ffffff",
    "accent": "#3d5afe",
    "danger": "#f44336",
    "success": "#4caf50",
    "border": "#333333",
    "log": "#1a1a1a"
}

LIGHT = {
    "bg": "#f5f5f5",
    "panel": "#ffffff",
    "fg": "#000000",
    "accent": "#3d5afe",
    "danger": "#e53935",
    "success": "#43a047",
    "border": "#cccccc",
    "log": "#ffffff"
}


# ================= stdout redirect =================
class RedirectText:
    def __init__(self, widget):
        self.widget = widget

    def write(self, s):
        if s:
            self.widget.after(0, lambda: self._write(s))

    def _write(self, s):
        self.widget.insert(tk.END, s)
        self.widget.see(tk.END)

    def flush(self):
        pass


# ================= UI =================
class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Trading Bot Manager")
        self.root.geometry("750x800")
        self.root.minsize(750, 800)

        self.theme = "dark"
        self.C = DARK
        self.tray_icon = None

        self.ui_font = font.Font(family="Arial", size=11)
        self.root.configure(bg=self.C["bg"])

        self.setup_styles()
        self.create_layout()

        sys.stdout = RedirectText(self.log_text)
        sys.stderr = RedirectText(self.log_text)

        self.refresh_ui()

    # ---------- STYLE ----------
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=self.C["panel"],
            foreground=self.C["fg"],
            fieldbackground=self.C["panel"],
            rowheight=28
        )

        style.configure(
            "Treeview.Heading",
            background=self.C["bg"],
            foreground=self.C["fg"],
            font=("Arial", self.ui_font["size"], "bold")
        )

        style.map(
            "Treeview",
            background=[("selected", self.C["accent"])],
            foreground=[("selected", "#ffffff")]
        )

    # ---------- LAYOUT ----------
    def create_layout(self):
        main = tk.Frame(self.root, bg=self.C["bg"])
        main.pack(fill=tk.BOTH, expand=True)

        # ================= 상단바 =================
        topbar = tk.Frame(main, bg=self.C["panel"], height=40)
        topbar.pack(fill=tk.X)

        # 왼쪽 제작자 라벨
        self.creator_lbl = tk.Label(
            topbar, text="제작자: qqqa",
            bg=self.C["panel"], fg=self.C["fg"],
            font=("Arial", 10, "bold")
        )
        self.creator_lbl.pack(side=tk.LEFT, padx=10)

        # 오른쪽 컨테이너
        right_frame = tk.Frame(topbar, bg=self.C["panel"])
        right_frame.pack(side=tk.RIGHT, padx=10)

        # 폰트 사이즈 콤보박스
        self.font_cb = ttk.Combobox(
            right_frame,
            values=[8, 9, 10, 11, 12, 14, 16],
            width=4,
            state="readonly"
        )
        self.font_cb.set(11)
        self.font_cb.pack(side=tk.LEFT, padx=6)
        self.font_cb.bind("<<ComboboxSelected>>", self.change_font_size)

        # 다크모드 토글 버튼 (설정 아이콘)
        self.theme_btn = tk.Button(
            right_frame,
            text="⚙",  # Tkinter에서 제공할 수 있는 간단 설정 아이콘
            font=("Arial", 12, "bold"),
            command=self.toggle_theme,
            bg=self.C["panel"],
            fg=self.C["fg"],
            relief="flat",
            padx=6,
            pady=2
        )
        self.theme_btn.pack(side=tk.LEFT, padx=6)

        # ================= BUTTON BAR (CENTER) =================
        btns = tk.Frame(main, bg=self.C["bg"])
        btns.pack(pady=15)

        def mkbtn(txt, cmd, clr):
            return tk.Button(
                btns,
                text=txt,
                command=cmd,
                bg=clr,
                fg=self.C["fg"],
                relief="flat",
                padx=14,
                pady=6,
                font=("Arial", 10, "bold")
            )

        mkbtn("User Insert", self.run_user_insert, self.C["panel"]).pack(side=tk.LEFT, padx=5)
        mkbtn("Init Trade", self.run_inittrade_insert, self.C["panel"]).pack(side=tk.LEFT, padx=5)
        mkbtn("Delete Trade", self.run_delettrade_insert, self.C["danger"]).pack(side=tk.LEFT, padx=5)
        mkbtn("Toggle Play", self.toggle_play, self.C["success"]).pack(side=tk.LEFT, padx=5)
        mkbtn("Clear Log", self.clear_log, self.C["panel"]).pack(side=tk.LEFT, padx=5)
        mkbtn("Tray Mode", self.hide_to_tray, self.C["accent"]).pack(side=tk.LEFT, padx=5)

        # ================= USER LIST (CENTER) =================
        tree_wrap = tk.Frame(main, bg=self.C["bg"])
        tree_wrap.pack(fill=tk.X, padx=20)

        self.tree = ttk.Treeview(
            tree_wrap,
            columns=("userid", "play", "thread"),
            show="headings",
            height=6
        )

        for col, w in [("userid", 200), ("play", 100), ("thread", 140)]:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=w, anchor="center")

        self.tree.pack(fill=tk.X)

        # ================= LOG PANEL (FULL WIDTH) =================
        self.log_text = tk.Text(
            main,
            bg=self.C["log"],
            fg="#00ff00",
            font=("Consolas", self.ui_font["size"]),
            borderwidth=0,
            padx=10,
            pady=10
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    # ---------- CORE ----------
    def refresh_ui(self):
        self.tree.delete(*self.tree.get_children())
        db = SessionLocal()
        users = db.query(UserInformation).all()
        running = set(RUNNING_THREADS.keys())

        for u in users:
            self.tree.insert(
                "",
                tk.END,
                iid=u.userid,
                values=(
                    u.userid,
                    u.play,
                    "Running" if u.userid in running else "Stopped"
                )
            )
        db.close()

    def toggle_play(self):
        sel = self.tree.selection()
        if not sel:
            return
        uid = sel[0]
        db = SessionLocal()
        u = db.query(UserInformation).filter(UserInformation.userid == uid).first()
        if u:
            u.play = not u.play
            db.commit()
        db.close()
        self.refresh_ui()

    def run_inittrade_insert(self):
        if messagebox.askyesno("확인", "초기 트레이드값을 입력하시겠습니까?"):
            init_trade_insert()

    def run_delettrade_insert(self):
        if messagebox.askyesno("확인", "트레이드 값을 초기화 하시겠습니까?"):
            delete_trade_insert()

    def clear_log(self):
        self.log_text.delete("1.0", tk.END)

    # ---------- FONT ----------
    def change_font_size(self, e=None):
        size = int(self.font_cb.get())
        self.ui_font.configure(size=size)
        self.setup_styles()
        self.log_text.configure(font=("Consolas", size))

    # ---------- THEME ----------
    def apply_theme(self, widget):
        try:
            if isinstance(widget, tk.Frame):
                widget.configure(bg=self.C["bg"])
            elif isinstance(widget, tk.Text):
                widget.configure(bg=self.C["log"], fg="#00ff00")
            elif isinstance(widget, tk.Button):
                widget.configure(bg=self.C["panel"], fg=self.C["fg"])
            elif isinstance(widget, tk.Label):
                # 제작자 라벨도 적용
                widget.configure(bg=self.C["panel"], fg=self.C["fg"])
        except:
            pass
        for child in widget.winfo_children():
            self.apply_theme(child)

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.C = LIGHT if self.theme == "light" else DARK
        self.root.configure(bg=self.C["bg"])
        self.apply_theme(self.root)
        self.setup_styles()

    # ---------- TRAY ----------
    def hide_to_tray(self):
        self.root.withdraw()
        if not self.tray_icon:
            self.start_tray()

    def start_tray(self):
        def icon_img():
            img = Image.new("RGB", (64, 64), self.C["accent"])
            d = ImageDraw.Draw(img)
            d.rectangle((16, 16, 48, 48), fill="white")
            return img

        def show(icon, item):
            self.root.after(0, self.root.deiconify)

        def quit_app(icon, item):
            icon.stop()
            self.root.after(0, self.root.destroy)

        self.tray_icon = pystray.Icon(
            "TradingBot",
            icon_img(),
            menu=pystray.Menu(
                pystray.MenuItem("Show", show),
                pystray.MenuItem("Exit", quit_app)
            )
        )
        self.tray_icon.run_detached()


    def run_user_insert(self, userid="testuser"):
        db = SessionLocal()
        user = db.query(UserInformation).filter(UserInformation.userid == userid).first()
        db.close()

        user_data = None
        if user:
            user_data = {
                "userid" : userid,
                "ticker": user.ticker,
                "userprompt": user.userprompt,
                "llm_model": user.llm_model,
                "openai": user.openai,
                "grok": user.grok,
                "gemma": user.gemma,
                "trade_interval": user.trade_interval,
                "start_time": user.start_time,
                "end_time": user.end_time
            }

        UserForm(self.root, self.C, userid=userid, user_data=user_data, on_save=self.refresh_ui, ui_font=self.ui_font)


if __name__ == "__main__":
    main.startup()
    root = tk.Tk()
    AppUI(root)
    root.mainloop()
