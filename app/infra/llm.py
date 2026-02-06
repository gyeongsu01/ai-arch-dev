# app/infra/llm.py
from __future__ import annotations
from typing import Any, Dict, List, Optional
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.infra.config import Config

# 실제 운영 시엔 langchain_openai 등 사용
# 여기선 시뮬레이터 구현을 Real LLM으로 교체

# 전역 변수로 두기보다 메서드 인자로 받는 것이 깔끔하지만, 
# 기존 코드 구조 유지를 위해 활용하거나 메서드 내부로 이동
DEFAULT_SYSTEM_PROMPT = """You are a helpful AI assistant that can use tools to help answer user queries.
Analyze the user's request and determine if any available tools should be used."""

class LLMClient:
    def __init__(self):
        # Gemini 모델 초기화
        self.llm = ChatGoogleGenerativeAI(
            model=Config.LLM_MODEL_NAME,
            temperature=0,
            google_api_key=Config.GOOGLE_API_KEY, 
            convert_system_message_to_human=True
        )

    def predict_tool_call(self, system_prompt: str, user_query: str, tools_desc: str) -> Optional[Dict[str, Any]]:
        """
        LLM에게 상황을 설명하고, 사용할 도구가 있다면 JSON 포맷으로 응답받음
        """
        # 만약 호출부에서 system_prompt를 안 넘겨주면 기본값 사용
        if not system_prompt:
            system_prompt = DEFAULT_SYSTEM_PROMPT

        prompt = f"""
        {system_prompt}
        
        [Available Tools]
        {tools_desc}
        
        [Instruction]
        1. Analyze the user's query.
        2. If a tool is needed, respond strictly in JSON format:
           {{ "action_id": "tool_id", "params": {{ "param_name": "value" }} }}
        3. If no tool is needed, respond with just the text: "NO_TOOL"
        4. Do NOT include markdown code blocks (```json ... ```). Just raw JSON string.
        
        User Query: {user_query}
        """

        messages = [HumanMessage(content=prompt)]
        response = self.llm.invoke(messages)
        content = response.content.strip()

        # 디버깅용 출력
        # print(f"DEBUG: LLM RAW OUTPUT: {content}")

        if "NO_TOOL" in content:
            return None
        
        try:
            if "```" in content:
                # 첫 번째 ```json (또는 그냥 ```) 과 마지막 ``` 사이의 내용 추출
                content = content.split("```")[1]
                if content.strip().startswith("json"):
                    content = content.strip()[4:]
            
            tool_call = json.loads(content.strip())
            return tool_call
        except json.JSONDecodeError:
            print(f"ERROR: Failed to parse LLM output as JSON. Output: {content}")
            return None
    
    def generate_response(self, query: str, tool_result: List[Dict[str, Any]]) -> str:
        """
        도구 실행 결과를 바탕으로 최종 응답 생성
        """
        context = ""
        if tool_result:
            context = f"[Context from Tools]\n{json.dumps(tool_result, ensure_ascii=False, indent=2)}"

        prompt = f"""
        User Query: {query}

        {context}

        Please provide a helpful response based on the context above.
        If the context is empty, answer based on your general knowledge.
        """

        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content

# FakeLLM 별칭 (기존 코드 호환성용)
FakeLLM = LLMClient