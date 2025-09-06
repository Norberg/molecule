import requests
from bs4 import BeautifulSoup
import re
import sys

class ChemicalInfo:
    def __init__(self, name = None, summary=None, smiles=None, chemical_formula=None, std_molar_entropy=None, std_enthalpy_of_formation=None):
        self.name = name
        self.summary = self.clean_text(summary)
        self.smiles = smiles 
        self.chemical_formula = chemical_formula
        self.std_molar_entropy = self.extract_value(self.clean_text(std_molar_entropy))
        self.std_enthalpy_of_formation = self.extract_value(self.clean_text(std_enthalpy_of_formation))
    
    def __str__(self):
        return f"Name: {self.name}\nSummary: {self.summary}\nSMILES: {self.smiles}\nChemical Formula: {self.chemical_formula}\nStd Molar Entropy: {self.std_molar_entropy}\nStd Enthalpy of Formation: {self.std_enthalpy_of_formation}"

    @staticmethod
    def clean_text(text):
        if text:
            # Remove notes like [1], [2], etc.
            return re.sub(r'\[\d+\]', '', text)
        return text
    
    @staticmethod
    def extract_value(text):
        ''' extract the first numeric value from a string '''
        if text:
            # Normalize Unicode minus (U+2212) to ASCII '-'
            text = text.replace('\u2212', '-')
            match = re.search(r'-?\d+(?:\.\d+)?', text)
            if match:
                return match.group()

def extract_smiles(soup):
    smiles_section = soup.find('a', title="Simplified molecular-input line-entry system")
    if smiles_section:
        smiles_list = smiles_section.find_next('ul', class_='mw-collapsible-content')
        if smiles_list:
            smiles = smiles_list.find('div').text.strip()
            return ChemicalInfo.clean_text(smiles)
    return None

def extract_value_with_unit(soup, title):
    section = soup.find('a', title=title)
    if section:
        value_td = section.find_parent('td').find_next_sibling('td')
        if value_td:
            return ChemicalInfo.clean_text(value_td.text.strip())
    return None

def extract_summary(soup):
    summary = soup.find('p').text.strip() if soup.find('p') else None
    if not summary or len(summary) < 20:
        additional_p = soup.find('p').find_next_sibling('p')
        if additional_p:
            summary = additional_p.text.strip()
    return summary

def extract_wikipedia_info(url):
    if "m.wikipedia.org" in url:
        url = url.replace("m.wikipedia.org", "wikipedia.org")
    headers = {
        'User-Agent': 'Molecule (https://github.com/Norberg/molecule)'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
    except Exception as e:
        raise RuntimeError(f"Failed to fetch {url}: {e}") from e

    if response.status_code != 200:
        raise requests.HTTPError(f"HTTP {response.status_code} for {url}")

    html = response.content

    soup = BeautifulSoup(html, 'html.parser')

    info = ChemicalInfo(
        name = soup.find('h1').text.strip() if soup.find('h1') else None,
        summary = extract_summary(soup),
        smiles = extract_smiles(soup),
        chemical_formula = extract_value_with_unit(soup, "Chemical formula"),
        std_molar_entropy = extract_value_with_unit(soup, "Standard molar entropy"),
        std_enthalpy_of_formation = extract_value_with_unit(soup, "Standard enthalpy change of formation")
    )
    
    return info


def main():

    url = 'https://en.wikipedia.org/wiki/Benzene'
    if len(sys.argv) == 2:
            url = sys.argv[1]
    elif len(sys.argv) > 2:
        print("Usage: python wiki_fetch.py <url>")
        sys.exit(1)
    info = extract_wikipedia_info(url)
    print(info)

if __name__ == "__main__":
    main()
