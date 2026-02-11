# Test

一个用于测试的小仓库，当前包含 Python GUI 工具：`chinese_extractor_gui.py`。

## 功能
- 支持上传 `.txt` 文件（也可直接粘贴文本）
- 提取每段“序号.正文”中的中文内容
- 去掉序号
- 去掉中英文括号里的内容（例如英文镜头描述）
- 保留中文标点
- 自动将所有段落拼接为一整段文本
- 支持简繁互转（繁体→简体 / 简体→繁体）
  - 优先 `opencc`
  - 其次 `hanziconv`
- 支持导出 `.txt`
- 黑蓝主题界面

## 运行
```bash
python3 chinese_extractor_gui.py
```
