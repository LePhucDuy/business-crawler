from typing import List, Optional
from bs4 import BeautifulSoup

def find_label_value(soup: BeautifulSoup, label_candidates: List[str]) -> Optional[str]:
    """
    Defensively search for a label in the page and return the adjacent value.
    This works for structures like <th>Label</th><td>Value</td> or <dt>Label</dt><dd>Value</dd>
    """
    for candidate in label_candidates:
        elements = soup.find_all(string=lambda text: text and candidate.lower() in text.lower())
        for el in elements:
            parent = el.parent
            if parent.name in ('th', 'dt', 'td'):
                next_sibling = parent.find_next_sibling(['td', 'dd'])
                if next_sibling:
                    return " ".join(next_sibling.get_text(strip=True).split())
            
            if parent.name == 'span':
                next_sibling = parent.find_next_sibling()
                if next_sibling:
                    return " ".join(next_sibling.get_text(strip=True).split())
                    
    return None
