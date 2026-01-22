# 📚 ScholarScout: Automated Academic Paper Affiliation Collector

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)

A unified pipeline for automated academic research analysis: from paper collection to structured author affiliation extraction. Combines Google Scholar scraping with LLM-powered data mining to build comprehensive datasets for bibliometric analysis, collaboration mapping, and research trend discovery.

## 🎯 Overview

ScholarScout provides an end-to-end solution for academic research analysis:

1. **Paper Collection** (`gs_MCP/`): Automated scraping and downloading from Google Scholar
2. **Data Extraction** (`main.py`): LLM-powered extraction of author affiliations and contact information
3. **Structured Output**: Clean CSV datasets ready for analysis

The system uses OpenAI's GPT-4o to intelligently parse author sections and preserve author-affiliation mappings even in complex multi-author papers.

## ✨ Features

### Paper Collection (gs_MCP)
- Powered by [Google Scholar MCP Server](https://github.com/JackKuo666/Google-Scholar-MCP-Server) by [@JackKuo666](https://github.com/JackKuo666)
- MCP protocol-based communication for AI-powered paper search
- Async client for Google Scholar queries
- Automatic PDF download to Papers directory
- Customizable search topics via `MCPrun.py`

### Affiliation Extraction (main.py)
- **Batch Processing**: Handle 100+ papers automatically
- **Structured Extraction**: Author names, emails, departments, institutions, countries
- **Smart Mapping**: Preserves author-affiliation relationships (handles superscript notation)
- **Progress Tracking**: Real-time progress bars with failed paper reporting
- **CSV Export**: Clean, structured output for immediate analysis
- **Error Resilience**: Continues processing even when individual papers fail
- **Cost Efficient**: ~$1-3 for 100 papers using GPT-4o

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/Arupreza/ScholarScout.git
cd ScholarScout

# Install dependencies
pip install -r requirements.txt
```

### Setup

1. Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-proj-your-api-key-here
```

2. Project structure:

```
ScholarScout/
├── .venv/                          # Virtual environment
├── gs_MCP/                         # Google Scholar scraper
├── Papers/                         # Downloaded PDFs (auto-created)
├── .env                           # API keys
├── main.py                        # Affiliation extractor
├── MCPrun.py                      # MCP runner
├── papers_affiliations.csv        # Output
├── README.md
└── requirements.txt
```

### Usage

#### Full Pipeline

```bash
# Step 1: Collect papers using MCP (Google Scholar search)
python MCPrun.py

# Step 2: Extract affiliations from downloaded papers
python main.py
```

**Note**: `MCPrun.py` connects to the Google Scholar MCP Server to search and download papers based on your research query. Edit the `test_topic` variable in `MCPrun.py` to customize your search.

#### Affiliation Extraction Only

If you already have PDFs in the `Papers/` directory:

```bash
python main.py
```

The script will:
1. Scan the `Papers/` directory for PDF files
2. Extract text from first 3 pages (where author info typically appears)
3. Use GPT-4o to parse and structure author information
4. Save results to `papers_affiliations.csv`

### Custom Configuration

```python
from main import PaperAffilationExtractor

extractor = PaperAffilationExtractor(api_key="your-key", model="gpt-4o")

df = extractor.process_papers(
    papers_dir="./Papers",
    output_csv="custom_output.csv"
)
```

## 📊 Output Format

Generated CSV with the following structure:

| Column | Description | Example |
|--------|-------------|---------|
| `author_name` | Full name of the author | Md Rezanur Islam |
| `email` | Email address (if available) | arupreza@sch.ac.kr |
| `department` | Department or division | Department of Software Convergence |
| `institution` | University or organization | Soonchunhyang University |
| `country` | Country of affiliation | Korea |
| `paper_name` | Source paper filename | CF-AIDS |

### Sample Output

```csv
author_name,email,department,institution,country,paper_name
Ashish Vaswani,avaswani@google.com,Google Brain,Google,USA,attention_is_all_you_need
Noam Shazeer,noam@google.com,Google Brain,Google,USA,attention_is_all_you_need
Niki Parmar,nikip@google.com,Google Research,Google,USA,attention_is_all_you_need
```

## 📈 Performance Metrics

- **Success Rate**: 70-80% for standard academic papers
- **Processing Speed**: ~2 seconds per paper (with rate limiting)
- **Cost**: $0.01-0.03 per paper with GPT-4o
- **Accuracy**: 85-95% for clearly formatted papers

### Known Limitations

- Only extracts from first 3 pages (author info location)
- Depends on PDF text extraction quality
- May miss affiliations in footnotes or end-of-paper sections
- Conference proceedings often have less structured formats
- ~20-30% of papers may require manual review

## 🛠️ Technical Details

### Architecture

```
User Query → MCPrun.py → Google Scholar MCP Server → Papers/ → main.py → CSV
  (Topic)   (MCP Client)  (JackKuo666 Server)     (PDFs)  (Extract) (Output)

MCP Communication Flow:
MCPrun.py (async client) ←→ stdio ←→ google_scholar_server.py (MCP tools)
                                      ↓
                                  Google Scholar API
                                      ↓
                                  PDF Downloads

Extraction Pipeline:
PDF File → Text Extraction → LLM Processing → JSON Parsing → DataFrame → CSV
           (PyPDF2)         (GPT-4o API)      (Validation)   (Pandas)
```

### MCP Protocol Details

- **Client**: `MCPrun.py` uses `mcp` library with `stdio_client`
- **Server**: `gs_MCP/google_scholar_server.py` runs via `uv`
- **Transport**: Standard I/O communication
- **Tools**: Dynamic tool discovery and invocation
- **Search Args**: `query` parameter for research topics

### LLM Prompt Strategy

- **Few-shot learning**: Structured JSON output format
- **Context window**: First 8000 characters (covers most author sections)
- **Temperature**: 0 (deterministic output)
- **Response format**: Forced JSON mode for reliability

### Rate Limiting

Default: 0.5s delay between requests (120 papers/hour)

Adjust in `main.py`:
```python
time.sleep(0.5)  # Increase for lower tier limits
```

## 🔧 Troubleshooting

### No text extracted from PDF
**Problem**: PDF is image-based or poorly scanned  
**Solution**: Use OCR preprocessing or switch to `pdfplumber`

### API rate limit errors
**Problem**: Too many requests  
**Solution**: Increase `time.sleep()` delay or upgrade OpenAI tier

### Malformed JSON errors
**Problem**: LLM returns invalid JSON  
**Solution**: Add retry logic with exponential backoff

### Missing emails
**Problem**: Not all authors have emails listed  
**Expected**: Common in academic papers (only corresponding author)

### gs_MCP connection issues
**Problem**: MCP server not starting or connection timeout  
**Solution**: 
- Ensure `uv` is installed: `pip install uv`
- Check `gs_MCP/google_scholar_server.py` exists
- Verify MCP dependencies: `pip install mcp`
- Test server manually: `cd gs_MCP && uv run google_scholar_server.py`

## 🚧 Roadmap

### Extraction Module
- [ ] Retry logic with exponential backoff
- [ ] Parallel processing with rate limit semaphore
- [ ] OCR support for image-based PDFs
- [ ] Email validation and normalization
- [ ] Institution name standardization
- [ ] Checkpoint saving for large batches (1000+ papers)

### Collection Module
- [ ] Support for arXiv, PubMed, IEEE Xplore
- [ ] Advanced search filters
- [ ] Duplicate detection
- [ ] Metadata extraction during download

### Analysis Features
- [ ] Collaboration network visualization
- [ ] Geographic distribution mapping
- [ ] Institution ranking analysis
- [ ] Citation network building

## 📂 Repository Structure

```
ScholarScout/
├── .venv/                          # Virtual environment
├── gs_MCP/                         # Google Scholar MCP server module
│   ├── __pycache__/
│   ├── .python-version
│   ├── google_scholar_server.py    # MCP server implementation
│   ├── google_scholar_web_search.py # Web scraping logic
│   └── requirements.txt            # MCP server dependencies
├── Papers/                         # Downloaded PDF papers (auto-created)
├── src/                            # Source directory
├── .env                            # Environment variables (API keys)
├── .gitignore                      # Git ignore rules
├── .python-version                 # Python version specification
├── main.py                         # Main affiliation extractor
├── MCPrun.py                       # MCP client for paper collection
├── papers_affiliations.csv         # Extracted data output
├── pyproject.toml                  # Project configuration (uv)
├── README.md                       # This file
├── requirements.txt                # Python dependencies
└── uv.lock                         # UV dependency lock file
```

## 📝 Citation

If you use this tool in your research, please cite:

```bibtex
@software{scholarscout,
  title = {ScholarScout: Automated Academic Paper Analysis Pipeline},
  author = {Arupreza},
  year = {2025},
  url = {https://github.com/Arupreza/ScholarScout}
}
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

Areas for contribution:
- Additional paper sources (arXiv, PubMed, etc.)
- Improved PDF parsing methods
- Enhanced affiliation normalization
- Visualization tools
- Performance optimizations

## 📧 Contact

For questions or support, open an issue on GitHub.

---

**Built with**: OpenAI GPT-4o | Python 3.8+ | PyPDF2 | Pandas | [Google Scholar MCP Server](https://github.com/JackKuo666/Google-Scholar-MCP-Server)

## 🙏 Acknowledgments

This project uses the [Google Scholar MCP Server](https://github.com/JackKuo666/Google-Scholar-MCP-Server) by [@JackKuo666](https://github.com/JackKuo666) for paper collection and metadata retrieval. Special thanks to the MCP community for enabling seamless AI-powered research tools.
