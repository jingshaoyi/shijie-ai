"""
AI服务层 - 使用LiteLLM统一调用
支持100+LLM提供商，自动从环境变量读取API Key
"""
import os
from typing import AsyncGenerator, Optional
import litellm
from litellm import acompletion
from tenacity import retry, stop_after_attempt, wait_exponential
from app.core.logging import get_logger
from app.config import get_settings

logger = get_logger(__name__)
settings = get_settings()

# 配置LiteLLM
litellm.set_verbose = False

# ========================================
# 关键修复：确保API Key环境变量被正确设置
# ========================================

def setup_api_keys():
    """设置API Keys环境变量 - 从settings或旧版配置读取"""
    
    # 阿里云 DashScope - 支持 DASHSCOPE_API_KEY 或 ALIBABA_API_KEY
    if not os.environ.get("DASHSCOPE_API_KEY"):
        # 优先使用 DASHSCOPE_API_KEY
        dashscope_key = getattr(settings, "DASHSCOPE_API_KEY", None)
        if dashscope_key:
            os.environ["DASHSCOPE_API_KEY"] = dashscope_key
            logger.info("dashscope_api_key_set_from_settings")
        # 兼容旧版 ALIBABA_API_KEY
        elif getattr(settings, "ALIBABA_API_KEY", None):
            os.environ["DASHSCOPE_API_KEY"] = settings.ALIBABA_API_KEY
            logger.info("dashscope_api_key_set_from_alibaba_api_key")
    
    # DeepSeek
    if not os.environ.get("DEEPSEEK_API_KEY"):
        deepseek_key = getattr(settings, "DEEPSEEK_API_KEY", None)
        if deepseek_key:
            os.environ["DEEPSEEK_API_KEY"] = deepseek_key
    
    # OpenAI
    if not os.environ.get("OPENAI_API_KEY"):
        openai_key = getattr(settings, "OPENAI_API_KEY", None)
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
    
    # Anthropic
    if not os.environ.get("ANTHROPIC_API_KEY"):
        anthropic_key = getattr(settings, "ANTHROPIC_API_KEY", None)
        if anthropic_key:
            os.environ["ANTHROPIC_API_KEY"] = anthropic_key

# 执行设置
setup_api_keys()

# 记录环境变量状态（不显示具体值）
logger.info("api_keys_status", 
    dashscope_set=bool(os.environ.get("DASHSCOPE_API_KEY")),
    deepseek_set=bool(os.environ.get("DEEPSEEK_API_KEY")),
    openai_set=bool(os.environ.get("OPENAI_API_KEY")),
    anthropic_set=bool(os.environ.get("ANTHROPIC_API_KEY"))
)


