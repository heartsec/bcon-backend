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
    
    async def extract_variable(
        self,
        client: AsyncChatClient,
        conversation_id: str,
        variable_name: str,
        user_id: str
    ) -> Optional[Any]:
        """
        从 Dify conversation variables API 提取变量
        
        Args:
            client: AsyncChatClient 实例
            conversation_id: 对话 ID
            variable_name: 要提取的变量名
            user_id: 用户 ID
            
        Returns:
            变量值,如果未找到则返回 None
        """
        if not conversation_id:
            logger.warning(f"Cannot extract '{variable_name}': conversation_id is empty")
            return None
        
        value = await self._get_variable_from_api(
            client=client,
            conversation_id=conversation_id,
            variable_name=variable_name,
            user_id=user_id
        )
        
        if value is not None:
            logger.info(f"Successfully extracted '{variable_name}' from conversation variables API")
            return value
        
        logger.warning(f"Variable '{variable_name}' not found in conversation variables")
        return None
    
    async def extract_multiple_variables(
        self,
        client: AsyncChatClient,
        conversation_id: str,
        variable_names: list[str],
        user_id: str
    ) -> Dict[str, Any]:
        """
        批量提取多个 Dify 对话变量
        
        Args:
            client: AsyncChatClient 实例
            conversation_id: 对话 ID
            variable_names: 要提取的变量名列表
            user_id: 用户 ID
            
        Returns:
            包含所有成功提取变量的字典 {variable_name: value}
        """
        extracted = {}
        
        for var_name in variable_names:
            value = await self.extract_variable(
                client=client,
                conversation_id=conversation_id,
                variable_name=var_name,
                user_id=user_id
            )
            if value is not None:
                extracted[var_name] = value
        
        logger.info(f"Successfully extracted {len(extracted)}/{len(variable_names)} variables: {list(extracted.keys())}")
        return extracted
    
    async def _get_variable_from_api(
        self,
        client: AsyncChatClient,
        conversation_id: str,
        variable_name: str,
        user_id: str
    ) -> Optional[Any]:
        """
        从 Dify conversation variables API 获取变量
        
        Args:
            client: AsyncChatClient 实例
            conversation_id: 对话 ID
            variable_name: 变量名
            user_id: 用户 ID
            
        Returns:
            变量值,如果未找到或出错则返回 None
        """
        try:
            logger.info(f"Fetching conversation variables for: {conversation_id}")
            variables_response = await client.get_conversation_variables(
                conversation_id=conversation_id,
                user=user_id
            )
            variables_response.raise_for_status()
            variables_data = variables_response.json()
            
            logger.debug(f"Conversation variables response: {variables_data}")
            
            # 从返回的变量列表中查找指定变量
            # 返回格式: {"data": [{"name": "...", "value": "...", "value_type": "..."}], "has_more": false}
            if 'data' in variables_data:
                variables_list = variables_data['data']
                if isinstance(variables_list, list):
                    for var in variables_list:
                        if var.get('name') == variable_name:
                            value = self._parse_variable_value(var)
                            logger.debug(f"Found '{variable_name}' with value_type: {var.get('value_type')}")
                            return value
            
            logger.debug(f"Variable '{variable_name}' not found in conversation variables")
            
        except Exception as e:
            logger.error(f"Failed to get conversation variables: {str(e)}", exc_info=True)
        
        return None
    
    @staticmethod
    def _parse_variable_value(var: Dict[str, Any]) -> Any:
        """
        解析变量值,根据 value_type 进行相应处理
        
        Args:
            var: 变量对象,包含 name, value, value_type 等字段
            
        Returns:
            解析后的变量值
        """
        value = var.get('value')
        value_type = var.get('value_type')
        
        # 如果是 JSON 类型且值为字符串,尝试解析
        if value_type == 'json' and isinstance(value, str):
            import json
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON value: {value[:100]}...")
                return value
        
        return value
    
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
                
                # 从 conversation variables API 提取变量
                confirmation_record = await self.extract_variable(
                    client=client,
                    conversation_id=conversation_id,
                    variable_name='confirmation_record',
                    user_id=user_id
                )
                
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
