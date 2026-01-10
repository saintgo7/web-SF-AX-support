"""Semantic similarity module using sentence transformers.

This module provides text similarity computation for matching expert profiles
with demand descriptions using multilingual sentence embeddings.
"""
import logging
from functools import lru_cache
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class SemanticMatcher:
    """Semantic text matcher using sentence-transformers.

    Uses a multilingual model that supports Korean text for computing
    semantic similarity between expert profiles and demand descriptions.
    """

    # Model name - multilingual for Korean support
    MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

    _model = None
    _initialized = False

    @classmethod
    def _get_model(cls):
        """Lazy load the sentence transformer model."""
        if cls._model is None:
            try:
                from sentence_transformers import SentenceTransformer

                logger.info(f"Loading sentence transformer model: {cls.MODEL_NAME}")
                cls._model = SentenceTransformer(cls.MODEL_NAME)
                cls._initialized = True
                logger.info("Sentence transformer model loaded successfully")
            except ImportError:
                logger.warning(
                    "sentence-transformers not installed. "
                    "Falling back to keyword-based similarity."
                )
                cls._initialized = False
            except Exception as e:
                logger.error(f"Failed to load sentence transformer: {e}")
                cls._initialized = False

        return cls._model

    @classmethod
    def compute_similarity(cls, text1: str, text2: str) -> float:
        """Compute semantic similarity between two texts.

        Args:
            text1: First text to compare
            text2: Second text to compare

        Returns:
            Similarity score between 0 and 1
        """
        if not text1 or not text2:
            return 0.0

        model = cls._get_model()

        if model is not None:
            try:
                # Encode both texts
                embeddings = model.encode([text1, text2], convert_to_numpy=True)

                # Compute cosine similarity
                similarity = np.dot(embeddings[0], embeddings[1]) / (
                    np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
                )

                # Convert to 0-1 range (cosine similarity is -1 to 1)
                return float(max(0, (similarity + 1) / 2))
            except Exception as e:
                logger.warning(f"Semantic similarity computation failed: {e}")
                return cls._fallback_similarity(text1, text2)
        else:
            return cls._fallback_similarity(text1, text2)

    @classmethod
    def batch_similarities(
        cls,
        query: str,
        candidates: list[str],
    ) -> list[float]:
        """Compute similarities between a query and multiple candidates.

        Args:
            query: Query text
            candidates: List of candidate texts to compare against

        Returns:
            List of similarity scores (0-1) for each candidate
        """
        if not query or not candidates:
            return [0.0] * len(candidates)

        model = cls._get_model()

        if model is not None:
            try:
                # Encode query and all candidates
                all_texts = [query] + candidates
                embeddings = model.encode(all_texts, convert_to_numpy=True)

                query_embedding = embeddings[0]
                candidate_embeddings = embeddings[1:]

                # Compute similarities
                similarities = []
                for cand_emb in candidate_embeddings:
                    sim = np.dot(query_embedding, cand_emb) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(cand_emb)
                    )
                    similarities.append(float(max(0, (sim + 1) / 2)))

                return similarities
            except Exception as e:
                logger.warning(f"Batch similarity computation failed: {e}")
                return [cls._fallback_similarity(query, c) for c in candidates]
        else:
            return [cls._fallback_similarity(query, c) for c in candidates]

    @classmethod
    def _fallback_similarity(cls, text1: str, text2: str) -> float:
        """Fallback keyword-based similarity when model is unavailable.

        Uses Jaccard similarity on word sets.
        """
        if not text1 or not text2:
            return 0.0

        # Tokenize (simple whitespace split for Korean/English)
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        # Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    @classmethod
    def find_most_similar(
        cls,
        query: str,
        candidates: list[str],
        top_n: int = 5,
        min_score: float = 0.3,
    ) -> list[tuple[int, float]]:
        """Find the most similar candidates to a query.

        Args:
            query: Query text
            candidates: List of candidate texts
            top_n: Maximum number of results to return
            min_score: Minimum similarity threshold

        Returns:
            List of (index, score) tuples sorted by score descending
        """
        if not query or not candidates:
            return []

        similarities = cls.batch_similarities(query, candidates)

        # Create (index, score) pairs and filter by min_score
        indexed_scores = [
            (i, score)
            for i, score in enumerate(similarities)
            if score >= min_score
        ]

        # Sort by score descending
        indexed_scores.sort(key=lambda x: x[1], reverse=True)

        return indexed_scores[:top_n]

    @classmethod
    def compute_profile_match(
        cls,
        expert_bio: str,
        expert_specialties: list[str],
        demand_description: str,
        demand_requirements: list[str],
    ) -> dict:
        """Compute comprehensive profile match score.

        Combines bio-to-description similarity with specialty matching.

        Args:
            expert_bio: Expert's biography/introduction
            expert_specialties: Expert's specialty areas
            demand_description: Demand description text
            demand_requirements: Demand requirement keywords

        Returns:
            Match result with scores and details
        """
        # Bio to description similarity
        bio_similarity = cls.compute_similarity(
            expert_bio or "",
            demand_description or "",
        )

        # Specialty to requirements similarity
        expert_spec_text = " ".join(expert_specialties or [])
        demand_req_text = " ".join(demand_requirements or [])
        spec_similarity = cls.compute_similarity(expert_spec_text, demand_req_text)

        # Combined score (weighted average)
        combined_score = (bio_similarity * 0.4) + (spec_similarity * 0.6)

        return {
            "bio_similarity": round(bio_similarity * 100, 1),
            "specialty_similarity": round(spec_similarity * 100, 1),
            "combined_score": round(combined_score * 100, 1),
            "details": {
                "expert_bio_length": len(expert_bio or ""),
                "demand_description_length": len(demand_description or ""),
                "expert_specialties": expert_specialties or [],
                "demand_requirements": demand_requirements or [],
            },
        }

    @classmethod
    def is_model_available(cls) -> bool:
        """Check if the semantic model is available.

        Returns:
            True if model can be loaded, False otherwise
        """
        cls._get_model()
        return cls._initialized