# ========================================
# 模型ID到LiteLLM模型字符串的映射
# ========================================
MODEL_MAP = {
    # ===== 阿里云通义千问 =====
    # 使用 dashscope/ 前缀，需要 LiteLLM >= 1.52.0
    "qwen-plus": "dashscope/qwen-plus",
    "qwen-turbo": "dashscope/qwen-turbo",
    "qwen-max": "dashscope/qwen-max",
    "qwen-coder-plus": "dashscope/qwen-coder-plus",
    "qwen-math-plus": "dashscope/qwen-math-plus",

    # ===== DeepSeek =====
    "deepseek-chat": "deepseek/deepseek-chat",
    "deepseek-reasoner": "deepseek/deepseek-reasoner",
    "deepseek-coder": "deepseek/deepseek-coder",

    # ===== OpenAI =====
    "gpt-4o": "openai/gpt-4o",
    "gpt-4o-mini": "openai/gpt-4o-mini",
    "gpt-4-turbo": "openai/gpt-4-turbo",
    "gpt-4": "openai/gpt-4",
    "gpt-3.5-turbo": "openai/gpt-3.5-turbo",
    "o1-preview": "openai/o1-preview",
    "o1-mini": "openai/o1-mini",

    # ===== Anthropic Claude =====
    "claude-3-5-sonnet-20241022": "anthropic/claude-3-5-sonnet-20241022",
    "claude-3-opus-20240229": "anthropic/claude-3-opus-20240229",
    "claude-3-sonnet-20240229": "anthropic/claude-3-sonnet-20240229",
    "claude-3-haiku-20240307": "anthropic/claude-3-haiku-20240307",

    # ===== Google Gemini =====
    "gemini-2.0-flash-exp": "gemini/gemini-2.0-flash-exp",
    "gemini-1.5-pro": "gemini/gemini-1.5-pro",
    "gemini-1.5-flash": "gemini/gemini-1.5-flash",
    "gemini-pro": "gemini/gemini-pro",

    # ===== 智谱AI =====
    "glm-4-plus": "zhipu/glm-4-plus",
    "glm-4": "zhipu/glm-4",
    "glm-4-air": "zhipu/glm-4-air",
    "glm-4-flash": "zhipu/glm-4-flash",
    "glm-4v": "zhipu/glm-4v",
    "chatglm3-6b": "zhipu/chatglm3-6b",

    # ===== Moonshot =====
    "moonshot-v1-8k": "moonshot/moonshot-v1-8k",
    "moonshot-v1-32k": "moonshot/moonshot-v1-32k",
    "moonshot-v1-128k": "moonshot/moonshot-v1-128k",

    # ===== 零一万物 =====
    "yi-large": "yi/yi-large",
    "yi-medium": "yi/yi-medium",
    "yi-vision": "yi/yi-vision",

    # ===== 百川智能 =====
    "baichuan4": "baichuan/baichuan4",
    "baichuan3-turbo": "baichuan/baichuan3-turbo",

    # ===== 讯飞星火 =====
    "spark-desk-v4": "xunfei/spark-desk-v4",
    "spark-desk-v3.5": "xunfei/spark-desk-v3.5",

    # ===== 百度文心 =====
    "ernie-bot-4": "baidu/ernie-bot-4",
    "ernie-bot": "baidu/ernie-bot",
    "ernie-speed": "baidu/ernie-speed",

    # ===== 腾讯混元 =====
    "hunyuan-pro": "tencent/hunyuan-pro",
    "hunyuan-standard": "tencent/hunyuan-standard",

    # ===== MiniMax =====
    "abab6.5": "minimax/abab6.5",
    "abab6": "minimax/abab6",

    # ===== 阶跃星辰 =====
    "step-2-16k": "stepfun/step-2-16k",
    "step-1-8k": "stepfun/step-1-8k",

    # ===== 商汤 =====
    "sensechat-5": "sensetime/sensechat-5",
    "sensechat": "sensetime/sensechat",

    # ===== 字节豆包 =====
    "doubao-pro-4k": "bytedance/doubao-pro-4k",
    "doubao-lite-4k": "bytedance/doubao-lite-4k",

    # ===== 华为盘古 =====
    "pangu-master": "huawei/pangu-master",

    # ===== 360 =====
    "360gpt-pro": "360/360gpt-pro",

    # ===== Ollama本地模型 =====
    "llama3.1-8b": "ollama/llama3.1:8b",
    "llama3.1-70b": "ollama/llama3.1:70b",
    "llama3.1-405b": "ollama/llama3.1:405b",
    "qwen2.5-7b": "ollama/qwen2.5:7b",
    "qwen2.5-72b": "ollama/qwen2.5:72b",
    "mistral-large": "ollama/mistral-large",
    "mixtral-8x22b": "ollama/mixtral:8x22b",
    "gemma2-9b": "ollama/gemma2:9b",
    "gemma2-27b": "ollama/gemma2:27b",
    "phi4": "ollama/phi4",
    "deepseek-r1:14b": "ollama/deepseek-r1:14b",
    "deepseek-r1:32b": "ollama/deepseek-r1:32b",

    # ===== 其他国际模型 =====
    "command-r-plus": "cohere/command-r-plus",
    "command-r": "cohere/command-r",
    "jamba-1.5-large": "ai21/jamba-1.5-large",
    "nova-pro": "bedrock/nova-pro",
    "nova-lite": "bedrock/nova-lite",
}


def get_litellm_model(model_id: Optional[str] = None) -> str:
    """
    获取LiteLLM模型字符串
    支持直接传入完整格式（如 openai/gpt-4o）或简写ID（如 gpt-4o）
    """
    if not model_id:
        return settings.DEFAULT_MODEL

    # 如果已经是完整格式，直接返回
    if "/" in model_id:
        return model_id

    # 从映射表查找
    return MODEL_MAP.get(model_id, settings.DEFAULT_MODEL)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True
)
async def chat_completion(
    messages: list,
    model: Optional[str] = None,
    max_tokens: int = 4096,
    temperature: float = 0.7,
) -> str:
    """
    非流式对话 - 带自动重试
    """
    model_str = get_litellm_model(model)

    logger.info("llm_chat_start", model=model_str, message_count=len(messages))

    try:
        response = await acompletion(
            model=model_str,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        content = response.choices[0].message.content
        logger.info("llm_chat_success", model=model_str, response_length=len(content))
        return content

    except Exception as e:
        logger.error("llm_chat_error", model=model_str, error=str(e))
        raise


async def stream_chat(
    messages: list,
    model: Optional[str] = None,
    max_tokens: int = 4096,
    temperature: float = 0.7,
) -> AsyncGenerator[str, None]:
    """
    流式对话 - SSE输出
    """
    model_str = get_litellm_model(model)

    logger.info("llm_stream_start", model=model_str, message_count=len(messages))

    try:
        response = await acompletion(
            model=model_str,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )

        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

        logger.info("llm_stream_complete", model=model_str)

    except Exception as e:
        logger.error("llm_stream_error", model=model_str, error=str(e))
        raise
