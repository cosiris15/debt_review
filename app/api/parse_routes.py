"""
Material Parsing API Routes

提供材料智能解析功能：
- 使用阿里云 qwen-vl-ocr 进行 OCR 识别（支持手写体）
- 使用 LLM 从 OCR 结果中提取结构化信息
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
import os
import tempfile
import logging
import base64

from app.core.auth import get_current_user, AuthenticatedUser
from app.core.config import settings
from app.services.ocr_service import get_ocr_service

logger = logging.getLogger(__name__)

parse_router = APIRouter(prefix="/parse", tags=["Parse"])


# ============== 数据模型 ==============

class ParsedCreditor(BaseModel):
    """解析出的债权人信息"""
    creditor_name: str
    declared_amount: Optional[float] = None
    source_file: str
    batch_number: int = 1
    creditor_number: int = 1
    confidence: float = 0.0  # 解析置信度 0-1


class MaterialParseResponse(BaseModel):
    """材料解析响应"""
    creditors: List[ParsedCreditor]
    confidence: float  # 整体置信度
    warnings: List[str] = []
    file_count: int


# ============== 辅助函数 ==============

async def extract_text_from_pdf(file_path: str) -> str:
    """从 PDF 文件提取文本"""
    try:
        import pymupdf  # PyMuPDF
        doc = pymupdf.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
        return text
    except ImportError:
        logger.warning("PyMuPDF not installed, trying pdfplumber")
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += (page.extract_text() or "") + "\n"
            return text
        except ImportError:
            raise HTTPException(500, "PDF 处理库未安装。请安装 pymupdf 或 pdfplumber")
    except Exception as e:
        logger.error(f"PDF 提取失败: {e}")
        raise HTTPException(400, f"PDF 文件处理失败: {str(e)}")


async def encode_image_base64(file_path: str) -> str:
    """将图片编码为 base64"""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


async def parse_with_llm(contents: List[dict], project_id: str) -> MaterialParseResponse:
    """
    使用 LLM 解析材料内容，提取债权人信息

    Args:
        contents: 包含文件内容的列表 [{filename, content, type}]
        project_id: 项目ID
    """
    from langchain_anthropic import ChatAnthropic
    from langchain_core.messages import HumanMessage, SystemMessage

    # 构造系统提示
    system_prompt = """你是一个专业的债权审查助手。请从提供的债权申报材料中提取债权人信息。

对于每个识别出的债权人，请提取：
1. 债权人名称（必填）
2. 申报金额（如有）
3. 来源文件

请以 JSON 格式返回结果：
```json
{
  "creditors": [
    {
      "creditor_name": "债权人名称",
      "declared_amount": 金额数字或null,
      "source_file": "来源文件名",
      "confidence": 0.95
    }
  ],
  "overall_confidence": 0.9,
  "warnings": ["可能的问题或不确定的地方"]
}
```

