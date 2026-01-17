"""
Hugging Face Inference API Client
==================================

This module provides a lightweight wrapper around the Hugging Face Inference API
for zero-shot text classification capabilities.

Purpose:
- Enable AI agents to classify text without pre-trained custom models
- Support sentiment analysis, intent detection, and category prediction
- Provide quick ML inference for hackathon/demo scenarios

What is Zero-Shot Classification?
----------------------------------
Zero-shot classification allows you to classify text into categories WITHOUT
training a model. You just provide:
1. The text to classify
2. A list of possible labels

Example:
    text = "This route is very dangerous at night"
    labels = ["safe", "warning", "danger"]
    result = classify_text(text, labels)
    # Returns: {"label": "danger", "confidence": 0.92}

Use Cases in Safety Route:
- Classify user reports: "Is this report about crime, lighting, or crowds?"
- Analyze sentiment: "Is user feedback positive, neutral, or negative?"
- Intent detection: "Does user need emergency help or just route info?"

Technical Details:
- Uses Hugging Face's free Inference API (no local model needed)
- Model: facebook/bart-large-mnli (general-purpose zero-shot classifier)
- API Documentation: https://huggingface.co/docs/api-inference/

Author: Safety Route Team
Date: January 2026
"""

import os
import requests
from typing import List, Dict, Optional


# ============================================================================
# CONFIGURATION
# ============================================================================

# Hugging Face API endpoint for the zero-shot classification model
# facebook/bart-large-mnli is a pre-trained model that works well for general classification
HF_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"

# Read API token from environment variable
# Get your free token at: https://huggingface.co/settings/tokens
# Set it in your .env file as: HF_API_TOKEN=hf_xxxxxxxxxxxxx
HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")


# ============================================================================
# MAIN CLASSIFICATION FUNCTION
# ============================================================================

def classify_text(text: str, labels: List[str]) -> Dict[str, any]:
    """
    Classify text into one of the provided labels using zero-shot classification.
    
    This function sends text to Hugging Face's API and gets back predictions
    about which label best matches the text content.
    
    How it works:
    1. Sends text and candidate labels to Hugging Face API
    2. Model analyzes the text semantically (understands meaning)
    3. Returns the most likely label with a confidence score
    
    Args:
        text (str): The text to classify
            Examples:
            - "I saw suspicious activity near the park"
            - "The street lights are not working"
            - "Very crowded area, hard to walk"
        
        labels (List[str]): List of possible categories/labels
            Examples:
            - ["crime", "lighting", "crowd"]
            - ["safe", "moderate", "dangerous"]
            - ["positive", "neutral", "negative"]
    
    Returns:
        Dict containing:
            - label (str): The predicted category
            - confidence (float): Confidence score (0.0 to 1.0)
            - error (str, optional): Error message if something went wrong
    
    Examples:
        >>> # Classify a safety report
        >>> result = classify_text(
        ...     text="Someone broke into a car here last night",
        ...     labels=["crime", "lighting", "crowd", "infrastructure"]
        ... )
        >>> print(result)
        {'label': 'crime', 'confidence': 0.94}
        
        >>> # Classify route safety level
        >>> result = classify_text(
        ...     text="Well-lit street with many people around",
        ...     labels=["safe", "moderate", "risky", "dangerous"]
        ... )
        >>> print(result)
        {'label': 'safe', 'confidence': 0.87}
        
        >>> # Classify user sentiment
        >>> result = classify_text(
        ...     text="This app saved my life! Amazing route suggestions!",
        ...     labels=["positive", "neutral", "negative"]
        ... )
        >>> print(result)
        {'label': 'positive', 'confidence': 0.96}
    
    Error Handling:
        - If API token is missing: Returns first label with 0.0 confidence
        - If API is down: Returns fallback response with error message
        - If network fails: Returns fallback response with error details
        
        All errors return a valid dictionary, so your code won't crash.
    
    Performance Notes:
        - First request may be slow (model loading on HF servers)
        - Subsequent requests are faster (model stays loaded ~5 minutes)
        - Typical response time: 1-3 seconds
        - Free tier has rate limits (check HF documentation)
    """
    
    # -------------------------------------------------------------------------
    # STEP 1: Check if API token is configured
    # -------------------------------------------------------------------------
    if not HF_API_TOKEN:
        # API token is required for Hugging Face API
        # Return fallback response instead of crashing
        return {
            "label": labels[0] if labels else "unknown",
            "confidence": 0.0,
            "error": "HF_API_TOKEN not configured. Set it in your .env file."
        }
    
    # -------------------------------------------------------------------------
    # STEP 2: Prepare API request
    # -------------------------------------------------------------------------
    
    # Authorization header with Bearer token
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    
    # Request payload in the format expected by HF Inference API
    payload = {
        "inputs": text,  # The text to classify
        "parameters": {
            "candidate_labels": labels  # The possible categories
        }
    }
    
    # -------------------------------------------------------------------------
    # STEP 3: Send request to Hugging Face API
    # -------------------------------------------------------------------------
    try:
        # Make POST request to HF API
        # Timeout after 10 seconds to avoid hanging
        response = requests.post(
            HF_API_URL, 
            headers=headers, 
            json=payload, 
            timeout=10
        )
        
        # Check if request was successful (200 OK)
        if response.status_code != 200:
            # API returned an error (401 Unauthorized, 503 Service Unavailable, etc.)
            return {
                "label": labels[0] if labels else "unknown",
                "confidence": 0.0,
                "error": f"API error: {response.status_code} - {response.text[:100]}"
            }
        
        # -------------------------------------------------------------------------
        # STEP 4: Parse API response
        # -------------------------------------------------------------------------
        
        # Parse JSON response from API
        result = response.json()
        
        # HF API returns results sorted by confidence (highest first)
        # Response format:
        # {
        #     "labels": ["crime", "lighting", "crowd"],
        #     "scores": [0.94, 0.04, 0.02]
        # }
        
        # Get the top predicted label (highest confidence)
        top_label = result.get("labels", [labels[0]])[0]
        
        # Get the confidence score for top label
        top_score = result.get("scores", [0.0])[0]
        
        # -------------------------------------------------------------------------
        # STEP 5: Return structured result
        # -------------------------------------------------------------------------
        return {
            "label": top_label,
            "confidence": round(float(top_score), 4)  # Round to 4 decimal places
        }
    
    # -------------------------------------------------------------------------
    # ERROR HANDLING
    # -------------------------------------------------------------------------
    except requests.exceptions.RequestException as e:
        # Network errors: timeout, connection refused, DNS failure, etc.
        return {
            "label": labels[0] if labels else "unknown",
            "confidence": 0.0,
            "error": f"Network error: {str(e)}"
        }
    
    except Exception as e:
        # Unexpected errors: JSON parsing, key errors, etc.
        return {
            "label": labels[0] if labels else "unknown",
            "confidence": 0.0,
            "error": f"Unexpected error: {str(e)}"
        }


