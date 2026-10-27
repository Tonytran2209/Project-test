"""Automatic draft preparation and persistent Ready inbox; never queues sends."""
from __future__ import annotations

from collections import defaultdict

from app.linkedin_message_template import build_message, template_uses_company
from app.outreach_message_company import attach_target_companies
from app.outreach_message_preparation_store import (
    get_message_preparation_candidates, get_campaign_message_template_for_batch,
    get_outreach_supabase_client,
)


# @layer business
# @feature messages
def prepare_accepted_ready_batches(*, client) -> dict:
    candidates = get_message_preparation_candidates(client=client).get('items') or []
    groups = defaultdict(list)
    templates = {}
    skipped = 0
    for offset in range(0, len(candidates), 100):
        chunk = candidates[offset:offset + 100]
        rows = (client.table('outreach_job_targets').select('id,ready_first_name,auto_message_dismissed')
                .in_('id', [c['source_target_id'] for c in chunk]).execute()).data or []
        metadata = {str(row['id']): row for row in rows}
        for item in chunk:
            saved = metadata.get(str(item['source_target_id']), {})
            name = str(saved.get('ready_first_name') or '').strip()
            campaign = item.get('campaign_id')
            if not campaign or saved.get('auto_message_dismissed'):
                skipped += 1
                continue
            if campaign not in templates:
                templates[campaign] = get_campaign_message_template_for_batch(
                    None, campaign_id=campaign, client=client).get('message_template') or ''
            template = templates[campaign]
            candidate = dict(item)
            candidate['message_text'] = None
            try:
                if template_uses_company(template):
                    attach_target_companies([candidate], client=client)
                if name and template:
                    candidate['message_text'] = build_message(name, template, company=candidate.get('company_name', ''))
            except ValueError:
                # Missing personalization must not prevent creating the recipient
                # snapshot. Queue validation still checks template/company, and
                # the sending worker reads the actual name from LinkedIn.
                pass
            candidate['first_name'] = name or None
            groups[(item['connect_batch_id'], campaign, template)].append(candidate)
    created = []
    for (source_id, campaign, template), items in groups.items():
        result = client.rpc('prepare_outreach_ready_batch', {
            'p_source_id': source_id, 'p_campaign_id': campaign,
            'p_template': template, 'p_targets': items,
        }).execute().data
        if result and result.get('created'):
            created.append(result)
    return {'batches': created, 'skipped': skipped}


# @layer database
# @feature messages
def list_ready_batch_notifications(*, client=None) -> list[dict]:
    client = client if client is not None else get_outreach_supabase_client()
    return (client.table('outreach_ready_notifications').select('*,outreach_message_batches!inner(status)')
            .eq('outreach_message_batches.status', 'prepared')
            .order('created_at', desc=True).limit(200).execute()).data or []


def mark_ready_batch_seen(batch_id: str, *, client=None) -> None:
    from datetime import datetime, timezone
    client = client if client is not None else get_outreach_supabase_client()
    (client.table('outreach_ready_notifications').update({'seen_at': datetime.now(timezone.utc).isoformat()})
     .eq('batch_id', batch_id).execute())


def delete_ready_message_batches(batch_ids: list[str], *, client=None) -> dict:
    from uuid import UUID
    ids = list(dict.fromkeys(str(UUID(str(value))) for value in batch_ids))
    if not ids or len(ids) > 200:
        raise ValueError('Select between 1 and 200 Ready batches.')
    client = client if client is not None else get_outreach_supabase_client()
    return client.rpc('delete_outreach_ready_batches', {'p_batch_ids': ids}).execute().data
