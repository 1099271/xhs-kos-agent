"""
内容生成Agent
基于用户画像和分析结果，生成个性化的高质量内容
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import asyncio
import json

from app.agents.llm_manager import AgentLLMCaller, ModelProvider
from app.agents.llamaindex_manager import LlamaIndexManager
from app.prompts.content_generator_prompts import get_content_generator_prompt
from app.prompts import PromptManager
from app.utils.logger import app_logger as logger


@dataclass
class ContentGenerationRequest:
    """内容生成请求"""
    user_profile: Dict[str, Any]
    content_type: str  # "creative", "storytelling", "educational", "entertainment", "promotional"
    topic: str
    platform: str  # "xhs", "weibo", "douyin", etc.
    requirements: Dict[str, Any]
    brand_guidelines: Optional[Dict[str, Any]] = None
    constraints: Optional[Dict[str, Any]] = None


@dataclass
class GeneratedContent:
    """生成的内容结果"""
    content_id: str
    title: str
    main_content: str
    hashtags: List[str]
    media_suggestions: Dict[str, Any]
    engagement_hooks: List[str]
    platform_specific: Dict[str, str]
    metadata: Dict[str, Any]
    generation_timestamp: datetime
    ai_explanation: str


@dataclass
class ContentStrategy:
    """内容策略配置"""
    tone: str  # "professional", "casual", "humorous", "inspiring", etc.
    style: str  # "storytelling", "educational", "entertaining", "promotional"
    target_emotion: str  # "curiosity", "trust", "excitement", "relatability"
    call_to_action: str
    engagement_priority: List[str]  # 优先级排序的参与目标


class ContentGeneratorAgent:
    """内容生成智能体 - 基于用户洞察生成个性化内容"""
    
    def __init__(self, preferred_model_provider: Optional[ModelProvider] = None):
        self.name = "ContentGeneratorAgent"
        self.llm_caller = AgentLLMCaller(self.name, preferred_model_provider)
        self.llamaindex_manager = LlamaIndexManager()
        self.prompt_manager = PromptManager()
        
        # 内容类型映射
        self.content_type_mapping = {
            "creative": "creative_content_generation",
            "storytelling": "storytelling_content", 
            "educational": "educational_content",
            "entertainment": "entertainment_content",
            "promotional": "promotional_content"
        }
        
        logger.info("ContentGeneratorAgent initialized")
    
    async def generate_content(
        self, 
        request: ContentGenerationRequest
    ) -> GeneratedContent:
        """生成个性化内容"""
        try:
            logger.info(f"Starting content generation for user: {request.user_profile.get('user_id', 'unknown')}")
            
            # 1. 基于用户画像获取上下文信息
            context_info = await self._get_user_context(request.user_profile)
            
            # 2. 构建内容生成提示词
            prompt = self._build_generation_prompt(request, context_info)
            
            # 3. 调用LLM生成内容
            response = await self.llm_caller.call_llm(prompt)
            
            # 4. 解析和优化生成结果
            content = self._parse_generated_content(response, request)
            
            # 5. 添加平台特定优化
            platform_optimized = await self._optimize_for_platform(content, request.platform)
            
            logger.info(f"Content generation completed for content_id: {content.content_id}")
            return platform_optimized
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise
    
    async def generate_content_batch(
        self, 
        requests: List[ContentGenerationRequest]
    ) -> List[GeneratedContent]:
        """批量生成内容"""
        logger.info(f"Starting batch content generation for {len(requests)} requests")
        
        tasks = [self.generate_content(request) for request in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 过滤掉异常结果
        valid_results = [r for r in results if not isinstance(r, Exception)]
        failed_count = len(results) - len(valid_results)
        
        if failed_count > 0:
            logger.warning(f"Batch generation completed with {failed_count} failures")
        
        return valid_results
    
    async def _get_user_context(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """获取用户上下文信息用于内容个性化"""
        try:
            user_id = user_profile.get('user_id')
            if not user_id:
                return self._get_default_context()
            
            # 使用LlamaIndex获取用户相关内容
            semantic_results = await self.llamaindex_manager.query_user_content(
                query=f"用户{user_id}的兴趣偏好和行为模式",
                user_id=user_id,
                top_k=5
            )
            
            # 提取关键词和主题
            interests = user_profile.get('interests', [])
            pain_points = user_profile.get('pain_points', [])
            content_preferences = user_profile.get('content_preferences', {})
            
            return {
                "user_insights": semantic_results,
                "interests": interests,
                "pain_points": pain_points,
                "content_preferences": content_preferences,
                "engagement_patterns": user_profile.get('engagement_patterns', {})
            }
            
        except Exception as e:
            logger.warning(f"Failed to get user context: {str(e)}")
            return self._get_default_context()
    
    def _build_generation_prompt(
        self, 
        request: ContentGenerationRequest, 
        context_info: Dict[str, Any]
    ) -> str:
        """构建内容生成提示词"""
        
        # 获取对应的提示词模板
        content_type_key = self.content_type_mapping.get(request.content_type, "creative_content_generation")
        prompt_template = get_content_generator_prompt(content_type_key)
        
        # 构建变量映射
        variables = {
            "target_audience_profile": self._format_user_profile(request.user_profile, context_info),
            "content_requirements": json.dumps(request.requirements, ensure_ascii=False, indent=2),
            "brand_tone_guidelines": json.dumps(request.brand_guidelines or {}, ensure_ascii=False, indent=2),
            "creative_constraints": json.dumps(request.constraints or {}, ensure_ascii=False, indent=2)
        }
        
        # 处理特定内容类型的额外变量
        if request.content_type == "storytelling":
            variables.update({
                "story_theme": request.topic,
                "character_settings": request.requirements.get('character_settings', ''),
                "plot_requirements": request.requirements.get('plot_requirements', ''),
                "emotional_objectives": request.requirements.get('emotional_objectives', '')
            })
        elif request.content_type == "educational":
            variables.update({
                "knowledge_topic": request.topic,
                "audience_knowledge_level": request.requirements.get('knowledge_level', 'beginner'),
                "learning_objectives": request.requirements.get('learning_objectives', ''),
                "content_depth_requirements": request.requirements.get('depth', 'intermediate')
            })
        elif request.content_type == "promotional":
            variables.update({
                "product_service_info": request.requirements.get('product_info', ''),
                "sales_objectives": request.requirements.get('sales_goals', ''),
                "target_customer_profile": self._format_user_profile(request.user_profile, context_info),
                "competitive_advantages": request.requirements.get('competitive_advantages', '')
            })
        else:
            variables["content_requirements"] = f"主题: {request.topic}\n" + variables["content_requirements"]
        
        return prompt_template.format(**variables)
    
    def _format_user_profile(self, user_profile: Dict[str, Any], context_info: Dict[str, Any]) -> str:
        """格式化用户画像信息"""
        profile_parts = []
        
        # 基本信息
        if 'nickname' in user_profile:
            profile_parts.append(f"用户昵称: {user_profile['nickname']}")
        
        # 兴趣偏好
        interests = context_info.get('interests', [])
        if interests:
            profile_parts.append(f"兴趣领域: {', '.join(interests)}")
        
        # 痛点需求
        pain_points = context_info.get('pain_points', [])
        if pain_points:
            profile_parts.append(f"主要痛点: {', '.join(pain_points)}")
        
        # 内容偏好
        content_prefs = context_info.get('content_preferences', {})
        if content_prefs:
            profile_parts.append(f"内容偏好: {json.dumps(content_prefs, ensure_ascii=False)}")
        
        # 参与模式
        engagement = context_info.get('engagement_patterns', {})
        if engagement:
            profile_parts.append(f"互动习惯: {json.dumps(engagement, ensure_ascii=False)}")
        
        return "\n".join(profile_parts)
    
    def _parse_generated_content(
        self, 
        llm_response: str, 
        request: ContentGenerationRequest
    ) -> GeneratedContent:
        """解析LLM生成的内容"""
        import uuid
        
        # 这里简化处理，实际应该解析结构化响应
        content_id = str(uuid.uuid4())
        
        # 提取标题（假设在第一行）
        lines = llm_response.strip().split('\n')
        title = lines[0] if lines else "未命名内容"
        
        # 提取话题标签
        hashtags = self._extract_hashtags(llm_response)
        
        # 生成内容元数据
        metadata = {
            "request_id": content_id,
            "content_type": request.content_type,
            "platform": request.platform,
            "user_id": request.user_profile.get("user_id"),
            "generation_model": self.llm_caller.model_name
        }
        
        return GeneratedContent(
            content_id=content_id,
            title=title,
            main_content=llm_response,
            hashtags=hashtags,
            media_suggestions={},
            engagement_hooks=[],
            platform_specific={},
            metadata=metadata,
            generation_timestamp=datetime.now(),
            ai_explanation="基于用户画像和上下文信息生成的个性化内容"
        )
    
    def _extract_hashtags(self, content: str) -> List[str]:
        """从内容中提取话题标签"""
        import re
        
        # 匹配中文和英文的话题标签
        hashtags = re.findall(r'#([\u4e00-\u9fa5\w]+)', content)
        
        # 如果提取不到，生成默认标签
        if not hashtags:
            hashtags = ["内容分享", "生活记录", "今日分享"]
        
        return list(set(hashtags))[:10]  # 限制最多10个标签
    
    async def _optimize_for_platform(
        self, 
        content: GeneratedContent, 
        platform: str
    ) -> GeneratedContent:
        """针对特定平台优化内容"""
        platform_optimizations = {
            "xhs": {
                "max_chars": 1000,
                "hashtag_limit": 10,
                "visual_priority": "high",
                "tone": "friendly"
            },
            "weibo": {
                "max_chars": 2000,
                "hashtag_limit": 20,
                "trending_focus": True,
                "tone": "casual"
            },
            "douyin": {
                "max_chars": 500,
                "hashtag_limit": 5,
                "video_first": True,
                "tone": "entertaining"
            }
        }
        
        optimization = platform_optimizations.get(platform, platform_optimizations["xhs"])
        
        # 应用平台限制
        max_chars = optimization["max_chars"]
        if len(content.main_content) > max_chars:
            content.main_content = content.main_content[:max_chars-3] + "..."
        
        # 限制标签数量
        max_hashtags = optimization["hashtag_limit"]
        content.hashtags = content.hashtags[:max_hashtags]
        
        # 添加平台特定字段
        content.platform_specific = optimization
        
        return content
    
    def _get_default_context(self) -> Dict[str, Any]:
        """获取默认上下文"""
        return {
            "user_insights": [],
            "interests": ["general"],
            "pain_points": ["information_overload"],
            "content_preferences": {"style": "balanced"},
            "engagement_patterns": {"type": "casual"}
        }
    
    async def validate_content_quality(self, content: GeneratedContent) -> Dict[str, Any]:
        """验证生成内容的质量"""
        quality_checks = {
            "length_appropriate": len(content.main_content) > 50,
            "has_hashtags": len(content.hashtags) > 0,
            "engagement_hooks": len(content.engagement_hooks) >= 2,
            "platform_optimized": bool(content.platform_specific),
            "ai_explanation": bool(content.ai_explanation)
        }
        
        overall_score = sum(quality_checks.values()) / len(quality_checks)
        
        return {
            "quality_score": overall_score,
            "checks": quality_checks,
            "recommendations": self._get_quality_recommendations(quality_checks)
        }
    
    def _get_quality_recommendations(self, checks: Dict[str, bool]) -> List[str]:
        """获取质量改进建议"""
        recommendations = []
        
        if not checks.get("length_appropriate", False):
            recommendations.append("内容过短，建议增加更多有价值的信息")
        
        if not checks.get("has_hashtags", False):
            recommendations.append("建议添加相关话题标签以提高发现性")
        
        if not checks.get("engagement_hooks", False):
            recommendations.append("建议增加更多互动元素以提高用户参与度")
        
        return recommendations