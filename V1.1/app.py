#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
群星领袖指令生成器 - 重构版后端逻辑
功能与 v6.3 完全一致，优化了代码结构、性能与可读性
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
import sqlite3
import time
import re
import shutil
from datetime import datetime
from PIL import Image, ImageTk
import importer
import trans
import prel
from ui import UI

# ==================== 路径与常量 ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MOMO_DIR = os.path.join(BASE_DIR, "momodata")
DATA_DIR = os.path.join(MOMO_DIR, "data")
ICON_DIR = os.path.join(DATA_DIR, "icons")
CONFIG_DIR = os.path.join(MOMO_DIR, "config")
PRESETS_DIR = os.path.join(MOMO_DIR, "presets")
DB_PATH = os.path.join(DATA_DIR, "leader_traits.db")
SETTINGS_PATH = os.path.join(CONFIG_DIR, "settings.json")

# 加载配置中的路径（若存在）
def load_paths_from_settings():
    global MOMO_DIR, DATA_DIR, ICON_DIR, CONFIG_DIR, PRESETS_DIR, DB_PATH, SETTINGS_PATH
    if os.path.exists(SETTINGS_PATH):
        try:
            with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            MOMO_DIR = settings.get('momo_dir', MOMO_DIR)
            DATA_DIR = settings.get('data_dir', DATA_DIR)
            ICON_DIR = settings.get('icon_dir', ICON_DIR)
            CONFIG_DIR = settings.get('config_dir', CONFIG_DIR)
            PRESETS_DIR = settings.get('presets_dir', PRESETS_DIR)
            DB_PATH = settings.get('db_path', DB_PATH)
            SETTINGS_PATH = os.path.join(CONFIG_DIR, "settings.json")
        except Exception:
            pass

load_paths_from_settings()

# 确保目录存在
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ICON_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(PRESETS_DIR, exist_ok=True)


