"""
Faithfulness and Coverage Validation for Summarization Models
Validates if summaries are hallucinating or missing key information
"""

import nltk
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer, util
import spacy
import torch

# Download required NLTK data
nltk.download('punkt', quiet=True)

class SummarizationValidator:
    """
    Validates summaries using Faithfulness and Coverage metrics
    
    Faithfulness: Does summary contain only facts from original?
    Coverage: Does summary include main points from original?
    """
    
    def __init__(self):
        # Load sentence embedding model (converts text to vectors)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load NLP model (for entity extraction like names, places)
        self.nlp = spacy.load('en_core_web_sm')
    
    # ============================================
    # METRIC 1: FAITHFULNESS (No Hallucination)
    # ============================================
    
    def calculate_faithfulness(self, original_text, summary):
        """
        Faithfulness Check: How much of summary is actually in original?
        
        High faithfulness = No hallucination (GOOD)
        Low faithfulness = Summary makes up facts (BAD - HALLUCINATING)
        """
        
        # Step 1: Break into sentences
        original_sentences = sent_tokenize(original_text)
        summary_sentences = sent_tokenize(summary)
        
        print("\n" + "="*70)
        print("FAITHFULNESS CHECK - Does summary contain only true facts?")
        print("="*70)
        print(f"Original: {len(original_sentences)} sentences")
        print(f"Summary: {len(summary_sentences)} sentences")
        
        # Step 2: Convert sentences to vectors
        original_embeddings = self.embedding_model.encode(
            original_sentences, 
            convert_to_tensor=True
        )
        summary_embeddings = self.embedding_model.encode(
            summary_sentences, 
            convert_to_tensor=True
        )
        
        # Step 3: For each summary sentence, find best match in original
        faithful_sentences = 0
        hallucinated_sentences = []
        
        for i, summary_sent in enumerate(summary_sentences):
            summary_emb = summary_embeddings[i]
            
            # Find most similar original sentence
            similarities = util.pytorch_cos_sim(
                summary_emb, 
                original_embeddings
            )[0]
            
            max_similarity = max(similarities).item()
            best_match_idx = torch.argmax(similarities).item()
            
            # If similarity > 0.5, consider it faithful
            if max_similarity > 0.5:
                faithful_sentences += 1
                status = "FAITHFUL"
            else:
                hallucinated_sentences.append(summary_sent)
                status = "HALLUCINATED"
            
            print(f"\nSentence {i+1}: {status} (similarity: {max_similarity:.2f})")
            print(f"  Summary: {summary_sent[:70]}...")
            print(f"  Match: {original_sentences[best_match_idx][:70]}...")
        
        # Calculate faithfulness score
        faithfulness_score = (
            faithful_sentences / len(summary_sentences) 
            if summary_sentences 
            else 0
        )
        
        print(f"\nFAITHFULNESS SCORE: {faithfulness_score:.1%}")
        print(f"({faithful_sentences}/{len(summary_sentences)} sentences are faithful)")
        
        if hallucinated_sentences:
            print(f"\nWARNING - HALLUCINATED SENTENCES:")
            for sent in hallucinated_sentences:
                print(f"  - {sent}")
        
        return {
            "faithfulness_score": faithfulness_score,
            "faithful_sentences": faithful_sentences,
            "total_sentences": len(summary_sentences),
            "hallucinated_sentences": hallucinated_sentences,
            "is_hallucinating": faithfulness_score < 0.8,
        }
    
    # ============================================
    # METRIC 2: COVERAGE (Missing Information)
    # ============================================
    
    def calculate_coverage(self, original_text, summary):
        """
        Coverage Check: Does summary include main points from original?
        
        High coverage = Summary captures key info (GOOD)
        Low coverage = Summary misses important points (BAD)
        """
        
        # Step 1: Extract important entities (names, places, organizations)
        original_doc = self.nlp(original_text)
        summary_doc = self.nlp(summary)
        
        # Get entities from original
        original_entities = set()
        for ent in original_doc.ents:
            original_entities.add((ent.text.lower(), ent.label_))
        
        # Get entities from summary
        summary_entities = set()
        for ent in summary_doc.ents:
            summary_entities.add((ent.text.lower(), ent.label_))
        
        print("\n" + "="*70)
        print("COVERAGE CHECK - Does summary cover main points?")
        print("="*70)
        print(f"Original entities: {original_entities}")
        print(f"Summary entities: {summary_entities}")
        
        # Step 2: Check coverage of key entities
        covered_entities = summary_entities & original_entities
        missing_entities = original_entities - summary_entities
        
        entity_coverage = (
            len(covered_entities) / len(original_entities)
            if original_entities
            else 0
        )
        
        print(f"\nCovered entities ({len(covered_entities)}/{len(original_entities)}):")
        for ent in covered_entities:
            print(f"  - {ent[0]} ({ent[1]})")
        
        if missing_entities:
            print(f"\nMissing entities ({len(missing_entities)}):")
            for ent in missing_entities:
                print(f"  - {ent[0]} ({ent[1]})")
        
        # Step 3: Check coverage of important sentences
        original_sentences = sent_tokenize(original_text)
        
        original_embeddings = self.embedding_model.encode(
            original_sentences,
            convert_to_tensor=True
        )
        summary_embeddings = self.embedding_model.encode(
            summary,
            convert_to_tensor=True
        )
        summary_emb = torch.mean(summary_embeddings, dim=0)
        
        # Similarity of each original sentence to summary
        sentence_importances = util.pytorch_cos_sim(
            original_embeddings,
            summary_emb.unsqueeze(0)
        ).squeeze()
        
        # Get top-N important sentences
        top_n = min(3, len(original_sentences))
        top_indices = torch.topk(sentence_importances, top_n).indices
        
        covered_important = 0
        print(f"\nKey sentences coverage:")
        for idx in top_indices:
            sent = original_sentences[idx]
            similarity = sentence_importances[idx].item()
            
            if similarity > 0.4:
                covered_important += 1
                status = "COVERED"
            else:
                status = "MISSING"
            
            print(f"  {status}: {sent[:70]}... (similarity: {similarity:.2f})")
        
        # Calculate coverage score
        sentence_coverage = covered_important / top_n if top_n > 0 else 0
        
        # Combined coverage (60% entities, 40% key sentences)
        coverage_score = (0.6 * entity_coverage) + (0.4 * sentence_coverage)
        
        print(f"\nCOVERAGE SCORE: {coverage_score:.1%}")
        print(f"(Entity coverage: {entity_coverage:.1%}, Key sentence coverage: {sentence_coverage:.1%})")
        
        return {
            "coverage_score": coverage_score,
            "entity_coverage": entity_coverage,
            "sentence_coverage": sentence_coverage,
            "covered_entities": covered_entities,
            "missing_entities": missing_entities,
            "is_incomplete": coverage_score < 0.6,
        }
    
    # ============================================
    # COMBINED VALIDATION
    # ============================================
    
    def validate_summary(self, original_text, summary):
        """
        Run both Faithfulness and Coverage checks
        Returns overall quality score
        """
        
        print("\n\n" + "="*70)
        print("SUMMARY VALIDATION")
        print("="*70)
        
        print(f"\nORIGINAL TEXT:")
        print(f"{original_text[:300]}...\n")
        
        print(f"SUMMARY:")
        print(f"{summary}\n")
        
        # Calculate both metrics
        faithfulness = self.calculate_faithfulness(original_text, summary)
        coverage = self.calculate_coverage(original_text, summary)
        
        # Make decision
        print("\n" + "="*70)
        print("FINAL VERDICT")
        print("="*70)
        
        if faithfulness['is_hallucinating']:
            print("WARNING - HALLUCINATION DETECTED")
            print("Summary contains facts not in original")
        else:
            print("PASS - No hallucination detected")
        
        if coverage['is_incomplete']:
            print("WARNING - INCOMPLETE COVERAGE")
            print("Summary misses important information")
        else:
            print("PASS - Good coverage of key points")
        
        # Overall quality
        overall_quality = (
            (faithfulness['faithfulness_score'] * 0.5) +
            (coverage['coverage_score'] * 0.5)
        )
        
        print(f"\nOVERALL QUALITY SCORE: {overall_quality:.1%}")
        
        if overall_quality >= 0.8:
            print("Status: GOOD QUALITY")
        elif overall_quality >= 0.6:
            print("Status: ACCEPTABLE")
        else:
            print("Status: POOR QUALITY")
        
        return {
            "faithfulness": faithfulness,
            "coverage": coverage,
            "overall_quality": overall_quality,
            "is_valid": overall_quality >= 0.6 and not faithfulness['is_hallucinating'],
        }


