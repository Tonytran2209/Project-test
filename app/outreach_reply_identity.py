"""URL-only membership in an account's successfully sent target list."""
from __future__ import annotations

from html.parser import HTMLParser
from urllib.parse import urljoin

from app.outreach_reply_direction import profile_slug_key


def canonical_member_url(final_url: str, html: str) -> str:
    """Use a member page's canonical/og:url link, never a login or external URL."""
    if not profile_slug_key(final_url):
        raise RuntimeError('Profile lookup did not reach a LinkedIn member page.')
    urls, invalid_links = [], []

    class Links(HTMLParser):
        def handle_starttag(self, tag, attrs):
            values = dict(attrs)
            href = None
            if tag == 'link' and 'canonical' in str(values.get('rel') or '').lower().split():
                href = values.get('href')
            elif tag == 'meta' and str(values.get('property') or '').lower() == 'og:url':
                href = values.get('content')
            if href:
                url = urljoin(final_url, href)
                if profile_slug_key(url):
                    urls.append(url)
                else:
                    invalid_links.append(url)
    parser = Links()
    parser.feed(html)
    if invalid_links:
        raise RuntimeError('Profile page advertised a non-member canonical URL; identity is unverified.')
    if len({profile_slug_key(url) for url in urls}) > 1:
        raise RuntimeError('Conflicting member canonical URLs; identity is unverified.')
    return urls[0] if urls else final_url


# @layer business
# @feature replies
def match_sent_profile_url(profile_url: str, sent_profiles: list[dict], account_id: str,
                           resolve_url, cache: dict[str, str]) -> list[dict]:
    """Resolve only the opened recipient, then compare stored URLs locally.

    The resolver must raise on blocked/failed requests, never treat a failed
    identity lookup as evidence that a person is outside the sent list.
    Original target IDs and stored URLs are never changed here.
    """
    key = profile_slug_key(profile_url)
    if not key:
        return []
    eligible = [p for p in sent_profiles if p.get('status') == 'sent'
                and p.get('assigned_account_id') == account_id
                and profile_slug_key(p.get('linkedin_url'))]
    direct = [p for p in eligible if profile_slug_key(p['linkedin_url']) == key]
    if direct or not eligible:
        return direct

    def canonical(url):
        initial = profile_slug_key(url)
        if initial not in cache:
            resolved = profile_slug_key(resolve_url(url))
            if not resolved:
                raise RuntimeError('Member URL could not be resolved; preserving the previous Replies snapshot.')
            cache[initial] = resolved
        return cache[initial]

    observed = canonical(profile_url)
    return [p for p in eligible if profile_slug_key(p['linkedin_url']) == observed]
