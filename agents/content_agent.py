# agents/content_agent.py

import os
import requests
import google.generativeai as genai
from models.a2a import A2AMessage, MessagePart

class ContentAgent:
    def __init__(self):
        self.gnews_api_key = os.getenv('GNEWS_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not self.gnews_api_key or not self.gemini_api_key:
            raise ValueError("API keys for GNews and Gemini must be set.")
        
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def extract_topic_with_ai(self, raw_text: str):
        """Uses Gemini to extract a clean, simple search topic from raw text."""
        
        # --- THIS IS THE UPDATED PROMPT ---
        prompt = f"""
        Analyze the following user text and extract only the main subject, entity, or topic.
        Your job is to return a 1-3 word keyword phrase suitable for a news API search.
        Do NOT add extra words like 'news', 'updates', 'stock', or 'information'.

        Example 1:
        User Text: "nvidia nvidia nvidia give me content ideas on nvidia"
        Search Topic: "Nvidia"

        Example 2:
        User Text: "tell me what apple is doing with the iphone 17"
        Search Topic: "iPhone 17"
        
        Example 3:
        User Text: "I want content ideas about breakthroughs in AI"
        Search Topic: "AI breakthroughs"

        User Text: "{raw_text}"
        
        Search Topic:
        """
        # ------------------------------------
        
        try:
            response = self.model.generate_content(prompt)
            clean_topic = response.text.strip().replace("*", "").replace("\"", "")
            return clean_topic, None
        except Exception as e:
            return None, f"Failed to extract topic with AI: {e}"

    def fetch_latest_news(self, topic: str):
        # We'll add quotes around the topic for a more precise search
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
        As a creative strategist, generate a single, compelling content idea (e.g., a YouTube video title and description, or a blog post title).
        The user's topic is: "{topic}"
        A relevant news headline is: "{headline}" (Source: {source})
        Provide a unique, actionable angle.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text, None
        except Exception as e:
            return None, f"Failed to generate content with AI model: {e}"

    def process_message(self, user_message: A2AMessage) -> A2AMessage:
        """The main entry point for our agent's logic."""
        
        if not user_message.parts or not user_message.parts[0].text:
            raise ValueError("User message is empty or has no text part.")
        
        raw_user_text = user_message.parts[0].text.strip()
        print(f"DEBUG: Received raw text from Telex: '{raw_user_text}'")

        clean_topic, error = self.extract_topic_with_ai(raw_user_text)
        if error:
            return A2AMessage(role="agent", parts=[MessagePart(kind="text", text=error)])
        
        print(f"DEBUG: AI extracted clean topic: '{clean_topic}'")

        article, error = self.fetch_latest_news(clean_topic)
        if error:
            return A2AMessage(role="agent", parts=[MessagePart(kind="text", text=error)])

        content_idea, error = self.generate_content_idea(clean_topic, article)
        if error:
            return A2AMessage(role="agent", parts=[MessagePart(kind="text", text=error)])

        response_text = f"Content Idea:\n{content_idea.strip()}\n\nBased on the headline: '{article['title']}'"
        agent_response = A2AMessage(
            role="agent",
            parts=[MessagePart(kind="text", text=response_text)]
        )
        return agent_response