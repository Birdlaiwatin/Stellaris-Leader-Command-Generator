import re

def remove_comments_and_format_block(block_lines: list[str]) -> str:
    """
    处理单个顶级块（通常是一个 effect / modifier / trigger 等）
    去注释 → 保护字符串 → 压缩为单行 → 规范空格
    """
    processed_lines = []
    str_counter = 0
    str_map = {}

    for line in block_lines:
        # 1. 移除注释
        line = re.split(r'\s*#', line, 1)[0].rstrip()
        if not line.strip():
            continue

        # 2. 保护字符串
        def protect_str(match):
            nonlocal str_counter
            placeholder = f"__STR_{str_counter}__"
            str_map[placeholder] = match.group(0)
            str_counter += 1
            return placeholder

        # 先处理双引号字符串
        line = re.sub(r'"([^"\\]*(?:\\.[^"\\]*)*)"', protect_str, line)
        # 再处理单引号字符串
        line = re.sub(r"'([^'\\]*(?:\\.[^'\\]*)*)'", protect_str, line)
        
        processed_lines.append(line)

    if not processed_lines:
        return ""

    # 3. 合并成单行
    result = ' '.join(processed_lines)

    # 4. 保护带下划线的长标识符
    identifiers = set(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', result))
    underscore_protected = {}
    for i, word in enumerate(identifiers):
        if '_' in word and word not in str_map.values():
            placeholder = f"__ID_{i}__"
            underscore_protected[placeholder] = word
            result = result.replace(word, placeholder)

    # 5. 规范空格
    result = re.sub(r'\s+', ' ', result)
    result = re.sub(r'\s*([=<>!]=?|\+=|-=|\*=|/=|==|!=|>=|<=|>|<)\s*', r' \1 ', result)
    result = re.sub(r'\s*([{}[\](),;])\s*', r'\1 ', result)
    result = re.sub(r'\s+', ' ', result)  # 再次压缩空格

    # 6. 恢复标识符
    for ph, original in underscore_protected.items():
        result = result.replace(ph, original)

    # 7. 恢复字符串
    for ph, original in str_map.items():
        result = result.replace(ph, original)

    return result.strip()


def format_stellaris_script(text: str) -> str:
    """
    主处理函数：按顶级块分割 → 分别格式化 → 用单个换行符连接
    改进：通过跟踪花括号正确识别块边界
    """
    lines = text.splitlines()
    blocks = []
    current_block = []
    brace_depth = 0
    in_block = False
    
    for line in lines:
        stripped = line.strip()
        
        # 跳过纯注释行
        if stripped.startswith('#'):
            continue
            
        # 如果这是空行
        if not stripped:
            # 如果在块中，添加到当前块
            if in_block and current_block:
                current_block.append('')
            continue
        
        # 分析行中的花括号
        open_braces = line.count('{')
        close_braces = line.count('}')
        
        # 更新花括号深度
        if not in_block and open_braces > 0:
            in_block = True
            brace_depth = open_braces - close_braces
        else:
            brace_depth += open_braces - close_braces
        
        # 将行添加到当前块
        current_block.append(line)
        
        # 如果花括号深度为0，表示当前块结束
        if in_block and brace_depth <= 0:
            # 处理并添加当前块
            formatted = remove_comments_and_format_block(current_block)
            if formatted:
                blocks.append(formatted)
            # 重置状态
            current_block = []
            in_block = False
            brace_depth = 0
    
    # 处理最后一个块（如果存在）
    if current_block:
        formatted = remove_comments_and_format_block(current_block)
        if formatted:
            blocks.append(formatted)
    
    # 用单个换行符连接所有格式化后的块
    return '\n'.join(block for block in blocks if block)
