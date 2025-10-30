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

    # NEW FUNCTION: The first AI step to clean up the user's input
    def extract_topic_with_ai(self, raw_text: str):
        """Uses Gemini to extract a clean search topic from raw text."""
        
        prompt = f"""
        Analyze the following user text and extract a concise, 2-4 word search query topic.
        Your only job is to return the search query topic and nothing else.
        For example, if the user text is "nvidia nvidia give me content ideas on nvidia", you should return "Nvidia stock news".
        If the user text is "tell me about what apple is doing with the iphone 17", you should return "Apple iPhone 17".
        
        User Text: "{raw_text}"
        
        Search Topic:
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Clean up the response to make sure it's just the topic
            clean_topic = response.text.strip().replace("*", "")
            return clean_topic, None
        except Exception as e:
            return None, f"Failed to extract topic with AI: {e}"

    # This function remains the same
    def fetch_latest_news(self, topic: str):
        url = f"https://gnews.io/api/v4/search?q=\"{topic}\"&lang=en&max=1&token={self.gnews_api_key}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get('articles'):
                return data['articles'][0], None
            return None, "No news articles found for the extracted topic."
        except requests.exceptions.RequestException as e:
            return None, f"Failed to fetch news: {e}"

    # This function remains the same
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

    # UPDATED: The main process function now uses the new multi-step logic
    def process_message(self, user_message: A2AMessage) -> A2AMessage:
        """The main entry point for our agent's logic."""
        
        if not user_message.parts or not user_message.parts[0].text:
            raise ValueError("User message is empty or has no text part.")
        
        raw_user_text = user_message.parts[0].text.strip()
        print(f"DEBUG: Received raw text from Telex: '{raw_user_text}'")

        # 1. NEW STEP: Extract a clean topic using AI
        clean_topic, error = self.extract_topic_with_ai(raw_user_text)
        if error:
            return A2AMessage(role="agent", parts=[MessagePart(kind="text", text=error)])
        
        print(f"DEBUG: AI extracted clean topic: '{clean_topic}'")

        # 2. Fetch news using the CLEAN topic
        article, error = self.fetch_latest_news(clean_topic)
        if error:
            return A2AMessage(role="agent", parts=[MessagePart(kind="text", text=error)])

        # 3. Generate content idea using the CLEAN topic and the article
        content_idea, error = self.generate_content_idea(clean_topic, article)
        if error:
            return A2AMessage(role="agent", parts=[MessagePart(kind="text", text=error)])

        # 4. Success! Build the agent's response
        response_text = f"Content Idea:\n{content_idea.strip()}\n\nBased on the headline: '{article['title']}'"
        agent_response = A2AMessage(
            role="agent",
            parts=[MessagePart(kind="text", text=response_text)]
        )
        return agent_response