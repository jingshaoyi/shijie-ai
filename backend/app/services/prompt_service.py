# app/services/prompt_service.py
"""
提示词模板服务
支持动态生成、缓存、自动更新提示词模板
"""
import json
import random
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.prompt_template import PromptTemplate, PromptTemplateHistory, DynamicPrompt
from app.services.ai_service import chat_completion
import logging

logger = logging.getLogger(__name__)


class PromptService:
    """提示词服务类"""
    
    # 默认提示词模板库
    DEFAULT_TEMPLATES = {
        # 工作总结模板
        "work_summary": {
            "base": """你是一位专业的{position}工作顾问。请根据以下信息生成一份{period}工作总结。

写作风格：{style}
工作内容：
{content}

要求：
1. 按照{style}的风格撰写
2. 包含工作概述、主要成果、存在问题、下阶段计划等部分
3. 语言专业、条理清晰
4. 适当使用数据支撑

请直接输出工作总结内容：""",
            "variants": [
                "请帮我写一份{period}工作总结，岗位是{position}，风格要求{style}。",
                "作为{position}，需要一份{period}的工作总结，风格为{style}。",
                "生成{position}岗位的{period}工作总结，采用{style}风格。"
            ]
        },
        
        # 知识科普模板
        "science": {
            "base": """你是一位{category}领域的科普作家。请用{difficulty}的方式解释以下知识：

问题：{question}
知识领域：{category}

要求：
1. 用通俗易懂的语言解释复杂的概念
2. 可以适当使用类比和例子帮助理解
3. 内容要有趣且准确
4. 结构清晰，层次分明
5. 适当加入一些相关的趣味知识

请开始科普：""",
            "variants": [
                "请科普一下{category}知识：{question}，要求{difficulty}。",
                "用{difficulty}的方式解释{category}：{question}",
                "作为{category}科普专家，请解答：{question}（{difficulty}）"
            ]
        },
        
        # 诗歌创作模板
        "poetry": {
            "base": """你是一位诗人。请创作一首{genre}，风格为{style}。

主题：{theme}
{requirement}

要求：
1. 紧扣主题，意境深远
2. 语言优美，富有感染力
3. 符合{genre}的特点
4. 可以适当使用修辞手法
5. 请为诗歌起一个合适的标题

请直接输出诗歌内容（包含标题）：""",
            "variants": [
                "创作一首关于{theme}的{genre}，风格{style}。",
                "以{theme}为主题，写一首{style}风格的{genre}。",
                "请为我写一首{genre}，主题是{theme}，要{style}的感觉。"
            ]
        },
        
        # 小红书文案模板
        "copywriting": {
            "base": """请帮我写一篇小红书风格的{type}文案。

产品/主题信息：
{product_info}

文案风格：{style}

要求：
1. 符合小红书平台风格，活泼有趣
2. 适当使用emoji表情
3. 添加相关话题标签 #话题
4. 开头要有吸引力，引发好奇
5. 结构清晰，段落分明

请直接输出文案内容：""",
            "variants": [
                "写一篇{type}的小红书文案，风格{style}。",
                "帮我写{type}的种草文案，要{style}的风格。",
                "生成{type}的小红书推广文案，风格为{style}。"
            ]
        },
        
        # 邮件撰写模板
        "email": {
            "base": """请帮我写一封{type}，语气要求：{tone}。

邮件概要：
{content}

要求：
1. 格式规范，语言得体
2. 内容完整，逻辑清晰
3. 符合{tone}的语气要求
4. 包含收件人称呼、正文、落款等完整格式

请直接输出邮件内容：""",
            "variants": [
                "写一封{type}，语气{tone}。",
                "帮我写{type}，要求{tone}的语气。",
                "生成{type}模板，风格{tone}。"
            ]
        },

        # 代码解释模板
        "code_explain": {
            "base": """你是一位资深{language}开发工程师。请用{depth}的方式解释以下代码：

编程语言：{language}
代码：
```
{code}
```

{question}

要求：
1. 先概括代码的整体功能
2. 逐段/逐函数解释核心逻辑
3. 说明关键变量和数据流
4. 指出代码中的设计模式或技巧
5. 如有问题，指出潜在bug或优化建议

请开始解释：""",
            "variants": [
                "请用{depth}的方式解释这段{language}代码：\n```\n{code}\n```\n{question}",
                "作为{language}专家，请分析以下代码：\n```\n{code}\n```\n解释深度：{depth}，{question}",
                "帮我理解这段{language}代码（{depth}）：\n```\n{code}\n```\n{question}"
            ]
        },

        # 学习规划模板
        "study_plan": {
            "base": """你是一位专业的学习规划师。请帮我制定一份详细的学习计划。

学习目标：{goal}
学习周期：{period}
每日学习时长：{daily_time}
当前水平：{level}
补充说明：{extra}

要求：
1. 将学习周期划分为多个阶段，每个阶段有明确目标
2. 每个阶段列出具体的学习内容和推荐资源
3. 安排每日/每周的学习任务
4. 设置里程碑和检验标准
5. 给出学习建议和注意事项

请直接输出学习计划：""",
            "variants": [
                "制定{goal}学习计划，周期{period}，每天{daily_time}，水平{level}。{extra}",
                "帮我规划{goal}的学习路线，{period}内完成，每天学{daily_time}，{level}起步。{extra}",
                "生成{goal}学习方案：周期{period}，日投入{daily_time}，当前{level}。{extra}"
            ]
        },

        # 产品描述模板
        "product_desc": {
            "base": """请为以下产品撰写一段{style}风格的描述文案。

产品类型：{type}
产品信息：
{product_info}

要求：
1. 标题吸引眼球，突出核心卖点
2. 产品简介简洁有力，一句话说明价值
3. 核心功能/特点分点描述，每点有说服力
4. 适用场景和目标用户
5. 结尾有行动引导

请直接输出产品描述：""",
            "variants": [
                "写一段{type}产品的{style}描述文案。产品信息：{product_info}",
                "为以下产品生成{style}风格的描述：{type} - {product_info}",
                "撰写{style}风格的产品文案，类型{type}，详情：{product_info}"
            ]
        }
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def initialize_default_templates(self):
        """初始化默认提示词模板"""
        for category, templates in self.DEFAULT_TEMPLATES.items():
            # 检查是否已存在
            existing = self.db.query(PromptTemplate).filter(
                PromptTemplate.category == category,
                PromptTemplate.template_key == f"{category}_base"
            ).first()
            
            if not existing:
                # 创建基础模板
                template = PromptTemplate(
                    template_key=f"{category}_base",
                    category=category,
                    sub_key="base",
                    template_content=templates["base"],
                    variables=self._extract_variables(templates["base"]),
                    description=f"{category}基础提示词模板",
                    generation_params={"temperature": 0.7, "model": "dashscope/qwen-plus"}
                )
                self.db.add(template)
                
                # 创建变体模板
                for i, variant in enumerate(templates["variants"]):
                    variant_template = PromptTemplate(
                        template_key=f"{category}_variant_{i}",
                        category=category,
                        sub_key=f"variant_{i}",
                        template_content=variant,
                        variables=self._extract_variables(variant),
                        description=f"{category}变体提示词模板 {i+1}",
                        generation_params={"temperature": 0.8, "model": "dashscope/qwen-plus"}
                    )
                    self.db.add(variant_template)
        
        self.db.commit()
        logger.info("默认提示词模板初始化完成")
    
    def _extract_variables(self, template: str) -> List[str]:
        """从模板中提取变量名"""
        pattern = r'\{([^}]+)\}'
        matches = re.findall(pattern, template)
        return list(set(matches))
    
    def get_template(self, category: str, sub_key: Optional[str] = None) -> Optional[PromptTemplate]:
        """获取提示词模板"""
        query = self.db.query(PromptTemplate).filter(
            PromptTemplate.category == category,
            PromptTemplate.is_active == 1
        )
        
        if sub_key:
            query = query.filter(PromptTemplate.sub_key == sub_key)
        
        # 优先返回最新版本
        return query.order_by(PromptTemplate.version.desc()).first()
    
    def get_random_template(self, category: str) -> Optional[PromptTemplate]:
        """随机获取一个模板（增加多样性）"""
        templates = self.db.query(PromptTemplate).filter(
            PromptTemplate.category == category,
            PromptTemplate.is_active == 1
        ).all()
        
        if not templates:
            return None
        
        # 根据使用次数加权随机选择（使用少的优先）
        weights = [1 / (t.usage_count + 1) for t in templates]
        total = sum(weights)
        weights = [w / total for w in weights]
        
        return random.choices(templates, weights=weights, k=1)[0]
    
    def generate_prompt(self, category: str, variables: Dict[str, Any], 
                       sub_key: Optional[str] = None,
                       use_cache: bool = True,
                       cache_ttl_hours: int = 24) -> str:
        """
        生成提示词
        
        Args:
            category: 模板分类
            variables: 变量字典
            sub_key: 子分类key
            use_cache: 是否使用缓存
            cache_ttl_hours: 缓存有效期（小时）
        
        Returns:
            生成的提示词
        """
        # 生成缓存key
        cache_key = self._generate_cache_key(category, variables, sub_key)
        
        # 检查缓存
        if use_cache:
            cached = self._get_cached_prompt(cache_key)
            if cached:
                logger.info(f"使用缓存的提示词: {cache_key}")
                return cached
        
        # 获取模板
        if sub_key:
            template = self.get_template(category, sub_key)
        else:
            template = self.get_random_template(category)
        
        if not template:
            # 使用默认模板
            template_content = self.DEFAULT_TEMPLATES.get(category, {}).get("base", "")
            if not template_content:
                raise ValueError(f"未找到分类 {category} 的模板")
        else:
            template_content = template.template_content
            # 更新使用次数
            template.usage_count += 1
            self.db.commit()
        
        # 替换变量
        prompt = self._replace_variables(template_content, variables)
        
        # 缓存结果
        if use_cache:
            self._cache_prompt(cache_key, category, prompt, variables, cache_ttl_hours)
        
        return prompt
    
    def _replace_variables(self, template: str, variables: Dict[str, Any]) -> str:
        """替换模板中的变量"""
        result = template
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            result = result.replace(placeholder, str(value))
        return result
    
    def _generate_cache_key(self, category: str, variables: Dict[str, Any], 
                           sub_key: Optional[str] = None) -> str:
        """生成缓存key"""
        var_str = json.dumps(variables, sort_keys=True, ensure_ascii=False)
        key = f"{category}:{sub_key or 'default'}:{hash(var_str)}"
        return key
    
    def _get_cached_prompt(self, cache_key: str) -> Optional[str]:
        """获取缓存的提示词"""
        cached = self.db.query(DynamicPrompt).filter(
            DynamicPrompt.cache_key == cache_key,
            DynamicPrompt.expires_at > datetime.utcnow()
        ).first()
        
        return cached.prompt_content if cached else None
    
    def _cache_prompt(self, cache_key: str, category: str, prompt: str, 
                     context: Dict[str, Any], ttl_hours: int):
        """缓存提示词"""
        # 删除旧缓存
        self.db.query(DynamicPrompt).filter(
            DynamicPrompt.cache_key == cache_key
        ).delete()
        
        # 创建新缓存
        cached = DynamicPrompt(
            cache_key=cache_key,
            category=category,
            prompt_content=prompt,
            context=context,
            expires_at=datetime.utcnow() + timedelta(hours=ttl_hours)
        )
        self.db.add(cached)
        self.db.commit()
    
    async def regenerate_template(self, category: str, sub_key: Optional[str] = None,
                                  ai_model: str = "dashscope/qwen-plus") -> Optional[PromptTemplate]:
        """
        使用AI重新生成提示词模板
        
        Args:
            category: 分类
            sub_key: 子分类
            ai_model: AI模型
        
        Returns:
            新生成的模板
        """
        # 获取当前模板作为参考
        current = self.get_template(category, sub_key)
        
        # 构建生成新模板的提示词
        meta_prompt = f"""你是一位提示词工程专家。请基于以下信息，生成一个新的、有创意的提示词模板。

分类：{category}
子分类：{sub_key or '默认'}

当前模板参考：
{current.template_content if current else '无'}

要求：
1. 保持相同的功能和变量
2. 使用不同的表达方式，增加多样性
3. 可以调整语气和风格
4. 确保所有变量都被正确使用

请直接输出新的提示词模板内容："""
        
        try:
            # 调用AI生成新模板
            new_content = await chat_completion(
                messages=[{"role": "user", "content": meta_prompt}],
                model=ai_model
            )
            
            # 清理内容
            new_content = new_content.strip()
            
            # 创建新版本
            new_version = (current.version + 1) if current else 1
            
            template = PromptTemplate(
                template_key=current.template_key if current else f"{category}_{sub_key or 'base'}",
                category=category,
                sub_key=sub_key or "base",
                template_content=new_content,
                variables=self._extract_variables(new_content),
                version=new_version,
                description=f"AI生成版本 {new_version}",
                generation_params={"temperature": 0.9, "model": ai_model},
                last_generated_at=datetime.utcnow()
            )
            
            self.db.add(template)
            
            # 记录历史
            if current:
                history = PromptTemplateHistory(
                    template_id=current.id,
                    template_key=current.template_key,
                    old_content=current.template_content,
                    new_content=new_content,
                    change_reason="AI自动更新",
                    generated_by="scheduled"
                )
                self.db.add(history)
            
            self.db.commit()
            
            logger.info(f"模板 {category}/{sub_key} 已更新到版本 {new_version}")
            return template
            
        except Exception as e:
            logger.error(f"重新生成模板失败: {e}")
            self.db.rollback()
            return None
    
    async def regenerate_all_templates(self, categories: Optional[List[str]] = None):
        """重新生成所有模板"""
        if categories is None:
            categories = list(self.DEFAULT_TEMPLATES.keys())
        
        results = []
        for category in categories:
            # 获取该分类下的所有子分类
            templates = self.db.query(PromptTemplate).filter(
                PromptTemplate.category == category,
                PromptTemplate.is_active == 1
            ).all()
            
            sub_keys = set(t.sub_key for t in templates if t.sub_key)
            if not sub_keys:
                sub_keys = {"base"}
            
            for sub_key in sub_keys:
                result = await self.regenerate_template(category, sub_key)
                results.append({
                    "category": category,
                    "sub_key": sub_key,
                    "success": result is not None
                })
        
        # 清除所有缓存
        self.clear_expired_cache()
        
        return results
    
    def clear_expired_cache(self):
        """清除过期的缓存"""
        deleted = self.db.query(DynamicPrompt).filter(
            DynamicPrompt.expires_at < datetime.utcnow()
        ).delete()
        
        self.db.commit()
        logger.info(f"清除了 {deleted} 条过期缓存")
        return deleted
    
    def get_template_stats(self) -> Dict[str, Any]:
        """获取模板统计信息"""
        stats = {
            "total_templates": self.db.query(PromptTemplate).count(),
            "active_templates": self.db.query(PromptTemplate).filter(
                PromptTemplate.is_active == 1
            ).count(),
            "total_usage": self.db.query(func.sum(PromptTemplate.usage_count)).scalar() or 0,
            "cached_prompts": self.db.query(DynamicPrompt).count(),
            "expired_cache": self.db.query(DynamicPrompt).filter(
                DynamicPrompt.expires_at < datetime.utcnow()
            ).count(),
            "categories": {}
        }
        
        # 按分类统计
        for category in self.DEFAULT_TEMPLATES.keys():
            count = self.db.query(PromptTemplate).filter(
                PromptTemplate.category == category
            ).count()
            usage = self.db.query(func.sum(PromptTemplate.usage_count)).filter(
                PromptTemplate.category == category
            ).scalar() or 0
            stats["categories"][category] = {
                "templates": count,
                "usage": usage
            }
        
        return stats
