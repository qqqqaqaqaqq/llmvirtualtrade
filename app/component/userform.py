# user_form.py
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timezone, timedelta

from app.repositories.DBController import user_insert

class UserForm:
    def __init__(self, parent, theme_colors, userid=None, user_data=None, on_save=None, ui_font=None):
        self.C = theme_colors
        self.userid = userid
        self.user_data = user_data
        self.on_save = on_save
        # 전달받은 폰트
        self.ui_font = ui_font or ("Arial", 10)

        self.win = tk.Toplevel(parent)
        self.win.title("User Configuration")
        self.win.geometry("600x900")
        self.win.configure(bg=self.C["bg"])
        self.win.grab_set()

        # 저장할 위젯 레퍼런스
        self.widgets_to_font = []

        self.build_form()

    def build_form(self):
        canvas = tk.Canvas(self.win, bg=self.C["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.win, orient="vertical", command=canvas.yview)
        form = tk.Frame(canvas, bg=self.C["bg"])
        form.columnconfigure(0, weight=1)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.create_window((0, 0), window=form, anchor="nw", width=560)
        form.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        row = 0

        def label(text):
            nonlocal row
            lbl = tk.Label(
                form, text=text, bg=self.C["bg"], fg=self.C["accent"],
                font=(self.ui_font.actual("family"), self.ui_font.actual("size"), "bold"),
                anchor="center"
            )
            lbl.grid(row=row, column=0, sticky="ew", pady=(15,3))
            self.widgets_to_font.append(lbl)
            row += 1

        # --------- TICKER ---------
        label("TICKER (Enter to add)")
        self.ticker_ent = tk.Entry(form, bg=self.C["panel"], fg=self.C["fg"],
                                   borderwidth=0,
                                   font=(self.ui_font.actual("family"), self.ui_font.actual("size")))
        self.ticker_ent.grid(row=row, column=0, sticky="we", ipady=6)
        self.widgets_to_font.append(self.ticker_ent)

        self.ticker_dict = {}
        self.ticker_box = tk.Listbox(form, bg=self.C["panel"], fg=self.C["fg"], height=5, borderwidth=0,
                                     font=(self.ui_font.actual("family"), self.ui_font.actual("size")))
        self.ticker_box.grid(row=row+1, column=0, sticky="we", pady=5)
        self.widgets_to_font.append(self.ticker_box)

        def add_t(e=None):
            v = self.ticker_ent.get().strip().upper()
            if v and v not in self.ticker_dict:
                self.ticker_dict[v] = True
                self.ticker_box.insert(tk.END, f"{v} : True")
                self.ticker_ent.delete(0, tk.END)

        self.ticker_ent.bind("<Return>", add_t)

        def del_t():
            sel = self.ticker_box.curselection()
            if sel:
                k = self.ticker_box.get(sel[0]).split(":")[0].strip()
                self.ticker_dict.pop(k, None)
                self.ticker_box.delete(sel[0])

        del_btn = tk.Button(form, text="DELETE SELECTED", command=del_t,
                            bg=self.C["danger"], fg="white", relief="flat",
                            font=(self.ui_font.actual("family"), self.ui_font.actual("size")))
        del_btn.grid(row=row+2, column=0, sticky="we", pady=5)
        self.widgets_to_font.append(del_btn)
        row += 3

        # --------- USER PROMPT ---------
        label("USER PROMPT")
        self.user_prompt = tk.Text(form, height=10, bg=self.C["panel"], fg=self.C["fg"], borderwidth=0,
                                   font=(self.ui_font.actual("family"), self.ui_font.actual("size")))
        self.user_prompt.grid(row=row, column=0, sticky="we", padx=10)
        self.widgets_to_font.append(self.user_prompt)
        row += 1

        # --------- LLM MODEL ---------
        label("LLM MODEL")
        self.llm_cb = ttk.Combobox(form, values=["GPT_5.0_mini", "GROK_3.0_mini",
                                                 "GEMINI_3.0_flash_preview", "GEMINI_2.5_pro"],
                                   state="readonly", font=(self.ui_font.actual("family"), self.ui_font.actual("size")))
        self.llm_cb.grid(row=row, column=0, sticky="we", padx=10)
        self.llm_cb.current(0)
        row += 1

        # --------- TRADE INTERVAL ---------
        label("TRADE INTERVAL")
        self.interval_cb = ttk.Combobox(form, values=[1800, 3600, 14400, 86400],
                                        state="readonly", font=(self.ui_font.actual("family"), self.ui_font.actual("size")))
        self.interval_cb.grid(row=row, column=0, sticky="we", padx=10)
        self.interval_cb.current(0)
        row += 1

        # --------- API KEYS ---------
        label("OPENAI API KEY")
        self.openai_ent = tk.Entry(form, bg=self.C["panel"], fg=self.C["fg"], borderwidth=0,
                                   font=(self.ui_font.actual("family"), self.ui_font.actual("size")))
        self.openai_ent.grid(row=row, column=0, sticky="we", ipady=6, padx=10)
        self.widgets_to_font.append(self.openai_ent)
        row += 1

        label("GROK API KEY")
        self.grok_ent = tk.Entry(form, bg=self.C["panel"], fg=self.C["fg"], borderwidth=0,
                                 font=(self.ui_font.actual("family"), self.ui_font.actual("size")))
        self.grok_ent.grid(row=row, column=0, sticky="we", ipady=6, padx=10)
        self.widgets_to_font.append(self.grok_ent)
        row += 1

        label("GEMMA API KEY")
        self.gemma_ent = tk.Entry(form, bg=self.C["panel"], fg=self.C["fg"], borderwidth=0,
                                  font=(self.ui_font.actual("family"), self.ui_font.actual("size")))
        self.gemma_ent.grid(row=row, column=0, sticky="we", ipady=6, padx=10)
        self.widgets_to_font.append(self.gemma_ent)
        row += 1

        # --------- START/END DATE ---------
        label("START DATE")
        self.start_date = DateEntry(form, date_pattern="yyyy-mm-dd",
                                    background=self.C["panel"], foreground=self.C["fg"],
                                    headersbackground=self.C["bg"], headersforeground=self.C["fg"],
                                    selectbackground=self.C["accent"], normalbackground=self.C["panel"],
                                    font=(self.ui_font.actual("family"), self.ui_font.actual("size")))
        self.start_date.grid(row=row, column=0, sticky="we", padx=10)
        row += 1

        label("END DATE")
        self.end_date = DateEntry(form, date_pattern="yyyy-mm-dd",
                                  background=self.C["panel"], foreground=self.C["fg"],
                                  headersbackground=self.C["bg"], headersforeground=self.C["fg"],
                                  selectbackground=self.C["accent"], normalbackground=self.C["panel"],
                                  font=(self.ui_font.actual("family"), self.ui_font.actual("size")))
        self.end_date.grid(row=row, column=0, sticky="we", padx=10)
        row += 1

        # --------- 기존 데이터 불러오기 ---------
        if self.user_data:
            for k, v in (self.user_data.get("ticker") or {}).items():
                self.ticker_dict[k] = v
                self.ticker_box.insert(tk.END, f"{k} : {v}")
            self.user_prompt.insert("1.0", self.user_data["userprompt"])
            self.llm_cb.set(self.user_data["llm_model"])
            self.interval_cb.set(str(self.user_data["trade_interval"]))
            self.openai_ent.insert(0, self.user_data["openai"])
            self.grok_ent.insert(0, self.user_data["grok"])
            self.gemma_ent.insert(0, self.user_data["gemma"])
            if self.user_data["start_time"]:
                self.start_date.set_date(self.user_data["start_time"])
            if self.user_data["end_time"]:
                self.end_date.set_date(self.user_data["end_time"])

        # --------- 저장 버튼 ---------
        save_btn = tk.Button(form, text="SAVE CONFIGURATION", command=self.submit,
                             bg=self.C["accent"], fg="white", relief="flat",
                             font=(self.ui_font.actual("family"), self.ui_font.actual("size"), "bold"), pady=12)
        save_btn.grid(row=row, column=0, sticky="we", pady=30, padx=10)
        self.widgets_to_font.append(save_btn)

    # --------- 폰트 업데이트 메서드 ---------
    def update_font(self, new_font):
        self.ui_font = new_font
        for w in self.widgets_to_font:
            if isinstance(w, (tk.Entry, tk.Text, tk.Label, tk.Button)):
                w.configure(font=(self.ui_font.actual("family"), self.ui_font.actual("size")))
            elif isinstance(w, ttk.Combobox):
                w.configure(font=(self.ui_font.actual("family"), self.ui_font.actual("size")))

    def submit(self):
        if not self.ticker_dict:
            messagebox.showwarning("경고", "티커를 입력하세요.")
            return

        start_dt = datetime.combine(self.start_date.get_date(), datetime.min.time(), tzinfo=timezone.utc) + timedelta(minutes=5)
        end_dt = datetime.combine(self.end_date.get_date(), datetime.min.time(), tzinfo=timezone.utc) + timedelta(minutes=5)

        user_insert(
            userid=self.userid,
            ticker=self.ticker_dict,
            userprompt=self.user_prompt.get("1.0", tk.END).strip(),
            llm_model=self.llm_cb.get(),
            openai=self.openai_ent.get().strip(),
            grok=self.grok_ent.get().strip(),
            gemma=self.gemma_ent.get().strip(),
            trade_interval=int(self.interval_cb.get()),
            trading_fee=0.0,
            start_time=start_dt,
            end_time=end_dt
        )

        if self.on_save:
            self.on_save()
        self.win.destroy()
