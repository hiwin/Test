#!/usr/bin/env python3
"""提取带序号段落中的中文文本并导出为 TXT 的图形工具。"""

from __future__ import annotations

import re
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext


def to_simplified(text: str) -> str:
    """将文本尽可能转换为简体中文（优先 OpenCC，其次 HanziConv）。"""
    try:
        from opencc import OpenCC  # type: ignore

        return OpenCC("t2s").convert(text)
    except Exception:
        pass

    try:
        from hanziconv import HanziConv  # type: ignore

        return HanziConv.toSimplified(text)
    except Exception:
        # 环境中没有简繁转换库时，回退为原文。
        return text


def extract_chinese_text(raw_text: str) -> str:
    """提取每段序号后的中文，去除英文括号段并拼接。"""
    if not raw_text.strip():
        return ""

    lines = [line.strip() for line in raw_text.splitlines()]
    result_parts: list[str] = []

    for line in lines:
        if not line:
            continue

        # 跳过纯括号英文描述行，例如 (camera, ...)
        if re.fullmatch(r"\([^\u4e00-\u9fff]*\)", line):
            continue

        # 仅处理“序号.正文”样式，自动去掉序号
        line = re.sub(r"^\s*\d+\s*[\.、]\s*", "", line)

        # 去除括号内容（中英文括号都支持）
        line = re.sub(r"\([^)]*\)", "", line)
        line = re.sub(r"（[^）]*）", "", line)

        # 保留中文、中文标点及常见空白
        filtered = re.findall(r"[\u4e00-\u9fffA-Za-z0-9，。！？；：、“”‘’《》【】（）—…·\s]+", line)
        text = "".join(filtered).strip()

        if text:
            result_parts.append(text)

    merged = "".join(result_parts)
    return to_simplified(merged)


class ExtractorApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("中文提取并转简体工具")
        self.root.geometry("900x680")

        title = tk.Label(
            root,
            text="粘贴原文后，提取序号后中文并导出 TXT",
            font=("Microsoft YaHei", 14, "bold"),
        )
        title.pack(pady=8)

        input_label = tk.Label(root, text="输入原始文本：", anchor="w")
        input_label.pack(fill="x", padx=12)

        self.input_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=16)
        self.input_text.pack(fill="both", expand=True, padx=12, pady=6)

        button_frame = tk.Frame(root)
        button_frame.pack(fill="x", padx=12, pady=6)

        extract_btn = tk.Button(button_frame, text="提取并转换", command=self.extract)
        extract_btn.pack(side="left")

        save_btn = tk.Button(button_frame, text="导出 TXT", command=self.save_txt)
        save_btn.pack(side="left", padx=8)

        clear_btn = tk.Button(button_frame, text="清空", command=self.clear)
        clear_btn.pack(side="left")

        output_label = tk.Label(root, text="输出结果：", anchor="w")
        output_label.pack(fill="x", padx=12)

        self.output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=12)
        self.output_text.pack(fill="both", expand=True, padx=12, pady=(6, 12))

        hint = (
            "说明：支持多段不同序号。会自动去掉序号和括号内容，保留中文标点，"
            "并将所有段落连贯拼接。"
        )
        tk.Label(root, text=hint, fg="#666").pack(fill="x", padx=12, pady=(0, 8))

    def extract(self) -> None:
        raw = self.input_text.get("1.0", tk.END)
        result = extract_chinese_text(raw)

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, result)

        if not result:
            messagebox.showwarning("提示", "未提取到有效中文内容，请检查输入格式。")

    def save_txt(self) -> None:
        content = self.output_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("提示", "请先提取结果后再导出。")
            return

        path = filedialog.asksaveasfilename(
            title="保存 TXT",
            defaultextension=".txt",
            filetypes=[("Text File", "*.txt"), ("All Files", "*.*")],
            initialfile="提取结果.txt",
        )
        if not path:
            return

        Path(path).write_text(content, encoding="utf-8")
        messagebox.showinfo("成功", f"已导出：{path}")

    def clear(self) -> None:
        self.input_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)


def main() -> None:
    root = tk.Tk()
    app = ExtractorApp(root)
    _ = app
    root.mainloop()


if __name__ == "__main__":
    main()
