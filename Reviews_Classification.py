import pandas as pd
from openai import OpenAI
import os
from tqdm import tqdm
import time
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv("setvar.env"))

# Configuration
INPUT_FILE = 'Trust_Pilot_Reviews.xlsx'
OUTPUT_FILE = 'Trust_Pilot_Review_Analysis_v2.xlsx'
COMMENT_COLUMN = 'text'
OPENAI_MODEL = "gpt-4-1106-preview"
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
                {"role": "system", "content": "You are a helpful assistant that analyzes customer reviews. Identify 2-4 main themes in this review. Focus on customer experience aspects like usability, customer support, moderation issues, etc. Respond with just keywords separated by commas."},
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

def classify_reviews(reviews):
    """Classify reviews into themes and return analysis."""
    # Dictionary to track themes and reviews
    theme_reviews = {}  # {theme: [review_indices]}
    processed_reviews_count = 0  # Track how many reviews were actually processed
    
    print("Analyzing reviews to identify themes...")
    for i, review in enumerate(tqdm(reviews)):
        if not review or len(str(review).strip()) < 5:  # Skip empty or very short reviews
            continue
            
        themes = summarize_review(review)
        processed_reviews_count += 1
        
        # Add review to each theme it belongs to
        for theme in themes:
            if theme not in theme_reviews:
                theme_reviews[theme] = []
            theme_reviews[theme].append(i)
        
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
    
    # Select top themes - use all themes instead of limiting to MAX_THEMATICS
    # to ensure we count all reviews that were processed
    top_themes = list(consolidated_reviews.keys())
    
    # Prepare results
    results = []
    for theme in top_themes:
        review_indices = consolidated_reviews.get(theme, [])
        review_indices = list(set(review_indices))  # Remove duplicates
        example_indices = review_indices[:3]  # Get first 3 examples
        examples = [reviews[i] for i in example_indices]
        
        results.append({
            "Theme": theme,
            "Count": len(review_indices),
            "Example 1": examples[0] if len(examples) > 0 else "",
            "Example 2": examples[1] if len(examples) > 1 else "",
            "Example 3": examples[2] if len(examples) > 2 else ""
        })
    
    # Sort by count and select top MAX_THEMATICS themes for final output
    results.sort(key=lambda x: x["Count"], reverse=True)
    results = results[:MAX_THEMATICS]
    
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
                {"role": "system", "content": "You are a helpful assistant that groups similar themes together. Map each theme to a broader category from this list: moderation, customer support, website usability, trustworthiness, overall satisfaction."},
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
    theme_counts = [(theme, len(theme_reviews.get(theme, []))) for theme in themes]
    theme_counts.sort(key=lambda x: x[1], reverse=True)
    return [theme for theme, count in theme_counts[:max_themes]]

def save_results(results, output_file):
    """Save the analysis results to an Excel file."""
    df = pd.DataFrame(results)
    
    # Calculate and print summary statistics
    total_reviews_counted = sum(row["Count"] for row in results)
    
    # Get total reviews and verify counts
    reviews, _ = read_reviews(INPUT_FILE)
    total_input_reviews = len(reviews)
    
    print(f"Total reviews in input file: {total_input_reviews}")
    print(f"Total reviews counted across all themes: {total_reviews_counted}")
    
    if total_reviews_counted < total_input_reviews:
        print(f"WARNING: Total theme counts ({total_reviews_counted}) is less than total input reviews ({total_input_reviews})")
    
    # Add a total row to the DataFrame
    total_row = pd.DataFrame([{
        "Theme": "TOTAL",
        "Count": total_reviews_counted,
        "Example 1": "",
        "Example 2": "",
        "Example 3": ""
    }])
    
    # Sort by count descending
    df = df.sort_values(by='Count', ascending=False)
    
    # Append total row
    df = pd.concat([df, total_row], ignore_index=True)
    
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