# ==================== 数据库查询（独立函数） ====================
def get_traits_with_filters(ruler=None, commander=None, scientist=None,
                            council=None, governor=None, special=None,
                            profession=None, attribute=None,
                            search_text=None, search_by='name',
                            exclude_negative=False):
    """根据筛选条件从数据库获取特质"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = """
        SELECT id, number, name, code, attribute, exclusive_with, effect, effect_color, icon_path
        FROM traits WHERE 1=1
    """
    params = []

    # 添加筛选条件（与原来一致）
    if ruler is not None:
        query += " AND ruler = ?"
        params.append(1 if ruler else 0)
    if commander is not None:
        query += " AND commander = ?"
        params.append(1 if commander else 0)
    if scientist is not None:
        query += " AND scientist = ?"
        params.append(1 if scientist else 0)
    if council is not None:
        query += " AND council = ?"
        params.append(1 if council else 0)
    if governor is not None:
        query += " AND governor = ?"
        params.append(1 if governor else 0)
    if special is not None:
        query += " AND special = ?"
        params.append(1 if special else 0)

    if profession and profession != "无":
        query += " AND (profession_requirements = ? OR profession_requirements LIKE ? OR profession_requirements LIKE ? OR profession_requirements LIKE ?)"
        params.extend([profession, f"{profession},%", f"%,{profession}", f"%,{profession},%"])

    if attribute and attribute != "全部":
        query += " AND attribute = ?"
        params.append(attribute)

    if exclude_negative:
        query += " AND attribute != '负面'"

    if search_text and search_text.strip():
        if search_by == 'name':
            query += " AND name LIKE ?"
            params.append(f"%{search_text.strip()}%")
        elif search_by == 'number':
            try:
                num = int(search_text.strip())
                query += " AND number = ?"
                params.append(num)
            except ValueError:
                query += " AND 1=0"
        elif search_by == 'effect':
            query += " AND effect LIKE ?"
            params.append(f"%{search_text.strip()}%")

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results


def get_all_attributes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT attribute FROM traits WHERE attribute IS NOT NULL AND attribute != ''")
    attrs = [row[0] for row in cursor.fetchall()]
    conn.close()
    return attrs


def get_all_professions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT profession_requirements FROM traits WHERE profession_requirements IS NOT NULL AND profession_requirements != ''")
    rows = cursor.fetchall()
    profs = set()
    for row in rows:
        for p in row[0].split(','):
            p = p.strip()
            if p:
                profs.add(p)
    conn.close()
    return sorted(profs)


# ==================== Tooltip 类（悬浮提示） ====================
class ToolTip:
    """悬浮提示，显示效果文本（带颜色）"""
    def __init__(self, widget, app, text='', color=None):
        self.widget = widget
        self.app = app
        self.text = text
        self.color = color if color else '#000000'
        self.tip_window = None
        widget.bind('<Enter>', self.enter)
        widget.bind('<Leave>', self.leave)
        widget.bind('<Button-1>', self.on_click)

    def enter(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.wm_attributes("-topmost", True)
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("Microsoft YaHei", 9), fg=self.color)
        label.pack()
        tw.update_idletasks()
        tw_width = tw.winfo_width()
        tw_height = tw.winfo_height()
        screen_width = tw.winfo_screenwidth()
        screen_height = tw.winfo_screenheight()
        if x + tw_width > screen_width:
            x = screen_width - tw_width - 5
        if y + tw_height > screen_height:
            y = screen_height - tw_height - 5
        tw.geometry(f"+{x}+{y}")

    def leave(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

    def on_click(self, event):
        if hasattr(self.widget, 'trait_code'):
            self.app.remove_trait_by_code(self.widget.trait_code)


# ==================== 最小化窗口管理器（内部类） ====================
class MiniWindowManager:
    """管理悬浮最小化按钮"""
    def __init__(self, app):
        self.app = app
        self.mini_window = None
        self.button_press_time = 0
        self.button_dragging = False
        self.button_drag_timer = None
        self.pos_label = None
        self.mini_label = None
        self.drag_data = {"x": 0, "y": 0}
        self._create_mini_window()

    def _create_mini_window(self):
        """创建悬浮窗口"""
        self.mini_window = tk.Toplevel(self.app.root)
        self.mini_window.title("")
        self.mini_window.overrideredirect(True)
        self.mini_window.configure(bg='#2d2d3d')
        self.mini_window.wm_attributes("-topmost", True)

        frame = tk.Frame(self.mini_window, bg='#89dceb', relief=tk.FLAT, borderwidth=2)
        frame.pack(padx=1, pady=1)

        self.mini_label = tk.Label(frame, text="🎮 领袖生成器", bg='#89dceb', fg='#1e1e2e',
                                    font=('Microsoft YaHei UI', 9, 'bold'), padx=10, pady=5)
        self.mini_label.pack()

        self.pos_label = tk.Label(self.mini_window, text="", bg='#2d2d3d', fg='#89dceb',
                                   font=('Microsoft YaHei UI', 8))

        # 绑定事件
        self.mini_label.bind("<Enter>", lambda e: self.mini_label.config(bg='#74c7ec'))
        self.mini_label.bind("<Leave>", lambda e: self.mini_label.config(bg='#89dceb'))
        self.mini_label.bind("<ButtonPress-1>", self.on_press)
        self.mini_label.bind("<B1-Motion>", self.on_drag)
        self.mini_label.bind("<ButtonRelease-1>", self.on_release)
        self.mini_label.bind("<Button-3>", self.show_menu)

        self.mini_window.withdraw()
        self.position_mini_button()

    def position_mini_button(self):
        """将悬浮按钮置于屏幕右侧中央"""
        self.mini_window.update_idletasks()
        sw = self.mini_window.winfo_screenwidth()
        sh = self.mini_window.winfo_screenheight()
        w = self.mini_window.winfo_reqwidth()
        h = self.mini_window.winfo_reqheight()
        x = sw - w - 20
        y = (sh - h) // 2
        self.mini_window.geometry(f"+{x}+{y}")

    def on_press(self, event):
        self.button_press_time = time.time()
        self.drag_data["x"] = event.x_root
        self.drag_data["y"] = event.y_root
        self.button_drag_timer = self.mini_window.after(200, self.start_drag)
        self.mini_label.config(bg='#94e2d5')

    def start_drag(self):
        self.button_dragging = True
        self.pos_label.place(x=0, y=self.mini_window.winfo_height()+2)
        self.mini_label.config(bg='#94e2d5', relief=tk.SUNKEN)

    def on_drag(self, event):
        if self.button_dragging:
            dx = event.x_root - self.drag_data["x"]
            dy = event.y_root - self.drag_data["y"]
            x = self.mini_window.winfo_x() + dx
            y = self.mini_window.winfo_y() + dy
            sw = self.mini_window.winfo_screenwidth()
            sh = self.mini_window.winfo_screenheight()
            w = self.mini_window.winfo_reqwidth()
            h = self.mini_window.winfo_reqheight()
            x = max(0, min(x, sw - w))
            y = max(0, min(y, sh - h))
            self.mini_window.geometry(f"+{x}+{y}")
            self.pos_label.config(text=f"位置: {int(x/sw*100)}%, {int(y/sh*100)}%")
            self.drag_data["x"] = event.x_root
            self.drag_data["y"] = event.y_root

    def on_release(self, event):
        if self.button_drag_timer:
            self.mini_window.after_cancel(self.button_drag_timer)
            self.button_drag_timer = None

        if self.button_dragging:
            self.button_dragging = False
            self.pos_label.place_forget()
            self.mini_label.config(bg='#89dceb', relief=tk.FLAT)
            self.save_position()
        else:
            press_duration = time.time() - self.button_press_time
            if press_duration < 0.2:
                self.app.open_from_mini()

    def save_position(self):
        try:
            cfg_path = os.path.join(CONFIG_DIR, "window.json")
            cfg = {}
            if os.path.exists(cfg_path):
                with open(cfg_path, 'r') as f:
                    cfg = json.load(f)
            cfg["mini_pos"] = (self.mini_window.winfo_x(), self.mini_window.winfo_y())
            with open(cfg_path, 'w') as f:
                json.dump(cfg, f)
        except:
            pass

    def load_position(self):
        try:
            cfg_path = os.path.join(CONFIG_DIR, "window.json")
            if os.path.exists(cfg_path):
                with open(cfg_path, 'r') as f:
                    cfg = json.load(f)
                if "mini_pos" in cfg:
                    x, y = cfg["mini_pos"]
                    self.mini_window.geometry(f"+{x}+{y}")
                    return
        except:
            pass
        self.position_mini_button()

    def show_menu(self, event):
        menu = tk.Menu(self.mini_window, tearoff=0, bg='#313244', fg='#cdd6f4')
        menu.add_command(label="打开主窗口", command=self.app.open_from_mini)
        menu.add_command(label="随机领袖", command=self.app.random_leader)
        menu.add_command(label="重置位置", command=self.position_mini_button)
        menu.add_separator()
        menu.add_command(label="退出", command=self.app.on_closing)
        menu.tk_popup(event.x_root, event.y_root)


# ==================== 主应用程序类 ====================
class StellarisLeaderGenerator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("群星领袖指令生成器 v6.3")
        self.root.geometry("950x750")

        # 窗口状态
        self.window_state = "normal"
        self.always_on_top = True
        self.opacity = 0.85
        self.drag_data = {"x": 0, "y": 0, "dragging": False}
        self.normal_geometry = None

        # 数据缓存
        self.icon_cache = {}                # code -> PhotoImage
        self.trait_selected = {}             # iid -> bool
        self.trait_effect = {}                # iid -> (effect, color)
        self.trait_code_iid = {}              # code -> iid
        self.current_traits = []              # 当前显示的特质列表
        self.all_attributes = ["全部"] + get_all_attributes()
        self.all_professions = ["无"] + get_all_professions()

        # 预设相关
        self.preset_items = []                # [(名称, 代码)]
        self.load_buttons = []                 # [(显示名称, 代码, 源文件路径)]

        # 调度任务ID
        self._filter_job = None
        self._preview_job = None
        self.last_selected_iid = None

        # 导入Excel数据
        excel_path = os.path.join(BASE_DIR, "traits.xlsx")
        importer.run_import(excel_path)

        # 创建预设管理器
        self.preset_manager = prel.PresetManager(PRESETS_DIR)

        # 创建UI（必须在此之后，因为UI需要访问app的变量和方法）
        self.ui = UI(self.root, self)

        # 初始化变量引用（UI创建时已经创建了变量，但需要赋值给app属性方便访问）
        self._assign_ui_variables()

        # 创建悬浮窗口管理器
        self.mini_manager = MiniWindowManager(self)

        # 刷新预设列表
        self.refresh_preset_list()
        self.refresh_load_list()

        # 初始筛选和预览
        self.filter_traits()
        self.generate_preview()

        # 设置窗口属性
        self.root.wm_attributes("-topmost", self.always_on_top)
        self.root.wm_attributes("-alpha", self.opacity)

        # 绑定事件
        self._bind_events()

        # 为高级效果标志添加跟踪，自动更新文本框
        self.flag_immune.trace_add('write', lambda *a: self.update_effect_text_from_flags())
        self.flag_no_upkeep.trace_add('write', lambda *a: self.update_effect_text_from_flags())
        self.flag_quality.trace_add('write', lambda *a: self.update_effect_text_from_flags())
        self.change_trait_after_create.trace_add('write', lambda *a: self.update_effect_text_from_flags())
        self.trait_action.trace_add('write', lambda *a: self.update_effect_text_from_flags())

        # 加载保存的窗口配置
        self._load_window_config()

    # ---------- 变量赋值（方便app直接引用） ----------
    def _assign_ui_variables(self):
        """将UI中的变量绑定到app属性"""
        # 基本信息
        self.name_var = self.ui.name_var
        self.random_name = self.ui.random_name
        self.leader_class_gen_var = self.ui.leader_class_gen_var
        self.skill_var = self.ui.skill_var
        self.gender_var = self.ui.gender_var
        self.use_fixed_age = self.ui.use_fixed_age
        self.adv_set_age = self.ui.adv_set_age
        self.adv_age_min = self.ui.adv_age_min
        self.adv_age_max = self.ui.adv_age_max
        self.adv_hide_age = self.ui.adv_hide_age

        # 高级设置
        self.immortal_var = self.ui.immortal_var
        self.event_leader_var = self.ui.event_leader_var
        self.adv_custom_desc = self.ui.adv_custom_desc
        self.adv_catch_phrase = self.ui.adv_catch_phrase
        self.random_bg = self.ui.random_bg
        self.adv_bg_planet = self.ui.adv_bg_planet
        self.adv_bg_job = self.ui.adv_bg_job
        self.adv_bg_ethic = self.ui.adv_bg_ethic
        self.adv_can_move = self.ui.adv_can_move
        self.adv_can_council = self.ui.adv_can_council
        self.adv_hide_leader = self.ui.adv_hide_leader
        self.leader_tier = self.ui.leader_tier
        self.adv_sub_type = self.ui.adv_sub_type
        self.adv_randomize_traits = self.ui.adv_randomize_traits
        self.adv_use_regnal_name = self.ui.adv_use_regnal_name

        # 筛选变量
        self.filter_ruler = self.ui.filter_ruler
        self.filter_commander = self.ui.filter_commander
        self.filter_scientist = self.ui.filter_scientist
        self.filter_council = self.ui.filter_council
        self.filter_governor = self.ui.filter_governor
        self.filter_special = self.ui.filter_special
        self.profession_var = self.ui.profession_var
        self.attr_var = self.ui.attr_var
        self.exclude_negative = self.ui.exclude_negative
        self.search_var = self.ui.search_var
        self.search_by_var = self.ui.search_by_var

        # 高级效果页变量
        self.flag_immune = self.ui.flag_immune
        self.flag_no_upkeep = self.ui.flag_no_upkeep
        self.flag_quality = self.ui.flag_quality
        self.change_trait_after_create = self.ui.change_trait_after_create
        self.trait_action = self.ui.trait_action

        # 其他变量
        self.opacity_var = self.ui.opacity_var
        self.topmost_var = self.ui.topmost_var

    # ---------- 窗口控制 ----------
    def start_drag(self, event):
        self.drag_data["x"] = event.x_root
        self.drag_data["y"] = event.y_root
        self.drag_data["dragging"] = True

    def on_drag(self, event):
        if self.drag_data["dragging"]:
            x = self.root.winfo_x() + (event.x_root - self.drag_data["x"])
            y = self.root.winfo_y() + (event.y_root - self.drag_data["y"])
            self.root.geometry(f"+{x}+{y}")
            self.drag_data["x"] = event.x_root
            self.drag_data["y"] = event.y_root

    def stop_drag(self, event):
        self.drag_data["dragging"] = False

    def update_opacity(self, val):
        self.opacity = float(val)
        self.root.wm_attributes("-alpha", self.opacity)

    def toggle_topmost(self):
        self.always_on_top = self.topmost_var.get()
        self.root.wm_attributes("-topmost", self.always_on_top)
        if self.mini_manager.mini_window:
            self.mini_manager.mini_window.wm_attributes("-topmost", self.always_on_top)

    def toggle_window(self):
        if self.window_state == "normal":
            self.normal_geometry = self.root.geometry()
            self.root.withdraw()
            self.mini_manager.load_position()
            self.mini_manager.mini_window.deiconify()
            self.window_state = "minimized"
            self.update_status("已最小化")
        else:
            self.mini_manager.mini_window.withdraw()
            self.root.deiconify()
            if self.normal_geometry:
                self.root.geometry(self.normal_geometry)
            self.window_state = "normal"
            self.update_status("窗口已恢复")

    def open_from_mini(self):
        self.toggle_window()

    # ---------- 设置窗口 ----------
    def apply_path_settings(self, settings):
        global MOMO_DIR, DATA_DIR, ICON_DIR, CONFIG_DIR, PRESETS_DIR, DB_PATH, SETTINGS_PATH
        MOMO_DIR = settings.get('momo_dir', MOMO_DIR)
        DATA_DIR = settings.get('data_dir', DATA_DIR)
        ICON_DIR = settings.get('icon_dir', ICON_DIR)
        CONFIG_DIR = settings.get('config_dir', CONFIG_DIR)
        PRESETS_DIR = settings.get('presets_dir', PRESETS_DIR)
        DB_PATH = settings.get('db_path', DB_PATH)
        SETTINGS_PATH = os.path.join(CONFIG_DIR, 'settings.json')

        os.makedirs(MOMO_DIR, exist_ok=True)
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(ICON_DIR, exist_ok=True)
        os.makedirs(CONFIG_DIR, exist_ok=True)
        os.makedirs(PRESETS_DIR, exist_ok=True)

        self.preset_manager.presets_dir = PRESETS_DIR

    def save_settings_file(self, settings):
        try:
            with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            messagebox.showerror('保存失败', f'无法保存配置文件：{e}', parent=self.root)
            return False

    def show_settings(self):
        # 保持与原功能一致，此处代码较长，仅做少量优化（如使用局部变量）
        settings_win = tk.Toplevel(self.root)
        settings_win.title('设置')
        settings_win.geometry('520x320')
        settings_win.configure(bg='#2d2d3d')
        settings_win.resizable(False, False)
        settings_win.attributes('-topmost', True)
        settings_win.transient(self.root)
        settings_win.grab_set()
        settings_win.focus_force()

        current = {
            'momo_dir': MOMO_DIR,
            'data_dir': DATA_DIR,
            'icon_dir': ICON_DIR,
            'config_dir': CONFIG_DIR,
            'presets_dir': PRESETS_DIR,
            'db_path': DB_PATH,
        }

        entries = {}

        def add_path_row(label_text, key, row):
            tk.Label(settings_win, text=label_text, bg='#2d2d3d', fg='#cdd6f4').grid(row=row, column=0, sticky='w', padx=10, pady=6)
            entry = tk.Entry(settings_win, width=45)
            entry.insert(0, current[key])
            entry.grid(row=row, column=1, padx=5, pady=6)
            entries[key] = entry
            def choose_path():
                if key == 'db_path':
                    p = filedialog.asksaveasfilename(defaultextension='.db', initialfile=os.path.basename(current[key]), initialdir=os.path.dirname(current[key]), parent=settings_win)
                else:
                    p = filedialog.askdirectory(initialdir=current[key], parent=settings_win)
                if p:
                    entry.delete(0, tk.END)
                    entry.insert(0, p)
            tk.Button(settings_win, text='浏览', command=choose_path, width=6).grid(row=row, column=2, padx=5)

        add_path_row('MOMO 目录', 'momo_dir', 0)
        add_path_row('数据目录', 'data_dir', 1)
        add_path_row('图标目录', 'icon_dir', 2)
        add_path_row('配置目录', 'config_dir', 3)
        add_path_row('预设目录', 'presets_dir', 4)
        add_path_row('数据库路径', 'db_path', 5)

        def on_save():
            new_settings = {k: v.get().strip() for k, v in entries.items()}
            if not new_settings['momo_dir'] or not new_settings['data_dir']:
                messagebox.showwarning('路径错误', 'MOMO 目录和数据目录不能为空。', parent=settings_win)
                return
            self.apply_path_settings(new_settings)
            if self.save_settings_file(new_settings):
                messagebox.showinfo('保存成功', '设置已保存，建议重启程序生效。', parent=settings_win)
                settings_win.destroy()

        btn_frame = tk.Frame(settings_win, bg='#2d2d3d')
        btn_frame.grid(row=6, column=0, columnspan=3, pady=15)
        tk.Button(btn_frame, text='保存', command=on_save, bg='#89dceb', fg='#1e1e2e', width=10).pack(side=tk.LEFT, padx=20)
        tk.Button(btn_frame, text='取消', command=settings_win.destroy, bg='#313244', fg='#cdd6f4', width=10).pack(side=tk.LEFT, padx=20)

    # ---------- 随机领袖（简单实现） ----------
    def random_leader(self):
        import random
        self.name_var.set(random.choice(["Galactic Emperor", "Stellar Scholar", "Void Admiral"]))
        self.leader_class_gen_var.set(random.choice(["ruler", "commander", "scientist"]))
        self.skill_var.set(random.randint(2,8))
        for iid in self.trait_selected:
            self.trait_selected[iid] = random.random() > 0.5
        self._update_tree_selection_display()
        self.update_icon_bar()
        self.schedule_update_preview()
        self.open_from_mini()

    def update_status(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.ui.status_bar.config(text=f"{ts} | {msg}")

    # ---------- 智能刷新 ----------
    def schedule_filter_traits(self):
        if self._filter_job:
            self.root.after_cancel(self._filter_job)
        self._filter_job = self.root.after(200, self.filter_traits)

    def schedule_update_preview(self):
        if self._preview_job:
            self.root.after_cancel(self._preview_job)
        self._preview_job = self.root.after(200, self.generate_preview)

    # ---------- Treeview 操作 ----------
    def toggle_trait_selection(self, iid, shift_pressed=False):
        current = self.trait_selected.get(iid, False)
        if shift_pressed and self.last_selected_iid:
            items = self.ui.tree.get_children()
            if self.last_selected_iid in items and iid in items:
                idx1 = items.index(self.last_selected_iid)
                idx2 = items.index(iid)
                start, end = sorted([idx1, idx2])
                for item in items[start:end+1]:
                    self.trait_selected[item] = True
                self._update_tree_selection_display()
                self.update_icon_bar()
                self.schedule_update_preview()
                return
        else:
            if not current:
                tags = self.ui.tree.item(iid, 'tags')
                code = tags[0]
                exclusive_with = tags[1] if len(tags) > 1 else ''
                if exclusive_with:
                    ex_list = [x.strip() for x in exclusive_with.split(',') if x.strip()]
                    conflict_codes = []
                    for other_iid, sel in self.trait_selected.items():
                        if sel:
                            other_tags = self.ui.tree.item(other_iid, 'tags')
                            other_code = other_tags[0]
                            if other_code in ex_list:
                                conflict_codes.append(other_code)
                    if conflict_codes:
                        conflict_names = []
                        for c in conflict_codes:
                            for t in self.current_traits:
                                if t[3] == c:
                                    conflict_names.append(f"[{t[1]}] {t[2]}")
                                    break
                        conflict_str = "\n".join(conflict_names)
                        if not messagebox.askyesno(
                            "特质冲突提醒",
                            f"该特质与以下已选特质存在冲突：\n{conflict_str}\n\n是否仍要选中？",
                            parent=self.root
                        ):
                            return

        self.trait_selected[iid] = not current
        self.ui.tree.set(iid, 'select', '☑' if self.trait_selected[iid] else '☐')
        self.last_selected_iid = iid
        self.update_icon_bar()
        if self.change_trait_after_create.get():
            self.update_effect_text_from_flags()
        else:
            self.schedule_update_preview()

    def _update_tree_selection_display(self):
        for iid, selected in self.trait_selected.items():
            self.ui.tree.set(iid, 'select', '☑' if selected else '☐')
        self.update_icon_bar()

    def _populate_tree(self, traits):
        for item in self.ui.tree.get_children():
            self.ui.tree.delete(item)
        self.trait_selected.clear()
        self.trait_effect.clear()
        self.trait_code_iid.clear()
        self.last_selected_iid = None

        for tid, number, name, code, attr_name, exclusive, effect, effect_color, icon_path in traits:
            img = None
            if icon_path and os.path.exists(icon_path):
                try:
                    if code in self.icon_cache:
                        img = self.icon_cache[code]
                    else:
                        pil_img = Image.open(icon_path)
                        pil_img = pil_img.resize((20, 20), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(pil_img)
                        self.icon_cache[code] = photo
                        img = photo
                except:
                    pass

            iid = self.ui.tree.insert('', 'end',
                                      values=('☐', '', number, name, code, effect or ''),
                                      image=img if img else '')
            self.trait_selected[iid] = False
            self.trait_effect[iid] = (effect or '', effect_color or '')
            self.trait_code_iid[code] = iid
            self.ui.tree.item(iid, tags=(code, exclusive or ''))

    # ---------- 全选/清除 ----------
    def select_all_traits(self):
        for iid in self.ui.tree.get_children():
            self.trait_selected[iid] = True
        self._update_tree_selection_display()
        self.update_icon_bar()
        if self.change_trait_after_create.get():
            self.update_effect_text_from_flags()
        else:
            self.schedule_update_preview()

    def clear_all_selected(self):
        for iid in self.trait_selected:
            self.trait_selected[iid] = False
        self._update_tree_selection_display()
        self.update_icon_bar()
        if self.change_trait_after_create.get():
            self.update_effect_text_from_flags()
        else:
            self.schedule_update_preview()

    # ---------- 图标栏更新 ----------
    def update_icon_bar(self):
        for widget in self.ui.icon_bar_frame.winfo_children():
            widget.destroy()

        selected_iids = [iid for iid, sel in self.trait_selected.items() if sel]
        for iid in selected_iids:
            code = self.ui.tree.item(iid, 'tags')[0]
            icon_path = None
            effect_text = ''
            effect_color = ''
            for t in self.current_traits:
                if t[3] == code:
                    icon_path = t[8]
                    effect_text, effect_color = self.trait_effect.get(iid, ('', ''))
                    break
            if icon_path and os.path.exists(icon_path):
                try:
                    if code in self.icon_cache:
                        photo = self.icon_cache[code]
                    else:
                        pil_img = Image.open(icon_path)
                        pil_img = pil_img.resize((20, 20), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(pil_img)
                        self.icon_cache[code] = photo
                    icon_label = tk.Label(self.ui.icon_bar_frame, image=photo, bg=self.ui.bg)
                    icon_label.image = photo
                    icon_label.pack(side=tk.LEFT, padx=2)
                    icon_label.trait_code = code
                    ToolTip(icon_label, self, effect_text, effect_color)
                except:
                    pass

    def remove_trait_by_code(self, code):
        iid = self.trait_code_iid.get(code)
        if iid and self.trait_selected.get(iid, False):
            self.trait_selected[iid] = False
            self.ui.tree.set(iid, 'select', '☐')
            self.update_icon_bar()
            self.schedule_update_preview()

    # ---------- 筛选 ----------
    def filter_traits(self, event=None):
        # 保存当前选中的特质代码
        selected_codes = []
        for iid, sel in self.trait_selected.items():
            if sel:
                tags = self.ui.tree.item(iid, 'tags')
                if tags:
                    selected_codes.append(tags[0])

        # 获取筛选条件
        ruler = self.filter_ruler.get() if self.filter_ruler.get() else None
        commander = self.filter_commander.get() if self.filter_commander.get() else None
        scientist = self.filter_scientist.get() if self.filter_scientist.get() else None
        council = self.filter_council.get() if self.filter_council.get() else None
        governor = self.filter_governor.get() if self.filter_governor.get() else None
        special = self.filter_special.get() if self.filter_special.get() else None

        profession = self.profession_var.get()
        if profession == "无":
            profession = None
        attr = self.attr_var.get()
        if attr == "全部":
            attr = None

        search_text = self.search_var.get()
        search_by = self.search_by_var.get()
        if search_by == "名称":
            search_by = 'name'
        elif search_by == "序号":
            search_by = 'number'
        else:
            search_by = 'effect'

        exclude_negative = self.exclude_negative.get()

        # 执行查询
        self.current_traits = get_traits_with_filters(
            ruler=ruler, commander=commander, scientist=scientist,
            council=council, governor=governor, special=special,
            profession=profession, attribute=attr,
            search_text=search_text, search_by=search_by,
            exclude_negative=exclude_negative
        )

        # 填充树
        self._populate_tree(self.current_traits)

        # 恢复选中状态
        for code in selected_codes:
            if code in self.trait_code_iid:
                iid = self.trait_code_iid[code]
                self.trait_selected[iid] = True
        self._update_tree_selection_display()

        self.update_status(f"加载 {len(self.current_traits)} 个特质")
        self.schedule_update_preview()

    # ---------- 生成并复制 ----------
    def generate_and_copy(self):
        self.generate_preview()
        if self.copy_code():
            self.ui.notebook.select(self.ui.notebook.tabs().index(self.ui.notebook.tabs()[-2]))
            self.update_status("代码已复制")

    # ---------- 恢复默认设置 ----------
    def reset_all_defaults(self):
        # 基本信息
        self.name_var.set("random")
        self.leader_class_gen_var.set("ruler")
        self.skill_var.set(3)
        self.gender_var.set("随机")
        self.use_fixed_age.set(False)
        self.adv_set_age.set(0)
        self.adv_age_min.set(25)
        self.adv_age_max.set(60)
        self.adv_hide_age.set(False)

        # 高级设置
        self.immortal_var.set(False)
        self.event_leader_var.set(False)
        self.adv_custom_desc.set("")
        self.adv_catch_phrase.set("")
        self.random_bg.set(True)
        self.adv_bg_planet.set("")
        self.adv_bg_job.set("")
        self.adv_bg_ethic.set("")
        self.adv_can_move.set(True)
        self.adv_can_council.set(True)
        self.adv_hide_leader.set(False)
        self.leader_tier.set("")
        self.adv_sub_type.set("")
        self.adv_randomize_traits.set(True)
        self.adv_use_regnal_name.set(False)
        self.change_trait_after_create.set(False)
        self.trait_action.set("")

        # 高级效果页
        self.flag_immune.set(False)
        self.flag_no_upkeep.set(False)
        self.flag_quality.set("")

        # 筛选条件
        self.filter_ruler.set(False)
        self.filter_commander.set(False)
        self.filter_scientist.set(False)
        self.filter_council.set(False)
        self.filter_governor.set(False)
        self.filter_special.set(False)
        self.profession_var.set("无")
        self.attr_var.set("全部")
        self.exclude_negative.set(False)
        self.search_var.set("")
        self.search_by_var.set("名称")

        # 清除所有选中特质
        for iid in list(self.trait_selected.keys()):
            self.trait_selected[iid] = False
        self._update_tree_selection_display()
        self.update_icon_bar()

        # 重新筛选和预览
        self.filter_traits()
        self.generate_preview()
        self.update_status("已恢复默认设置")

    # ---------- 高级效果标志自动生成 ----------
    def update_effect_text_from_flags(self):
        """根据当前标志生成完整的 effect 块，并填入高级效果文本框"""
        lines = []
        if self.flag_immune.get():
            lines.append("    set_leader_flag = immune_to_negative_traits")
        if self.flag_no_upkeep.get():
            lines.append("    set_leader_flag = should_not_have_upkeep")
        quality = self.flag_quality.get()
        if quality:
            lines.append(f"    set_leader_flag = {quality}")

        if self.change_trait_after_create.get():
            selected_codes = [self.ui.tree.item(iid, 'tags')[0]
                              for iid, sel in self.trait_selected.items() if sel]
            trait_action = self.trait_action.get()
            if trait_action == 'add_trait':
                for code in selected_codes:
                    lines.append(f"    add_trait = {code}")
            elif trait_action == 'remove_trait':
                for code in selected_codes:
                    lines.append(f"    remove_trait = {code}")

        if lines:
            effect_block = "effect = {\n" + "\n".join(lines) + "\n}"
        else:
            effect_block = ""

        self.ui.adv_effect_text.delete("1.0", tk.END)
        if effect_block:
            self.ui.adv_effect_text.insert("1.0", effect_block)

        self.schedule_update_preview()

    # ---------- 生成预览代码 ----------
    def generate_preview(self):
        # 收集所有配置
        name = self.name_var.get().strip()
        if self.random_name.get():
            name = "random"
        leader_class = self.leader_class_gen_var.get()
        skill = self.skill_var.get()
        gender = self.gender_var.get()

        immortal = self.immortal_var.get()
        event_leader = self.event_leader_var.get()
        set_age = self.adv_set_age.get()
        age_min = self.adv_age_min.get()
        age_max = self.adv_age_max.get()
        hide_age = self.adv_hide_age.get()
        sub_type = self.adv_sub_type.get().strip()
        can_move = self.adv_can_move.get()
        can_council = self.adv_can_council.get()
        hide_leader = self.adv_hide_leader.get()
        randomize_traits = self.adv_randomize_traits.get()
        use_regnal = self.adv_use_regnal_name.get()
        custom_desc = self.adv_custom_desc.get().strip()
        catch_phrase = self.adv_catch_phrase.get().strip()
        skip_bg = not self.random_bg.get()
        bg_planet = self.adv_bg_planet.get().strip()
        bg_job = self.adv_bg_job.get().strip()
        bg_ethic = self.adv_bg_ethic.get().strip()
        tier = self.leader_tier.get()

        user_effect = self.ui.adv_effect_text.get("1.0", tk.END).strip()

        selected_traits = []
        for iid, sel in self.trait_selected.items():
            if sel:
                tags = self.ui.tree.item(iid, 'tags')
                code = tags[0]
                selected_traits.append(code)

        # 构建代码行
        lines = []
        lines.append("create_leader = {")

        # 基础信息
        if name.lower() == "random":
            lines.append("    name = random")
        elif name:
            lines.append(f'    name = "{name}"')

        lines.append("    species = root")
        lines.append(f"    class = {leader_class}")
        lines.append(f"    skill = {skill}")

        if gender != "随机":
            gender_map = {"随机": "random", "男": "male", "女": "female", "不确定": "indeterminable"}
            eng_gender = gender_map.get(gender, "random")
            if eng_gender != "random":
                lines.append(f"    gender = {eng_gender}")

        if immortal:
            lines.append("    immortal = yes")
        if event_leader:
            lines.append("    event_leader = yes")

        # 年龄
        if set_age > 0:
            lines.append(f"    set_age = {set_age}")
        elif age_min > 0 and age_max > 0:
            lines.append(f"    leader_age_min = {age_min}")
            lines.append(f"    leader_age_max = {age_max}")
        if hide_age:
            lines.append("    hide_age = yes")

        if sub_type:
            lines.append(f"    sub_type = {sub_type}")
        if not can_move:
            lines.append("    can_manually_change_location = no")
        if not can_council:
            lines.append("    can_assign_to_council = no")
        if hide_leader:
            lines.append("    hide_leader = yes")
        if not randomize_traits:
            lines.append("    randomize_traits = no")
        if use_regnal:
            lines.append("    use_regnal_name = yes")
        if custom_desc:
            lines.append(f"    custom_description = {custom_desc}")
        if catch_phrase:
            lines.append(f'    custom_catch_phrase = "{catch_phrase}"')
        if skip_bg:
            lines.append("    skip_background_generation = yes")
        else:
            if bg_planet:
                lines.append(f"    background_planet = {bg_planet}")
            if bg_job:
                lines.append(f"    background_job = {bg_job}")
            if bg_ethic:
                ethic_map = {
                    "唯心主义": "ethic_spiritualist",
                    "唯物主义": "ethic_materialist",
                    "军国主义": "ethic_militarist",
                    "和平主义": "ethic_pacifist",
                    "排外主义": "ethic_xenophobe",
                    "亲外主义": "ethic_xenophile",
                    "威权主义": "ethic_authoritarian",
                    "平等主义": "ethic_egalitarian",
                    "格式塔": "ethic_gestalt_consciousness",
                }
                eng_ethic = ethic_map.get(bg_ethic, bg_ethic)
                lines.append(f"    background_ethic = {eng_ethic}")
        if tier == "renowned":
            lines.append("    tier = leader_tier_renowned")
        elif tier == "legendary":
            lines.append("    tier = leader_tier_legendary")

        # 特质（如果不是先创后改）
        if selected_traits and not self.change_trait_after_create.get():
            lines.append("    traits = {")
            for idx, code in enumerate(selected_traits, 1):
                lines.append(f"        {idx} = {code}")
            lines.append("    }")

        # 用户效果块
        if user_effect:
            effect_lines = user_effect.splitlines()
            for eline in effect_lines:
                lines.append(f"    {eline}")

        lines.append("}")

        code = "\n".join(lines)
        self.display_code(code)
        self.update_preset_info()
        self.update_status("指令已生成")

    def display_code(self, code):
        self.ui.code_text.delete(1.0, tk.END)
        self.ui.code_text.insert(1.0, code)
        self.highlight_syntax()

    def highlight_syntax(self):
        keywords = ["create_leader", "name", "species", "class", "skill", "gender",
                    "traits", "immortal", "event_leader", "randomize_traits",
                    "set_age", "leader_age_min", "leader_age_max", "hide_age",
                    "sub_type", "can_manually_change_location", "can_assign_to_council",
                    "hide_leader", "use_regnal_name", "effect", "custom_description",
                    "custom_catch_phrase", "skip_background_generation", "background_planet",
                    "background_job", "background_ethic", "tier"]
        for kw in keywords:
            start = "1.0"
            while True:
                pos = self.ui.code_text.search(kw, start, stopindex=tk.END)
                if not pos:
                    break
                end = f"{pos}+{len(kw)}c"
                self.ui.code_text.tag_add("keyword", pos, end)
                start = end
        # 字符串高亮
        start = "1.0"
        while True:
            pos = self.ui.code_text.search('"', start, stopindex=tk.END)
            if not pos:
                break
            end = self.ui.code_text.search('"', f"{pos}+1c", stopindex=tk.END)
            if not end:
                break
            end = f"{end}+1c"
            self.ui.code_text.tag_add("string", pos, end)
            start = end
        for bool_val in ["yes", "no"]:
            start = "1.0"
            while True:
                pos = self.ui.code_text.search(bool_val, start, stopindex=tk.END)
                if not pos:
                    break
                end = f"{pos}+{len(bool_val)}c"
                self.ui.code_text.tag_add("boolean", pos, end)
                start = end

    def copy_code(self):
        code = self.ui.code_text.get(1.0, tk.END).strip()
        if code:
            self.root.clipboard_clear()
            self.root.clipboard_append(code)
            self.update_status("代码已复制")
            return True
        return False

    def save_code(self):
        code = self.ui.code_text.get(1.0, tk.END)
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")])
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(code)
            self.update_status(f"已保存至 {os.path.basename(path)}")

    # ---------- 预设管理 ----------
    def refresh_preset_list(self):
        self.ui.preset_listbox.delete(0, tk.END)
        self.preset_items.clear()
        hidden_files = self.preset_manager.get_hidden_preset_files()
        for filepath in hidden_files:
            presets = self.preset_manager.load_all_presets_from_file(filepath)
            for name, code in presets:
                self.preset_items.append((name, code))
                self.ui.preset_listbox.insert(tk.END, name)

    def refresh_load_list(self):
        self.ui.load_listbox.delete(0, tk.END)
        self.load_buttons.clear()
        visible_files = self.preset_manager.get_visible_preset_files()
        for filepath in visible_files:
            presets = self.preset_manager.load_all_presets_from_file(filepath)
            for name, code in presets:
                self.load_buttons.append((name, code, filepath))
                self.ui.load_listbox.insert(tk.END, name)

    def on_preset_select(self, event):
        selection = self.ui.preset_listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        name, code = self.preset_items[idx]
        self.apply_preset_code(code)

    def on_load_select(self, event):
        selection = self.ui.load_listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        name, code, filepath = self.load_buttons[idx]
        self.apply_preset_code(code)

    def copy_file_to_presets(self):
        selection = self.ui.load_listbox.curselection()
        if not selection:
            messagebox.showwarning("未选择", "请先在加载列表中选择一个按钮")
            return
        idx = selection[0]
        name, code, src_path = self.load_buttons[idx]

        base_name = os.path.basename(src_path)
        name_without_ext, ext = os.path.splitext(base_name)
        dest_path = os.path.join(PRESETS_DIR, base_name)
        counter = 1
        while os.path.exists(dest_path):
            new_name = f"{name_without_ext}_{counter}{ext}"
            dest_path = os.path.join(PRESETS_DIR, new_name)
            counter += 1

        try:
            shutil.copy2(src_path, dest_path)
            self.update_status(f"已复制到 {os.path.basename(dest_path)}")
            self.refresh_load_list()
        except Exception as e:
            messagebox.showerror("错误", f"复制文件失败：{e}")

    def export_as_preset(self):
        button_name = self.ui.export_name_entry.get().strip()
        if not button_name:
            messagebox.showwarning("输入错误", "请输入按钮名称")
            return
        preview_code = self.ui.code_text.get(1.0, tk.END).strip()
        if not preview_code:
            messagebox.showwarning("无代码", "当前预览代码为空")
            return

        preset_block = f"#$button{button_name}\n{preview_code}\n\n"
        dest_file = os.path.join(PRESETS_DIR, "user_presets.txt")
        try:
            with open(dest_file, 'a', encoding='utf-8') as f:
                f.write(preset_block)
            self.update_status("已导出到 user_presets.txt")
            self.refresh_load_list()
        except Exception as e:
            messagebox.showerror("错误", f"导出失败：{e}")

    def apply_preset_code(self, code_block):
        # 清除当前选中
        for iid in self.trait_selected:
            self.trait_selected[iid] = False
        self._update_tree_selection_display()

        # 解析基本字段（简化版）
        name_match = re.search(r'name\s*=\s*"?([^"\n]+)"?', code_block)
        if name_match:
            self.name_var.set(name_match.group(1).strip())

        class_match = re.search(r'class\s*=\s*(\w+)', code_block)
        if class_match:
            self.leader_class_gen_var.set(class_match.group(1))

        skill_match = re.search(r'skill\s*=\s*(\d+)', code_block)
        if skill_match:
            self.skill_var.set(int(skill_match.group(1)))

        gender_match = re.search(r'gender\s*=\s*(\w+)', code_block)
        if gender_match:
            g = gender_match.group(1)
            gender_map_rev = {"male": "男", "female": "女", "indeterminable": "不确定", "random": "随机"}
            self.gender_var.set(gender_map_rev.get(g, "随机"))

        immortal_match = re.search(r'immortal\s*=\s*(yes|no)', code_block)
        if immortal_match:
            self.immortal_var.set(immortal_match.group(1) == 'yes')

        event_match = re.search(r'event_leader\s*=\s*(yes|no)', code_block)
        if event_match:
            self.event_leader_var.set(event_match.group(1) == 'yes')

        sub_match = re.search(r'sub_type\s*=\s*(\w+)', code_block)
        if sub_match:
            self.adv_sub_type.set(sub_match.group(1))

        # 解析特质
        traits_start = code_block.find('traits = {')
        if traits_start != -1:
            brace_count = 1
            pos = traits_start + len('traits = {')
            while pos < len(code_block) and brace_count > 0:
                if code_block[pos] == '{':
                    brace_count += 1
                elif code_block[pos] == '}':
                    brace_count -= 1
                pos += 1
            traits_block = code_block[traits_start:pos]
            trait_codes = re.findall(r'\d+\s*=\s*(\w+)', traits_block)
            for item in self.ui.tree.get_children():
                tags = self.ui.tree.item(item, 'tags')
                code = tags[0]
                if code in trait_codes:
                    self.trait_selected[item] = True
            self._update_tree_selection_display()

        self.generate_preview()

    def update_preset_info(self):
        name = self.name_var.get().strip()
        leader_class = self.leader_class_gen_var.get()
        skill = self.skill_var.get()
        gender = self.gender_var.get()
        immortal = self.immortal_var.get()
        event_leader = self.event_leader_var.get()
        selected_traits = []
        for iid, sel in self.trait_selected.items():
            if sel:
                tags = self.ui.tree.item(iid, 'tags')
                code = tags[0]
                selected_traits.append(code)

        lines = []
        lines.append(f"名称: {name}")
        lines.append(f"职业: {leader_class}")
        lines.append(f"技能等级: {skill}")
        lines.append(f"性别: {gender}")
        if immortal:
            lines.append("永生: 是")
        if event_leader:
            lines.append("事件领袖: 是")
        lines.append("")
        lines.append("特质:")
        if selected_traits:
            for code in selected_traits:
                trait_name = code
                for t in self.current_traits:
                    if t[3] == code:
                        trait_name = f"[{t[1]}] {t[2]}"
                        break
                lines.append(f"  {trait_name}")
        else:
            lines.append("  (无)")

        info = "\n".join(lines)

        self.ui.preset_info_text.config(state=tk.NORMAL)
        self.ui.preset_info_text.delete(1.0, tk.END)
        self.ui.preset_info_text.insert(1.0, info)
        self.ui.preset_info_text.config(state=tk.DISABLED)

    # ---------- 帮助 ----------
    def show_help(self):
        help_text = """群星领袖指令生成器 v6.3

