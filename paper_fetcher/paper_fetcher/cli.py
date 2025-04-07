import click
from typing import List, Optional
import logging
import csv
from pathlib import Path
from .api import PubMedClient
from .analysis import AffiliationAnalyzer
from .models import Paper, ProcessedPaper

@click.command()
@click.argument("query")
@click.option("--max", default=100, help="Maximum results to fetch (default: 100)")
@click.option("-f", "--file", default=None, help="Output CSV file path (prints to console if omitted)")
@click.option("-d", "--debug", is_flag=True, help="Enable debug logging")
def main(query: str, max: int, file: Optional[str], debug: bool):
    """
    Fetch PubMed papers with pharmaceutical/biotech industry affiliations.
    
    Examples:
      paper-fetcher "cancer AND immunotherapy" -f results.csv
      paper-fetcher "diabetes treatment" -d --max 50
    """
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize with your actual credentials
        client = PubMedClient(email="janmeshjoshi1510@gmail.com", api_key="79d72f171483fee9a74c7f8166e29f347008")
        analyzer = AffiliationAnalyzer("company_list.txt")
        
        logger.info(f"Searching PubMed for: {query}")
        article_ids = client.search_articles(query, max)
        
        if not article_ids:
            logger.warning("No articles found matching your query")
            return
            
        logger.info(f"Found {len(article_ids)} articles. Fetching details...")
        articles = client.fetch_article_details(article_ids)
        
        processed_papers = []
        for article in articles:
            try:
                paper = Paper(
                    pubmed_id=article["pubmed_id"],
                    title=article["title"],
                    publication_date=article["publication_date"],
                    authors=article["authors"],
                    abstract=article["abstract"]
                )
                
                non_academic, companies = analyzer.analyze_authors(paper.authors)
                corresponding = analyzer.find_corresponding_author(paper.authors)
                
                if companies:
                    processed = ProcessedPaper(
                        pubmed_id=paper.pubmed_id,
                        title=paper.title,
                        publication_date=paper.publication_date,
                        non_academic_authors=[a["name"] for a in non_academic],
                        company_affiliations=companies,
                        corresponding_email=corresponding.get("email", "")
                    )
                    processed_papers.append(processed)
                    if debug:
                        logger.debug(f"Found industry paper: {paper.title}")
                        logger.debug(f"Companies: {companies}")
                        logger.debug(f"Authors: {non_academic}")
                elif debug:
                    logger.debug(f"No industry affiliation in: {paper.title}")
                    logger.debug(f"Affiliations: {[a['affiliation'] for a in paper.authors if a.get('affiliation')]}")
                    
            except KeyError as e:
                logger.warning(f"Skipping article due to missing data: {e}")
                continue
        
        if not processed_papers:
            logger.warning("No papers with industry affiliations found")
            return
            
        if file:
            export_to_csv(processed_papers, file)
            logger.info(f"Results saved to {file}")
        else:
            print_results(processed_papers)
            
    except Exception as e:
        logger.error(f"Error: {e}")
        raise click.ClickException(f"Processing failed: {e}")

def export_to_csv(papers: List[ProcessedPaper], path: str):
    """Export processed papers to CSV with proper formatting"""
    try:
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                "PubmedID", "Title", "Publication Date",
                "Non-academic Author(s)", "Company Affiliation(s)", 
                "Corresponding Author Email"
            ])
            writer.writeheader()
            for paper in papers:
                writer.writerow({
                    "PubmedID": paper.pubmed_id,
                    "Title": paper.title,
                    "Publication Date": paper.publication_date,
                    "Non-academic Author(s)": "; ".join(paper.non_academic_authors),
                    "Company Affiliation(s)": "; ".join(paper.company_affiliations),
                    "Corresponding Author Email": paper.corresponding_email
                })
    except IOError as e:
        raise click.ClickException(f"Failed to write CSV: {e}")

def print_results(papers: List[ProcessedPaper]):
    """Print results to console in readable format"""
    click.echo(f"\nFound {len(papers)} papers with industry affiliations:")
    for i, paper in enumerate(papers, 1):
        click.echo(f"\n[{i}] {paper.title}")
        click.echo(f"PMID: {paper.pubmed_id} | Date: {paper.publication_date}")
        click.echo("Industry Authors:")
        for author in paper.non_academic_authors:
            click.echo(f"  • {author}")
        click.echo(f"Companies: {', '.join(paper.company_affiliations)}")
        click.echo(f"Contact Email: {paper.corresponding_email or 'Not available'}")

if __name__ == "__main__":
    main()