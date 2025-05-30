import pandas as pd
from openai import OpenAI
import os
from tqdm import tqdm
import time
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv("setvar.env"))

# Configuration
INPUT_FILE = 'Trust_Pilot_Reviews.xlsx'
OUTPUT_FILE = 'Review_Flagging_Analysis.xlsx'
COMMENT_COLUMN = 'text'
OPENAI_MODEL = "gpt-4o"  # Using a more powerful model for better detection

# Set up OpenAI client with API key
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
if not os.getenv('OPENAI_API_KEY'):
    raise ValueError("Please set your OPENAI_API_KEY environment variable")

def read_reviews(file_path):
    """Read the Excel file and return reviews with their original indices."""
    try:
        df = pd.read_excel(file_path)
        # Create a dictionary of index -> review text for easy reference
        reviews_dict = {i: review for i, review in enumerate(df[COMMENT_COLUMN].dropna().tolist())}
        return reviews_dict, df
    except Exception as e:
        print(f"Error reading file: {e}")
        return {}, None

def detect_flagging_issue(review):
    """Check if a review mentions dissatisfaction with review flagging on Trustpilot using OpenAI API."""
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a specialized review analyst focusing on detecting mentions of flagged reviews that were deemed unsatisfactory by the reviewer. Return 'YES' if the review mentions that a review was flagged and the user was dissatisfied with the outcome. Return 'NO' otherwise. Only return YES or NO."},
                {"role": "user", "content": f"Review: {review}\n\nDoes this review mention a flagged review that had an unsatisfactory outcome?"}
            ],
            temperature=0.1,
            max_tokens=5
        )
        result = response.choices[0].message.content.strip().upper()
        return result == "YES"
    except Exception as e:
        print(f"Error detecting flagged review issue: {e}")
        return False

def score_relevance_to_flagging_issue(review):
    """Score how strongly a review discusses dissatisfaction with flagged reviews (0-10)."""
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a specialized review analyst. Score how strongly this review discusses dissatisfaction with flagged reviews on Trustpilot on a scale from 0-10, where:\n0 = No mention at all\n1-3 = Brief or ambiguous mention\n4-7 = Clear mention but not the main focus\n8-10 = Extensive discussion of frustration with Trustpilot’s flagging system as a central theme\nProvide ONLY the numeric score without explanation."},
                {"role": "user", "content": f"Review: {review}\n\nScore (0-10):"}
            ],
            temperature=0.1,
            max_tokens=5
        )
        score_text = response.choices[0].message.content.strip()
        digits = ''.join(filter(str.isdigit, score_text))
        return int(digits) if digits else 0
    except Exception as e:
        print(f"Error scoring relevance: {e}")
        return 0

def extract_flagging_details(review):
    """Extract key details about the flagged review mention."""
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a specialized review analyst. For this review that mentions dissatisfaction with review flagging, extract the following details:\n1. Why was the review flagged?\n2. What response did Trustpilot give?\n3. What specific frustrations did the reviewer express?\nKeep your answer brief and factual. If information is not present, indicate 'Not specified'."},
                {"role": "user", "content": f"Review: {review}"}
            ],
            temperature=0.1,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error extracting details: {e}")
        return "Error extracting details"

def identify_removal_reviews(reviews_dict):
    """Identify reviews that mention review removal."""
    removal_reviews = []
    
    print("Analyzing reviews for mentions of review removal...")
    for idx, review in tqdm(reviews_dict.items()):
        if not review or len(str(review).strip()) < 5:  # Skip empty or very short reviews
            continue
            
        # First quick check if the review mentions removal
        if detect_flagging_issue(review):
            # If yes, score its relevance
            relevance_score = score_relevance_to_flagging_issue(review)
            
            # If score is above threshold, include in results
            if relevance_score >= 3:  # Adjust threshold as needed
                details = extract_flagging_details(review)
                
                removal_reviews.append({
                    "Review_Index": idx,
                    "Review_Text": review,
                    "Relevance_Score": relevance_score,
                    "Details": details
                })
        
        # Rate limit handling
        time.sleep(0.3)
    
    return removal_reviews

def save_results(results, output_file):
    """Save the analysis results to an Excel file."""
    df = pd.DataFrame(results)
    
    # Sort by relevance score descending
    df = df.sort_values(by='Relevance_Score', ascending=False)
    
    df.to_excel(output_file, index=False)
    print(f"Results saved to {output_file}")
    print(f"Found {len(results)} reviews mentioning review flagging.")

def main():
    # Read reviews
    reviews_dict, df = read_reviews(INPUT_FILE)
    if not reviews_dict:
        return
    
    print(f"Found {len(reviews_dict)} reviews to analyze.")
    
    # Identify reviews about review removal
    removal_reviews = identify_removal_reviews(reviews_dict)
    
    # Save results
    save_results(removal_reviews, OUTPUT_FILE)

if __name__ == "__main__":
    main()