使用说明：
- 基本信息：设置领袖名称、职业、技能、性别等，点击“生成领袖”按钮可一键复制代码并跳转预览。
- 年龄设置：可选择固定年龄或随机范围，通过复选框切换。
- 名称随机：勾选“随机”则名称设为 random（可手动修改）。
- 性别：新增“不确定”选项。
- 高级设置：位于基本信息下方，包含特殊属性、自定义内容、背景故事、权限控制、级别、科学家子类型。
  - 背景故事：勾选“随机生成背景”则跳过手动指定，不勾选时可手动指定星球、职业、伦理。
- 特质选择：独立标签页，包含筛选、全选、清除、图标栏、特质列表。
- 高级效果：独立标签页，可添加 set_leader_flag（避免负面特质、无需维护费），以及品质选择（著名领袖、传奇领袖），点击“恢复默认”可清空所有效果。
- 预设领袖：左侧预设列表（内置），中间加载列表（用户文件），右侧当前配置预览。点击列表项自动应用对应预设。
- 加载列表下方按钮：左侧“复制打开文件”将选中按钮所属的原始文件复制到 presets 目录；右侧“刷新”刷新列表。
- 代码预览页：新增导出功能，输入按钮名称后点击“导出为预设领袖”可将当前代码保存到 user_presets.txt，并显示在加载列表中。
- 转化为指令：将预览代码包装为 effect 块，并格式化后显示，方便直接用于事件或控制台。

