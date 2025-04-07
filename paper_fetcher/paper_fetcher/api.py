from typing import List, Dict, Optional
from Bio import Entrez
import time
import logging
import certifi
import ssl
import os

#  SSL
ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

class PubMedClient:
    """Client for fetching data from PubMed API with proper error handling"""

    def __init__(self, email: str, api_key: Optional[str] = None):
        """Initialize the PubMed client with rate limiting"""
        Entrez.email = "janmeshjoshi1510@gmail.com"
        if api_key:
            Entrez.api_key = "79d72f171483fee9a74c7f8166e29f347008"
        self.delay = 0.34  # PubMed's 3 requests limit
        self.logger = logging.getLogger(__name__)
        
        self._dtd_dir = os.path.join(os.path.dirname(__file__), "biopython_dtds")
        try:
            os.makedirs(self._dtd_dir, exist_ok=True)
            Entrez.local_dtd_dir = self._dtd_dir
        except OSError as e:
            self.logger.warning(f"Couldn't create DTD directory: {e}. Using default location.")

    def search_articles(self, query: str, max_results: int = 100) -> List[str]:
        """Search PubMed and return article IDs"""
        try:
            handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
            result = Entrez.read(handle)
            handle.close()
            time.sleep(self.delay)
            return result["IdList"]
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            raise RuntimeError(f"PubMed search failed: {e}")

    def fetch_article_details(self, article_ids: List[str]) -> List[Dict]:
        """Fetch complete article details"""
        try:
            if not article_ids:
                return []
                
            id_str = ",".join(article_ids)
            handle = Entrez.efetch(db="pubmed", id=id_str, retmode="xml")
            records = Entrez.read(handle)
            handle.close()
            time.sleep(self.delay)
            
            # Ensure consistent structure
            return [self._parse_article(article) for article in records.get("PubmedArticle", [])]
        except Exception as e:
            self.logger.error(f"Fetch failed: {e}")
            raise RuntimeError(f"Failed to fetch articles: {e}")

    def _parse_article(self, article_data: Dict) -> Dict:
        """Parse raw article data into structured format"""
        try:
            medline = article_data["MedlineCitation"]
            article = medline["Article"]
            
            return {
                "pubmed_id": str(medline["PMID"]),
                "title": article.get("ArticleTitle", ""),
                "publication_date": self._parse_date(article),
                "authors": self._parse_authors(article),
                "abstract": self._parse_abstract(article),
            }
        except KeyError as e:
            self.logger.warning(f"Missing expected field in article: {e}")
            raise ValueError(f"Incomplete article data: {e}")
    
    def _parse_date(self, article: Dict) -> str:
    #Extract publication date in YYYY-MM-DD format with robust fallbacks
        try:
        # Try ArticleDate first
            if "ArticleDate" in article and article["ArticleDate"]:
                date = article["ArticleDate"][0]
                return f"{date.get('Year', '')}-{date.get('Month', '01')}-{date.get('Day', '01')}"
        
        # Fallback to Journal Issue Date
            if "Journal" in article and "JournalIssue" in article["Journal"]:
                issue = article["Journal"]["JournalIssue"]
                if "PubDate" in issue:
                    pub_date = issue["PubDate"]
                    year = pub_date.get("Year", "")
                    month = pub_date.get("Month", "01")
                    day = pub_date.get("Day", "01")
                    return f"{year}-{month}-{day}"
        
            return ""  # Final fallback
        except Exception as e:
            self.logger.warning(f"Date parsing fallback used: {e}")
            return ""
    
    def _parse_authors(self, article: Dict) -> List[Dict]:
        """Extract author information with affiliations"""
        try:
            return [
                {
                    "last_name": author.get("LastName", ""),
                    "first_name": author.get("ForeName", ""),
                    "affiliation": self._parse_affiliation(author),
                }
                for author in article.get("AuthorList", [])
                if author.get("@ValidYN", "Y") == "Y"
            ]
        except (AttributeError, TypeError) as e:
            self.logger.warning(f"Invalid author format: {e}")
            return []
    
    def _parse_affiliation(self, author: Dict) -> str:
        """Extract primary affiliation"""
        try:
            if "AffiliationInfo" in author and author["AffiliationInfo"]:
                return author["AffiliationInfo"][0].get("Affiliation", "")
            return ""
        except (AttributeError, IndexError) as e:
            self.logger.warning(f"Invalid affiliation format: {e}")
            return ""
    
    def _parse_abstract(self, article: Dict) -> str:
        """Extract abstract text"""
        try:
            if "Abstract" in article:
                abstract_text = article["Abstract"].get("AbstractText", [])
                if isinstance(abstract_text, list):
                    return " ".join(str(text) for text in abstract_text)
                return str(abstract_text)
            return ""
        except Exception as e:
            self.logger.warning(f"Failed to parse abstract: {e}")
            return ""