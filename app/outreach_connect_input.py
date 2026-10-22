"""Keep pasted company names paired with their original URL positions."""

from __future__ import annotations


def prepare_connect_entries(urls, company_names=None) -> list[tuple[str, str]]:
    raw_urls = [str(url or "").strip() for url in urls]
    if company_names is None:
        return [(url, "") for url in raw_urls if url]
    if not isinstance(company_names, list) or any(
        not isinstance(name, str) for name in company_names
    ):
        raise ValueError("Company names must be a list of text values.")
    if len(company_names) != len(raw_urls):
        raise ValueError("Enter one company name for each URL, in the same order.")
    entries = []
    for index, (url, name) in enumerate(zip(raw_urls, company_names), start=1):
        name = name.strip()
        if not url or not name:
            raise ValueError(f"Row {index}: URL and company name must both be filled in.")
        if any(char in url or char in name for char in ("\n", "\r", "\t")):
            raise ValueError(f"Row {index}: enter one URL and one company per line.")
        if len(name) > 200:
            raise ValueError(f"Row {index}: company name must be at most 200 characters.")
        entries.append((url, name))
    return entries
