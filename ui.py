#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
群星领袖指令生成器 - 重构版前端界面
功能与 v6.3 完全一致，优化了布局代码，提高了可读性
"""

import tkinter as tk
from tkinter import ttk


class UI:
    def __init__(self, root, app_controller):
        self.root = root
        self.app = app_controller

        # 主题颜色（保持原样）
        self.bg = '#1e1e2e'
        self.fg = '#cdd6f4'
        self.bg_dark = '#2d2d3d'
        self.fg_bright = '#89dceb'
        self.fg_green = '#a6e3a1'
        self.fg_red = '#f38ba8'
        self.fg_orange = '#fab387'
        self.fg_purple = '#cba6f7'
        self.bg_entry = '#313244'
        self.select_bg = self.fg_bright
        self.select_fg = self.bg
        self.tree_bg = '#1e1e2e'
        self.tree_fg = self.fg
        self.tree_select_bg = '#45475a'

        # 控件引用（将在创建时赋值）
        self.tree = None
        self.preset_info_text = None
        self.preset_listbox = None
        self.load_listbox = None
        self.code_text = None
        self.status_bar = None
        self.notebook = None
        self.icon_bar_frame = None
        self.icon_bar_canvas = None
        self.adv_effect_text = None
        self.transform_text = None
        self.export_name_entry = None

        # 变量（由 app 绑定）
        self.name_var = None
        self.leader_class_gen_var = None
        self.gender_var = None
        self.skill_var = None
        self.immortal_var = None
        self.event_leader_var = None

        self.filter_ruler = None
        self.filter_commander = None
        self.filter_scientist = None
        self.filter_council = None
        self.filter_governor = None
        self.filter_special = None
        self.profession_var = None
        self.attr_var = None
        self.search_var = None
        self.search_by_var = None
        self.exclude_negative = None

        # 高级设置变量
        self.adv_set_age = None
        self.adv_age_min = None
        self.adv_age_max = None
        self.adv_hide_age = None
        self.adv_sub_type = None
        self.adv_can_move = None
        self.adv_can_council = None
        self.adv_hide_leader = None
        self.adv_randomize_traits = None
        self.adv_use_regnal_name = None
        self.adv_custom_desc = None
        self.adv_catch_phrase = None
        self.adv_bg_planet = None
        self.adv_bg_job = None
        self.adv_bg_ethic = None
        self.random_bg = None
        self.leader_tier = None

        # 高级效果页变量
        self.flag_immune = None
        self.flag_no_upkeep = None
        self.flag_quality = None
        self.change_trait_after_create = None
        self.trait_action = None

        # 年龄模式控制
        self.use_fixed_age = None
        self.fixed_age_frame = None
        self.range_age_frame = None

        # 窗口控制变量
        self.opacity_var = None
        self.topmost_var = None

        self.setup_ui()

    def setup_ui(self):
        self.root.configure(bg=self.bg)

        self.main_container = tk.Frame(self.root, bg=self.bg)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self.create_title_bar()
        self.create_content()
        self.create_status_bar()

    # ---------- 标题栏 ----------
    def create_title_bar(self):
        bar = tk.Frame(self.main_container, bg=self.bg_dark, height=30)
        bar.pack(fill=tk.X, padx=1, pady=1)
        bar.pack_propagate(False)

        # 绑定拖动事件
        bar.bind("<ButtonPress-1>", self.app.start_drag)
        bar.bind("<B1-Motion>", self.app.on_drag)
        bar.bind("<ButtonRelease-1>", self.app.stop_drag)

        title = tk.Label(bar, text="✨ 群星领袖指令生成器", bg=self.bg_dark, fg=self.fg_bright,
                         font=('Microsoft YaHei UI', 10, 'bold'))
        title.pack(side=tk.LEFT, padx=10)
        title.bind("<ButtonPress-1>", self.app.start_drag)
        title.bind("<B1-Motion>", self.app.on_drag)
        title.bind("<ButtonRelease-1>", self.app.stop_drag)

        ctrl = tk.Frame(bar, bg=self.bg_dark)
        ctrl.pack(side=tk.RIGHT, padx=5)

        # 最小化按钮
        tk.Button(ctrl, text="—", command=self.app.toggle_window,
                  bg=self.bg_dark, fg=self.fg, activebackground='#45475a',
                  activeforeground=self.fg, bd=0, font=('Segoe UI', 12), width=3
                  ).pack(side=tk.LEFT, padx=2)

        tk.Label(ctrl, text="透明:", bg=self.bg_dark, fg='#bac2de',
                 font=('Microsoft YaHei UI', 9)).pack(side=tk.LEFT, padx=(10,5))
        self.opacity_var = tk.DoubleVar(value=self.app.opacity)
        tk.Scale(ctrl, from_=0.3, to=1.0, resolution=0.05, orient=tk.HORIZONTAL,
                 variable=self.opacity_var, command=self.app.update_opacity,
                 length=60, bg=self.bg_dark, fg='#bac2de', highlightthickness=0,
                 sliderrelief=tk.FLAT, troughcolor='#45475a', activebackground=self.fg_bright
                 ).pack(side=tk.LEFT, padx=(0,10))

        self.topmost_var = tk.BooleanVar(value=self.app.always_on_top)
        tk.Checkbutton(ctrl, text="置顶", variable=self.topmost_var,
                       command=self.app.toggle_topmost, bg=self.bg_dark, fg='#bac2de',
                       activebackground=self.bg_dark, activeforeground='#bac2de',
                       selectcolor='#45475a', font=('Microsoft YaHei UI', 9)
                       ).pack(side=tk.LEFT, padx=(0,10))

        tk.Button(ctrl, text="设置", command=self.app.show_settings,
                  bg=self.bg_dark, fg=self.fg, activebackground='#45475a',
                  activeforeground=self.fg, bd=0, font=('Segoe UI', 10), width=5
                  ).pack(side=tk.LEFT, padx=2)
        tk.Button(ctrl, text="?", command=self.app.show_help,
                  bg=self.bg_dark, fg=self.fg, activebackground='#45475a',
                  activeforeground=self.fg, bd=0, font=('Segoe UI', 10), width=3
                  ).pack(side=tk.LEFT, padx=2)

    # ---------- 主内容区域 ----------
    def create_content(self):
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=2, pady=(0,2))

        style = ttk.Style()
        style.theme_create("custom", parent="alt", settings={
            "TNotebook": {"configure": {"background": self.bg}},
            "TNotebook.Tab": {
                "configure": {"background": "#45475a", "foreground": self.fg, "padding": [10,5]},
                "map": {"background": [("selected", self.fg_bright)], "foreground": [("selected", self.bg)]}
            }
        })
        style.theme_use("custom")

        # 创建各标签页
        self.create_leader_tab()
        self.create_trait_tab()
        self.create_advanced_effect_tab()
        self.create_preset_tab()
        self.create_preview_tab()
        self.create_transform_tab()

    # ---------- 领袖设置页 ----------
    def create_leader_tab(self):
        tab = tk.Frame(self.notebook, bg=self.bg)
        self.notebook.add(tab, text="领袖设置")

        # ===== 基本信息框 =====
        basic_frame = tk.LabelFrame(tab, text="基本信息", bg=self.bg, fg=self.fg_bright,
                                     font=('Microsoft YaHei UI', 10, 'bold'))
        basic_frame.pack(fill=tk.X, padx=10, pady=(10,5))

        grid_basic = tk.Frame(basic_frame, bg=self.bg)
        grid_basic.pack(padx=10, pady=10)

        # 名称
        tk.Label(grid_basic, text="名称:", bg=self.bg, fg=self.fg).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar(value="random")
        name_entry = tk.Entry(grid_basic, textvariable=self.name_var, bg=self.bg_entry, fg=self.fg,
                 insertbackground=self.fg, width=20)
        name_entry.grid(row=0, column=1, padx=5, pady=5)
        name_entry.bind('<KeyRelease>', lambda e: self.app.schedule_update_preview())

        self.random_name = tk.BooleanVar(value=False)
        tk.Checkbutton(grid_basic, text="随机", variable=self.random_name,
                       bg=self.bg, fg=self.fg, selectcolor='#45475a',
                       command=self.app.schedule_update_preview).grid(row=0, column=2, padx=(0,20))

        # 职业
        tk.Label(grid_basic, text="职业:", bg=self.bg, fg=self.fg).grid(row=0, column=3, sticky=tk.W, padx=(20,5), pady=5)
        self.leader_class_gen_var = tk.StringVar(value="ruler")
        class_combo = ttk.Combobox(grid_basic, textvariable=self.leader_class_gen_var,
                                    values=["ruler", "commander", "scientist"],
                                    state="readonly", width=10)
        class_combo.grid(row=0, column=4, padx=5, pady=5)
        class_combo.bind('<<ComboboxSelected>>', lambda e: self.app.schedule_update_preview())

        # 技能等级
        tk.Label(grid_basic, text="技能等级:", bg=self.bg, fg=self.fg).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.skill_var = tk.IntVar(value=3)
        spin_skill = tk.Spinbox(grid_basic, from_=1, to=10, textvariable=self.skill_var,
                   bg=self.bg_entry, fg=self.fg, width=5)
        spin_skill.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        spin_skill.bind('<KeyRelease>', lambda e: self.app.schedule_update_preview())
        spin_skill.bind('<<Increment>>', lambda e: self.app.schedule_update_preview())
        spin_skill.bind('<<Decrement>>', lambda e: self.app.schedule_update_preview())

        # 性别
        tk.Label(grid_basic, text="性别:", bg=self.bg, fg=self.fg).grid(row=1, column=2, sticky=tk.W, padx=(20,5), pady=5)
        gender_frame = tk.Frame(grid_basic, bg=self.bg)
        gender_frame.grid(row=1, column=3, columnspan=2, sticky=tk.W, pady=5)
        self.gender_var = tk.StringVar(value="随机")
        for g in ["随机", "男", "女", "不确定"]:
            rb = tk.Radiobutton(gender_frame, text=g, variable=self.gender_var, value=g,
                           bg=self.bg, fg=self.fg, selectcolor='#45475a',
                           activebackground=self.bg, command=self.app.schedule_update_preview)
            rb.pack(side=tk.LEFT, padx=2)

        # ===== 年龄设置 =====
        age_frame = tk.LabelFrame(basic_frame, text="年龄设置", bg=self.bg, fg=self.fg_bright,
                                   font=('Microsoft YaHei UI', 9, 'bold'))
        age_frame.pack(fill=tk.X, padx=10, pady=5)

        mode_frame = tk.Frame(age_frame, bg=self.bg)
        mode_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Label(mode_frame, text="年龄模式:", bg=self.bg, fg=self.fg).pack(side=tk.LEFT, padx=5)
        self.use_fixed_age = tk.BooleanVar(value=False)
        rb_fixed = tk.Radiobutton(mode_frame, text="固定年龄", variable=self.use_fixed_age,
                                   value=True, bg=self.bg, fg=self.fg, selectcolor='#45475a',
                                   command=self.toggle_age_mode)
        rb_fixed.pack(side=tk.LEFT, padx=10)
        rb_range = tk.Radiobutton(mode_frame, text="随机范围", variable=self.use_fixed_age,
                                   value=False, bg=self.bg, fg=self.fg, selectcolor='#45475a',
                                   command=self.toggle_age_mode)
        rb_range.pack(side=tk.LEFT, padx=10)

        self.fixed_age_frame = tk.Frame(age_frame, bg=self.bg)
        tk.Label(self.fixed_age_frame, text="固定年龄 (set_age):", bg=self.bg, fg=self.fg).pack(side=tk.LEFT, padx=5)
        self.adv_set_age = tk.IntVar(value=0)
        spin_set_age = tk.Spinbox(self.fixed_age_frame, from_=0, to=1000, textvariable=self.adv_set_age,
                                   bg=self.bg_entry, fg=self.fg, width=8)
        spin_set_age.pack(side=tk.LEFT, padx=5)
        spin_set_age.bind('<KeyRelease>', lambda e: self.app.schedule_update_preview())
        spin_set_age.bind('<<Increment>>', lambda e: self.app.schedule_update_preview())
        spin_set_age.bind('<<Decrement>>', lambda e: self.app.schedule_update_preview())
        tk.Label(self.fixed_age_frame, text="(0 表示不启用)", bg=self.bg, fg='#6c7086').pack(side=tk.LEFT, padx=5)

        self.range_age_frame = tk.Frame(age_frame, bg=self.bg)
        tk.Label(self.range_age_frame, text="最小年龄 (leader_age_min):", bg=self.bg, fg=self.fg).pack(side=tk.LEFT, padx=5)
        self.adv_age_min = tk.IntVar(value=25)
        spin_age_min = tk.Spinbox(self.range_age_frame, from_=0, to=1000, textvariable=self.adv_age_min,
                                   bg=self.bg_entry, fg=self.fg, width=8)
        spin_age_min.pack(side=tk.LEFT, padx=5)
        spin_age_min.bind('<KeyRelease>', lambda e: self.app.schedule_update_preview())
        spin_age_min.bind('<<Increment>>', lambda e: self.app.schedule_update_preview())
        spin_age_min.bind('<<Decrement>>', lambda e: self.app.schedule_update_preview())

        tk.Label(self.range_age_frame, text="最大年龄 (leader_age_max):", bg=self.bg, fg=self.fg).pack(side=tk.LEFT, padx=5)
        self.adv_age_max = tk.IntVar(value=60)
        spin_age_max = tk.Spinbox(self.range_age_frame, from_=0, to=1000, textvariable=self.adv_age_max,
                                   bg=self.bg_entry, fg=self.fg, width=8)
        spin_age_max.pack(side=tk.LEFT, padx=5)
        spin_age_max.bind('<KeyRelease>', lambda e: self.app.schedule_update_preview())
        spin_age_max.bind('<<Increment>>', lambda e: self.app.schedule_update_preview())
        spin_age_max.bind('<<Decrement>>', lambda e: self.app.schedule_update_preview())

        hide_frame = tk.Frame(age_frame, bg=self.bg)
        hide_frame.pack(fill=tk.X, padx=5, pady=5)
        self.adv_hide_age = tk.BooleanVar(value=False)
        tk.Checkbutton(hide_frame, text="隐藏年龄 (hide_age)", variable=self.adv_hide_age,
                       bg=self.bg, fg=self.fg, selectcolor='#45475a', command=self.app.schedule_update_preview
                       ).pack(side=tk.LEFT)

        self.toggle_age_mode()  # 初始化显示

        # 生成按钮
        btn_frame = tk.Frame(basic_frame, bg=self.bg)
        btn_frame.pack(fill=tk.X, pady=10)
        tk.Button(btn_frame, text="✨ 生成领袖", command=self.app.generate_and_copy,
                  bg=self.fg_bright, fg=self.bg, activebackground='#74c7ec',
                  font=('Microsoft YaHei UI', 10, 'bold'), padx=30, pady=5).pack()

        # ===== 高级设置框（滚动区域） =====
        advanced_main_frame = tk.LabelFrame(tab, text="高级设置", bg=self.bg, fg=self.fg_bright,
                                             font=('Microsoft YaHei UI', 10, 'bold'))
        advanced_main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建滚动 Canvas
        canvas = tk.Canvas(advanced_main_frame, bg=self.bg, highlightthickness=0)
        scrollbar = ttk.Scrollbar(advanced_main_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def _resize_scrollable_frame(event):
            canvas.itemconfig("all", width=event.width)
        canvas.bind('<Configure>', _resize_scrollable_frame)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 内部内容使用 grid 布局，两列
        scrollable_frame.grid_columnconfigure(0, weight=1)
        scrollable_frame.grid_columnconfigure(1, weight=1)

        row = 0

        # 特殊属性
        special_frame = tk.LabelFrame(scrollable_frame, text="特殊属性", bg=self.bg, fg=self.fg_bright,
                                      font=('Microsoft YaHei UI', 9, 'bold'))
        special_frame.grid(row=row, column=0, sticky=tk.EW, padx=5, pady=5, columnspan=2)
        row += 1

        self.immortal_var = tk.BooleanVar()
        tk.Checkbutton(special_frame, text="永生", variable=self.immortal_var,
                       bg=self.bg, fg=self.fg_red, selectcolor='#45475a',
                       command=self.app.schedule_update_preview).pack(side=tk.LEFT, padx=5)

        self.event_leader_var = tk.BooleanVar()
        tk.Checkbutton(special_frame, text="事件领袖", variable=self.event_leader_var,
                       bg=self.bg, fg=self.fg_orange, selectcolor='#45475a',
                       command=self.app.schedule_update_preview).pack(side=tk.LEFT, padx=5)

        # 自定义内容
        custom_frame = tk.LabelFrame(scrollable_frame, text="自定义内容", bg=self.bg, fg=self.fg_bright,
                                     font=('Microsoft YaHei UI', 9, 'bold'))
        custom_frame.grid(row=row, column=0, sticky=tk.EW, padx=5, pady=5, columnspan=2)
        row += 1

        tk.Label(custom_frame, text="自定义描述键 (custom_description):", bg=self.bg, fg=self.fg).pack(anchor=tk.W, padx=5, pady=2)
        self.adv_custom_desc = tk.StringVar(value="")
        entry_custom_desc = tk.Entry(custom_frame, textvariable=self.adv_custom_desc, bg=self.bg_entry, fg=self.fg,
                 insertbackground=self.fg, width=30)
        entry_custom_desc.pack(padx=5, pady=2, fill=tk.X)
        entry_custom_desc.bind('<KeyRelease>', lambda e: self.app.schedule_update_preview())

        tk.Label(custom_frame, text="自定义座右铭 (custom_catch_phrase):", bg=self.bg, fg=self.fg).pack(anchor=tk.W, padx=5, pady=2)
        self.adv_catch_phrase = tk.StringVar(value="")
        entry_catch = tk.Entry(custom_frame, textvariable=self.adv_catch_phrase, bg=self.bg_entry, fg=self.fg,
                 insertbackground=self.fg, width=30)
        entry_catch.pack(padx=5, pady=2, fill=tk.X)
        entry_catch.bind('<KeyRelease>', lambda e: self.app.schedule_update_preview())

        # 背景故事
        bg_frame = tk.LabelFrame(scrollable_frame, text="背景故事", bg=self.bg, fg=self.fg_bright,
                                 font=('Microsoft YaHei UI', 9, 'bold'))
        bg_frame.grid(row=row, column=0, sticky=tk.EW, padx=5, pady=5, columnspan=2)
        row += 1

        self.random_bg = tk.BooleanVar(value=True)
        tk.Checkbutton(bg_frame, text="随机生成背景", variable=self.random_bg,
                       bg=self.bg, fg=self.fg, selectcolor='#45475a',
                       command=self.app.schedule_update_preview).pack(anchor=tk.W, padx=5, pady=2)

        tk.Label(bg_frame, text="背景星球 (background_planet):", bg=self.bg, fg=self.fg).pack(anchor=tk.W, padx=5, pady=2)
        self.adv_bg_planet = tk.StringVar(value="")
        planet_combo = ttk.Combobox(bg_frame, textvariable=self.adv_bg_planet,
                                     values=["", "capital_planet", "event_target:homeworld", "from"],
                                     state="normal", width=30)
        planet_combo.pack(padx=5, pady=2, fill=tk.X)
        planet_combo.bind('<<ComboboxSelected>>', lambda e: self.app.schedule_update_preview())
        planet_combo.bind('<KeyRelease>', lambda e: self.app.schedule_update_preview())

        tk.Label(bg_frame, text="背景职业 (background_job):", bg=self.bg, fg=self.fg).pack(anchor=tk.W, padx=5, pady=2)
        self.adv_bg_job = tk.StringVar(value="")
        entry_bg_job = tk.Entry(bg_frame, textvariable=self.adv_bg_job, bg=self.bg_entry, fg=self.fg,
                 insertbackground=self.fg, width=30)
        entry_bg_job.pack(padx=5, pady=2, fill=tk.X)
        entry_bg_job.bind('<KeyRelease>', lambda e: self.app.schedule_update_preview())

        tk.Label(bg_frame, text="背景伦理 (background_ethic):", bg=self.bg, fg=self.fg).pack(anchor=tk.W, padx=5, pady=2)
        ethic_options = ["", "唯心主义", "唯物主义", "军国主义", "和平主义", "排外主义", "亲外主义",
                         "威权主义", "平等主义", "格式塔"]
        self.adv_bg_ethic = tk.StringVar(value="")
        ethic_combo = ttk.Combobox(bg_frame, textvariable=self.adv_bg_ethic,
                                    values=ethic_options, state="normal", width=30)
        ethic_combo.pack(padx=5, pady=2, fill=tk.X)
        ethic_combo.bind('<<ComboboxSelected>>', lambda e: self.app.schedule_update_preview())
        ethic_combo.bind('<KeyRelease>', lambda e: self.app.schedule_update_preview())

        # 权限控制
        perm_frame = tk.LabelFrame(scrollable_frame, text="权限控制", bg=self.bg, fg=self.fg_bright,
                                   font=('Microsoft YaHei UI', 9, 'bold'))
        perm_frame.grid(row=row, column=0, sticky=tk.EW, padx=5, pady=5, columnspan=2)
        row += 1

        self.adv_can_move = tk.BooleanVar(value=True)
        tk.Checkbutton(perm_frame, text="可手动改变位置 (can_manually_change_location)",
                       variable=self.adv_can_move, bg=self.bg, fg=self.fg, selectcolor='#45475a',
                       command=self.app.schedule_update_preview).pack(anchor=tk.W, padx=5, pady=2)

        self.adv_can_council = tk.BooleanVar(value=True)
        tk.Checkbutton(perm_frame, text="可指派到内阁 (can_assign_to_council)",
                       variable=self.adv_can_council, bg=self.bg, fg=self.fg, selectcolor='#45475a',
                       command=self.app.schedule_update_preview).pack(anchor=tk.W, padx=5, pady=2)

        self.adv_hide_leader = tk.BooleanVar(value=False)
        tk.Checkbutton(perm_frame, text="隐藏领袖 (hide_leader)",
                       variable=self.adv_hide_leader, bg=self.bg, fg=self.fg, selectcolor='#45475a',
                       command=self.app.schedule_update_preview).pack(anchor=tk.W, padx=5, pady=2)

        self.adv_use_regnal_name = tk.BooleanVar(value=False)
        tk.Checkbutton(perm_frame, text="使用统治名 (use_regnal_name)",
                       variable=self.adv_use_regnal_name, bg=self.bg, fg=self.fg, selectcolor='#45475a',
                       command=self.app.schedule_update_preview).pack(anchor=tk.W, padx=5, pady=2)

        # 级别
        tier_frame = tk.LabelFrame(scrollable_frame, text="级别", bg=self.bg, fg=self.fg_bright,
                                   font=('Microsoft YaHei UI', 9, 'bold'))
        tier_frame.grid(row=row, column=0, sticky=tk.EW, padx=5, pady=5, columnspan=2)
        row += 1

        self.leader_tier = tk.StringVar(value="")
        rb_tier_none = tk.Radiobutton(tier_frame, text="普通", variable=self.leader_tier,
                                       value="", bg=self.bg, fg=self.fg, selectcolor='#45475a',
                                       command=self.app.schedule_update_preview)
        rb_tier_none.pack(side=tk.LEFT, padx=5)
        rb_tier_renowned = tk.Radiobutton(tier_frame, text="著名", variable=self.leader_tier,
                                           value="renowned", bg=self.bg, fg=self.fg, selectcolor='#45475a',
                                           command=self.app.schedule_update_preview)
        rb_tier_renowned.pack(side=tk.LEFT, padx=5)
        rb_tier_legendary = tk.Radiobutton(tier_frame, text="传奇", variable=self.leader_tier,
                                            value="legendary", bg=self.bg, fg=self.fg, selectcolor='#45475a',
                                            command=self.app.schedule_update_preview)
        rb_tier_legendary.pack(side=tk.LEFT, padx=5)

        # 科学家子类型
        sub_frame = tk.LabelFrame(scrollable_frame, text="科学家子类型", bg=self.bg, fg=self.fg_bright,
                                  font=('Microsoft YaHei UI', 9, 'bold'))
        sub_frame.grid(row=row, column=0, sticky=tk.EW, padx=5, pady=5, columnspan=2)
        row += 1

        sub_types = ["", "physics", "society", "engineering", "psionics"]
        self.adv_sub_type = tk.StringVar(value="")
        adv_sub_combo = ttk.Combobox(sub_frame, textvariable=self.adv_sub_type,
                                      values=sub_types, state="readonly", width=15)
        adv_sub_combo.pack(padx=5, pady=2)
        adv_sub_combo.bind('<<ComboboxSelected>>', lambda e: self.app.schedule_update_preview())

        # 恢复默认按钮
        btn_frame = tk.Frame(scrollable_frame, bg=self.bg)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=10)
        row += 1
        tk.Button(btn_frame, text="恢复默认设置", command=self.app.reset_all_defaults,
                  bg=self.fg_orange, fg=self.bg, activebackground='#fab387', width=20).pack()

    def toggle_age_mode(self):
        if self.use_fixed_age.get():
            self.fixed_age_frame.pack(fill=tk.X, padx=5, pady=5)
            self.range_age_frame.pack_forget()
        else:
            self.fixed_age_frame.pack_forget()
            self.range_age_frame.pack(fill=tk.X, padx=5, pady=5)
        self.app.schedule_update_preview()

    # ---------- 特质选择页 ----------
    def create_trait_tab(self):
        tab = tk.Frame(self.notebook, bg=self.bg)
        self.notebook.add(tab, text="特质选择")

        # ===== 筛选条件 =====
        filter_frame = tk.LabelFrame(tab, text="筛选条件", bg=self.bg, fg=self.fg_bright,
                                      font=('Microsoft YaHei UI', 10, 'bold'))
        filter_frame.pack(fill=tk.X, padx=10, pady=(10,5))

        type_frame = tk.Frame(filter_frame, bg=self.bg)
        type_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(type_frame, text="领袖类型:", bg=self.bg, fg=self.fg).pack(side=tk.LEFT, padx=(0,5))
        self.filter_ruler = tk.BooleanVar()
        tk.Checkbutton(type_frame, text="行政官", variable=self.filter_ruler,
                       bg=self.bg, fg=self.fg, selectcolor='#45475a', command=self.app.schedule_filter_traits
                       ).pack(side=tk.LEFT, padx=2)
        self.filter_commander = tk.BooleanVar()
        tk.Checkbutton(type_frame, text="指挥官", variable=self.filter_commander,
                       bg=self.bg, fg=self.fg, selectcolor='#45475a', command=self.app.schedule_filter_traits
                       ).pack(side=tk.LEFT, padx=2)
        self.filter_scientist = tk.BooleanVar()
        tk.Checkbutton(type_frame, text="科学家", variable=self.filter_scientist,
                       bg=self.bg, fg=self.fg, selectcolor='#45475a', command=self.app.schedule_filter_traits
                       ).pack(side=tk.LEFT, padx=2)

        other_frame = tk.Frame(filter_frame, bg=self.bg)
        other_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(other_frame, text="其他:", bg=self.bg, fg=self.fg).pack(side=tk.LEFT, padx=(0,5))
        self.filter_council = tk.BooleanVar()
        tk.Checkbutton(other_frame, text="内阁", variable=self.filter_council,
                       bg=self.bg, fg=self.fg, selectcolor='#45475a', command=self.app.schedule_filter_traits
                       ).pack(side=tk.LEFT, padx=2)
        self.filter_governor = tk.BooleanVar()
        tk.Checkbutton(other_frame, text="总督", variable=self.filter_governor,
                       bg=self.bg, fg=self.fg, selectcolor='#45475a', command=self.app.schedule_filter_traits
                       ).pack(side=tk.LEFT, padx=2)
        self.filter_special = tk.BooleanVar()
        tk.Checkbutton(other_frame, text="特殊", variable=self.filter_special,
                       bg=self.bg, fg=self.fg, selectcolor='#45475a', command=self.app.schedule_filter_traits
                       ).pack(side=tk.LEFT, padx=2)

        row_frame = tk.Frame(filter_frame, bg=self.bg)
        row_frame.pack(fill=tk.X, padx=5, pady=2)

        tk.Label(row_frame, text="职业需求:", bg=self.bg, fg=self.fg).pack(side=tk.LEFT, padx=(0,5))
        self.profession_var = tk.StringVar(value="无")
        profession_combo = ttk.Combobox(row_frame, textvariable=self.profession_var,
                                         values=self.app.all_professions, state="readonly", width=15)
        profession_combo.pack(side=tk.LEFT, padx=(0,10))
        profession_combo.bind('<<ComboboxSelected>>', lambda e: self.app.schedule_filter_traits())

        tk.Label(row_frame, text="属性筛选:", bg=self.bg, fg=self.fg).pack(side=tk.LEFT, padx=(0,5))
        self.attr_var = tk.StringVar(value="全部")
        attr_combo = ttk.Combobox(row_frame, textvariable=self.attr_var,
                                   values=self.app.all_attributes, state="readonly", width=10)
        attr_combo.pack(side=tk.LEFT)
        attr_combo.bind('<<ComboboxSelected>>', lambda e: self.app.schedule_filter_traits())

        self.exclude_negative = tk.BooleanVar(value=False)
        tk.Checkbutton(row_frame, text="排除负面", variable=self.exclude_negative,
                       bg=self.bg, fg=self.fg, selectcolor='#45475a',
                       command=self.app.schedule_filter_traits).pack(side=tk.LEFT, padx=20)

        # 随机化未指定特质
        randomize_frame = tk.Frame(filter_frame, bg=self.bg)
        randomize_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(randomize_frame, text="随机化未指定特质:", bg=self.bg, fg=self.fg).pack(side=tk.LEFT, padx=(0,5))
        self.adv_randomize_traits = tk.BooleanVar(value=True)
        tk.Radiobutton(randomize_frame, text="是", variable=self.adv_randomize_traits,
                       value=True, bg=self.bg, fg=self.fg, selectcolor='#45475a',
                       command=self.app.schedule_update_preview).pack(side=tk.LEFT, padx=2)
        tk.Radiobutton(randomize_frame, text="否", variable=self.adv_randomize_traits,
                       value=False, bg=self.bg, fg=self.fg, selectcolor='#45475a',
                       command=self.app.schedule_update_preview).pack(side=tk.LEFT, padx=2)

        # 搜索框
        search_frame = tk.Frame(filter_frame, bg=self.bg)
        search_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(search_frame, text="搜索:", bg=self.bg, fg=self.fg).pack(side=tk.LEFT, padx=(0,5))
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, bg=self.bg_entry, fg=self.fg,
                 insertbackground=self.fg, width=20)
        search_entry.pack(side=tk.LEFT, padx=(0,10))
        search_entry.bind('<KeyRelease>', lambda e: self.app.schedule_filter_traits())

        self.search_by_var = tk.StringVar(value="名称")
        search_by_combo = ttk.Combobox(search_frame, textvariable=self.search_by_var,
                                       values=["名称", "序号", "效果"], state="readonly", width=8)
        search_by_combo.pack(side=tk.LEFT, padx=(0,10))
        search_by_combo.bind('<<ComboboxSelected>>', lambda e: self.app.schedule_filter_traits())

        tk.Button(search_frame, text="搜索", command=self.app.filter_traits,
                  bg=self.fg_bright, fg=self.bg, activebackground='#74c7ec',
                  font=('Microsoft YaHei UI', 9)).pack(side=tk.LEFT, padx=2)

        tk.Button(search_frame, text="全选", command=self.app.select_all_traits,
                  bg=self.fg_green, fg=self.bg, activebackground='#94e2d5',
                  font=('Microsoft YaHei UI', 9), width=6).pack(side=tk.LEFT, padx=5)

        # ===== 图标展示栏 =====
        icon_bar_container = tk.Frame(tab, bg=self.bg)
        icon_bar_container.pack(fill=tk.X, padx=10, pady=(5,0))

        tk.Label(icon_bar_container, text="已选特质图标 (点击可移除):", bg=self.bg, fg=self.fg_bright,
                 font=('Microsoft YaHei UI', 9)).pack(side=tk.LEFT, padx=(0,10))

        tk.Button(icon_bar_container, text="清除所有", command=self.app.clear_all_selected,
                  bg=self.fg_red, fg=self.bg, activebackground='#f38ba8',
                  font=('Microsoft YaHei UI', 9)).pack(side=tk.RIGHT, padx=5)

        icon_bar_scroll_container = tk.Frame(tab, bg=self.bg, height=30)
        icon_bar_scroll_container.pack(fill=tk.X, padx=10, pady=(0,5))
        icon_bar_scroll_container.pack_propagate(False)

        self.icon_bar_canvas = tk.Canvas(icon_bar_scroll_container, bg=self.bg, highlightthickness=0)
        self.icon_bar_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        icon_h_scroll = tk.Scrollbar(icon_bar_scroll_container, orient=tk.HORIZONTAL, command=self.icon_bar_canvas.xview)
        icon_h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.icon_bar_canvas.configure(xscrollcommand=icon_h_scroll.set)

        self.icon_bar_frame = tk.Frame(self.icon_bar_canvas, bg=self.bg)
        self.icon_bar_canvas.create_window((0,0), window=self.icon_bar_frame, anchor='nw')

        def on_frame_configure(e):
            self.icon_bar_canvas.configure(scrollregion=self.icon_bar_canvas.bbox('all'))
        self.icon_bar_frame.bind('<Configure>', on_frame_configure)

        def on_icon_bar_mousewheel(event):
            if event.delta:
                self.icon_bar_canvas.xview_scroll(-1 * (event.delta // 120), "units")
            elif event.num == 4:
                self.icon_bar_canvas.xview_scroll(-1, "units")
            elif event.num == 5:
                self.icon_bar_canvas.xview_scroll(1, "units")
        self.icon_bar_canvas.bind("<MouseWheel>", on_icon_bar_mousewheel)
        self.icon_bar_canvas.bind("<Button-4>", on_icon_bar_mousewheel)
        self.icon_bar_canvas.bind("<Button-5>", on_icon_bar_mousewheel)

        # ===== 特质列表 =====
        trait_frame = tk.Frame(tab, bg=self.bg)
        trait_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        tree_container = tk.Frame(trait_frame, bg=self.bg)
        tree_container.pack(fill=tk.BOTH, expand=True)

        columns = ('select', 'icon', 'number', 'name', 'code', 'effect')
        self.tree = ttk.Treeview(tree_container, columns=columns, show='tree headings',
                                  height=20, selectmode='extended')
        self.tree.heading('select', text='✔')
        self.tree.heading('icon', text='')
        self.tree.heading('number', text='序号')
        self.tree.heading('name', text='名称')
        self.tree.heading('code', text='代码')
        self.tree.heading('effect', text='效果')

        self.tree.column('select', width=40, anchor='center')
        self.tree.column('icon', width=30, anchor='center')
        self.tree.column('number', width=60, anchor='center')
        self.tree.column('name', width=200, anchor='w')
        self.tree.column('code', width=150, anchor='w')
        self.tree.column('effect', width=800, minwidth=400, anchor='w', stretch=True)

        style = ttk.Style()
        style.configure("Treeview",
                        background=self.tree_bg,
                        foreground=self.tree_fg,
                        fieldbackground=self.tree_bg,
                        selectbackground=self.tree_select_bg)
        style.map('Treeview', background=[('selected', self.tree_select_bg)])

        v_scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        h_scrollbar = ttk.Scrollbar(trait_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(xscrollcommand=h_scrollbar.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        h_scrollbar.pack(fill=tk.X, padx=5, pady=(0,5))

        self.tree.bind('<ButtonRelease-1>', self.on_tree_row_click)

    def on_tree_row_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region in ('cell', 'tree'):
            item = self.tree.identify_row(event.y)
            if item:
                shift_pressed = event.state & 0x0001
                self.app.toggle_trait_selection(item, shift_pressed)

    # ---------- 高级效果页 ----------
    def create_advanced_effect_tab(self):
        tab = tk.Frame(self.notebook, bg=self.bg)
        self.notebook.add(tab, text="高级效果")

        canvas = tk.Canvas(tab, bg=self.bg, highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        row = 0

        # 效果标志
        flag_frame = tk.LabelFrame(scrollable_frame, text="效果标志 (set_leader_flag)", bg=self.bg, fg=self.fg_bright,
                                    font=('Microsoft YaHei UI', 10, 'bold'))
        flag_frame.grid(row=row, column=0, sticky=tk.EW, padx=10, pady=5, columnspan=2)
        row += 1

        self.flag_immune = tk.BooleanVar(value=False)
        tk.Checkbutton(flag_frame, text="避免负面特质 (immune_to_negative_traits)",
                       variable=self.flag_immune, bg=self.bg, fg=self.fg, selectcolor='#45475a',
                       command=self.app.schedule_update_preview).pack(anchor=tk.W, padx=5, pady=2)

        self.flag_no_upkeep = tk.BooleanVar(value=False)
        tk.Checkbutton(flag_frame, text="无需维护费 (should_not_have_upkeep)",
                       variable=self.flag_no_upkeep, bg=self.bg, fg=self.fg, selectcolor='#45475a',
                       command=self.app.schedule_update_preview).pack(anchor=tk.W, padx=5, pady=2)

        # 先创领袖后改特质
        self.trait_frame = tk.LabelFrame(scrollable_frame, text="先创领袖后改特质", bg=self.bg, fg=self.fg_bright,
                                         font=('Microsoft YaHei UI', 10, 'bold'))
        self.trait_frame.grid(row=row, column=0, sticky=tk.EW, padx=10, pady=5, columnspan=2)
        row += 1

        self.change_trait_after_create = tk.BooleanVar(value=False)
        cb_change_trait = tk.Checkbutton(self.trait_frame, text="先创领袖后改特质",
                                         variable=self.change_trait_after_create,
                                         bg=self.bg, fg=self.fg, selectcolor='#45475a',
                                         command=lambda: (self.app.schedule_update_preview(),
                                                          self._update_trait_radio_state()))
        cb_change_trait.pack(anchor=tk.W, padx=5, pady=2)

        self.trait_action = tk.StringVar(value="")
        rb_trait_add = tk.Radiobutton(self.trait_frame, text="加特质 add_trait", variable=self.trait_action,
                                      value="add_trait", bg=self.bg, fg=self.fg, selectcolor='#45475a',
                                      command=self.app.schedule_update_preview)
        rb_trait_add.pack(anchor=tk.W, padx=20, pady=2)
        rb_trait_remove = tk.Radiobutton(self.trait_frame, text="减特质 remove_trait", variable=self.trait_action,
                                         value="remove_trait", bg=self.bg, fg=self.fg, selectcolor='#45475a',
                                         command=self.app.schedule_update_preview)
        rb_trait_remove.pack(anchor=tk.W, padx=20, pady=2)

        self._update_trait_radio_state()

        # 品质选择
        quality_frame = tk.LabelFrame(scrollable_frame, text="领袖品质", bg=self.bg, fg=self.fg_bright,
                                      font=('Microsoft YaHei UI', 10, 'bold'))
        quality_frame.grid(row=row, column=0, sticky=tk.EW, padx=10, pady=5, columnspan=2)
        row += 1

        self.flag_quality = tk.StringVar(value="")
        tk.Radiobutton(quality_frame, text="无", variable=self.flag_quality,
                       value="", bg=self.bg, fg=self.fg, selectcolor='#45475a',
                       command=self.app.schedule_update_preview).pack(anchor=tk.W, padx=5, pady=2)
        tk.Radiobutton(quality_frame, text="著名领袖 (renowned_leader)",
                       variable=self.flag_quality, value="renowned_leader",
                       bg=self.bg, fg=self.fg, selectcolor='#45475a',
                       command=self.app.schedule_update_preview).pack(anchor=tk.W, padx=5, pady=2)
        tk.Radiobutton(quality_frame, text="传奇领袖 (legendary_leader)",
                       variable=self.flag_quality, value="legendary_leader",
                       bg=self.bg, fg=self.fg, selectcolor='#45475a',
                       command=self.app.schedule_update_preview).pack(anchor=tk.W, padx=5, pady=2)

        # 自定义效果代码文本框
        effect_frame = tk.LabelFrame(scrollable_frame, text="自定义效果代码 (可手动编辑)", bg=self.bg, fg=self.fg_bright,
                                     font=('Microsoft YaHei UI', 10, 'bold'))
        effect_frame.grid(row=row, column=0, sticky=tk.EW, padx=10, pady=5, columnspan=2)
        effect_frame.columnconfigure(0, weight=1)
        row += 1

        self.adv_effect_text = tk.Text(effect_frame, bg=self.bg_entry, fg=self.fg,
                                        insertbackground=self.fg, height=10,
                                        font=('Consolas', 9))
        self.adv_effect_text.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        self.adv_effect_text.bind('<KeyRelease>', lambda e: self.app.schedule_update_preview())

    def _update_trait_radio_state(self):
        state = tk.NORMAL if self.change_trait_after_create.get() else tk.DISABLED
        for child in self.trait_frame.winfo_children():
            if isinstance(child, tk.Radiobutton):
                child.config(state=state)
        if not self.change_trait_after_create.get():
            self.trait_action.set("")

    # ---------- 预设领袖页 ----------
    def create_preset_tab(self):
        tab = tk.Frame(self.notebook, bg=self.bg)
        self.notebook.add(tab, text="预设领袖")

        left_frame = tk.Frame(tab, bg=self.bg, width=200)
        middle_frame = tk.Frame(tab, bg=self.bg, width=200)
        right_frame = tk.Frame(tab, bg=self.bg)

        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(10,5), pady=10)
        middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=10)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5,10), pady=10)

        left_frame.pack_propagate(False)
        middle_frame.pack_propagate(False)

        # 左侧：内置预设
        tk.Label(left_frame, text="预设（内置）", bg=self.bg, fg=self.fg_bright,
                 font=('Microsoft YaHei UI', 10, 'bold')).pack(anchor=tk.W)

        list_frame_left = tk.Frame(left_frame, bg=self.bg)
        list_frame_left.pack(fill=tk.BOTH, expand=True)

        self.preset_listbox = tk.Listbox(list_frame_left, bg=self.bg_entry, fg=self.fg,
                                          selectbackground=self.select_bg, selectforeground=self.select_fg,
                                          font=('Microsoft YaHei UI', 9))
        self.preset_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll_left = tk.Scrollbar(list_frame_left, orient=tk.VERTICAL, command=self.preset_listbox.yview)
        scroll_left.pack(side=tk.RIGHT, fill=tk.Y)
        self.preset_listbox.config(yscrollcommand=scroll_left.set)

        # 中间：加载列表
        tk.Label(middle_frame, text="加载列表", bg=self.bg, fg=self.fg_bright,
                 font=('Microsoft YaHei UI', 10, 'bold')).pack(anchor=tk.W)

        list_frame_mid = tk.Frame(middle_frame, bg=self.bg)
        list_frame_mid.pack(fill=tk.BOTH, expand=True)

        self.load_listbox = tk.Listbox(list_frame_mid, bg=self.bg_entry, fg=self.fg,
                                        selectbackground=self.select_bg, selectforeground=self.select_fg,
                                        font=('Microsoft YaHei UI', 9))
        self.load_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll_mid = tk.Scrollbar(list_frame_mid, orient=tk.VERTICAL, command=self.load_listbox.yview)
        scroll_mid.pack(side=tk.RIGHT, fill=tk.Y)
        self.load_listbox.config(yscrollcommand=scroll_mid.set)

        btn_frame_mid = tk.Frame(middle_frame, bg=self.bg)
        btn_frame_mid.pack(fill=tk.X, pady=5)
        tk.Button(btn_frame_mid, text="复制打开文件", command=self.app.copy_file_to_presets,
                  bg=self.fg_bright, fg=self.bg, activebackground='#74c7ec',
                  width=12).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame_mid, text="刷新", command=self.app.refresh_load_list,
                  bg=self.fg_green, fg=self.bg, activebackground='#94e2d5',
                  width=8).pack(side=tk.LEFT, padx=2)

        # 右侧：信息预览
        tk.Label(right_frame, text="当前配置", bg=self.bg, fg=self.fg_bright,
                 font=('Microsoft YaHei UI', 10, 'bold')).pack(anchor=tk.W)

        info_frame = tk.Frame(right_frame, bg=self.bg)
        info_frame.pack(fill=tk.BOTH, expand=True)

        self.preset_info_text = tk.Text(info_frame, bg=self.bg_entry, fg=self.fg,
                                         insertbackground=self.fg, font=('Consolas', 9),
                                         wrap=tk.WORD)
        self.preset_info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll_right = tk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.preset_info_text.yview)
        scroll_right.pack(side=tk.RIGHT, fill=tk.Y)
        self.preset_info_text.config(yscrollcommand=scroll_right.set)

    # ---------- 代码预览页 ----------
    def create_preview_tab(self):
        tab = tk.Frame(self.notebook, bg=self.bg)
        self.notebook.add(tab, text="代码预览")

        self.code_text = tk.Text(tab, bg=self.bg_entry, fg=self.fg,
                                  insertbackground=self.fg, font=('Consolas', 10), wrap=tk.WORD)
        self.code_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.code_text.tag_configure("keyword", foreground=self.fg_red)
        self.code_text.tag_configure("string", foreground=self.fg_green)
        self.code_text.tag_configure("number", foreground=self.fg_orange)
        self.code_text.tag_configure("comment", foreground="#6c7086")
        self.code_text.tag_configure("boolean", foreground=self.fg_purple)

        btn_frame = tk.Frame(tab, bg=self.bg)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0,10))
        tk.Button(btn_frame, text="📋 复制代码", command=self.app.copy_code,
                  bg=self.fg_bright, fg=self.bg, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="💾 保存到文件", command=self.app.save_code,
                  bg=self.fg_green, fg=self.bg, width=12).pack(side=tk.LEFT, padx=5)

        export_frame = tk.Frame(tab, bg=self.bg)
        export_frame.pack(fill=tk.X, padx=10, pady=(0,10))
        tk.Label(export_frame, text="预设名称:", bg=self.bg, fg=self.fg).pack(side=tk.LEFT, padx=(0,5))
        self.export_name_entry = tk.Entry(export_frame, bg=self.bg_entry, fg=self.fg,
                                           insertbackground=self.fg, width=20)
        self.export_name_entry.pack(side=tk.LEFT, padx=(0,10))
        tk.Button(export_frame, text="📤 导出为预设领袖", command=self.app.export_as_preset,
                  bg=self.fg_orange, fg=self.bg, width=18).pack(side=tk.LEFT, padx=5)

    # ---------- 转化为指令页 ----------
    def create_transform_tab(self):
        tab = tk.Frame(self.notebook, bg=self.bg)
        self.notebook.add(tab, text="转化为指令")

        self.transform_text = tk.Text(tab, bg=self.bg_entry, fg=self.fg,
                                       insertbackground=self.fg, font=('Consolas', 10), wrap=tk.WORD)
        self.transform_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        btn_frame = tk.Frame(tab, bg=self.bg)
        btn_frame.pack(fill=tk.X, padx=10, pady=(0,10))

        tk.Button(btn_frame, text="🔄 转化指令", command=self.app.transform_command,
                  bg=self.fg_bright, fg=self.bg, width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="📋 复制代码", command=self.app.copy_transform_code,
                  bg=self.fg_green, fg=self.bg, width=15).pack(side=tk.LEFT, padx=5)

    # ---------- 状态栏 ----------
    def create_status_bar(self):
        self.status_bar = tk.Label(self.main_container, text="就绪 | 生成器 v6.3",
                                    bg=self.bg_dark, fg='#bac2de', anchor=tk.W,
                                    font=('Microsoft YaHei UI', 8))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=1, pady=1)