注意：
- 如果材料中包含多个债权人，请分别提取
- 金额请转换为数字（元），不要包含单位
- 如果无法确定某些信息，可以留空或标注较低的置信度
- 请认真分析材料内容，不要遗漏任何债权人"""

    # 构造消息内容
    message_content = []

    for item in contents:
        if item["type"] == "text":
            message_content.append({
                "type": "text",
                "text": f"=== 文件: {item['filename']} ===\n{item['content']}"
            })
        elif item["type"] == "image":
            message_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{item['mime_type']};base64,{item['content']}"
                }
            })
            message_content.append({
                "type": "text",
                "text": f"(上图来自文件: {item['filename']})"
            })

    # 添加指令
    message_content.append({
        "type": "text",
        "text": "\n请分析以上材料，提取所有债权人信息。"
    })

    try:
        # 使用 Claude 进行分析（支持图片）
        llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            api_key=settings.ANTHROPIC_API_KEY,
            max_tokens=4096
        )

        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=message_content)
        ])

        # 解析 LLM 响应
        response_text = response.content
        if isinstance(response_text, list):
            response_text = response_text[0].get("text", "") if response_text else ""

        # 提取 JSON
        import json
        import re

        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text)
        if json_match:
            result = json.loads(json_match.group(1))
        else:
            # 尝试直接解析
            result = json.loads(response_text)

        # 转换为响应模型
        creditors = []
        for i, c in enumerate(result.get("creditors", [])):
            creditors.append(ParsedCreditor(
                creditor_name=c.get("creditor_name", ""),
                declared_amount=c.get("declared_amount"),
                source_file=c.get("source_file", "unknown"),
                batch_number=1,
                creditor_number=i + 1,
                confidence=c.get("confidence", 0.8)
            ))

        return MaterialParseResponse(
            creditors=creditors,
            confidence=result.get("overall_confidence", 0.8),
            warnings=result.get("warnings", []),
            file_count=len(contents)
        )

    except Exception as e:
        logger.error(f"LLM 解析失败: {e}")
        raise HTTPException(500, f"智能解析失败: {str(e)}")


# ============== API 端点 ==============

@parse_router.post("/materials", response_model=MaterialParseResponse)
async def parse_materials(
    project_id: str = Form(...),
    files: List[UploadFile] = File(...),
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    解析上传的债权申报材料，返回识别出的债权人信息

    支持格式：PDF（包括扫描件）、图片（jpg/png/webp）、Word（.docx）、Excel（.xlsx）

    处理流程：
    1. 使用阿里云 qwen-vl-ocr 进行 OCR（支持手写体）
    2. 使用 LLM 从 OCR 文本中提取结构化信息

    Returns:
        MaterialParseResponse: 包含解析出的债权人列表、置信度和警告
    """
    if not files:
        raise HTTPException(400, "请上传至少一个文件")

    # 限制文件数量和大小
    MAX_FILES = 50
    MAX_SIZE_MB = 50

    if len(files) > MAX_FILES:
        raise HTTPException(400, f"最多支持 {MAX_FILES} 个文件")

    # 获取 OCR 服务
    ocr_service = get_ocr_service()

    # 处理上传的文件
    contents = []
    warnings = []

    # 支持的文件类型
    SUPPORTED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".webp", ".docx", ".xlsx"}

    with tempfile.TemporaryDirectory() as temp_dir:
        for file in files:
            filename = file.filename or "unknown"
            ext = os.path.splitext(filename)[1].lower()

            # 检查文件类型
            if ext not in SUPPORTED_EXTENSIONS:
                warnings.append(f"不支持的文件类型: {filename}")
                continue

            # 检查文件大小
            file.file.seek(0, 2)
            size = file.file.tell()
            file.file.seek(0)

            if size > MAX_SIZE_MB * 1024 * 1024:
                warnings.append(f"文件 {filename} 超过 {MAX_SIZE_MB}MB，已跳过")
                continue

            # 保存临时文件
            temp_path = os.path.join(temp_dir, filename)
            with open(temp_path, "wb") as f:
                content = await file.read()
                f.write(content)

            # 使用 OCR 服务处理文件
            try:
                logger.info(f"OCR 处理文件: {filename}")
                text = await ocr_service.ocr_file(temp_path)

                if text.strip():
                    contents.append({
                        "filename": filename,
                        "content": text,
                        "type": "text"
                    })
                else:
                    warnings.append(f"文件 {filename} 未识别到文本内容")

            except Exception as e:
                logger.error(f"OCR 处理文件 {filename} 失败: {e}")
                warnings.append(f"处理文件 {filename} 失败: {str(e)}")

    if not contents:
        raise HTTPException(400, "没有可处理的文件内容。" + (f" 警告: {'; '.join(warnings)}" if warnings else ""))

    # 调用 LLM 解析 OCR 结果
    result = await parse_with_llm(contents, project_id)

    # 合并警告
    result.warnings = warnings + result.warnings

    return result


class ParsedProjectInfo(BaseModel):
    """从裁定书解析出的项目信息"""
    case_number: str  # 案号，如 (2025)沪03破399号
    debtor_name: str  # 债务人名称
    bankruptcy_date: str  # 破产受理日期 (YYYY-MM-DD 格式)
    court_name: Optional[str] = None  # 法院名称
    confidence: Optional[float] = None  # 解析置信度 0-1


