# agents/content_agent.py

import os
import requests
from uuid import uuid4
import google.generativeai as genai
from models.a2a import A2AMessage, MessagePart, TaskResult, TaskStatus, Artifact

class ContentAgent:
    def __init__(self):
        self.gnews_api_key = os.getenv('GNEWS_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not self.gnews_api_key or not self.gemini_api_key:
            raise ValueError("API keys for GNews and Gemini must be set.")
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash') 

    def extract_topic_with_ai(self, raw_text: str):
        prompt = f"""
        Analyze the following user text and extract only the main subject, entity, or topic.
        Your job is to return a 1-3 word keyword phrase suitable for a news API search.
        Do NOT add extra words like 'news', 'updates', 'stock', or 'information'.
        Example 1: User Text: "nvidia nvidia nvidia" -> Search Topic: "Nvidia"
        Example 2: User Text: "tell me what apple is doing with the iphone 17" -> Search Topic: "iPhone 17"
        User Text: "{raw_text}"
        Search Topic:
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip().replace("*", "").replace("\"", ""), None
        except Exception as e:
            return None, f"Failed to extract topic with AI: {e}"

    def fetch_latest_news(self, topic: str):
        url = f"https://gnews.io/api/v4/search?q=\"{topic}\"&lang=en&max=1&token={self.gnews_api_key}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get('articles'):
                return data['articles'][0], None
            return None, f"No news articles found for the topic: '{topic}'"
        except requests.exceptions.RequestException as e:
            return None, f"Failed to fetch news: {e}"

    def generate_content_idea(self, topic: str, article: dict):
        headline = article['title']
        source = article['source']['name']
        prompt = f"""
        As a creative strategist, generate a single, compelling content idea (e.g., a YouTube video title and description).
        The user's topic is: "{topic}"
        A relevant news headline is: "{headline}" (Source: {source})
        Provide a unique, actionable angle.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text, None
        except Exception as e:
            return None, f"Failed to generate content with AI model: {e}"

    def process_message(self, user_message: A2AMessage, task_id: str = None, context_id: str = None) -> TaskResult:
        task_id = task_id or str(uuid4())
        context_id = context_id or str(uuid4())
        
        try:
            raw_user_text = user_message.parts[0].text.strip()
            clean_topic, error = self.extract_topic_with_ai(raw_user_text)
            if error: raise Exception(error)
            
            article, error = self.fetch_latest_news(clean_topic)
            if error: raise Exception(error)
            
            content_idea, error = self.generate_content_idea(clean_topic, article)
            if error: raise Exception(error)
            
            # --- Build the A2A Compliant Response ---
            response_text = f"Content Idea:\n{content_idea.strip()}\n\nBased on the headline: '{article['title']}'"
            agent_response_message = A2AMessage(role="agent", parts=[MessagePart(kind="text", text=response_text)], taskId=task_id)

            return TaskResult(
                id=task_id,
                contextId=context_id,
                status=TaskStatus(state="completed", message=agent_response_message),
                artifacts=[
                    Artifact(name="content_idea", parts=[MessagePart(kind="text", text=response_text)])
                ],
                history=[user_message, agent_response_message],
            )
        except Exception as e:
            error_message = A2AMessage(role="agent", parts=[MessagePart(kind="text", text=str(e))], taskId=task_id)
            return TaskResult(
                id=task_id,
                contextId=context_id,
                status=TaskStatus(state="failed", message=error_message),
                history=[user_message, error_message]
            )