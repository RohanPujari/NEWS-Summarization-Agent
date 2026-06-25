import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

class NewsSummarizer:
    def __init__(self):
        self.client = anthropic.Anthropic()
    
    def summarize(self, title, content):
        """Summarize using Claude"""
        
        if not content or len(content) < 50:
            return {
                "summary": None,
                "model": None,
                "error": "Content too short"
            }
        
        try:
            message = self.client.messages.create(
                model="claude-opus-4-6",
                max_tokens=256,
                messages=[{
                    "role": "user",
                    "content": f"Summarize in 80-120 words:\n\nTitle: {title}\n\nContent: {content}"
                }]
            )
            
            summary = message.content[0].text.strip()
            
            return {
                "summary": summary,
                "model": "claude",
                "error": None
            }
        
        except Exception as e:
            return {
                "summary": None,
                "model": None,
                "error": str(e)
            }