async def parse_ruling_with_llm(text: str, filename: str) -> ParsedProjectInfo:
    """
    使用 LLM 从裁定书文本中提取项目信息

    Args:
        text: 裁定书全文
        filename: 文件名
    """
    from langchain_anthropic import ChatAnthropic
    from langchain_core.messages import HumanMessage, SystemMessage
    import json
    import re

    system_prompt = """你是一个专业的法律文书分析助手。请从提供的破产裁定书中提取关键信息。

需要提取的信息：
1. **案号**：如 "(2025)沪03破399号"，通常在文书开头
2. **债务人名称**：被申请破产的公司全称
3. **破产受理日期**：法院裁定受理破产申请的日期
4. **法院名称**：作出裁定的法院

请严格按照以下 JSON 格式返回：
```json
{
  "case_number": "案号，如(2025)沪03破399号",
  "debtor_name": "债务人公司全称",
  "bankruptcy_date": "YYYY-MM-DD格式的日期",
  "court_name": "法院名称",
  "confidence": 0.95
}
```

注意事项：
- 案号格式通常为 (年份)法院代码+破+序号
- 日期必须转换为 YYYY-MM-DD 格式（如 2025年5月9日 → 2025-05-09）
- 如果是"决定书"而非"裁定书"，受理日期可能来自裁定书内容引用
- 置信度范围 0-1，根据信息清晰程度判断
- 如果某项信息无法确定，用空字符串表示，并降低置信度"""

    try:
        llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            api_key=settings.ANTHROPIC_API_KEY,
            max_tokens=1024
        )

        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"请分析以下裁定书内容，提取项目信息：\n\n{text}")
        ])

        response_text = response.content
        if isinstance(response_text, list):
            response_text = response_text[0].get("text", "") if response_text else ""

        # 提取 JSON
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text)
        if json_match:
            result = json.loads(json_match.group(1))
        else:
            result = json.loads(response_text)

        return ParsedProjectInfo(
            case_number=result.get("case_number", ""),
            debtor_name=result.get("debtor_name", ""),
            bankruptcy_date=result.get("bankruptcy_date", ""),
            court_name=result.get("court_name"),
            confidence=result.get("confidence", 0.8)
        )

    except Exception as e:
        logger.error(f"LLM 解析裁定书失败: {e}")
        raise HTTPException(500, f"智能解析裁定书失败: {str(e)}")


@parse_router.post("/ruling", response_model=ParsedProjectInfo)
async def parse_ruling(
    file: UploadFile = File(...),
    user: AuthenticatedUser = Depends(get_current_user)
):
    """
    解析破产裁定书 PDF，提取项目基本信息

    支持：民事裁定书、决定书等破产相关文书（包括扫描件）

    处理流程：
    1. 使用阿里云 qwen-vl-ocr 进行 OCR（支持扫描件）
    2. 使用 LLM 从 OCR 文本中提取结构化信息

    Returns:
        ParsedProjectInfo: 包含案号、债务人名称、破产受理日期、法院名称
    """
    # 验证文件类型
    filename = file.filename or "unknown"
    content_type = file.content_type or ""

    if not (content_type == "application/pdf" or filename.lower().endswith(".pdf")):
        raise HTTPException(400, "请上传 PDF 格式的裁定书文件")

    # 检查文件大小（最大 20MB）
    MAX_SIZE_MB = 20
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)

    if size > MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(400, f"文件大小超过 {MAX_SIZE_MB}MB 限制")

    # 获取 OCR 服务
    ocr_service = get_ocr_service()

    # 保存临时文件并使用 OCR 提取文本
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = os.path.join(temp_dir, filename)
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)

        try:
            logger.info(f"OCR 处理裁定书: {filename}")
            text = await ocr_service.ocr_pdf(temp_path)
        except Exception as e:
            logger.error(f"OCR 处理失败: {e}")
            raise HTTPException(400, f"文件处理失败: {str(e)}")

    if not text.strip():
        raise HTTPException(400, "无法从文件中识别文本内容")

    # 使用 LLM 解析
    result = await parse_ruling_with_llm(text, filename)

    # 验证必填字段
    if not result.debtor_name:
        raise HTTPException(400, "未能识别出债务人名称，请检查文件内容")

    return result
