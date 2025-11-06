"""Dify chatflow service for document processing"""
import logging
from typing import Dict, Any, Optional
from dify_client import AsyncChatClient
from app.config import settings

logger = logging.getLogger(__name__)


class DifyService:
    """Service for interacting with Dify chatflow"""
    
    def __init__(self):
        """Initialize Dify AsyncChatClient configuration"""
        self.api_key = settings.dify_api_key
        self.base_url = settings.dify_base_url
        self.app_id = settings.dify_app_id
        
        # 验证配置
        if not self.api_key:
            logger.warning("Dify API key is not configured. Please set DIFY_API_KEY in .env file")
        else:
            logger.info(f"Dify service initialized with base_url: {self.base_url}")
            if self.app_id:
                logger.info(f"Using Dify App ID: {self.app_id}")
    
    async def process_document(
        self, 
        preview_url: str, 
        user_id: str = "default-user",
        query: str = "请分析这个文档图片"
    ) -> Dict[str, Any]:
        """
        Process document using Dify chat workflow with async client
        
        Args:
            preview_url: URL of the document preview (image)
            query: Query message for the document
            user_id: User identifier
            
        Returns:
            Dictionary containing response and confirmation_record variable
        """
        # 检查 API key
        if not self.api_key:
            logger.error("Dify API key is not configured")
            return {
                "success": False,
                "error": "Dify API key is not configured. Please set DIFY_API_KEY in .env file",
                "confirmation_record": None
            }
        
        try:
            # 准备文件对象（使用 remote_url 方式传递图片）
            file = {
                "type": "image",
                "transfer_method": "remote_url",
                "url": preview_url
            }
            
            # 准备 inputs，将文件作为 front_page 变量传入
            inputs = {
                "front_page": file
            }
            
            logger.info(f"Sending document to Dify: {preview_url}")
            logger.debug(f"Query: {query}, User: {user_id}")
            
            # Use async context manager for proper resource cleanup
            async with AsyncChatClient(api_key=self.api_key) as client:
                # Set base_url if different from default
                if self.base_url:
                    client.base_url = self.base_url
                
                # 发送消息
                response = await client.create_chat_message(
                    inputs=inputs,
                    query=query,
                    user=user_id,
                    response_mode="blocking"
                )
                
                # Raise for HTTP errors
                response.raise_for_status()
                
                # Parse JSON response
                result = response.json()
                
                logger.info(f"Dify response received successfully")
                logger.debug(f"Full response: {result}")
                
                # 获取 conversation_id
                conversation_id = result.get('conversation_id')
                
                # Extract confirmation_record from conversation variables
                confirmation_record = None
                
                if conversation_id:
                    # 使用 get_conversation_variables 获取对话变量
                    try:
                        logger.info(f"Fetching conversation variables for: {conversation_id}")
                        variables_response = await client.get_conversation_variables(
                            conversation_id=conversation_id,
                            user=user_id
                        )
                        variables_response.raise_for_status()
                        variables_data = variables_response.json()
                        
                        logger.debug(f"Conversation variables response: {variables_data}")
                        
                        # 从返回的变量列表中查找 confirmation_record
                        # 返回格式: {"data": [{"name": "...", "value": "...", "value_type": "..."}], "has_more": false}
                        if 'data' in variables_data:
                            variables_list = variables_data['data']
                            if isinstance(variables_list, list):
                                for var in variables_list:
                                    if var.get('name') == 'confirmation_record':
                                        # 获取 value，如果是 JSON 字符串需要解析
                                        value = var.get('value')
                                        value_type = var.get('value_type')
                                        
                                        # 如果是 JSON 类型且是字符串，尝试解析
                                        if value_type == 'json' and isinstance(value, str):
                                            import json
                                            try:
                                                confirmation_record = json.loads(value)
                                            except json.JSONDecodeError:
                                                confirmation_record = value
                                        else:
                                            confirmation_record = value
                                        
                                        logger.info(f"Successfully extracted confirmation_record from variables list")
                                        logger.debug(f"confirmation_record value_type: {value_type}")
                                        break
                        
                        if not confirmation_record:
                            logger.warning(f"confirmation_record not found in conversation variables")
                    
                    except Exception as e:
                        logger.error(f"Failed to get conversation variables: {str(e)}", exc_info=True)
                
                # Fallback: 尝试从其他位置提取
                if not confirmation_record:
                    # Try to get from conversation_variables (for chat apps)
                    if 'conversation_variables' in result:
                        confirmation_record = result['conversation_variables'].get('confirmation_record')
                        logger.debug(f"Found confirmation_record in conversation_variables")
                    
                    # Try to get from workflow outputs
                    if not confirmation_record and 'outputs' in result:
                        confirmation_record = result['outputs'].get('confirmation_record')
                        logger.debug(f"Found confirmation_record in outputs")
                    
                    # Try to get from metadata
                    if not confirmation_record and 'metadata' in result:
                        confirmation_record = result['metadata'].get('confirmation_record')
                        logger.debug(f"Found confirmation_record in metadata")
                
                if not confirmation_record:
                    logger.warning("confirmation_record not found in any location")
                
                return {
                    "success": True,
                    "answer": result.get('answer', ''),
                    "confirmation_record": confirmation_record,
                    "conversation_id": result.get('conversation_id'),
                    "message_id": result.get('id'),
                    "metadata": result.get('metadata', {}),
                    "created_at": result.get('created_at')
                }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error processing document with Dify: {error_msg}", exc_info=True)
            
            # 提供更友好的错误信息
            if "401" in error_msg or "Unauthorized" in error_msg:
                error_msg = "Invalid Dify API key. Please check DIFY_API_KEY in .env file"
            elif "404" in error_msg:
                error_msg = "Dify API endpoint not found. Please check DIFY_BASE_URL in .env file"
            
            return {
                "success": False,
                "error": error_msg,
                "confirmation_record": None
            }


# Singleton instance
dify_service = DifyService()