# ============================================
# TEST CASES
# ============================================

if __name__ == "__main__":
    validator = SummarizationValidator()
    
    # TEST 1: GOOD Summary
    print("\n\n" + "="*70)
    print("TEST 1: GOOD SUMMARY (Claude should get this right)")
    print("="*70)
    
    original1 = """
    David Sullivan, billionaire co-owner of West Ham United, has been accused 
    by multiple women of abusing his power and preying on women for sex. 
    The BBC conducted a year-long investigation into the allegations. 
    Multiple victims came forward with similar stories. 
    Sullivan has denied all allegations.
    """
    
    summary1 = """
    Billionaire West Ham owner David Sullivan has been accused by multiple women 
    of abusing his power and preying on women for sex. The BBC's year-long 
    investigation corroborates these allegations. Sullivan denies the accusations.
    """
    
    result1 = validator.validate_summary(original1, summary1)
    
    # TEST 2: HALLUCINATING Summary
    print("\n\n" + "="*70)
    print("TEST 2: HALLUCINATING SUMMARY (This should fail validation)")
    print("="*70)
    
    original2 = original1
    
    summary2 = """
    George W. Sullivan, former chief of staff to Barack Obama, met with 
    the Duchess of Cornwall regarding Princess Diana's estate matters. 
    The meeting took place in Washington DC.
    """
    
    result2 = validator.validate_summary(original2, summary2)
    
    # TEST 3: INCOMPLETE Summary
    print("\n\n" + "="*70)
    print("TEST 3: INCOMPLETE SUMMARY (Missing key information)")
    print("="*70)
    
    summary3 = """
    David Sullivan has been accused of misconduct.
    """
    
    result3 = validator.validate_summary(original1, summary3)
    
    # COMPARISON
    print("\n\n" + "="*70)
    print("COMPARISON OF ALL SUMMARIES")
    print("="*70)
    
    summaries = [
        ("Good (Claude)", result1),
        ("Hallucinating (Pegasus)", result2),
        ("Incomplete", result3),
    ]
    
    for name, result in summaries:
        print(f"\n{name}:")
        print(f"  Faithfulness: {result['faithfulness']['faithfulness_score']:.1%}")
        print(f"  Coverage: {result['coverage']['coverage_score']:.1%}")
        print(f"  Overall Quality: {result['overall_quality']:.1%}")
        print(f"  Valid: {result['is_valid']}")