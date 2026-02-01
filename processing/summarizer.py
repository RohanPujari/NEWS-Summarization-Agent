from transformers import PegasusTokenizer, PegasusForConditionalGeneration
import torch


class PegasusSummarizer:
    def __init__(self):
        model_name = "google/pegasus-xsum"
        self.tokenizer = PegasusTokenizer.from_pretrained(model_name)
        self.model = PegasusForConditionalGeneration.from_pretrained(model_name)
        self.model.eval()

    def summarize(self, text: str) -> str:
        inputs = self.tokenizer(
            text,
            truncation=True,
            padding="longest",
            return_tensors="pt"
        )

        with torch.no_grad():
            summary_ids = self.model.generate(
                inputs["input_ids"],
                max_length=120,
                min_length=60,
                num_beams=4,
                early_stopping=True
            )

        return self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)


