from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Paper:
    #to present a research paper

    pubmed_id: str
    title: str
    publication_date: str
    authors: List[Dict]
    abstract: str

    def to_dict(self) -> Dict:
        #convert to dictionary for csv for export

        return{
            "pubmed_id": self.pubmed_id,
            "title": self.title,
            "publication_date": self.publication_date,
            "abstract": self.abstract,
            "authors": self.authors,
        }
    

@dataclass
class ProcessedPaper:
    #fiinal processed paper ready for export

    pubmed_id: str
    title: str
    publication_date: str
    non_academic_authors: List[str]
    company_affiliations: List[str]
    corresponding_email: str

    def to_csv_row(self) -> Dict:
        #format for csv output

        return {
            "PubmedID": self.pubmed_id,
            "Title": self.title,
            "Publication Date": self.publication_date,
            "Non-academic Author(s)": self.non_academic_authors,
            "Company Affiliation(s)": self.company_affiliations,
            "Corresponding Author Email": self.corresponding_email,
        }

