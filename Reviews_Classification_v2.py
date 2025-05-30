import pandas as pd
from openai import OpenAI
import os
from tqdm import tqdm
import time
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv("setvar.env"))

# Configuration
INPUT_FILE = 'Trust_Pilot_Reviews.xlsx'
OUTPUT_FILE = 'Trust_Pilot_Review_Analysis.xlsx'
COMMENT_COLUMN = 'text'
OPENAI_MODEL = "gpt-4o"
MAX_THEMATICS = 10

# Set up OpenAI client with API key
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
if not os.getenv('OPENAI_API_KEY'):
    raise ValueError("Please set your OPENAI_API_KEY environment variable")

def read_reviews(file_path):
    """Read the Excel file and return reviews as a list and dataframe."""
    try:
        df = pd.read_excel(file_path)
        reviews = df[COMMENT_COLUMN].dropna().tolist()
        return reviews, df
    except Exception as e:
        print(f"Error reading file: {e}")
        return [], None

def summarize_review(review):
    """Use OpenAI API to summarize a review and identify its main themes."""
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes customer reviews. Identify 2-4 main themes in this review. Focus on customer experience aspects like service quality, communication, product issues, etc. Respond with just keywords separated by commas."},
                {"role": "user", "content": f"Review: {review}\n\nIdentify the main themes in this review."}
            ],
            temperature=0.3,
            max_tokens=50
        )
        themes = response.choices[0].message.content.strip().lower()
        return [theme.strip() for theme in themes.split(',')]
    except Exception as e:
        print(f"Error summarizing review: {e}")
        time.sleep(2)  # Wait longer on error
        return []

def get_theme_relevance(review, theme):
    """Rate the relevance of a review to a specific theme."""
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a review classification assistant. Rate how relevant this review is to the given theme on a scale of 1-10, where 10 is extremely relevant."},
                {"role": "user", "content": f"Review: {review}\nTheme: {theme}\n\nRate the relevance (1-10):"}
            ],
            temperature=0.2,
            max_tokens=5
        )
        score_text = response.choices[0].message.content.strip()
        # Extract digits from response
        digits = ''.join(filter(str.isdigit, score_text))
        return int(digits) if digits else 5  # Default to medium relevance if parsing fails
    except Exception as e:
        print(f"Error rating relevance: {e}")
        return 5  # Default to medium relevance

