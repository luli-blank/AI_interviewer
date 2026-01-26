"""
Web 搜索工具

提供网络搜索能力，用于：
- 查询候选人提到的技术/公司信息
- 获取最新的行业动态
- 验证简历中的信息
"""

import os
import asyncio
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class WebSearchTool:
    """
    Web 搜索工具
    
    集成搜索 API 提供网络搜索能力
    支持多种搜索后端：
    - Tavily (推荐)
    - Serper
    - DuckDuckGo (免费后备)
    """
    
    def __init__(self):
        """初始化 Web 搜索工具"""
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        self._backend = self._determine_backend()
        
    def _determine_backend(self) -> str:
        """确定使用哪个搜索后端"""
        if self.tavily_api_key:
            return "tavily"
        elif self.serper_api_key:
            return "serper"
        else:
            return "duckduckgo"
    
    async def search(
        self,
        query: str,
        max_results: int = 5,
        search_type: str = "general"
    ) -> List[Dict[str, Any]]:
        """
        执行网络搜索
        
        Args:
            query: 搜索查询
            max_results: 最大结果数量
            search_type: 搜索类型 (general, news, technical)
            
        Returns:
            搜索结果列表
        """
        print(f"[Web Search] 🔍 Searching: '{query}' via {self._backend}")
        
        try:
            if self._backend == "tavily":
                return await self._search_tavily(query, max_results, search_type)
            elif self._backend == "serper":
                return await self._search_serper(query, max_results, search_type)
            else:
                return await self._search_duckduckgo(query, max_results)
                
        except Exception as e:
            print(f"[Web Search] ❌ Search error: {e}")
            return []
    
    async def _search_tavily(
        self,
        query: str,
        max_results: int,
        search_type: str
    ) -> List[Dict[str, Any]]:
        """使用 Tavily API 搜索"""
        try:
            from tavily import TavilyClient
            
            client = TavilyClient(api_key=self.tavily_api_key)
            
            # 根据搜索类型调整参数
            search_depth = "advanced" if search_type == "technical" else "basic"
            
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.search(
                    query=query,
                    max_results=max_results,
                    search_depth=search_depth
                )
            )
            
            results = []
            for item in response.get('results', []):
                results.append({
                    "title": item.get('title', ''),
                    "url": item.get('url', ''),
                    "content": item.get('content', ''),
                    "score": item.get('score', 0)
                })
            
            print(f"[Web Search] ✅ Tavily returned {len(results)} results")
            return results
            
        except ImportError:
            print("[Web Search] ⚠️ Tavily not installed, falling back to DuckDuckGo")
            return await self._search_duckduckgo(query, max_results)
        except Exception as e:
            print(f"[Web Search] ❌ Tavily error: {e}")
            return await self._search_duckduckgo(query, max_results)
    
    async def _search_serper(
        self,
        query: str,
        max_results: int,
        search_type: str
    ) -> List[Dict[str, Any]]:
        """使用 Serper API 搜索"""
        import aiohttp
        
        url = "https://google.serper.dev/search"
        headers = {
            "X-API-KEY": self.serper_api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "q": query,
            "num": max_results
        }
        
        if search_type == "news":
            payload["type"] = "news"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        results = []
                        for item in data.get('organic', [])[:max_results]:
                            results.append({
                                "title": item.get('title', ''),
                                "url": item.get('link', ''),
                                "content": item.get('snippet', ''),
                                "score": 1.0
                            })
                        
                        print(f"[Web Search] ✅ Serper returned {len(results)} results")
                        return results
                    else:
                        print(f"[Web Search] ❌ Serper error: {response.status}")
                        return await self._search_duckduckgo(query, max_results)
                        
        except Exception as e:
            print(f"[Web Search] ❌ Serper error: {e}")
            return await self._search_duckduckgo(query, max_results)
    
    async def _search_duckduckgo(
        self,
        query: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """使用 DuckDuckGo 搜索 (免费后备方案)"""
        try:
            from duckduckgo_search import DDGS
            
            loop = asyncio.get_running_loop()
            
            def _sync_search():
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=max_results))
                    return results
            
            raw_results = await loop.run_in_executor(None, _sync_search)
            
            results = []
            for item in raw_results:
                results.append({
                    "title": item.get('title', ''),
                    "url": item.get('href', ''),
                    "content": item.get('body', ''),
                    "score": 0.8  # 默认分数
                })
            
            print(f"[Web Search] ✅ DuckDuckGo returned {len(results)} results")
            return results
            
        except ImportError:
            print("[Web Search] ⚠️ duckduckgo_search not installed")
            return self._get_mock_results(query)
        except Exception as e:
            print(f"[Web Search] ❌ DuckDuckGo error: {e}")
            return self._get_mock_results(query)
    
    def _get_mock_results(self, query: str) -> List[Dict[str, Any]]:
        """获取模拟搜索结果（当所有搜索后端不可用时）"""
        return [{
            "title": f"关于 '{query}' 的搜索结果",
            "url": "https://example.com",
            "content": f"由于搜索服务暂时不可用，无法获取关于 '{query}' 的实时信息。建议稍后重试。",
            "score": 0.0
        }]
    
    async def search_technical_topic(self, topic: str) -> List[Dict[str, Any]]:
        """
        搜索技术主题
        
        Args:
            topic: 技术主题
            
        Returns:
            搜索结果
        """
        query = f"{topic} 技术 面试题 常见问题"
        return await self.search(query, max_results=3, search_type="technical")
    
    async def search_company_info(self, company: str) -> List[Dict[str, Any]]:
        """
        搜索公司信息
        
        Args:
            company: 公司名称
            
        Returns:
            搜索结果
        """
        query = f"{company} 公司 技术团队 业务"
        return await self.search(query, max_results=3, search_type="general")
    
    async def verify_technology(self, tech_name: str) -> Dict[str, Any]:
        """
        验证技术名称并获取相关信息
        
        Args:
            tech_name: 技术名称
            
        Returns:
            技术信息
        """
        results = await self.search(f"{tech_name} 是什么 用途 特点", max_results=3)
        
        if results:
            return {
                "exists": True,
                "name": tech_name,
                "description": results[0].get('content', ''),
                "sources": [r.get('url') for r in results]
            }
        else:
            return {
                "exists": False,
                "name": tech_name,
                "description": "",
                "sources": []
            }
    
    def format_results_for_prompt(self, results: List[Dict[str, Any]]) -> str:
        """
        格式化搜索结果用于 Prompt
        
        Args:
            results: 搜索结果列表
            
        Returns:
            格式化的文本
        """
        if not results:
            return "未找到相关搜索结果。"
        
        formatted = "### 网络搜索结果\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"**{i}. {result.get('title', 'N/A')}**\n"
            formatted += f"   {result.get('content', '')[:200]}...\n"
            formatted += f"   来源: {result.get('url', 'N/A')}\n\n"
        
        return formatted


# 单例实例
web_search_tool = WebSearchTool()
