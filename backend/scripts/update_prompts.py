#!/usr/bin/env python3
"""
定时更新提示词模板脚本
建议每天晚上运行一次，保持提示词的新鲜感

使用方法:
1. 宝塔定时任务: /www/server/pyporject_evn/shijieai/bin/python3 /home/py/shijie/scripts/update_prompts.py
2. crontab: 0 2 * * * /www/server/pyporject_evn/shijieai/bin/python3 /home/py/shijie/scripts/update_prompts.py
"""
import asyncio
import sys
import os
from datetime import datetime

# 自动切换到backend目录（确保能正确导入模块和找到数据库）
_script_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.dirname(_script_dir)  # scripts的父目录就是backend
os.chdir(_backend_dir)
sys.path.insert(0, _backend_dir)

# 确保数据库目录存在
_db_dir = os.path.join(_backend_dir, 'data')
if not os.path.exists(_db_dir):
    os.makedirs(_db_dir)

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.prompt_service import PromptService
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def update_all_prompts():
    """更新所有提示词模板"""
    db = SessionLocal()
    
    try:
        service = PromptService(db)
        
        # 先初始化默认模板（如果不存在）
        logger.info("检查并初始化默认模板...")
        service.initialize_default_templates()
        
        # 重新生成所有模板
        logger.info("开始重新生成所有提示词模板...")
        results = await service.regenerate_all_templates()
        
        # 统计结果
        success_count = sum(1 for r in results if r["success"])
        failed_count = len(results) - success_count
        
        logger.info(f"更新完成: 成功 {success_count} 个, 失败 {failed_count} 个")
        
        # 获取统计信息
        stats = service.get_template_stats()
        logger.info(f"当前模板统计:")
        logger.info(f"  - 总模板数: {stats['total_templates']}")
        logger.info(f"  - 活跃模板: {stats['active_templates']}")
        logger.info(f"  - 总使用次数: {stats['total_usage']}")
        logger.info(f"  - 缓存数量: {stats['cached_prompts']}")
        
        # 清理过期缓存
        deleted = service.clear_expired_cache()
        logger.info(f"已清理 {deleted} 条过期缓存")
        
        return {
            "success": True,
            "updated": success_count,
            "failed": failed_count,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"更新提示词模板时出错: {e}")
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        db.close()


async def update_specific_category(category: str):
    """更新指定分类的提示词模板"""
    db = SessionLocal()
    
    try:
        service = PromptService(db)
        
        logger.info(f"开始更新分类 '{category}' 的提示词模板...")
        result = await service.regenerate_template(category)
        
        if result:
            logger.info(f"分类 '{category}' 更新成功，版本: {result.version}")
            return {"success": True, "version": result.version}
        else:
            logger.error(f"分类 '{category}' 更新失败")
            return {"success": False, "error": "更新失败"}
            
    except Exception as e:
        logger.error(f"更新分类 '{category}' 时出错: {e}")
        return {"success": False, "error": str(e)}
    finally:
        db.close()


def main():
    """主函数"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始更新提示词模板...")
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        category = sys.argv[1]
        result = asyncio.run(update_specific_category(category))
    else:
        result = asyncio.run(update_all_prompts())
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 更新完成!")
    print(f"结果: {result}")
    
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    exit(main())