def classify_reviews(reviews):
    """Classify reviews into themes and return analysis."""
    # Dictionary to track themes and reviews with relevance scores
    theme_reviews = {}  # {theme: [(review_index, relevance_score, review_length)]}
    used_examples = set()  # Track which reviews have been used as examples
    
    print("Analyzing reviews to identify themes...")
    for i, review in enumerate(tqdm(reviews)):
        if not review or len(str(review).strip()) < 5:  # Skip empty or very short reviews
            continue
            
        themes = summarize_review(review)
        
        # Add review to each theme it belongs to
        for theme in themes:
            if theme not in theme_reviews:
                theme_reviews[theme] = []
            
            # Store the review index, will calculate relevance later if needed
            review_length = len(str(review))
            theme_reviews[theme].append((i, 0, review_length))  # Initial relevance score of 0
        
        # Rate limit handling
        time.sleep(0.3)
    
    # Check if we have enough themes
    if len(theme_reviews) < 2:
        print("WARNING: Very few themes identified. This might indicate an API issue.")
    
    # Consolidate similar themes
    print("\nConsolidating themes...")
    consolidated_theme_map = consolidate_themes(list(theme_reviews.keys()))
    
    # Remap reviews to consolidated themes
    consolidated_reviews = {}
    for old_theme, reviews_list in theme_reviews.items():
        new_theme = consolidated_theme_map.get(old_theme, old_theme)
        if new_theme not in consolidated_reviews:
            consolidated_reviews[new_theme] = []
        consolidated_reviews[new_theme].extend(reviews_list)
    
    # Select top themes
    top_themes = select_top_themes(consolidated_reviews.keys(), consolidated_reviews, MAX_THEMATICS)
    
    # Prepare results
    results = []
    for theme in top_themes:
        review_data = consolidated_reviews.get(theme, [])
        # Remove duplicates by keeping the first occurrence of each review index
        seen_indices = set()
        unique_reviews = []
        for item in review_data:
            if item[0] not in seen_indices:
                seen_indices.add(item[0])
                unique_reviews.append(item)
        
        # Sort reviews by length (descending) for initial ranking
        sorted_reviews = sorted(unique_reviews, key=lambda x: x[2], reverse=True)
        
        # Take top 10 longest reviews for relevance scoring
        candidate_reviews = sorted_reviews[:10] if len(sorted_reviews) > 10 else sorted_reviews
        
        print(f"Calculating relevance scores for theme: {theme}")
        # Calculate relevance scores for candidate reviews
        scored_reviews = []
        for idx, _, length in candidate_reviews:
            review_text = reviews[idx]
            relevance = get_theme_relevance(review_text, theme)
            scored_reviews.append((idx, relevance, length))
            time.sleep(0.3)  # Rate limiting
        
        # Sort by relevance (primary) and length (secondary)
        scored_reviews.sort(key=lambda x: (x[1], x[2]), reverse=True)
        
        # Select best examples that haven't been used yet
        examples = []
        for idx, _, _ in scored_reviews:
            if len(examples) >= 3:
                break
            if idx not in used_examples:
                examples.append(idx)
                used_examples.add(idx)
        
        # If we couldn't find enough unused examples, take the best ones regardless
        if len(examples) < 3:
            for idx, _, _ in scored_reviews:
                if len(examples) >= 3:
                    break
                if idx not in examples:  # Avoid duplicates within this theme
                    examples.append(idx)
                    used_examples.add(idx)
        
        results.append({
            "Theme": theme,
            "Count": len(seen_indices),
            "Example 1": reviews[examples[0]] if len(examples) > 0 else "",
            "Example 2": reviews[examples[1]] if len(examples) > 1 else "",
            "Example 3": reviews[examples[2]] if len(examples) > 2 else ""
        })
    
    return results

def consolidate_themes(themes):
    """Use OpenAI to consolidate similar themes into a mapping dictionary."""
    if not themes:
        return {}
        
    try:
        theme_list = ', '.join(themes)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that groups similar themes together. Map each theme to a broader category from this list: customer service, product quality, website usability, price/value, delivery experience, communication, trustworthiness, return/refund policy, customer support, overall satisfaction."},
                {"role": "user", "content": f"Here are themes extracted from customer reviews: {theme_list}\n\nFor each theme, map it to one of the broader categories. Respond in this format - 'original theme: broader category' with each mapping on a new line."}
            ],
            temperature=0.2,
            max_tokens=300
        )
        
        # Parse the response to create a mapping
        mappings = response.choices[0].message.content.strip().split('\n')
        theme_map = {}
        
        for mapping in mappings:
            if ':' in mapping:
                orig, broad = mapping.split(':', 1)
                theme_map[orig.strip().lower()] = broad.strip().lower()
        
        return theme_map
    except Exception as e:
        print(f"Error consolidating themes: {e}")
        return {theme: theme for theme in themes}  # Return identity mapping on error

def select_top_themes(themes, theme_reviews, max_themes):
    """Select the top themes based on frequency."""
    theme_counts = [(theme, len(set(idx for idx, _, _ in theme_reviews.get(theme, [])))) for theme in themes]
    theme_counts.sort(key=lambda x: x[1], reverse=True)
    return [theme for theme, count in theme_counts[:max_themes]]

def save_results(results, output_file):
    """Save the analysis results to an Excel file."""
    df = pd.DataFrame(results)
    
    # Calculate and print summary statistics
    total_reviews_counted = sum(row["Count"] for row in results)
    print(f"Total reviews counted across all themes: {total_reviews_counted}")
    
    # Sort by count descending
    df = df.sort_values(by='Count', ascending=False)
    
    df.to_excel(output_file, index=False)
    print(f"Results saved to {output_file}")

def main():
    # Read reviews
    reviews, df = read_reviews(INPUT_FILE)
    if not reviews:
        return
    
    print(f"Found {len(reviews)} reviews to analyze.")
    
    # Classify reviews
    analysis_results = classify_reviews(reviews)
    
    # Save results
    save_results(analysis_results, OUTPUT_FILE)

if __name__ == "__main__":
    main()