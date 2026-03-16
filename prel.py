#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
预设管理模块 - 处理内置预设、预设文件解析、文件列表等
"""

import os
import re

class PresetManager:
    """封装预设文件的读取、解析、内置预设生成等功能"""

    def __init__(self, presets_dir):
        """
        :param presets_dir: 预设文件存放的目录（例如 momodata/presets）
        """
        self.presets_dir = presets_dir
        os.makedirs(self.presets_dir, exist_ok=True)
        self._ensure_builtin_preset()

    # ---------- 内置预设数据 ----------
    @staticmethod
    def get_builtin_presets():
        """返回内置预设列表，每个元素为 (名称, 代码)"""
        return [
            ('🌟 标准科学家', '''create_leader = {
    name = "Dr. Aris"
    class = scientist
    skill = 5
    gender = female
    traits = {
        1 = leader_trait_maniacal
        1 = leader_trait_carefree
        1 = leader_trait_archaeologist
    }
    sub_type = physics
}'''),
            ('⚔️ 舰队司令', '''create_leader = {
    name = "Admiral Zhao"
    class = commander
    skill = 4
    gender = male
    traits = {
        1 = leader_trait_aggressive
        1 = leader_trait_engineer
        1 = leader_trait_unyielding
    }
}'''),
            ('🛡️ 陆军将军', '''create_leader = {
    name = "General Stone"
    class = commander
    skill = 4
    gender = male
    traits = {
        1 = leader_trait_butcher
        1 = leader_trait_dreaded
        1 = leader_trait_heavy_hitter
    }
}'''),
            ('🏛️ 卓越总督', '''create_leader = {
    name = "Governor Vex"
    class = ruler
    skill = 4
    gender = female
    traits = {
        1 = leader_trait_capitalist
        1 = leader_trait_private_mines
        1 = leader_trait_settler
    }
}'''),
            ('🔮 灵能导师', '''create_leader = {
    name = "Oracle"
    class = scientist
    skill = 5
    gender = female
    traits = {
        1 = leader_trait_psionic
        1 = leader_trait_maniacal
        1 = leader_trait_spark_of_genius
    }
    sub_type = psionics
}'''),
            ('🤖 机械领袖', '''create_leader = {
    name = "Unit-01"
    class = ruler
    skill = 4
    gender = random
    traits = {
        1 = leader_trait_robotist
        1 = leader_trait_assembler
        1 = leader_trait_synthetic
    }
    immortal = yes
}'''),
            ('👑 天才统治者', '''create_leader = {
    name = "Emperor"
    class = ruler
    skill = 5
    gender = male
    traits = {
        1 = trait_ruler_charismatic
        1 = trait_ruler_eye_for_talent
        1 = leader_trait_legendary_high_king
    }
}'''),
            ('🧬 克隆大军指挥官', '''create_leader = {
    name = "Clone Commander"
    class = commander
    skill = 4
    gender = male
    traits = {
        1 = leader_trait_clone_army_commander
        1 = leader_trait_aggressive
    }
}'''),
        ]

    # ---------- 内置预设文件创建 ----------
    def _ensure_builtin_preset(self):
        """确保 .builtin.txt 文件存在，若不存在则创建"""
        builtin_path = os.path.join(self.presets_dir, '.builtin.txt')
        if not os.path.exists(builtin_path):
            with open(builtin_path, 'w', encoding='utf-8') as f:
                for name, code in self.get_builtin_presets():
                    f.write(f'#$button{name}\n')
                    f.write(code)
                    f.write('\n\n')
            print("[预设] 已创建内置预设文件 .builtin.txt")

    # ---------- 单个预设文件解析 ----------
    @staticmethod
    def parse_preset_file(filepath):
        """
        解析一个预设文件（格式：以 #$button 开头的块）
        返回 [(名称, 代码), ...]
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        presets = []
        lines = content.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith('#$button'):
                button_name = line[8:].strip()
                i += 1
                code_lines = []
                brace_count = 0
                start_collecting = False
                while i < len(lines):
                    current_line = lines[i]
                    stripped = current_line.strip()
                    if stripped.startswith('#$button'):
                        break
                    if not start_collecting and re.search(r'create_leader\s*=\s*\{', current_line):
                        start_collecting = True
                    if start_collecting:
                        code_lines.append(current_line)
                        brace_count += current_line.count('{') - current_line.count('}')
                        if brace_count == 0 and start_collecting:
                            break
                    i += 1
                if code_lines:
                    code = '\n'.join(code_lines)
                    presets.append((button_name, code))
            else:
                i += 1
        return presets

    # ---------- 从文件加载所有预设 ----------
    def load_all_presets_from_file(self, filepath):
        """加载指定文件中的所有预设，失败时返回空列表"""
        if os.path.exists(filepath):
            try:
                return self.parse_preset_file(filepath)
            except Exception:
                return []
        return []

    # ---------- 获取预设文件列表 ----------
    def get_hidden_preset_files(self):
        """返回所有以 . 开头的预设文件（内置预设）的完整路径列表"""
        files = []
        for f in os.listdir(self.presets_dir):
            if f.startswith('.') and f.endswith('.txt'):
                files.append(os.path.join(self.presets_dir, f))
        return files

    def get_visible_preset_files(self):
        """返回所有不以 . 开头的预设文件（用户文件）的完整路径列表"""
        files = []
        for f in os.listdir(self.presets_dir):
            if not f.startswith('.') and f.endswith('.txt'):
                files.append(os.path.join(self.presets_dir, f))
        return files

    # ---------- 复制文件内容到用户预设文件 ----------
    def copy_to_preset_file(self, src_path, dest_filename='.user_presets.txt'):
        """
        将指定文件的内容追加到用户预设文件（默认为 .user_presets.txt）
        如果目标文件不存在，则自动创建。
        """
        dest_path = os.path.join(self.presets_dir, dest_filename)
        with open(src_path, 'r', encoding='utf-8') as f_src:
            content = f_src.read()
        with open(dest_path, 'a', encoding='utf-8') as f_dest:
            f_dest.write('\n')
            f_dest.write(content)
        return dest_path