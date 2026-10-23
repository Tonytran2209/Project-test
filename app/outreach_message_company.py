"""Resolve company data from the exact prospect belonging to a message target."""

from __future__ import annotations

from app.outreach_reply_direction import profile_slug_key


def attach_target_companies(targets: list[dict], *, client) -> None:
    ids = sorted({str(target.get("prospect_id") or "").strip() for target in targets} - {""})
    prospects = {}
    for offset in range(0, len(ids), 100):
        response = (client.table("outreach_prospects")
                    .select("id,linkedin_url,normalized_url,company_name")
                    .in_("id", ids[offset:offset + 100]).execute())
        for row in response.data or []:
            prospects[str(row.get("id") or "")] = row
    for target in targets:
        prospect = prospects.get(str(target.get("prospect_id") or "").strip())
        target_keys = {profile_slug_key(target[key]) for key in ("linkedin_url", "normalized_url") if target.get(key)}
        prospect_keys = {profile_slug_key(prospect[key]) for key in ("linkedin_url", "normalized_url") if prospect and prospect.get(key)}
        if not prospect or len(target_keys) != 1 or "" in target_keys or target_keys != prospect_keys:
            raise ValueError(f"Cannot match company data to recipient {target.get('linkedin_url') or target.get('id')}.")
        target["company_name"] = str(prospect.get("company_name") or "").strip()


def company_for_target(target: dict, *, client) -> str:
    resolved = dict(target)
    attach_target_companies([resolved], client=client)
    return resolved["company_name"]
