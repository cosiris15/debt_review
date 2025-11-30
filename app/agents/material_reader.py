"""
Material Reading Utilities

Reads debt claim materials from file system and prepares them for LLM prompts.
Handles different file sizes with appropriate strategies.
"""

from pathlib import Path
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

# Token 预算常量
# DeepSeek 支持 64K context，复杂金融案例需要更大预算
# 设置为50K tokens，留约14K给prompt和输出
MAX_MATERIAL_TOKENS = 50000
CHARS_PER_TOKEN = 1.5  # 中文约 1.5 字符/token


async def read_materials(materials_path: str) -> Tuple[str, Dict[str, Any]]:
    """
    读取材料文件内容。

    Args:
        materials_path: 材料文件或目录路径

    Returns:
        Tuple[材料内容文本, 元数据字典]
    """
    path = Path(materials_path)

    if not path.exists():
        logger.warning(f"材料路径不存在: {materials_path}")
        return "", {"error": "材料文件不存在", "path": materials_path}

    if path.is_file():
        return await _read_single_file(path)
    elif path.is_dir():
        return await _read_directory(path)
    else:
        return "", {"error": "不支持的路径类型", "path": materials_path}


async def _read_single_file(file_path: Path) -> Tuple[str, Dict[str, Any]]:
    """读取单个文件"""
    import asyncio

    def _read():
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content

    try:
        content = await asyncio.to_thread(_read)
    except UnicodeDecodeError:
        # 尝试其他编码
        def _read_gbk():
            with open(file_path, 'r', encoding='gbk') as f:
                return f.read()
        try:
            content = await asyncio.to_thread(_read_gbk)
        except Exception as e:
            logger.error(f"文件读取失败: {file_path}, 错误: {e}")
            return "", {"error": f"文件编码错误: {e}", "path": str(file_path)}

    metadata = {
        "file_name": file_path.name,
        "file_size": len(content),
        "estimated_tokens": len(content) / CHARS_PER_TOKEN,
        "strategy": "full_read"
    }

    # 检查是否超过 token 预算
    if metadata["estimated_tokens"] > MAX_MATERIAL_TOKENS:
        logger.warning(f"材料过大 ({metadata['estimated_tokens']:.0f} tokens)，需要截断处理")
        metadata["strategy"] = "truncated"
        # 截断到预算范围内
        max_chars = int(MAX_MATERIAL_TOKENS * CHARS_PER_TOKEN)
        content = content[:max_chars] + "\n\n[材料过长，已截断...]"

    return content, metadata


async def _read_directory(dir_path: Path) -> Tuple[str, Dict[str, Any]]:
    """读取目录下所有材料文件"""
    # 支持的文件类型
    supported_extensions = {'.md', '.txt', '.json'}

    files = [f for f in dir_path.iterdir()
             if f.is_file() and f.suffix.lower() in supported_extensions]

    if not files:
        return "", {"error": "目录中没有找到支持的材料文件", "path": str(dir_path)}

    # 按文件名排序
    files.sort(key=lambda f: f.name)

    all_content = []
    file_list = []
    total_chars = 0

    for f in files:
        content, meta = await _read_single_file(f)
        if content:
            all_content.append(f"=== 文件: {f.name} ===\n\n{content}\n")
            file_list.append(f.name)
            total_chars += len(content)

    if not all_content:
        return "", {"error": "所有文件读取失败", "path": str(dir_path)}

    combined = "\n".join(all_content)

    metadata = {
        "file_count": len(files),
        "file_list": file_list,
        "total_size": total_chars,
        "estimated_tokens": total_chars / CHARS_PER_TOKEN,
        "strategy": "multi_file"
    }

    # 检查组合内容是否超过预算
    if metadata["estimated_tokens"] > MAX_MATERIAL_TOKENS:
        logger.warning(f"组合材料过大 ({metadata['estimated_tokens']:.0f} tokens)，需要截断")
        metadata["strategy"] = "multi_file_truncated"
        max_chars = int(MAX_MATERIAL_TOKENS * CHARS_PER_TOKEN)
        combined = combined[:max_chars] + "\n\n[材料过长，已截断...]"

    return combined, metadata
