"""
ContentGeneratorAgent测试套件
"""

import asyncio
import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from app.agents.content_generator_agent import (
    ContentGeneratorAgent,
    ContentGenerationRequest,
    GeneratedContent,
    ContentStrategy
)


class TestContentGeneratorAgent:
    """ContentGeneratorAgent测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.agent = ContentGeneratorAgent()
        self.test_user_profile = {
            "user_id": "test_user_123",
            "nickname": "测试用户",
            "interests": ["美妆", "旅行", "美食"],
            "pain_points": ["选择困难", "信息过载"],
            "content_preferences": {"style": "casual", "length": "medium"},
            "engagement_patterns": {"likes": ["教程", "评测"], "comments": ["提问", "分享"]}
        }
    
    @pytest.mark.asyncio
    async def test_generate_content_creative(self):
        """测试创意内容生成"""
        request = ContentGenerationRequest(
            user_profile=self.test_user_profile,
            content_type="creative",
            topic="夏季护肤心得",
            platform="xhs",
            requirements={
                "tone": "friendly",
                "key_points": ["防晒", "补水", "控油"]
            }
        )
        
        # 模拟LLM响应
        mock_response = """
        夏日护肤秘籍大公开！☀️
        
        作为一个混油皮，夏天真的太难了！
        经过无数次踩雷，终于找到了我的夏日护肤公式：
        
        🌟 防晒：安耐晒小金瓶，清爽不油腻
        💧 补水：雅漾喷雾随身带，随时补水
        🛡️ 控油：理肤泉MAT乳，T区救星
        
        #夏日护肤 #混油皮救星 #护肤心得
        """
        
        with patch.object(self.agent.llm_caller, 'call_llm', return_value=mock_response):
            content = await self.agent.generate_content(request)
            
            assert isinstance(content, GeneratedContent)
            assert content.content_id is not None
            assert len(content.title) > 0
            assert len(content.main_content) > 0
            assert len(content.hashtags) > 0
            assert content.platform_specific is not None
    
    @pytest.mark.asyncio
    async def test_generate_content_storytelling(self):
        """测试故事性内容生成"""
        request = ContentGenerationRequest(
            user_profile=self.test_user_profile,
            content_type="storytelling",
            topic="我的第一次独自旅行",
            platform="xhs",
            requirements={
                "character_settings": "25岁女生，第一次独自出国",
                "emotional_objectives": "勇气、成长、自我发现"
            }
        )
        
        mock_response = """
        25岁，我鼓起勇气独自踏上了去日本的旅程✈️
        
        从在机场迷路到在便利店用翻译软件点饭，
        从不敢开口问路到主动和当地人聊天...
        
        原来一个人旅行真的会上瘾！
        
        #独自旅行 #成长日记 #日本旅行
        """
        
        with patch.object(self.agent.llm_caller, 'call_llm', return_value=mock_response):
            content = await self.agent.generate_content(request)
            
            assert isinstance(content, GeneratedContent)
            assert "独自旅行" in content.hashtags or "成长日记" in content.hashtags
    
    @pytest.mark.asyncio
    async def test_generate_content_educational(self):
        """测试教育性内容生成"""
        request = ContentGenerationRequest(
            user_profile=self.test_user_profile,
            content_type="educational",
            topic="新手化妆教程",
            platform="xhs",
            requirements={
                "knowledge_level": "beginner",
                "learning_objectives": "掌握基础化妆步骤",
                "depth": "step_by_step"
            }
        )
        
        mock_response = """
        新手化妆5步曲，手残党也能学会！💄
        
        第一步：妆前保湿（5分钟）
        第二步：底妆打底（3分钟）
        第三步：眉毛修饰（2分钟）
        第四步：眼影晕染（4分钟）
        第五步：口红点睛（1分钟）
        
        总耗时15分钟，通勤妆完成！
        
        #新手化妆教程 #通勤妆容 #化妆小白
        """
        
        with patch.object(self.agent.llm_caller, 'call_llm', return_value=mock_response):
            content = await self.agent.generate_content(request)
            
            assert isinstance(content, GeneratedContent)
            assert "#新手化妆教程" in content.hashtags
    
    @pytest.mark.asyncio
    async def test_generate_content_batch(self):
        """测试批量内容生成"""
        requests = [
            ContentGenerationRequest(
                user_profile=self.test_user_profile,
                content_type="creative",
                topic="夏季穿搭",
                platform="xhs",
                requirements={"tone": "casual"}
            ),
            ContentGenerationRequest(
                user_profile=self.test_user_profile,
                content_type="entertainment",
                topic="周末趣事",
                platform="xhs",
                requirements={"humor_style": "self_deprecating"}
            )
        ]
        
        mock_responses = [
            "夏日清爽穿搭分享～\n\n今天这套真的太凉快了！#夏日穿搭",
            "周末和闺蜜的搞笑日常🤣\n\n谁能想到会这样！#周末趣事"
        ]
        
        with patch.object(self.agent.llm_caller, 'call_llm', side_effect=mock_responses):
            contents = await self.agent.generate_content_batch(requests)
            
            assert len(contents) == 2
            assert all(isinstance(c, GeneratedContent) for c in contents)
    
    @pytest.mark.asyncio
    async def test_platform_optimization(self):
        """测试平台特定优化"""
        content = GeneratedContent(
            content_id="test_123",
            title="测试内容",
            main_content="这是一个很长的内容" * 200,  # 超长内容
            hashtags=["tag1", "tag2", "tag3", "tag4", "tag5", "tag6"],
            media_suggestions={},
            engagement_hooks=[],
            platform_specific={},
            metadata={},
            generation_timestamp=datetime.now(),
            ai_explanation="测试内容"
        )
        
        # 测试小红书优化
        optimized = await self.agent._optimize_for_platform(content, "xhs")
        assert len(optimized.main_content) <= 1000
        assert len(optimized.hashtags) <= 10
        assert "max_chars" in optimized.platform_specific
        
        # 测试微博优化
        optimized = await self.agent._optimize_for_platform(content, "weibo")
        assert len(optimized.main_content) <= 2000
        assert len(optimized.hashtags) <= 20
    
    @pytest.mark.asyncio
    async def test_extract_hashtags(self):
        """测试话题标签提取"""
        content = "这是一个关于#美妆分享#的#小红书#内容"
        hashtags = self.agent._extract_hashtags(content)
        
        assert "美妆分享" in hashtags
        assert "小红书" in hashtags
        assert len(hashtags) == 2
    
    @pytest.mark.asyncio
    async def test_content_quality_validation(self):
        """测试内容质量验证"""
        good_content = GeneratedContent(
            content_id="test_123",
            title="优质内容测试",
            main_content="这是一个内容丰富的测试内容，包含了足够的信息量和有价值的观点。",
            hashtags=["测试", "内容"],
            media_suggestions={"image": "test.jpg"},
            engagement_hooks=["提问", "互动"],
            platform_specific={"max_chars": 1000},
            metadata={},
            generation_timestamp=datetime.now(),
            ai_explanation="这是一个质量较高的内容"
        )
        
        quality_result = await self.agent.validate_content_quality(good_content)
        
        assert 0 <= quality_result["quality_score"] <= 1
        assert isinstance(quality_result["checks"], dict)
        assert isinstance(quality_result["recommendations"], list)
    
    def test_content_type_mapping(self):
        """测试内容类型映射"""
        assert self.agent.content_type_mapping["creative"] == "creative_content_generation"
        assert self.agent.content_type_mapping["storytelling"] == "storytelling_content"
        assert self.agent.content_type_mapping["educational"] == "educational_content"
        assert self.agent.content_type_mapping["entertainment"] == "entertainment_content"
        assert self.agent.content_type_mapping["promotional"] == "promotional_content"
    
    @pytest.mark.asyncio
    async def test_empty_user_context(self):
        """测试空用户上下文处理"""
        empty_profile = {}
        context = await self.agent._get_user_context(empty_profile)
        
        assert "user_insights" in context
        assert "interests" in context
        assert len(context["interests"]) > 0
    
    def test_format_user_profile(self):
        """测试用户画像格式化"""
        profile_data = {
            "user_insights": [{"type": "interest", "content": "美妆"}],
            "interests": ["化妆", "护肤"],
            "pain_points": ["选择困难"],
            "content_preferences": {"style": "casual"},
            "engagement_patterns": {"likes": ["教程"]}
        }
        
        formatted = self.agent._format_user_profile(self.test_user_profile, profile_data)
        
        assert "用户昵称: 测试用户" in formatted
        assert "兴趣领域: 美妆, 旅行, 美食" in formatted
        assert "主要痛点: 选择困难, 信息过载" in formatted


if __name__ == "__main__":
    pytest.main([__file__])