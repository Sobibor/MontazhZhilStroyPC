import tkinter as tk
from tkinter import ttk, messagebox
import product_crud as pc 
import client_crud as cc 
import order_crud as oc 
import logging
from datetime import datetime

logging.basicConfig(filename='app_errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    encoding='utf-8')

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ООО «МонтажЖилСтрой» - Система управления")
        self.root.geometry("1200x800") 
        self.root.configure(bg="#F0F0F0") 
        self.logger = logging.getLogger("MainAppGUI")

        self.BG_COLOR = "#F0F0F0"
        self.FRAME_BG_COLOR = "#FFFFFF" 
        self.TEXT_COLOR = "#333333"
        self.ACCENT_COLOR = "#0078D7"
        self.ACCENT_TEXT_COLOR = "#FFFFFF"
        self.WARNING_COLOR = "#D32F2F" 
        self.BORDER_COLOR = "#BDBDBD"
        self.TREEVIEW_HEADER_BG = "#E0E0E0"
        self.ROW_ALT_COLOR = "#F5F5F5" 

        self.DEFAULT_FONT = ("Segoe UI", 10)
        self.LABEL_FONT = ("Segoe UI", 10)
        self.ENTRY_FONT = ("Segoe UI", 10)
        self.BUTTON_FONT = ("Segoe UI", 10, "bold")
        self.TREEVIEW_FONT = ("Segoe UI", 9)
        self.TREEVIEW_HEADING_FONT = ("Segoe UI", 10, "bold")
        self.FRAME_LABEL_FONT = ("Segoe UI", 11, "bold")
        
        style = ttk.Style()
        style.theme_use("clam") 

        style.configure(".", font=self.DEFAULT_FONT, background=self.BG_COLOR, foreground=self.TEXT_COLOR)
        style.configure("TFrame", background=self.BG_COLOR)
        style.configure("Content.TFrame", background=self.FRAME_BG_COLOR) 
        style.configure("TLabel", font=self.LABEL_FONT, background=self.FRAME_BG_COLOR, foreground=self.TEXT_COLOR) 
        style.configure("BG.TLabel", font=self.LABEL_FONT, background=self.BG_COLOR, foreground=self.TEXT_COLOR) 
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), background=self.BG_COLOR, foreground=self.ACCENT_COLOR)
        style.configure("Total.TLabel", font=("Segoe UI", 12, "bold"), background=self.FRAME_BG_COLOR, foreground=self.TEXT_COLOR)
        style.configure("TLabelFrame", background=self.FRAME_BG_COLOR, bordercolor=self.BORDER_COLOR, relief="solid", borderwidth=1, padding=(15,10))
        style.configure("TLabelFrame.Label", font=self.FRAME_LABEL_FONT, foreground=self.TEXT_COLOR, background=self.FRAME_BG_COLOR, padding=(5,2))
        style.configure("TEntry", font=self.ENTRY_FONT, fieldbackground=self.FRAME_BG_COLOR, bordercolor=self.BORDER_COLOR, lightcolor=self.BORDER_COLOR, darkcolor=self.BORDER_COLOR, foreground=self.TEXT_COLOR)
        style.map("TEntry", bordercolor=[("focus", self.ACCENT_COLOR)])
        style.configure("TCombobox", font=self.ENTRY_FONT, fieldbackground=self.FRAME_BG_COLOR, background=self.FRAME_BG_COLOR, bordercolor=self.BORDER_COLOR, arrowcolor=self.TEXT_COLOR, foreground=self.TEXT_COLOR)
        style.map("TCombobox", 
                  fieldbackground=[("readonly", self.FRAME_BG_COLOR)],
                  bordercolor=[("focus", self.ACCENT_COLOR)],
                  selectbackground=[("readonly", self.ACCENT_COLOR)],
                  selectforeground=[("readonly", self.ACCENT_TEXT_COLOR)])
        style.configure("TButton", font=self.BUTTON_FONT, padding=(10, 5), relief="flat", borderwidth=0)
        style.map("TButton",
                  background=[("active", "#E0E0E0"), ("!disabled", "#F5F5F5")],
                  foreground=[("!disabled", self.TEXT_COLOR)])
        style.configure("Accent.TButton", font=self.BUTTON_FONT, background=self.ACCENT_COLOR, foreground=self.ACCENT_TEXT_COLOR)
        style.map("Accent.TButton", background=[("active", "#005A9E")])
        style.configure("Warning.TButton", font=self.BUTTON_FONT, background=self.WARNING_COLOR, foreground=self.ACCENT_TEXT_COLOR)
        style.map("Warning.TButton", background=[("active", "#A31F1F")])
        style.configure("Treeview.Heading", font=self.TREEVIEW_HEADING_FONT, background=self.TREEVIEW_HEADER_BG, foreground=self.TEXT_COLOR, relief="flat", padding=(5,5))
        style.map("Treeview.Heading", background=[("active", "#CACACA")])
        style.configure("Treeview", font=self.TREEVIEW_FONT, rowheight=28, fieldbackground=self.FRAME_BG_COLOR, background=self.FRAME_BG_COLOR, foreground=self.TEXT_COLOR)
        style.map("Treeview", background=[("selected", self.ACCENT_COLOR)], foreground=[("selected", self.ACCENT_TEXT_COLOR)])
        style.configure("TNotebook", background=self.BG_COLOR, borderwidth=0)
        style.configure("TNotebook.Tab", font=self.BUTTON_FONT, padding=(10, 5), background=self.BG_COLOR, foreground=self.TEXT_COLOR, borderwidth=1)
        style.map("TNotebook.Tab",
                  background=[("selected", self.FRAME_BG_COLOR), ("active", "#E0E0E0")],
                  foreground=[("selected", self.ACCENT_COLOR)],
                  expand=[("selected", [1, 1, 1, 0])])

        self.notebook = ttk.Notebook(root) 
        
        self.products_tab = ttk.Frame(self.notebook, padding=(10,10))
        self.notebook.add(self.products_tab, text='Товары')
        self.create_products_ui(self.products_tab)

        self.clients_tab = ttk.Frame(self.notebook, padding=(10,10))
        self.notebook.add(self.clients_tab, text='Клиенты')
        self.create_clients_ui(self.clients_tab)

        self.orders_tab = ttk.Frame(self.notebook, padding=(10,10))
        self.notebook.add(self.orders_tab, text='Заказы')
        self.create_orders_ui(self.orders_tab)
        
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)

    def _handle_crud_result(self, result, operation_description, entity_name=""):
        title_prefix = "Операция"
        if "товар" in operation_description: title_prefix = "Товар"
        elif "клиент" in operation_description: title_prefix = "Клиент"
        elif "заказ" in operation_description: title_prefix = "Заказ"

        if isinstance(result, int) or result is True:
            success_message = ""
            if isinstance(result, int): 
                 success_message = f"{entity_name.capitalize()} успешно добавлен(а) (ID: {result})."
            elif "обновлен" in operation_description or "изменен" in operation_description :
                 success_message = f"Данные для '{entity_name}' успешно обновлены."
            elif "удален" in operation_description:
                 success_message = f"{entity_name.capitalize()} успешно удален(а)."
            messagebox.showinfo(f"Успех ({title_prefix})", success_message)
            return True
        
        error_title = f"Ошибка {operation_description}"
        user_message = ""
        log_message = f"Error during {operation_description} for '{entity_name}': {result}"

        if result == "ConnectionError": user_message = "Не удалось подключиться к базе данных."
        elif result == "IntegrityErrorArticle": user_message = f"Товар с таким артикулом '{entity_name}' уже существует."
        elif result == "EmailExistsError": user_message = f"Клиент с Email '{entity_name}' уже существует."
        elif result == "NotFound": user_message = f"{title_prefix} '{entity_name}' не найден(а)."
        elif result == "NoDataToUpdate": user_message = "Нет данных для обновления."
        elif result == "HasOrdersError": user_message = f"Нельзя удалить клиента '{entity_name}', есть связанные заказы."
        elif result == "HasOrderItemsError": user_message = f"Нельзя удалить товар '{entity_name}', он используется в заказах."
        elif result == "StockCannotBeNegative": user_message = "Остаток товара не может быть отрицательным."
        elif result == "InvalidStatusError": user_message = f"Выбран неверный статус для заказа."
        elif result == "OrderCreationError": user_message = "Не удалось создать запись о заказе в базе данных."
        elif isinstance(result, str) and result.startswith("InsufficientStockError"):
            product_name_involved = result.split(":",1)[1] if ":" in result else "некоторых товаров"
            user_message = f"Недостаточно товара '{product_name_involved}' на складе для оформления заказа."
        elif isinstance(result, str) and result.startswith("StockReturnError"):
            user_message = f"Ошибка при возврате товаров на склад: {result.split(':',1)[1]}"
        elif isinstance(result, str) and (result.startswith("SQLiteError") or result.startswith("IntegrityError")):
            parts = result.split(":", 1)
            error_type = parts[0]
            technical_details = parts[1] if len(parts) > 1 else "Нет деталей"
            user_message = f"Произошла внутренняя ошибка базы данных ({error_type}). Обратитесь к администратору."
            log_message = f"{error_type} during {operation_description} for '{entity_name}': {technical_details}"
            self.logger.error(log_message)
        else:
            user_message = f"Произошла неизвестная ошибка: {result}"
            self.logger.error(log_message)
        messagebox.showerror(error_title, user_message)
        return False
    
    def _apply_treeview_row_tags(self, tree):
        for i, item_id in enumerate(tree.get_children()):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            tree.item(item_id, tags=(tag,))

    def create_products_ui(self, parent_tab):
        form_f = ttk.LabelFrame(parent_tab, text="Информация о товаре")
        form_f.pack(padx=10, pady=10, fill="x")
        btn_f = ttk.Frame(parent_tab, padding=(0, 10))
        btn_f.pack(padx=10, pady=(0,10), fill="x")
        tree_f = ttk.LabelFrame(parent_tab, text="Список товаров")
        tree_f.pack(padx=10, pady=(0,10), fill="both", expand=True)
        lbls = ["Название:", "Артикул:", "Категория:", "Описание:", "Цена:", "Кол-во на складе:"]
        self.p_entries = {}
        for i, lt in enumerate(lbls):
            ttk.Label(form_f, text=lt).grid(row=i, column=0, padx=5, pady=8, sticky="w")
            if lt == "Описание:":
                desc_frame = ttk.Frame(form_f, style="Content.TFrame", borderwidth=1, relief="solid")
                desc_frame.grid(row=i, column=1, padx=5, pady=8, sticky="ew")
                self.p_entries[lt.replace(":", "")] = tk.Text(desc_frame, height=4, width=40, relief=tk.FLAT, font=self.ENTRY_FONT, wrap=tk.WORD,
                                                                borderwidth=0, highlightthickness=0, background=self.FRAME_BG_COLOR, fg=self.TEXT_COLOR) 
                self.p_entries[lt.replace(":", "")].pack(expand=True, fill="both", padx=1, pady=1)
            else:
                self.p_entries[lt.replace(":", "")] = ttk.Entry(form_f, width=50)
                self.p_entries[lt.replace(":", "")].grid(row=i, column=1, padx=5, pady=8, sticky="ew")
        form_f.columnconfigure(1, weight=1)
        btn_configs = [
            ("Добавить товар", self.add_p_gui, "Accent.TButton"),
            ("Обновить товар", self.upd_p_gui, "TButton"),
            ("Удалить товар", self.del_p_gui, "Warning.TButton"),
            ("Очистить поля", self.clr_p_flds_gui, "TButton"),
            ("Обновить список", self.load_p_gui, "TButton")
        ]
        for text, cmd, style_name in btn_configs:
            ttk.Button(btn_f, text=text, command=cmd, style=style_name).pack(side="left", padx=(0,10))
        self.p_tree = ttk.Treeview(tree_f, columns=("ID", "Name", "Article", "Category", "Price", "Stock"), show="headings")
        p_hds = [("ID", 60, "center"), ("Name", 300, "w"), ("Article", 150, "center"), ("Category", 180, "w"), ("Price", 120, "e"), ("Stock", 120, "center")]
        for c, w, a in p_hds: 
            self.p_tree.heading(c, text=c)
            self.p_tree.column(c, width=w, anchor=a, minwidth=w, stretch=tk.YES if c=="Name" else tk.NO)
        p_scr_y = ttk.Scrollbar(tree_f, orient="vertical", command=self.p_tree.yview)
        p_scr_x = ttk.Scrollbar(tree_f, orient="horizontal", command=self.p_tree.xview)
        self.p_tree.configure(yscrollcommand=p_scr_y.set, xscrollcommand=p_scr_x.set)
        p_scr_y.pack(side="right", fill="y")
        p_scr_x.pack(side="bottom", fill="x")
        self.p_tree.pack(fill="both", expand=True, padx=(0,5), pady=(0,5)) 
        self.p_tree.bind("<<TreeviewSelect>>", self.on_p_sel_gui)
        self.sel_p_id = None
        self.p_tree.tag_configure("oddrow", background=self.FRAME_BG_COLOR)
        self.p_tree.tag_configure("evenrow", background=self.ROW_ALT_COLOR)
        self.load_p_gui()

    def load_p_gui(self):
        for i in self.p_tree.get_children(): self.p_tree.delete(i)
        products = pc.get_all_products()
        if isinstance(products, list):
            for idx, p in enumerate(products): 
                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                self.p_tree.insert("", "end", values=(p["id"], p["name"], p["article_number"], p.get("category",""), f"{p['price']:.2f}", p["stock_quantity"]), tags=(tag,))
        self.clr_p_flds_gui()

    def get_p_form_data(self):
        d = {};
        try:
            d["name"]=self.p_entries["Название"].get().strip()
            d["article_number"]=self.p_entries["Артикул"].get().strip()
            d["category"]=self.p_entries["Категория"].get().strip()
            d["description"]=self.p_entries["Описание"].get("1.0",tk.END).strip()
            pr_s, st_s = self.p_entries["Цена"].get().strip(), self.p_entries["Кол-во на складе"].get().strip()
            if not d["name"] or not d["article_number"]: messagebox.showerror("Ошибка валидации (Товар)", "Поля 'Название' и 'Артикул' обязательны."); return None
            d["price"]=float(pr_s) if pr_s else 0.0; d["stock_quantity"]=int(st_s) if st_s else 0
            if d["price"]<0 : messagebox.showerror("Ошибка валидации (Товар)", "Цена не может быть отрицательной."); return None
            if d["stock_quantity"]<0 : messagebox.showerror("Ошибка валидации (Товар)", "Кол-во на складе не может быть отрицательным."); return None
            return d
        except ValueError: messagebox.showerror("Ошибка валидации (Товар)", "'Цена' и 'Кол-во на складе' должны быть числами."); return None

    def add_p_gui(self):
        d = self.get_p_form_data()
        if d:
            res = pc.add_product(d["name"],d["article_number"],d["category"],d["description"],d["price"],d["stock_quantity"])
            entity_id_for_error = d["article_number"] if res == "IntegrityErrorArticle" else d["name"]
            if self._handle_crud_result(res, "добавления товара", entity_id_for_error): self.load_p_gui()
    
    def on_p_sel_gui(self, ev):
        sel_i = self.p_tree.focus()
        if sel_i:
            self.sel_p_id = self.p_tree.item(sel_i, "values")[0]; p_det = pc.get_product_by_id(self.sel_p_id)
            if p_det:
                for k,v_key in {"Название":"name", "Артикул":"article_number", "Категория":"category", "Цена":"price", "Кол-во на складе":"stock_quantity"}.items():
                    entry_widget = self.p_entries[k]
                    entry_widget.delete(0,tk.END)
                    entry_widget.insert(0, str(p_det.get(v_key,"") if p_det.get(v_key) is not None else ""))
                self.p_entries["Описание"].delete("1.0",tk.END); self.p_entries["Описание"].insert("1.0", p_det.get("description","") or "")
        else: self.clr_p_flds_gui()

    def upd_p_gui(self):
        if not self.sel_p_id: messagebox.showwarning("Внимание (Товар)", "Выберите товар для обновления."); return
        d = self.get_p_form_data()
        if d:
            res = pc.update_product(self.sel_p_id,d["name"],d["article_number"],d["category"],d["description"],d["price"],d["stock_quantity"])
            entity_id_for_error = d["article_number"] if res == "IntegrityErrorArticle" else d["name"]
            if self._handle_crud_result(res, f"обновления товара '{d['name']}'", entity_id_for_error): self.load_p_gui()

    def del_p_gui(self):
        if not self.sel_p_id: messagebox.showwarning("Внимание (Товар)", "Выберите товар для удаления."); return
        p_info = pc.get_product_by_id(self.sel_p_id); p_name = p_info['name'] if p_info else f"ID {self.sel_p_id}"
        if messagebox.askyesno("Подтверждение (Товар)", f"Удалить товар '{p_name}'?"):
            res = pc.delete_product(self.sel_p_id)
            if self._handle_crud_result(res, f"удаления товара", p_name): self.load_p_gui()
    
    def clr_p_flds_gui(self):
        for k_entry, widget in self.p_entries.items():
            if isinstance(widget, tk.Text): widget.delete("1.0", tk.END)
            elif isinstance(widget, ttk.Entry): widget.delete(0, tk.END)
        self.sel_p_id = None
        if self.p_tree.selection(): self.p_tree.selection_remove(self.p_tree.selection()[0])

    def create_clients_ui(self, parent_tab):
        form_f = ttk.LabelFrame(parent_tab, text="Информация о клиенте")
        form_f.pack(padx=10, pady=10, fill="x")
        btn_f = ttk.Frame(parent_tab, padding=(0, 10))
        btn_f.pack(padx=10, pady=(0,10), fill="x")
        tree_f = ttk.LabelFrame(parent_tab, text="Список клиентов")
        tree_f.pack(padx=10, pady=(0,10), fill="both", expand=True)
        cl_lbls = ["ФИО:", "Телефон:", "Email:", "Адрес:"]
        self.cl_entries = {}
        for i, lt in enumerate(cl_lbls):
            ttk.Label(form_f, text=lt).grid(row=i, column=0, padx=5, pady=8, sticky="w")
            if lt == "Адрес:":
                addr_frame = ttk.Frame(form_f, style="Content.TFrame", borderwidth=1, relief="solid")
                addr_frame.grid(row=i, column=1, padx=5, pady=8, sticky="ew")
                self.cl_entries[lt.replace(":", "")] = tk.Text(addr_frame, height=3, width=40, relief=tk.FLAT, font=self.ENTRY_FONT, wrap=tk.WORD,
                                                                borderwidth=0, highlightthickness=0, background=self.FRAME_BG_COLOR, fg=self.TEXT_COLOR)
                self.cl_entries[lt.replace(":", "")].pack(expand=True, fill="both", padx=1, pady=1)
            else:
                self.cl_entries[lt.replace(":", "")] = ttk.Entry(form_f, width=50)
                self.cl_entries[lt.replace(":", "")].grid(row=i, column=1, padx=5, pady=8, sticky="ew")
        form_f.columnconfigure(1, weight=1)
        cl_btn_configs = [
            ("Добавить клиента", self.add_cl_gui, "Accent.TButton"),
            ("Обновить клиента", self.upd_cl_gui, "TButton"),
            ("Удалить клиента", self.del_cl_gui, "Warning.TButton"),
            ("Очистить поля", self.clr_cl_flds_gui, "TButton"),
            ("Обновить список", self.load_cl_gui, "TButton")
        ]
        for text, cmd, style_name in cl_btn_configs:
            ttk.Button(btn_f, text=text, command=cmd, style=style_name).pack(side="left", padx=(0,10))
        self.cl_tree = ttk.Treeview(tree_f, columns=("ID", "FullName", "Phone", "Email", "Address"), show="headings")
        cl_hds = [("ID",60,"center"), ("FullName",250,"w"), ("Phone",150,"w"), ("Email",200,"w"), ("Address",300,"w")]
        for c,w,a in cl_hds: 
            self.cl_tree.heading(c, text=c.replace("FullName","ФИО").replace("Phone","Телефон"))
            self.cl_tree.column(c,width=w,anchor=a,minwidth=w, stretch=tk.YES if c in ["FullName", "Address"] else tk.NO)
        cl_scr_y = ttk.Scrollbar(tree_f, orient="vertical", command=self.cl_tree.yview)
        cl_scr_x = ttk.Scrollbar(tree_f, orient="horizontal", command=self.cl_tree.xview)
        self.cl_tree.configure(yscrollcommand=cl_scr_y.set, xscrollcommand=cl_scr_x.set)
        cl_scr_y.pack(side="right",fill="y"); cl_scr_x.pack(side="bottom", fill="x")
        self.cl_tree.pack(fill="both",expand=True, padx=(0,5), pady=(0,5))
        self.cl_tree.bind("<<TreeviewSelect>>", self.on_cl_sel_gui)
        self.sel_cl_id = None
        self.cl_tree.tag_configure("oddrow", background=self.FRAME_BG_COLOR)
        self.cl_tree.tag_configure("evenrow", background=self.ROW_ALT_COLOR)
        self.load_cl_gui()

    def load_cl_gui(self):
        for i in self.cl_tree.get_children(): self.cl_tree.delete(i)
        clients = cc.get_all_clients()
        if isinstance(clients, list):
            for idx, c in enumerate(clients): 
                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                self.cl_tree.insert("","end",values=(c["id"],c["full_name"],c.get("phone_number",""),c["email"],c.get("address","")), tags=(tag,))
        self.clr_cl_flds_gui()

    def get_cl_form_data(self):
        d = {}
        try:
            d["full_name"]=self.cl_entries["ФИО"].get().strip()
            d["phone_number"]=self.cl_entries["Телефон"].get().strip()
            d["email"]=self.cl_entries["Email"].get().strip()
            d["address"]=self.cl_entries["Адрес"].get("1.0",tk.END).strip()
            if not d["full_name"]: messagebox.showerror("Ошибка валидации (Клиент)", "Поле 'ФИО' обязательно."); return None
            return d
        except Exception as e: messagebox.showerror("Ошибка валидации (Клиент)", f"Ошибка сбора данных: {e}"); return None

    def add_cl_gui(self):
        d = self.get_cl_form_data()
        if d:
            res = cc.add_client(d["full_name"],d["phone_number"],d["email"],d["address"])
            entity_id_for_error = d["email"] if res == "EmailExistsError" else d["full_name"]
            if self._handle_crud_result(res, "добавления клиента", entity_id_for_error): self.load_cl_gui()
    
    def on_cl_sel_gui(self, ev):
        sel_i = self.cl_tree.focus()
        if sel_i:
            self.sel_cl_id = self.cl_tree.item(sel_i, "values")[0]; c_det = cc.get_client_by_id(self.sel_cl_id)
            if c_det:
                for k,v_key in {"ФИО":"full_name", "Телефон":"phone_number", "Email":"email"}.items():
                    entry_widget = self.cl_entries[k]
                    entry_widget.delete(0,tk.END)
                    entry_widget.insert(0, c_det.get(v_key,"") or "") 
                self.cl_entries["Адрес"].delete("1.0",tk.END); self.cl_entries["Адрес"].insert("1.0", c_det.get("address","") or "")
        else: self.clr_cl_flds_gui()

    def upd_cl_gui(self):
        if not self.sel_cl_id: messagebox.showwarning("Внимание (Клиент)", "Выберите клиента для обновления."); return
        d = self.get_cl_form_data()
        if d:
            res = cc.update_client(self.sel_cl_id,d["full_name"],d["phone_number"],d["email"],d["address"])
            entity_id_for_error = d["email"] if res == "EmailExistsError" else d["full_name"]
            if self._handle_crud_result(res, f"обновления клиента '{d['full_name']}'", entity_id_for_error): self.load_cl_gui()

    def del_cl_gui(self):
        if not self.sel_cl_id: messagebox.showwarning("Внимание (Клиент)", "Выберите клиента для удаления."); return
        cl_info = cc.get_client_by_id(self.sel_cl_id); cl_name = cl_info['full_name'] if cl_info else f"ID {self.sel_cl_id}"
        if messagebox.askyesno("Подтверждение (Клиент)", f"Удалить клиента '{cl_name}'?"):
            res = cc.delete_client(self.sel_cl_id)
            if self._handle_crud_result(res, f"удаления клиента", cl_name): self.load_cl_gui()

    def clr_cl_flds_gui(self):
        for k_entry, widget in self.cl_entries.items():
            if isinstance(widget, tk.Text): widget.delete("1.0", tk.END)
            elif isinstance(widget, ttk.Entry): widget.delete(0, tk.END)
        self.sel_cl_id = None
        if self.cl_tree.selection(): self.cl_tree.selection_remove(self.cl_tree.selection()[0])

    def create_orders_ui(self, parent_tab):
        new_order_frame = ttk.LabelFrame(parent_tab, text="Создание нового заказа")
        new_order_frame.pack(padx=10, pady=10, fill="x")
        new_order_frame.columnconfigure(1, weight=1) 

        ttk.Label(new_order_frame, text="Клиент:").grid(row=0, column=0, padx=5, pady=8, sticky="w")
        self.order_client_combobox = ttk.Combobox(new_order_frame, state="readonly", width=45)
        self.order_client_combobox.grid(row=0, column=1, columnspan=3, padx=5, pady=8, sticky="ew")
        self.populate_client_combobox()

        add_item_subframe = ttk.Frame(new_order_frame, style="Content.TFrame") 
        add_item_subframe.grid(row=1, column=0, columnspan=4, pady=10, sticky="ew")
        add_item_subframe.columnconfigure(1, weight=1) 

        ttk.Label(add_item_subframe, text="Товар:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.order_product_combobox = ttk.Combobox(add_item_subframe, state="readonly", width=35)
        self.order_product_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.order_product_combobox.bind("<<ComboboxSelected>>", self.on_order_product_selected)

        ttk.Label(add_item_subframe, text="Кол-во:").grid(row=0, column=2, padx=(10,0), pady=5, sticky="w")
        self.order_quantity_var = tk.StringVar(value="1")
        self.order_quantity_entry = ttk.Entry(add_item_subframe, textvariable=self.order_quantity_var, width=6)
        self.order_quantity_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        
        # Метка цены товара создается ЗДЕСЬ, ДО вызова populate_product_combobox
        self.order_product_price_label = ttk.Label(add_item_subframe, text="Цена: 0.00 (Ост: 0)")
        self.order_product_price_label.grid(row=0, column=4, padx=(10,0), pady=5, sticky="w")

        # Теперь вызываем populate_product_combobox, когда метка уже существует
        self.populate_product_combobox()

        ttk.Button(add_item_subframe, text="Добавить в заказ", command=self.add_item_to_current_order_gui, style="TButton").grid(row=0, column=5, padx=(10,5), pady=5, sticky="e")
        add_item_subframe.columnconfigure(5, weight=0) 

        current_items_frame = ttk.LabelFrame(new_order_frame, text="Позиции текущего заказа")
        current_items_frame.grid(row=2, column=0, columnspan=4, padx=5, pady=10, sticky="nsew")
        new_order_frame.grid_rowconfigure(2, weight=1)

        self.current_order_items_tree = ttk.Treeview(current_items_frame, columns=("ID", "Product", "Qty", "Price", "Subtotal"), show="headings", height=4)
        coi_hds = [("ID",0,"w"),("Product",300,"w"),("Qty",80,"center"),("Price",100,"e"),("Subtotal",120,"e")]
        for c,w,a in coi_hds: 
            self.current_order_items_tree.heading(c, text=c.replace("Product","Товар").replace("Qty","Кол-во").replace("Price","Цена").replace("Subtotal","Сумма"))
            self.current_order_items_tree.column(c, width=w, anchor=a, stretch= (c=="Product") )
        column_names_coi = [c[0] for c in coi_hds]
        if "ID" in column_names_coi: self.current_order_items_tree.column("ID", stretch=tk.NO, width=0)

        coi_scr_y = ttk.Scrollbar(current_items_frame, orient="vertical", command=self.current_order_items_tree.yview)
        self.current_order_items_tree.configure(yscrollcommand=coi_scr_y.set)
        coi_scr_y.pack(side="right", fill="y"); self.current_order_items_tree.pack(fill="both", expand=True, pady=(0,5))
        self.current_order_items_tree.bind("<Double-1>", self.remove_item_from_current_order_gui)
        self.current_order_items_data = []
        
        self.current_order_items_tree.tag_configure("oddrow", background=self.FRAME_BG_COLOR)
        self.current_order_items_tree.tag_configure("evenrow", background=self.ROW_ALT_COLOR)

        total_and_buttons_frame = ttk.Frame(new_order_frame, style="Content.TFrame")
        total_and_buttons_frame.grid(row=3, column=0, columnspan=4, padx=5, pady=(5,0), sticky="ew")
        total_and_buttons_frame.columnconfigure(1, weight=1) 

        self.current_order_total_label = ttk.Label(total_and_buttons_frame, text="Итого по заказу: 0.00 руб.", style="Total.TLabel")
        self.current_order_total_label.grid(row=0, column=0, padx=0, pady=5, sticky="w")
        
        ttk.Button(total_and_buttons_frame, text="Очистить", command=self.clear_current_order_gui, style="TButton").grid(row=0, column=2, padx=(0,10), pady=5, sticky="e")
        ttk.Button(total_and_buttons_frame, text="Оформить заказ", command=self.create_order_gui, style="Accent.TButton").grid(row=0, column=3, padx=0, pady=5, sticky="e")

        orders_list_frame = ttk.LabelFrame(parent_tab, text="Список оформленных заказов")
        orders_list_frame.pack(padx=10, pady=10, fill="both", expand=True)

        orders_list_actions_frame = ttk.Frame(orders_list_frame, style="Content.TFrame", padding=(0,5))
        orders_list_actions_frame.pack(fill="x", pady=(0,10))
        
        ttk.Button(orders_list_actions_frame, text="Обновить список", command=self.load_orders_gui, style="TButton").pack(side="left", padx=(0,10))
        self.order_status_label = ttk.Label(orders_list_actions_frame, text="Новый статус:")
        self.order_status_label.pack(side="left", padx=(10,0))
        self.order_status_combobox = ttk.Combobox(orders_list_actions_frame, values=oc.ORDER_STATUSES, state="readonly", width=18)
        self.order_status_combobox.pack(side="left", padx=5)
        self.update_order_status_button = ttk.Button(orders_list_actions_frame, text="Изменить статус", command=self.update_order_status_gui, style="TButton", state="disabled")
        self.update_order_status_button.pack(side="left", padx=(0,10))
        self.delete_order_button = ttk.Button(orders_list_actions_frame, text="Удалить заказ", command=self.delete_order_gui, style="Warning.TButton", state="disabled")
        self.delete_order_button.pack(side="left", padx=(0,10))
        self.view_order_details_button = ttk.Button(orders_list_actions_frame, text="Детали заказа", command=self.view_order_details_gui, style="TButton", state="disabled")
        self.view_order_details_button.pack(side="right", padx=0)

        self.orders_tree = ttk.Treeview(orders_list_frame, columns=("ID", "Client", "Date", "Status", "Total"), show="headings")
        o_hds = [("ID",70,"center"),("Client",280,"w"),("Date",170,"w"),("Status",150,"w"),("Total",120,"e")]
        for c,w,a in o_hds: 
            self.orders_tree.heading(c, text=c.replace("Client","Клиент").replace("Date","Дата").replace("Status","Статус").replace("Total","Сумма"))
            self.orders_tree.column(c,width=w,anchor=a,minwidth=w, stretch=tk.YES if c=="Client" else tk.NO)
        
        o_scr_y = ttk.Scrollbar(orders_list_frame, orient="vertical", command=self.orders_tree.yview)
        o_scr_x = ttk.Scrollbar(orders_list_frame, orient="horizontal", command=self.orders_tree.xview)
        self.orders_tree.configure(yscrollcommand=o_scr_y.set, xscrollcommand=o_scr_x.set)
        o_scr_y.pack(side="right",fill="y"); o_scr_x.pack(side="bottom", fill="x")
        self.orders_tree.pack(fill="both",expand=True, padx=(0,5), pady=(0,5))
        
        self.orders_tree.bind("<<TreeviewSelect>>", self.on_order_select_gui)
        self.sel_order_id = None
        
        self.orders_tree.tag_configure("oddrow", background=self.FRAME_BG_COLOR)
        self.orders_tree.tag_configure("evenrow", background=self.ROW_ALT_COLOR)
        self.load_orders_gui()
        
    def populate_client_combobox(self):
        clients = cc.get_all_clients()
        client_display_list = [f"{c['full_name']} (ID: {c['id']})" for c in clients]
        self.order_client_combobox['values'] = client_display_list
        self.clients_data_for_combobox = clients

    def populate_product_combobox(self):
        products = pc.get_all_products()
        product_display_list = [f"{p['name']} (Арт: {p['article_number']}, Ост: {p['stock_quantity']})" for p in products if p['stock_quantity'] > 0]
        self.order_product_combobox['values'] = product_display_list
        self.products_data_for_combobox = [p for p in products if p['stock_quantity'] > 0]
        self.on_order_product_selected() 

    def on_order_product_selected(self, event=None):
        selected_index = self.order_product_combobox.current()
        if selected_index >= 0 and self.products_data_for_combobox and selected_index < len(self.products_data_for_combobox):
            product = self.products_data_for_combobox[selected_index]
            self.order_product_price_label.config(text=f"Цена: {product['price']:.2f} (Ост: {product['stock_quantity']})")
        else:
            self.order_product_price_label.config(text="Цена: 0.00 (Ост: 0)")

    def add_item_to_current_order_gui(self):
        client_idx = self.order_client_combobox.current()
        product_idx = self.order_product_combobox.current()
        
        if client_idx < 0: messagebox.showwarning("Внимание", "Пожалуйста, выберите клиента."); return
        if product_idx < 0: messagebox.showwarning("Внимание", "Пожалуйста, выберите товар."); return
            
        try:
            quantity = int(self.order_quantity_var.get())
            if quantity <= 0: messagebox.showwarning("Внимание", "Количество должно быть больше нуля."); return
        except ValueError: messagebox.showwarning("Внимание", "Количество должно быть числом."); return

        if not self.products_data_for_combobox or product_idx >= len(self.products_data_for_combobox):
             messagebox.showerror("Ошибка", "Выбранный товар не найден в списке доступных.")
             return
        selected_product = self.products_data_for_combobox[product_idx]
        
        if quantity > selected_product['stock_quantity']:
            messagebox.showwarning("Недостаточно товара", f"На складе только {selected_product['stock_quantity']} шт. товара '{selected_product['name']}'.")
            return

        existing_item_tree_id = None
        existing_item_data_index = -1

        for i, item_data in enumerate(self.current_order_items_data):
            if item_data['product_id'] == selected_product['id']:
                existing_item_data_index = i
                for child_id in self.current_order_items_tree.get_children():
                    tree_item_values = self.current_order_items_tree.item(child_id, "values")
                    if tree_item_values and str(tree_item_values[0]) == str(selected_product['id']):
                        existing_item_tree_id = child_id
                        break
                break
        
        if existing_item_data_index != -1: 
            item_data = self.current_order_items_data[existing_item_data_index]
            new_quantity = item_data['quantity'] + quantity
            if new_quantity > selected_product['stock_quantity']:
                 messagebox.showwarning("Недостаточно товара", f"С учетом уже добавленного, на складе только {selected_product['stock_quantity']} шт. товара '{selected_product['name']}'.")
                 return
            item_data['quantity'] = new_quantity
            if existing_item_tree_id:
                subtotal = new_quantity * item_data['price_per_unit']
                self.current_order_items_tree.item(existing_item_tree_id, values=(selected_product['id'], selected_product['name'], new_quantity, f"{item_data['price_per_unit']:.2f}", f"{subtotal:.2f}"))
        else: 
            item_data = {
                'product_id': selected_product['id'],
                'product_name': selected_product['name'],
                'quantity': quantity,
                'price_per_unit': selected_product['price']
            }
            self.current_order_items_data.append(item_data)
            subtotal = quantity * selected_product['price']
            tag_idx = len(self.current_order_items_tree.get_children())
            tag = "evenrow" if tag_idx % 2 == 0 else "oddrow"
            self.current_order_items_tree.insert("", "end", values=(selected_product['id'], selected_product['name'], quantity, f"{selected_product['price']:.2f}", f"{subtotal:.2f}"), tags=(tag,))

        self.update_current_order_total()
        self.order_product_combobox.set('')
        self.order_product_price_label.config(text="Цена: 0.00 (Ост: 0)")
        self.order_quantity_var.set("1")

    def remove_item_from_current_order_gui(self, event=None):
        selected_tree_item = self.current_order_items_tree.focus()
        if not selected_tree_item: return
        
        item_values = self.current_order_items_tree.item(selected_tree_item, "values")
        if not item_values: 
            messagebox.showerror("Ошибка", "Не удалось получить данные выбранного товара.")
            return
        product_id_to_remove = item_values[0] 

        item_index_to_remove = -1
        for i, item_data in enumerate(self.current_order_items_data):
            if str(item_data['product_id']) == str(product_id_to_remove):
                item_index_to_remove = i
                break
        
        if item_index_to_remove != -1:
            del self.current_order_items_data[item_index_to_remove]
            self.current_order_items_tree.delete(selected_tree_item)
            self.update_current_order_total()
            self._apply_treeview_row_tags(self.current_order_items_tree)
        else:
            messagebox.showerror("Ошибка", "Не удалось найти товар для удаления.")

    def update_current_order_total(self):
        total = sum(item['quantity'] * item['price_per_unit'] for item in self.current_order_items_data)
        self.current_order_total_label.config(text=f"Итого по заказу: {total:.2f} руб.")

    def clear_current_order_gui(self):
        self.order_client_combobox.set('')
        self.order_product_combobox.set('')
        self.order_product_price_label.config(text="Цена: 0.00 (Ост: 0)")
        self.order_quantity_var.set("1")
        for i in self.current_order_items_tree.get_children():
            self.current_order_items_tree.delete(i)
        self.current_order_items_data = []
        self.update_current_order_total()

    def create_order_gui(self):
        client_idx = self.order_client_combobox.current()
        if client_idx < 0: messagebox.showwarning("Внимание", "Пожалуйста, выберите клиента."); return
        if not self.current_order_items_data: messagebox.showwarning("Внимание", "Добавьте хотя бы один товар в заказ."); return

        if not self.clients_data_for_combobox or client_idx >= len(self.clients_data_for_combobox):
            messagebox.showerror("Ошибка", "Выбранный клиент не найден.")
            return
        selected_client_data = self.clients_data_for_combobox[client_idx]
        client_id = selected_client_data['id']
        
        result = oc.add_order(client_id, self.current_order_items_data)
        
        if self._handle_crud_result(result, "создания заказа", f"для клиента {selected_client_data['full_name']}"):
            self.load_orders_gui()
            self.clear_current_order_gui()
            self.populate_product_combobox() 
            self.load_p_gui()

    def load_orders_gui(self):
        for i in self.orders_tree.get_children(): self.orders_tree.delete(i)
        orders = oc.get_all_orders_with_details()
        if isinstance(orders, list):
            for idx, o in enumerate(orders):
                order_date_formatted = datetime.strptime(o["order_date"], '%Y-%m-%d %H:%M:%S').strftime('%d.%m.%Y %H:%M')
                tag = "evenrow" if idx % 2 == 0 else "oddrow"
                self.orders_tree.insert("", "end", values=(o["id"], o["client_name"], order_date_formatted, o["status"], f"{o['total_amount']:.2f}"), tags=(tag,))
        self.sel_order_id = None
        self.update_order_action_buttons_state()

    def on_order_select_gui(self, event=None):
        selected_item = self.orders_tree.focus()
        if selected_item:
            item_values = self.orders_tree.item(selected_item, "values")
            if item_values:
                self.sel_order_id = item_values[0]
                current_status = item_values[3]
                self.order_status_combobox.set(current_status)
            else: 
                self.sel_order_id = None
        else:
            self.sel_order_id = None
        self.update_order_action_buttons_state()

    def update_order_action_buttons_state(self):
        state = "normal" if self.sel_order_id else "disabled"
        self.update_order_status_button.config(state=state)
        self.delete_order_button.config(state=state)
        self.view_order_details_button.config(state=state)
        if not self.sel_order_id:
             self.order_status_combobox.set('')

    def update_order_status_gui(self):
        if not self.sel_order_id: messagebox.showwarning("Внимание", "Выберите заказ для изменения статуса."); return
        new_status = self.order_status_combobox.get()
        if not new_status: messagebox.showwarning("Внимание", "Выберите новый статус заказа."); return

        selected_item_focus = self.orders_tree.focus()
        if not selected_item_focus: return 
        selected_item_values = self.orders_tree.item(selected_item_focus, "values")
        current_status_in_tree = selected_item_values[3] if selected_item_values else None

        if new_status == current_status_in_tree:
            messagebox.showinfo("Информация", "Выбранный статус совпадает с текущим статусом заказа.")
            return

        result = oc.update_order_status(self.sel_order_id, new_status)
        if self._handle_crud_result(result, f"изменения статуса заказа ID {self.sel_order_id}", f"заказ ID {self.sel_order_id}"):
            self.load_orders_gui()
            self.populate_product_combobox()
            self.load_p_gui()

    def delete_order_gui(self):
        if not self.sel_order_id: messagebox.showwarning("Внимание", "Выберите заказ для удаления."); return
        order_details_for_name = oc.get_order_details_by_id(self.sel_order_id)
        order_name_for_msg = f"ID {self.sel_order_id}"
        if order_details_for_name:
            order_name_for_msg = f"ID {self.sel_order_id} (клиент: {order_details_for_name['client_full_name']})"

        if messagebox.askyesno("Подтверждение", f"Удалить заказ {order_name_for_msg}? \nТовары будут возвращены на склад, если заказ не был 'Выполнен'."):
            result = oc.delete_order(self.sel_order_id)
            if self._handle_crud_result(result, "удаления заказа", order_name_for_msg):
                self.load_orders_gui()
                self.populate_product_combobox()
                self.load_p_gui()

    def view_order_details_gui(self):
        if not self.sel_order_id: messagebox.showwarning("Внимание", "Выберите заказ для просмотра деталей."); return
        details = oc.get_order_details_by_id(self.sel_order_id)
        if not details: self._handle_crud_result("NotFound", "просмотра деталей заказа", f"ID {self.sel_order_id}"); return

        details_window = tk.Toplevel(self.root)
        details_window.title(f"Детали заказа ID {self.sel_order_id}")
        details_window.geometry("750x550")
        details_window.configure(bg=self.BG_COLOR) 
        details_window.transient(self.root); details_window.grab_set()

        ttk.Label(details_window, text=f"Детали заказа ID {self.sel_order_id}", style="Header.TLabel").pack(pady=(10,5))

        info_frame = ttk.LabelFrame(details_window, text="Общая информация")
        info_frame.pack(padx=10, pady=5, fill="x")
        
        info_labels_data = [
            ("ID Заказа:", details['id']),
            ("Клиент:", f"{details['client_full_name']} (ID: {details['client_id']})"),
            ("Email клиента:", details.get('client_email', '-')),
            ("Телефон клиента:", details.get('client_phone_number', '-')),
            ("Дата заказа:", datetime.strptime(details["order_date"], '%Y-%m-%d %H:%M:%S').strftime('%d.%m.%Y %H:%M')),
            ("Статус:", details['status']),
            ("Общая сумма:", f"{details['total_amount']:.2f} руб.")
        ]
        for i, (label_text, value_text) in enumerate(info_labels_data):
            ttk.Label(info_frame, text=label_text, font=self.LABEL_FONT + ("bold",)).grid(row=i, column=0, sticky="w", pady=3, padx=5)
            ttk.Label(info_frame, text=value_text).grid(row=i, column=1, sticky="w", pady=3, padx=5)
        info_frame.columnconfigure(1, weight=1)

        items_frame = ttk.LabelFrame(details_window, text="Позиции заказа")
        items_frame.pack(padx=10, pady=10, fill="both", expand=True)

        items_tree = ttk.Treeview(items_frame, columns=("Article", "Product", "Qty", "Price", "Subtotal"), show="headings")
        it_hds = [("Article",120,"w"),("Product",280,"w"),("Qty",80,"center"),("Price",100,"e"),("Subtotal",100,"e")]
        for c,w,a in it_hds: 
            items_tree.heading(c, text=c.replace("Article","Артикул").replace("Product","Товар").replace("Qty","Кол-во").replace("Price","Цена").replace("Subtotal","Сумма"))
            items_tree.column(c,width=w,anchor=a,minwidth=w, stretch=tk.YES if c=="Product" else tk.NO)
        
        items_tree.tag_configure("oddrow_detail", background=self.FRAME_BG_COLOR) 
        items_tree.tag_configure("evenrow_detail", background=self.ROW_ALT_COLOR)

        for idx, item in enumerate(details['items']):
            tag = "evenrow_detail" if idx % 2 == 0 else "oddrow_detail"
            items_tree.insert("", "end", values=(item['product_article'], item['product_name'], item['quantity'], f"{item['price_per_unit']:.2f}", f"{(item['quantity'] * item['price_per_unit']):.2f}"), tags=(tag,))
        
        it_scr_y = ttk.Scrollbar(items_frame, orient="vertical", command=items_tree.yview)
        it_scr_x = ttk.Scrollbar(items_frame, orient="horizontal", command=items_tree.xview)
        items_tree.configure(yscrollcommand=it_scr_y.set, xscrollcommand=it_scr_x.set)
        it_scr_y.pack(side="right",fill="y"); it_scr_x.pack(side="bottom", fill="x")
        items_tree.pack(fill="both",expand=True, padx=(0,5), pady=(0,5))
        
        ttk.Button(details_window, text="Закрыть", command=details_window.destroy, style="Accent.TButton").pack(pady=15)
