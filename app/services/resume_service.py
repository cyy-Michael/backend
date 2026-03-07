import base64
import json
import httpx
from typing import Dict, List, Any, Optional
from app.core.config.services import service_settings
from loguru import logger

class ResumeService:
    def __init__(self):
        self.baidu_api_key = service_settings.BAIDU_API_KEY
        self.baidu_secret_key = service_settings.BAIDU_SECRET_KEY
        self.deepseek_api_key = service_settings.DEEPSEEK_API_KEY
        self.deepseek_base_url = service_settings.DEEPSEEK_BASE_URL
        self.baidu_access_token: Optional[str] = None
    
    async def get_baidu_access_token(self) -> str:
        """获取百度 access_token"""
        # 如果已有且不过期，可以直接返回 (这里简化处理，每次都重新获取或简单缓存)
        # 实际生产中应该检查过期时间并缓存
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.baidu_api_key,
            "client_secret": self.baidu_secret_key
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, params=params)
            data = response.json()
            if "access_token" in data:
                return data["access_token"]
            else:
                logger.error(f"Failed to get Baidu access token: {data}")
                raise Exception("Failed to get Baidu access token")

    async def extract_text_from_image(self, image_content: bytes) -> str:
        """使用百度 OCR 提取图片文字"""
        try:
            access_token = await self.get_baidu_access_token()
            url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic?access_token={access_token}"
            
            # 百度 OCR 需要 base64 编码的图片
            img_b64 = base64.b64encode(image_content).decode("utf-8")
            payload = {
                "image": img_b64
            }
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=payload, headers=headers)
                result = response.json()
                
                if "words_result" in result:
                    text_lines = [item["words"] for item in result["words_result"]]
                    return "\n".join(text_lines)
                else:
                    logger.error(f"OCR failed: {result}")
                    return ""
        except Exception as e:
            logger.error(f"OCR error: {str(e)}")
            raise e

    async def analyze_resume_text(self, text: str) -> Dict[str, List[str]]:
        """使用 DeepSeek 分析简历文本，提取研究方向和学术背景"""
        if not text:
            return {"research": [], "background": []}

        prompt = """
        你是一个专业的学术简历分析助手。请分析以下简历内容，提取出用户的“研究方向”和“学术背景”。
        
        请严格按照以下 JSON 格式输出，不要包含任何 Markdown 标记或其他无关文本：
        {
            "research": ["方向1", "方向2", ...],
            "background": ["学历信息", "学校名称", "重要奖项", "发表论文情况", ...]
        }
        
        简历内容如下：
        """
        
        messages = [
            {"role": "system", "content": "你是一个只输出 JSON 格式的助手。"},
            {"role": "user", "content": f"{prompt}\n{text}"}
        ]
        
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.deepseek_base_url}/chat/completions",
                    json=payload,
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    # 清理可能存在的 markdown 代码块标记
                    content = content.replace("```json", "").replace("```", "").strip()
                    try:
                        result = json.loads(content)
                        # 确保返回格式正确
                        return {
                            "research": result.get("research", []),
                            "background": result.get("background", [])
                        }
                    except json.JSONDecodeError:
                        logger.error(f"JSON decode error: {content}")
                        return {"research": [], "background": []}
                else:
                    logger.error(f"DeepSeek API error: {response.text}")
                    return {"research": [], "background": []}
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            return {"research": [], "background": []}

resume_service = ResumeService()
