import re
from typing import List, Dict, Tuple

class AffiliationAnalyzer:
    #Analyse author affiliation

    def __init__(self, company_list_path: str):
        with open(company_list_path, 'r') as f:
            self.companies = [line.strip().lower() for line in f if line.strip()]

            self.academic_keywords = [
                "university", "college", "institute",
                "hospital", "school", "academy"
            ]

    def is_industry_affiliation(self, affiliation: str) -> bool:
        #to check if affiliation contains industry markers

        if not affiliation:
            return False
        
        affil_lower = affiliation.lower()
        
        for company in self.companies:
            if company.lower() in affil_lower:
                return True
            return any(company in affil_lower for company in self.companies)
        
        industry_terms = [
        "pharma", "biotech", "bio-tech", 
        "pharmaceutical", "biopharma", "research institute",
        "labs", "healthcare", "drug discovery"
        ]
        
        return any(term in affil_lower for term in industry_terms)
    
    def is_academic_affiliation(self, affiliation: str) -> bool:
        #to check if affiliation contains academic marks

        if not affiliation:
            return False
        
        affil_lower = affiliation.lower()
        return any(keyword in affil_lower for keyword in self.academic_keywords)
    
    def extract_email(self, affiliation: str) -> str:
        #to extract email from affiliation string

        if not affiliation:
            return ""
        
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        match = re.search(email_pattern, affiliation)
        return match.group(0) if match else ""
    
    def analyze_authors(self, authors: List[Dict]) -> Tuple[List[Dict], List[str]]:
        #analyse authors and their affiliations.

        non_academic = []
        companies = set()

        for author in authors:
            affiliation = author.get("affiliation", "")
            if not affiliation:
                continue

            if self.is_industry_affiliation(affiliation):
                non_academic.append({
                    "name": f"{author.get('first_name','')} {author.get('last_name','')}".strip(),
                    "affiliation": affiliation
                }) 

                for company in self.companies:
                    if company in affiliation.lower():
                        companies.add(company.title())

        return non_academic, list(companies)
    
    def find_corresponding_author(self, authors: List[Dict]) -> Dict:
        #to identify corrsponding author with email

        for author in authors:
            affiliation = author.get("affiliation", "")
            email = self.extract_email(affiliation)
            if email:
                return {
                    "name": f"{author.get('last_name', '')} {author.get('first_name', '')}".strip(),
                    "email": email
                }
        return {}
        