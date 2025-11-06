"""测试日志配置"""
import logging
from app.config import settings

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

# 测试各种级别的日志
logger.debug("这是一条 DEBUG 日志")
logger.info("这是一条 INFO 日志")
logger.warning("这是一条 WARNING 日志")
logger.error("这是一条 ERROR 日志")
logger.critical("这是一条 CRITICAL 日志")

print(f"\n当前日志级别: {settings.log_level}")
print("如果你能看到 DEBUG 日志，说明配置成功！")