# ============================================================================
# HELPER FUNCTIONS (Optional - for future use)
# ============================================================================

def is_classification_confident(result: Dict, threshold: float = 0.7) -> bool:
    """
    Check if classification result is confident enough to trust.
    
    Sometimes the model isn't sure and returns low confidence scores.
    Use this to decide if you should trust the prediction or ask for
    human review.
    
    Args:
        result (Dict): Result from classify_text()
        threshold (float): Minimum confidence to consider "confident" (default: 0.7)
    
    Returns:
        bool: True if confidence >= threshold
    
    Example:
        >>> result = classify_text("Ambiguous text...", ["A", "B", "C"])
        >>> if is_classification_confident(result):
        ...     print(f"Confident prediction: {result['label']}")
        ... else:
        ...     print("Low confidence, needs human review")
    """
    return result.get("confidence", 0.0) >= threshold


def get_classification_explanation(result: Dict) -> str:
    """
    Generate human-readable explanation of classification result.
    
    Useful for debugging or showing users why a certain classification was made.
    
    Args:
        result (Dict): Result from classify_text()
    
    Returns:
        str: Explanation text
    
    Example:
        >>> result = classify_text("Crime reported here", ["crime", "lighting"])
        >>> print(get_classification_explanation(result))
        "Classified as 'crime' with 94% confidence"
    """
    label = result.get("label", "unknown")
    confidence = result.get("confidence", 0.0)
    confidence_pct = int(confidence * 100)
    
    if "error" in result:
        return f"Classification failed: {result['error']}"
    
    return f"Classified as '{label}' with {confidence_pct}% confidence"


# ============================================================================
# EXAMPLE USAGE & TESTING
# ============================================================================

if __name__ == "__main__":
    """
    Test the classification functionality.
    Run this file directly to see examples.
    """
    print("=== Hugging Face Classification Demo ===\n")
    
    # Check if API token is configured
    if not HF_API_TOKEN:
        print("⚠️ Warning: HF_API_TOKEN not set!")
        print("Set it in your environment or .env file to enable classification.\n")
    
    # Example 1: Classify safety report type
    print("1. Safety Report Classification:")
    report_text = "The street lights are broken and it's very dark at night"
    report_labels = ["crime", "lighting", "crowd", "infrastructure"]
    
    result1 = classify_text(report_text, report_labels)
    print(f"   Text: {report_text}")
    print(f"   Result: {result1}")
    print(f"   Explanation: {get_classification_explanation(result1)}\n")
    
    # Example 2: Classify route safety level
    print("2. Route Safety Classification:")
    route_text = "Well-lit street with many people, police station nearby"
    safety_labels = ["safe", "moderate", "risky", "dangerous"]
    
    result2 = classify_text(route_text, safety_labels)
    print(f"   Text: {route_text}")
    print(f"   Result: {result2}")
    print(f"   Explanation: {get_classification_explanation(result2)}\n")
    
    # Example 3: Classify user sentiment
    print("3. User Feedback Sentiment:")
    feedback_text = "This app is terrible, routes are always wrong!"
    sentiment_labels = ["positive", "neutral", "negative"]
    
    result3 = classify_text(feedback_text, sentiment_labels)
    print(f"   Text: {feedback_text}")
    print(f"   Result: {result3}")
    print(f"   Explanation: {get_classification_explanation(result3)}\n")
    
    # Example 4: Check confidence levels
    print("4. Confidence Check:")
    for res in [result1, result2, result3]:
        confident = is_classification_confident(res, threshold=0.7)
        status = "✅ High confidence" if confident else "⚠️ Low confidence"
        print(f"   {res.get('label', 'N/A')}: {status}")