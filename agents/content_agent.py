# agents/content_agent.py
# This is where our existing logic for fetching news and using Gemini goes.

import os
import requests
import google.generativeai as genai
from models.a2a import A2AMessage, MessagePart # Import our A2A models

class ContentAgent:
    def __init__(self):
        # Configure APIs inside the agent
        self.gnews_api_key = os.getenv('GNEWS_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not self.gnews_api_key or not self.gemini_api_key:
            raise ValueError("API keys for GNews and Gemini must be set.")
        
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def fetch_latest_news(self, topic: str):
        # (This is the same news fetching logic as before)
        url = f"https://gnews.io/api/v4/search?q={topic}&lang=en&max=1&token={self.gnews_api_key}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get('articles'):
                return data['articles'][0], None
            return None, "No news articles found."
        except requests.exceptions.RequestException as e:
            return None, f"Failed to fetch news: {e}"

    def generate_content_idea(self, topic: str, article: dict):
        # (This is the same Gemini logic as before)
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
        
        # 1. Extract the topic from the user's message
        # The A2A protocol puts the user's text in the 'parts' list
        if not user_message.parts or not user_message.parts[0].text:
            raise ValueError("User message is empty or has no text part.")
        topic = user_message.parts[0].text.strip()

        # 2. Fetch news
        article, error = self.fetch_latest_news(topic)
        if error:
            # If something goes wrong, return an error message as the agent's response
            return A2AMessage(role="agent", parts=[MessagePart(kind="text", text=error)])

        # 3. Generate content idea
        content_idea, error = self.generate_content_idea(topic, article)
        if error:
            return A2AMessage(role="agent", parts=[MessagePart(kind="text", text=error)])

        # 4. Success! Build the agent's response message in the A2A format
        response_text = f"Content Idea:\n{content_idea}\n\nBased on the headline: '{article['title']}'"
        agent_response = A2AMessage(
            role="agent",
            parts=[MessagePart(kind="text", text=response_text)]
        )
        return agent_response