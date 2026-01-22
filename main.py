import os
import json
import pandas as pd
from pathlib import Path
from openai import OpenAI
import PyPDF2
from typing import List, Dict
import time
from tqdm import tqdm
from dotenv import load_dotenv

class PaperAffilationExtractor:
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        
    def extract_text_from_pdf(self, pdf_path: str, max_pages: int = 3) -> str:
        """Extract text from first few pages where author info typically appears"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for i in range(min(max_pages, len(reader.pages))):
                    text += reader.pages[i].extract_text()
                return text
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return ""
    
    def extract_affiliations(self, text: str, paper_name: str) -> List[Dict]:
        """Use LLM to extract structured author affiliations"""
        
        prompt = f"""Extract all author information from this research paper text. For each author, extract:
- Author name
- Email address (if available)
- Department/Division (if available)
- Institution/University name
- Country

Return a JSON array of objects with this structure:
[
  {{
    "author_name": "John Doe",
    "email": "john.doe@university.edu",
    "department": "Department of Computer Science",
    "institution": "MIT",
    "country": "USA"
  }}
]

Rules:
- If a field is not available, use null
- Preserve the mapping between authors and their affiliations (pay attention to superscripts/numbers)
- Only extract authors, not editors or other contributors
- Return valid JSON only, no additional text

Paper text:
{text[:8000]}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting structured information from academic papers. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON response
            data = json.loads(content)
            
            # Handle different response formats
            if isinstance(data, dict):
                if 'authors' in data:
                    authors = data['authors']
                elif 'data' in data:
                    authors = data['data']
                else:
                    # Assume the dict itself contains a list
                    authors = list(data.values())[0] if data else []
            else:
                authors = data
            
            # Add paper name to each author
            for author in authors:
                author['paper_name'] = paper_name
                
            return authors
            
        except Exception as e:
            print(f"Error in LLM extraction for {paper_name}: {e}")
            return []
    
    def process_papers(self, papers_dir: str, output_csv: str = "papers_affiliations.csv"):
        """Process all papers in directory and create DataFrame"""
        
        papers_path = Path(papers_dir)
        pdf_files = list(papers_path.glob("*.pdf"))
        
        all_authors = []
        failed_papers = []
        
        print(f"Found {len(pdf_files)} PDF files")
        
        for pdf_file in tqdm(pdf_files, desc="Processing papers"):
            paper_name = pdf_file.stem
            
            # Extract text
            text = self.extract_text_from_pdf(str(pdf_file))
            
            if not text.strip():
                failed_papers.append(paper_name)
                continue
            
            # Extract affiliations
            authors = self.extract_affiliations(text, paper_name)
            
            if authors:
                all_authors.extend(authors)
            else:
                failed_papers.append(paper_name)
            
            # Rate limiting - adjust based on your API tier
            time.sleep(0.5)
        
        # Create DataFrame
        df = pd.DataFrame(all_authors)
        
        # Reorder columns
        column_order = ['author_name', 'email', 'department', 'institution', 'country', 'paper_name']
        existing_columns = [col for col in column_order if col in df.columns]
        df = df[existing_columns]
        
        # Save to CSV
        df.to_csv(output_csv, index=False)
        
        print(f"\n✓ Processed {len(pdf_files)} papers")
        print(f"✓ Extracted {len(all_authors)} author records")
        print(f"✓ Saved to {output_csv}")
        
        if failed_papers:
            print(f"\n⚠ Failed to process {len(failed_papers)} papers:")
            for paper in failed_papers[:10]:
                print(f"  - {paper}")
            if len(failed_papers) > 10:
                print(f"  ... and {len(failed_papers) - 10} more")
        
        return df

# Usage
if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()
    
    # Get API key from environment
    API_KEY = os.getenv("OPENAI_API_KEY")
    
    if not API_KEY:
        raise ValueError("OPENAI_API_KEY not found in .env file")
    
    extractor = PaperAffilationExtractor(api_key=API_KEY)
    
    # Process papers
    df = extractor.process_papers(
        papers_dir="/home/lisa/Arupreza/ScholarScout/Papers",
        output_csv="papers_affiliations.csv"
    )
    
    # Display sample
    print("\nSample of extracted data:")
    print(df.head(10))
    
    # Statistics
    print(f"\nStatistics:")
    print(f"Total authors: {len(df)}")
    print(f"Authors with emails: {df['email'].notna().sum()}")
    print(f"Unique papers: {df['paper_name'].nunique()}")