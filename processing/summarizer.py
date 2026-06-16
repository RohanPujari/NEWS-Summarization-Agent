import os
from dotenv import load_dotenv
load_dotenv()

import anthropic
from transformers import PegasusForConditionalGeneration, PegasusTokenizer

class NewsSummarizer:
    def __init__(self, use_claude=True, pegasus_fallback=True):
        self.use_claude = use_claude
        self.pegasus_fallback = pegasus_fallback
        
        if use_claude:
            self.client = anthropic.Anthropic()  # ← THIS LINE FIXED
        
        if pegasus_fallback:
            self.tokenizer = PegasusTokenizer.from_pretrained("google/pegasus-xsum")
            self.model = PegasusForConditionalGeneration.from_pretrained("google/pegasus-xsum")
    
    def summarize(self, title: str, content: str, use_claude=None):
        """Summarize with Claude, fallback to Pegasus"""
        
        if use_claude is None:
            use_claude = self.use_claude
        
        # Try Claude first
        if use_claude:
            try:
                summary = self._claude_summarize(title, content)
                return {"summary": summary, "model": "claude"}
            except Exception as e:
                print(f"Claude failed: {e}, falling back to Pegasus...")
        
        # Fallback to Pegasus
        if self.pegasus_fallback:
            summary = self._pegasus_summarize(title, content)
            return {"summary": summary, "model": "pegasus"}
        
        return {"summary": None, "model": None, "error": "All models failed"}
    
    def _claude_summarize(self, title: str, content: str) -> str:
        """Use Claude API for better quality"""
        prompt = f"""Summarize this news article in 80-120 words, capture the key facts.

Title: {title}
Content: {content}

Summary:"""
        
        message = self.client.messages.create(
            model="claude-opus-4-20250805",
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text.strip()
    
    def _pegasus_summarize(self, title: str, content: str) -> str:
        """Fallback to free Pegasus model"""
        combined_text = f"{title}. {content}"
        inputs = self.tokenizer.encode(combined_text, return_tensors="pt", max_length=1024, truncation=True)
        summary_ids = self.model.generate(inputs, max_length=120, min_length=60, do_sample=False)
        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary