from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch


class BartSummarizer:
    """
    BART-based summarizer using direct model inference (no pipeline dependency).
    """

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
        self.model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")

        self.model.eval()

    def summarize(self, text: str) -> str:
        if not text or len(text.split()) < 200:
            return ""

        inputs = self.tokenizer(
            text,
            max_length=1024,
            truncation=True,
            return_tensors="pt"
        )

        with torch.no_grad():
            summary_ids = self.model.generate(
                inputs["input_ids"],
                max_length=80,
                min_length=55,
                length_penalty=2.0,
                num_beams=4,
                early_stopping=True
            )

        summary = self.tokenizer.decode(
            summary_ids[0],
            skip_special_tokens=True
        )

        return summary