窗口控制：
- 拖动标题栏移动主窗口
- 点击“—”最小化为悬浮按钮，短点击恢复，长按拖动位置
- 调整透明度、置顶开关

快捷键：
Ctrl+G 生成并复制指令
F1    帮助
Ctrl+Q 退出
"""
        messagebox.showinfo("帮助", help_text)

    # ---------- 事件绑定 ----------
    def _bind_events(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        if self.mini_manager.mini_window:
            self.mini_manager.mini_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind("<Control-g>", lambda e: self.generate_and_copy())
        self.root.bind("<Control-q>", lambda e: self.on_closing())
        self.root.bind("<F1>", lambda e: self.show_help())
        self.ui.tree.bind("<MouseWheel>", self.on_mousewheel)
        self.ui.tree.bind("<Button-4>", self.on_mousewheel)
        self.ui.tree.bind("<Button-5>", self.on_mousewheel)

        self.ui.preset_listbox.bind('<<ListboxSelect>>', self.on_preset_select)
        self.ui.load_listbox.bind('<<ListboxSelect>>', self.on_load_select)

    def on_mousewheel(self, event):
        if event.state & 0x0001:
            if event.delta:
                self.ui.tree.xview_scroll(-1 * (event.delta // 120), "units")
            elif event.num == 4:
                self.ui.tree.xview_scroll(-1, "units")
            elif event.num == 5:
                self.ui.tree.xview_scroll(1, "units")
        else:
            if event.delta:
                self.ui.tree.yview_scroll(-1 * (event.delta // 120), "units")
            elif event.num == 4:
                self.ui.tree.yview_scroll(-1, "units")
            elif event.num == 5:
                self.ui.tree.yview_scroll(1, "units")
        return "break"

    # ---------- 转化为指令 ----------
    def transform_command(self):
        preview_code = self.ui.code_text.get(1.0, tk.END).strip()
        if not preview_code:
            return
        wrapped = f"""effect = {{
    every_country = {{
        limit = {{
            is_ai = no
        }}
        save_event_target_as = demoplayer
    }}
    event_target:demoplayer = {{
{preview_code}
    }}
}}"""
        try:
            formatted = trans.format_stellaris_script(wrapped)
        except Exception as e:
            print(f"格式化失败: {e}")
            formatted = wrapped
        self.ui.transform_text.delete(1.0, tk.END)
        self.ui.transform_text.insert(1.0, formatted)
        self.update_status("已转化为指令")

    def copy_transform_code(self):
        code = self.ui.transform_text.get(1.0, tk.END).strip()
        if code:
            self.root.clipboard_clear()
            self.root.clipboard_append(code)
            self.update_status("转化代码已复制")

    # ---------- 窗口关闭 ----------
    def on_closing(self):
        if messagebox.askokcancel("退出", "确定退出吗？"):
            self._save_window_config()
            self.root.destroy()

    def _save_window_config(self):
        try:
            cfg_path = os.path.join(CONFIG_DIR, "window.json")
            cfg = {}
            if os.path.exists(cfg_path):
                with open(cfg_path, 'r') as f:
                    cfg = json.load(f)
            cfg["main_geometry"] = self.root.geometry()
            cfg["opacity"] = self.opacity
            cfg["topmost"] = self.always_on_top
            with open(cfg_path, 'w') as f:
                json.dump(cfg, f)
        except:
            pass

    def _load_window_config(self):
        try:
            cfg_path = os.path.join(CONFIG_DIR, "window.json")
            if os.path.exists(cfg_path):
                with open(cfg_path, 'r') as f:
                    cfg = json.load(f)
                if "main_geometry" in cfg:
                    self.root.geometry(cfg["main_geometry"])
                if "opacity" in cfg:
                    self.opacity = cfg["opacity"]
                    self.opacity_var.set(self.opacity)
                    self.root.wm_attributes("-alpha", self.opacity)
                if "topmost" in cfg:
                    self.always_on_top = cfg["topmost"]
                    self.topmost_var.set(self.always_on_top)
                    self.root.wm_attributes("-topmost", self.always_on_top)
        except:
            pass

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = StellarisLeaderGenerator()
    app.run()
