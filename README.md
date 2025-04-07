# paper_fetcher

- The code is organised in modular way. Inside paper_fetcher folder, api.py file contains api integration and information retrieval, analysis.py file executes the necessary checks for author's affiliation, models.py deals with converting and exporting the data in csv format, cli.py handles inputs, and makes necessary calls.

- To install dependencies use command "poetry install"

- To execute program use command "poetry run paper_fetcher "keyword" -f test.csv"

- Tools/Libraries used: poetry, Entrez from Bio, certifi, ssl, dataclass

- LLM: ChatGPT chat link: https://chatgpt.com/share/67f39ecf-576c-8008-8f9c-28db7548f73d
