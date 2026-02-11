#!/usr/bin/env python3
"""提取带序号段落中的中文文本并导出为 TXT 的图形工具。"""

from __future__ import annotations

import re
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext


def convert_chinese(text: str, mode: str = "t2s") -> str:
    """简繁转换：mode=t2s(繁->简) 或 s2t(简->繁)，无依赖时原样返回。"""
    try:
        from opencc import OpenCC  # type: ignore

        return OpenCC(mode).convert(text)
    except Exception:
        pass

    try:
        from hanziconv import HanziConv  # type: ignore

        if mode == "t2s":
            return HanziConv.toSimplified(text)
        if mode == "s2t":
            return HanziConv.toTraditional(text)
        return text
    except Exception:
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

        # 去掉“序号.正文”样式中的序号
        line = re.sub(r"^\s*\d+\s*[\.、]\s*", "", line)

        # 去除括号内容（中英文括号都支持）
        line = re.sub(r"\([^)]*\)", "", line)
        line = re.sub(r"（[^）]*）", "", line)

        # 保留中文、中文标点、英文数字（避免 AI/20 被截断）
        filtered = re.findall(r"[\u4e00-\u9fffA-Za-z0-9，。！？；：、“”‘’《》【】（）—…·\s]+", line)
        text = "".join(filtered).strip()

        if text:
            result_parts.append(text)

    return "".join(result_parts)


class ExtractorApp:
    BG = "#0b1220"
    PANEL = "#111a2b"
    FG = "#dbeafe"
    ACCENT = "#2563eb"
    INPUT_BG = "#0f172a"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("中文提取 + 简繁转换工具")
        self.root.geometry("960x720")
        self.root.configure(bg=self.BG)

        self.convert_mode = tk.StringVar(value="t2s")

        title = tk.Label(
            root,
            text="上传 / 粘贴文本后，提取序号后中文并导出 TXT",
            font=("Microsoft YaHei", 14, "bold"),
            bg=self.BG,
            fg=self.FG,
        )
        title.pack(pady=10)

        top_frame = tk.Frame(root, bg=self.BG)
        top_frame.pack(fill="x", padx=12)

        load_btn = tk.Button(
            top_frame,
            text="上传 TXT",
            command=self.load_txt,
            bg=self.ACCENT,
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            relief=tk.FLAT,
            padx=10,
            pady=5,
        )
        load_btn.pack(side="left")

        mode_frame = tk.Frame(top_frame, bg=self.BG)
        mode_frame.pack(side="left", padx=16)
        tk.Label(mode_frame, text="转换方向：", bg=self.BG, fg=self.FG).pack(side="left")
        tk.Radiobutton(
            mode_frame,
            text="繁体→简体",
            variable=self.convert_mode,
            value="t2s",
            bg=self.BG,
            fg=self.FG,
            selectcolor=self.PANEL,
            activebackground=self.BG,
            activeforeground=self.FG,
        ).pack(side="left")
        tk.Radiobutton(
            mode_frame,
            text="简体→繁体",
            variable=self.convert_mode,
            value="s2t",
            bg=self.BG,
            fg=self.FG,
            selectcolor=self.PANEL,
            activebackground=self.BG,
            activeforeground=self.FG,
        ).pack(side="left")

        input_label = tk.Label(root, text="输入原始文本：", anchor="w", bg=self.BG, fg=self.FG)
        input_label.pack(fill="x", padx=12, pady=(10, 0))

        self.input_text = scrolledtext.ScrolledText(
            root,
            wrap=tk.WORD,
            height=15,
            bg=self.INPUT_BG,
            fg=self.FG,
            insertbackground=self.FG,
            relief=tk.FLAT,
        )
        self.input_text.pack(fill="both", expand=True, padx=12, pady=6)

        button_frame = tk.Frame(root, bg=self.BG)
        button_frame.pack(fill="x", padx=12, pady=6)

        extract_btn = tk.Button(
            button_frame,
            text="提取并转换",
            command=self.extract,
            bg=self.ACCENT,
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            relief=tk.FLAT,
            padx=10,
            pady=5,
        )
        extract_btn.pack(side="left")

        save_btn = tk.Button(
            button_frame,
            text="导出 TXT",
            command=self.save_txt,
            bg="#1e293b",
            fg=self.FG,
            activebackground="#334155",
            activeforeground=self.FG,
            relief=tk.FLAT,
            padx=10,
            pady=5,
        )
        save_btn.pack(side="left", padx=8)

        clear_btn = tk.Button(
            button_frame,
            text="清空",
            command=self.clear,
            bg="#1e293b",
            fg=self.FG,
            activebackground="#334155",
            activeforeground=self.FG,
            relief=tk.FLAT,
            padx=10,
            pady=5,
        )
        clear_btn.pack(side="left")

        output_label = tk.Label(root, text="输出结果：", anchor="w", bg=self.BG, fg=self.FG)
        output_label.pack(fill="x", padx=12)

        self.output_text = scrolledtext.ScrolledText(
            root,
            wrap=tk.WORD,
            height=12,
            bg=self.INPUT_BG,
            fg=self.FG,
            insertbackground=self.FG,
            relief=tk.FLAT,
        )
        self.output_text.pack(fill="both", expand=True, padx=12, pady=(6, 12))

        hint = (
            "说明：支持可变段落数量；自动去序号与括号内容；保留中文标点；"
            "可选择繁转简或简转繁。"
        )
        tk.Label(root, text=hint, fg="#93c5fd", bg=self.BG).pack(fill="x", padx=12, pady=(0, 8))

    def load_txt(self) -> None:
        path = filedialog.askopenfilename(
            title="选择 TXT 文件",
            filetypes=[("Text File", "*.txt"), ("All Files", "*.*")],
        )
        if not path:
            return

        content = Path(path).read_text(encoding="utf-8", errors="ignore")
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert(tk.END, content)

    def extract(self) -> None:
        raw = self.input_text.get("1.0", tk.END)
        extracted = extract_chinese_text(raw)
        result = convert_chinese(extracted, self.convert_mode.get())

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
