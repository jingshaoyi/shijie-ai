"""
AI模型列表 - 硬编码配置
支持市面上几乎所有主流模型，无需数据库
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from app.auth import get_current_user
from app.models.user import User
from app.config import get_settings

router = APIRouter(prefix="/models", tags=["AI模型"])
settings = get_settings()


class ModelResponse(BaseModel):
    model_id: str
    name: str
    provider: str
    description: Optional[str] = None
    is_default: bool = False


class ModelListResponse(BaseModel):
    models: List[ModelResponse]
    default_model: Optional[ModelResponse] = None


# ========================================
# 支持的AI模型列表 - 覆盖市面上几乎所有主流模型
# ========================================

SUPPORTED_MODELS = [
    # ========================================
    # 阿里云 - 通义千问 (国内首选)
    # ========================================
    ModelResponse(
        model_id="qwen-plus",
        name="通义千问Plus",
        provider="aliyun",
        description="阿里云通义千问大模型，综合能力强，适合大多数场景",
        is_default=True,
    ),
    ModelResponse(
        model_id="qwen-turbo",
        name="通义千问Turbo",
        provider="aliyun",
        description="阿里云通义千问快速版，响应速度快，成本低",
    ),
    ModelResponse(
        model_id="qwen-max",
        name="通义千问Max",
        provider="aliyun",
        description="阿里云通义千问旗舰版，能力最强，适合复杂任务",
    ),
    ModelResponse(
        model_id="qwen-coder-plus",
        name="通义千问Coder",
        provider="aliyun",
        description="阿里云代码专用模型，编程能力突出",
    ),
    ModelResponse(
        model_id="qwen-math-plus",
        name="通义千问Math",
        provider="aliyun",
        description="阿里云数学推理专用模型",
    ),
    # 阿里云视觉模型
    ModelResponse(
        model_id="qwen-vl-plus",
        name="通义千问VL Plus",
        provider="aliyun",
        description="阿里云通义千问视觉语言模型，支持图片理解",
    ),
    ModelResponse(
        model_id="qwen-vl-max",
        name="通义千问VL Max",
        provider="aliyun",
        description="阿里云通义千问旗舰视觉模型，图片理解能力最强",
    ),

    # ========================================
    # DeepSeek - 深度求索 (国产之光)
    # ========================================
    ModelResponse(
        model_id="deepseek-chat",
        name="DeepSeek Chat",
        provider="deepseek",
        description="DeepSeek对话模型，代码和推理能力强，性价比高",
    ),
    ModelResponse(
        model_id="deepseek-reasoner",
        name="DeepSeek R1",
        provider="deepseek",
        description="DeepSeek推理模型，深度思考，数学和逻辑推理突出",
    ),
    ModelResponse(
        model_id="deepseek-coder",
        name="DeepSeek Coder",
        provider="deepseek",
        description="DeepSeek代码专用模型",
    ),

    # ========================================
    # OpenAI - GPT系列 (国际主流)
    # ========================================
    ModelResponse(
        model_id="gpt-4o",
        name="GPT-4o",
        provider="openai",
        description="OpenAI GPT-4o，多模态能力强，综合能力优秀",
    ),
    ModelResponse(
        model_id="gpt-4o-mini",
        name="GPT-4o Mini",
        provider="openai",
        description="OpenAI GPT-4o Mini，性价比高，速度快",
    ),
    ModelResponse(
        model_id="gpt-4-turbo",
        name="GPT-4 Turbo",
        provider="openai",
        description="OpenAI GPT-4 Turbo，128K上下文",
    ),
    ModelResponse(
        model_id="gpt-4",
        name="GPT-4",
        provider="openai",
        description="OpenAI GPT-4，经典版本，稳定可靠",
    ),
    ModelResponse(
        model_id="gpt-3.5-turbo",
        name="GPT-3.5 Turbo",
        provider="openai",
        description="OpenAI GPT-3.5 Turbo，速度快，成本低",
    ),
    ModelResponse(
        model_id="o1-preview",
        name="o1 Preview",
        provider="openai",
        description="OpenAI o1预览版，推理能力极强",
    ),
    ModelResponse(
        model_id="o1-mini",
        name="o1 Mini",
        provider="openai",
        description="OpenAI o1迷你版，快速推理",
    ),

    # ========================================
    # Anthropic - Claude系列 (安全对齐)
    # ========================================
    ModelResponse(
        model_id="claude-3-5-sonnet-20241022",
        name="Claude 3.5 Sonnet",
        provider="anthropic",
        description="Anthropic Claude 3.5 Sonnet，最新版本，综合能力最强",
    ),
    ModelResponse(
        model_id="claude-3-opus-20240229",
        name="Claude 3 Opus",
        provider="anthropic",
        description="Anthropic Claude 3 Opus，旗舰模型，复杂任务首选",
    ),
    ModelResponse(
        model_id="claude-3-sonnet-20240229",
        name="Claude 3 Sonnet",
        provider="anthropic",
        description="Anthropic Claude 3 Sonnet，平衡性能和成本",
    ),
    ModelResponse(
        model_id="claude-3-haiku-20240307",
        name="Claude 3 Haiku",
        provider="anthropic",
        description="Anthropic Claude 3 Haiku，快速响应，成本低",
    ),

    # ========================================
    # Google - Gemini系列
    # ========================================
    ModelResponse(
        model_id="gemini-2.0-flash-exp",
        name="Gemini 2.0 Flash",
        provider="google",
        description="Google Gemini 2.0 Flash，多模态，速度快",
    ),
    ModelResponse(
        model_id="gemini-1.5-pro",
        name="Gemini 1.5 Pro",
        provider="google",
        description="Google Gemini 1.5 Pro，100万上下文",
    ),
    ModelResponse(
        model_id="gemini-1.5-flash",
        name="Gemini 1.5 Flash",
        provider="google",
        description="Google Gemini 1.5 Flash，快速响应",
    ),
    ModelResponse(
        model_id="gemini-pro",
        name="Gemini Pro",
        provider="google",
        description="Google Gemini Pro，经典版本",
    ),

    # ========================================
    # 智谱AI - GLM系列 (国内)
    # ========================================
    ModelResponse(
        model_id="glm-4-plus",
        name="GLM-4 Plus",
        provider="zhipu",
        description="智谱AI GLM-4 Plus，最新旗舰，中文能力顶尖",
    ),
    ModelResponse(
        model_id="glm-4",
        name="GLM-4",
        provider="zhipu",
        description="智谱AI GLM-4，综合能力优秀",
    ),
    ModelResponse(
        model_id="glm-4-air",
        name="GLM-4 Air",
        provider="zhipu",
        description="智谱AI GLM-4 Air，高性价比",
    ),
    ModelResponse(
        model_id="glm-4-flash",
        name="GLM-4 Flash",
        provider="zhipu",
        description="智谱AI GLM-4 Flash，免费快速",
    ),
    ModelResponse(
        model_id="glm-4v",
        name="GLM-4V",
        provider="zhipu",
        description="智谱AI GLM-4V，多模态视觉模型",
    ),
    ModelResponse(
        model_id="chatglm3-6b",
        name="ChatGLM3-6B",
        provider="zhipu",
        description="智谱AI ChatGLM3-6B，开源小模型",
    ),

    # ========================================
    # Moonshot - Kimi系列 (国内长文本)
    # ========================================
    ModelResponse(
        model_id="moonshot-v1-8k",
        name="Kimi 8K",
        provider="moonshot",
        description="Moonshot Kimi 8K，长文本处理能力强",
    ),
    ModelResponse(
        model_id="moonshot-v1-32k",
        name="Kimi 32K",
        provider="moonshot",
        description="Moonshot Kimi 32K，超长上下文",
    ),
    ModelResponse(
        model_id="moonshot-v1-128k",
        name="Kimi 128K",
        provider="moonshot",
        description="Moonshot Kimi 128K，极长文本处理",
    ),

    # ========================================
    # 零一万物 - Yi系列 (李开复)
    # ========================================
    ModelResponse(
        model_id="yi-large",
        name="Yi Large",
        provider="lingyiwanwu",
        description="零一万物 Yi Large，中文能力强",
    ),
    ModelResponse(
        model_id="yi-medium",
        name="Yi Medium",
        provider="lingyiwanwu",
        description="零一万物 Yi Medium，平衡选择",
    ),
    ModelResponse(
        model_id="yi-vision",
        name="Yi Vision",
        provider="lingyiwanwu",
        description="零一万物 Yi Vision，多模态模型",
    ),

    # ========================================
    # 百川智能 - Baichuan系列 (王小川)
    # ========================================
    ModelResponse(
        model_id="baichuan4",
        name="Baichuan 4",
        provider="baichuan",
        description="百川智能 Baichuan 4，最新旗舰",
    ),
    ModelResponse(
        model_id="baichuan3-turbo",
        name="Baichuan 3 Turbo",
        provider="baichuan",
        description="百川智能 Baichuan 3 Turbo，快速响应",
    ),

    # ========================================
    # 讯飞星火 - SparkDesk (科大讯飞)
    # ========================================
    ModelResponse(
        model_id="spark-desk-v4",
        name="讯飞星火 V4",
        provider="xunfei",
        description="讯飞星火认知大模型 V4，中文理解强",
    ),
    ModelResponse(
        model_id="spark-desk-v3.5",
        name="讯飞星火 V3.5",
        provider="xunfei",
        description="讯飞星火认知大模型 V3.5",
    ),

    # ========================================
    # 百度 - 文心一言 (ERNIE)
    # ========================================
    ModelResponse(
        model_id="ernie-bot-4",
        name="文心一言4.0",
        provider="baidu",
        description="百度文心一言4.0，最新版本",
    ),
    ModelResponse(
        model_id="ernie-bot",
        name="文心一言",
        provider="baidu",
        description="百度文心一言，经典版本",
    ),
    ModelResponse(
        model_id="ernie-speed",
        name="文心Speed",
        provider="baidu",
        description="百度文心Speed，快速响应",
    ),

    # ========================================
    # 腾讯 - 混元 (Hunyuan)
    # ========================================
    ModelResponse(
        model_id="hunyuan-pro",
        name="混元Pro",
        provider="tencent",
        description="腾讯混元大模型 Pro 版",
    ),
    ModelResponse(
        model_id="hunyuan-standard",
        name="混元Standard",
        provider="tencent",
        description="腾讯混元大模型 Standard 版",
    ),

    # ========================================
    # MiniMax - abab系列
    # ========================================
    ModelResponse(
        model_id="abab6.5",
        name="MiniMax abab6.5",
        provider="minimax",
        description="MiniMax abab6.5，多模态能力强",
    ),
    ModelResponse(
        model_id="abab6",
        name="MiniMax abab6",
        provider="minimax",
        description="MiniMax abab6，综合能力优秀",
    ),

    # ========================================
    # 阶跃星辰 - Step系列
    # ========================================
    ModelResponse(
        model_id="step-2-16k",
        name="阶跃Step-2",
        provider="stepfun",
        description="阶跃星辰 Step-2，万亿参数大模型",
    ),
    ModelResponse(
        model_id="step-1-8k",
        name="阶跃Step-1",
        provider="stepfun",
        description="阶跃星辰 Step-1，高效实用",
    ),

    # ========================================
    # 商汤 - SenseChat
    # ========================================
    ModelResponse(
        model_id="sensechat-5",
        name="商量SenseChat 5",
        provider="sensetime",
        description="商汤商量大模型5.0",
    ),
    ModelResponse(
        model_id="sensechat",
        name="商量SenseChat",
        provider="sensetime",
        description="商汤商量大模型",
    ),

    # ========================================
    # 字节跳动 - 豆包 (Doubao)
    # ========================================
    ModelResponse(
        model_id="doubao-pro-4k",
        name="豆包Pro",
        provider="bytedance",
        description="字节跳动豆包大模型 Pro",
    ),
    ModelResponse(
        model_id="doubao-lite-4k",
        name="豆包Lite",
        provider="bytedance",
        description="字节跳动豆包大模型 Lite",
    ),

    # ========================================
    # 华为 - 盘古 (Pangu)
    # ========================================
    ModelResponse(
        model_id="pangu-master",
        name="盘古Master",
        provider="huawei",
        description="华为盘古大模型 Master 版",
    ),

    # ========================================
    # 360 - 智脑
    # ========================================
    ModelResponse(
        model_id="360gpt-pro",
        name="360智脑Pro",
        provider="360",
        description="360智脑大模型 Pro 版",
    ),

    # ========================================
    # 月之暗面 - Kimi (重复，但保留不同命名)
    # ========================================
    # 已在 Moonshot 中定义

    # ========================================
    # 本地/开源模型 (通过Ollama等)
    # ========================================
    ModelResponse(
        model_id="llama3.1-8b",
        name="Llama 3.1 8B",
        provider="ollama",
        description="Meta Llama 3.1 8B，开源小模型，可本地部署",
    ),
    ModelResponse(
        model_id="llama3.1-70b",
        name="Llama 3.1 70B",
        provider="ollama",
        description="Meta Llama 3.1 70B，开源大模型，可本地部署",
    ),
    ModelResponse(
        model_id="llama3.1-405b",
        name="Llama 3.1 405B",
        provider="ollama",
        description="Meta Llama 3.1 405B，开源旗舰模型",
    ),
    ModelResponse(
        model_id="qwen2.5-7b",
        name="Qwen2.5 7B",
        provider="ollama",
        description="阿里通义千问2.5 7B，开源可本地部署",
    ),
    ModelResponse(
        model_id="qwen2.5-72b",
        name="Qwen2.5 72B",
        provider="ollama",
        description="阿里通义千问2.5 72B，开源大模型",
    ),
    ModelResponse(
        model_id="mistral-large",
        name="Mistral Large",
        provider="ollama",
        description="Mistral Large，欧洲开源模型",
    ),
    ModelResponse(
        model_id="mixtral-8x22b",
        name="Mixtral 8x22B",
        provider="ollama",
        description="Mixtral 8x22B，MOE架构开源模型",
    ),
    ModelResponse(
        model_id="gemma2-9b",
        name="Gemma 2 9B",
        provider="ollama",
        description="Google Gemma 2 9B，轻量级开源模型",
    ),
    ModelResponse(
        model_id="gemma2-27b",
        name="Gemma 2 27B",
        provider="ollama",
        description="Google Gemma 2 27B，开源大模型",
    ),
    ModelResponse(
        model_id="phi4",
        name="Phi-4",
        provider="ollama",
        description="Microsoft Phi-4，小模型大能力",
    ),
    ModelResponse(
        model_id="deepseek-r1:14b",
        name="DeepSeek R1 14B",
        provider="ollama",
        description="DeepSeek R1 14B，本地推理模型",
    ),
    ModelResponse(
        model_id="deepseek-r1:32b",
        name="DeepSeek R1 32B",
        provider="ollama",
        description="DeepSeek R1 32B，本地推理大模型",
    ),

    # ========================================
    # 其他国际模型
    # ========================================
    ModelResponse(
        model_id="command-r-plus",
        name="Cohere Command R+",
        provider="cohere",
        description="Cohere Command R+，企业级RAG模型",
    ),
    ModelResponse(
        model_id="command-r",
        name="Cohere Command R",
        provider="cohere",
        description="Cohere Command R，平衡选择",
    ),
    ModelResponse(
        model_id="jamba-1.5-large",
        name="AI21 Jamba 1.5 Large",
        provider="ai21",
        description="AI21 Jamba 1.5 Large，Mamba架构",
    ),
    ModelResponse(
        model_id="nova-pro",
        name="Amazon Nova Pro",
        provider="bedrock",
        description="Amazon Nova Pro，AWS Bedrock",
    ),
    ModelResponse(
        model_id="nova-lite",
        name="Amazon Nova Lite",
        provider="bedrock",
        description="Amazon Nova Lite，AWS Bedrock轻量版",
    ),
]


@router.get("/list", response_model=ModelListResponse)
async def get_models(user: User = Depends(get_current_user)):
    """获取支持的AI模型列表"""
    # 找到默认模型
    default_model = None
    for m in SUPPORTED_MODELS:
        if m.is_default:
            default_model = m
            break

    # 如果没有设置默认，使用第一个
    if not default_model and SUPPORTED_MODELS:
        default_model = SUPPORTED_MODELS[0]

    return ModelListResponse(
        models=SUPPORTED_MODELS,
        default_model=default_model
    )
