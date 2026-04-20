#!/usr/bin/env python3
"""Gmail CLI. Outputs JSON to stdout (read/thread output plain text).

Usage:
  uv run scripts/gmail.py profile
  uv run scripts/gmail.py search QUERY [--max N]
  uv run scripts/gmail.py read MESSAGE_ID
  uv run scripts/gmail.py read-raw MESSAGE_ID
  uv run scripts/gmail.py threads QUERY [--max N]
  uv run scripts/gmail.py thread THREAD_ID
  uv run scripts/gmail.py list-labels
  uv run scripts/gmail.py create-label NAME
  uv run scripts/gmail.py delete-label LABEL_ID
  uv run scripts/gmail.py label MESSAGE_ID [--add LABEL_ID ...] [--remove LABEL_ID ...]
  uv run scripts/gmail.py trash MESSAGE_ID
  uv run scripts/gmail.py untrash MESSAGE_ID
  uv run scripts/gmail.py draft --to TO [--cc CC] [--bcc BCC] [--subject S] --body BODY [--in-reply-to MSG_ID]
  uv run scripts/gmail.py send  --to TO [--cc CC] [--bcc BCC] [--subject S] --body BODY [--in-reply-to MSG_ID]
  uv run scripts/gmail.py attachment MESSAGE_ID ATTACHMENT_ID [OUTPUT_PATH]

Gmail search syntax (same as the Gmail UI):
  from:alice@example.com  is:unread  has:attachment  newer_than:7d  subject:"report"  label:foo

Common label IDs: INBOX, UNREAD, STARRED, IMPORTANT, SENT, DRAFT, TRASH, SPAM.
  Archive a message:     label MSG_ID --remove INBOX
  Mark as read:          label MSG_ID --remove UNREAD
  Star:                  label MSG_ID --add STARRED
"""

import argparse
import base64
import json
import sys
from email.message import EmailMessage

from google_client import gmail_service


def _b64url_decode(data):
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _headers(payload):
    return {h["name"]: h["value"] for h in payload.get("headers", [])}


def _walk_parts(payload):
    if "parts" in payload:
        for p in payload["parts"]:
            yield from _walk_parts(p)
    else:
        yield payload


def _extract_body(payload):
    """Return the best text body from a message payload, preferring text/plain."""
    plain = None
    html = None
    for part in _walk_parts(payload):
        mime = part.get("mimeType", "")
        data = part.get("body", {}).get("data")
        if not data:
            continue
        text = _b64url_decode(data).decode("utf-8", errors="replace")
        if mime == "text/plain" and plain is None:
            plain = text
        elif mime == "text/html" and html is None:
            html = text
    return plain or html or ""


def _list_attachments(payload):
    items = []
    for part in _walk_parts(payload):
        body = part.get("body", {})
        if body.get("attachmentId"):
            items.append({
                "attachmentId": body["attachmentId"],
                "filename": part.get("filename"),
                "mimeType": part.get("mimeType"),
                "size": body.get("size"),
            })
    return items


def _format_message(msg):
    hdrs = _headers(msg["payload"])
    lines = []
    for key in ("From", "To", "Cc", "Subject", "Date"):
        if key in hdrs:
            lines.append(f"{key}: {hdrs[key]}")
    lines.append(f"Message-Id: {msg['id']}")
    lines.append(f"Thread-Id: {msg['threadId']}")
    if msg.get("labelIds"):
        lines.append(f"Labels: {', '.join(msg['labelIds'])}")
    attachments = _list_attachments(msg["payload"])
    if attachments:
        lines.append(f"Attachments: {json.dumps(attachments)}")
    lines.append("")
    lines.append(_extract_body(msg["payload"]).rstrip())
    return "\n".join(lines)


def profile():
    svc = gmail_service()
    print(json.dumps(svc.users().getProfile(userId="me").execute(), indent=2))


def search(query, max_results):
    svc = gmail_service()
    resp = svc.users().messages().list(
        userId="me", q=query, maxResults=max_results,
    ).execute()
    results = []
    for m in resp.get("messages", []):
        msg = svc.users().messages().get(
            userId="me", id=m["id"], format="metadata",
            metadataHeaders=["From", "To", "Subject", "Date"],
        ).execute()
        hdrs = _headers(msg["payload"])
        results.append({
            "id": msg["id"],
            "threadId": msg["threadId"],
            "snippet": msg.get("snippet", ""),
            "labelIds": msg.get("labelIds", []),
            "from": hdrs.get("From"),
            "to": hdrs.get("To"),
            "subject": hdrs.get("Subject"),
            "date": hdrs.get("Date"),
        })
    print(json.dumps(results, indent=2))


def read(message_id):
    svc = gmail_service()
    msg = svc.users().messages().get(userId="me", id=message_id, format="full").execute()
    print(_format_message(msg))


def read_raw(message_id):
    svc = gmail_service()
    msg = svc.users().messages().get(userId="me", id=message_id, format="full").execute()
    print(json.dumps(msg, indent=2))


def threads(query, max_results):
    svc = gmail_service()
    resp = svc.users().threads().list(
        userId="me", q=query, maxResults=max_results,
    ).execute()
    items = [
        {"id": t["id"], "snippet": t.get("snippet", ""), "historyId": t.get("historyId")}
        for t in resp.get("threads", [])
    ]
    print(json.dumps(items, indent=2))


def thread(thread_id):
    svc = gmail_service()
    t = svc.users().threads().get(userId="me", id=thread_id, format="full").execute()
    parts = [_format_message(m) for m in t.get("messages", [])]
    print(("\n\n" + "-" * 60 + "\n\n").join(parts))


def list_labels():
    svc = gmail_service()
    print(json.dumps(svc.users().labels().list(userId="me").execute().get("labels", []), indent=2))


def create_label(name):
    svc = gmail_service()
    body = {
        "name": name,
        "labelListVisibility": "labelShow",
        "messageListVisibility": "show",
    }
    print(json.dumps(svc.users().labels().create(userId="me", body=body).execute(), indent=2))


def delete_label(label_id):
    svc = gmail_service()
    svc.users().labels().delete(userId="me", id=label_id).execute()
    print(json.dumps({"deleted": label_id}))


def modify_labels(message_id, add, remove):
    svc = gmail_service()
    body = {}
    if add:
        body["addLabelIds"] = add
    if remove:
        body["removeLabelIds"] = remove
    if not body:
        print("Nothing to change: pass --add and/or --remove.", file=sys.stderr)
        sys.exit(1)
    result = svc.users().messages().modify(userId="me", id=message_id, body=body).execute()
    print(json.dumps(result, indent=2))


def trash(message_id):
    svc = gmail_service()
    print(json.dumps(svc.users().messages().trash(userId="me", id=message_id).execute(), indent=2))


def untrash(message_id):
    svc = gmail_service()
    print(json.dumps(svc.users().messages().untrash(userId="me", id=message_id).execute(), indent=2))


def _build_message(to, cc, bcc, subject, body, in_reply_to):
    svc = gmail_service()
    msg = EmailMessage()
    msg["To"] = to
    if cc:
        msg["Cc"] = cc
    if bcc:
        msg["Bcc"] = bcc
    thread_id = None
    if in_reply_to:
        original = svc.users().messages().get(
            userId="me", id=in_reply_to, format="metadata",
            metadataHeaders=["Message-Id", "References", "Subject"],
        ).execute()
        thread_id = original["threadId"]
        hdrs = _headers(original["payload"])
        orig_msg_id = hdrs.get("Message-Id") or hdrs.get("Message-ID")
        if orig_msg_id:
            msg["In-Reply-To"] = orig_msg_id
            refs = hdrs.get("References", "")
            msg["References"] = (refs + " " + orig_msg_id).strip()
        if not subject:
            s = hdrs.get("Subject", "")
            subject = s if s.lower().startswith("re:") else f"Re: {s}"
    msg["Subject"] = subject or ""
    msg.set_content(body)
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    payload = {"raw": raw}
    if thread_id:
        payload["threadId"] = thread_id
    return svc, payload


def draft(to, cc, bcc, subject, body, in_reply_to):
    svc, message = _build_message(to, cc, bcc, subject, body, in_reply_to)
    result = svc.users().drafts().create(userId="me", body={"message": message}).execute()
    print(json.dumps(result, indent=2))


def send(to, cc, bcc, subject, body, in_reply_to):
    svc, message = _build_message(to, cc, bcc, subject, body, in_reply_to)
    result = svc.users().messages().send(userId="me", body=message).execute()
    print(json.dumps(result, indent=2))


def attachment(message_id, attachment_id, output_path):
    svc = gmail_service()
    data = svc.users().messages().attachments().get(
        userId="me", messageId=message_id, id=attachment_id,
    ).execute()
    content = _b64url_decode(data["data"])
    if not output_path:
        output_path = f"attachment_{attachment_id[:12]}"
    with open(output_path, "wb") as f:
        f.write(content)
    print(json.dumps({"saved": output_path, "size": len(content)}))


def main():
    if len(sys.argv) >= 2 and sys.argv[1] in ("-h", "--help", "help"):
        print(__doc__)
        sys.exit(0)

    parser = argparse.ArgumentParser(prog="gmail.py", description="Gmail CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("profile")

    p = sub.add_parser("search")
    p.add_argument("query")
    p.add_argument("--max", type=int, default=25)

    p = sub.add_parser("read")
    p.add_argument("message_id")

    p = sub.add_parser("read-raw")
    p.add_argument("message_id")

    p = sub.add_parser("threads")
    p.add_argument("query")
    p.add_argument("--max", type=int, default=25)

    p = sub.add_parser("thread")
    p.add_argument("thread_id")

    sub.add_parser("list-labels")

    p = sub.add_parser("create-label")
    p.add_argument("name")

    p = sub.add_parser("delete-label")
    p.add_argument("label_id")

    p = sub.add_parser("label")
    p.add_argument("message_id")
    p.add_argument("--add", action="append", default=[])
    p.add_argument("--remove", action="append", default=[])

    p = sub.add_parser("trash")
    p.add_argument("message_id")

    p = sub.add_parser("untrash")
    p.add_argument("message_id")

    for name in ("draft", "send"):
        p = sub.add_parser(name)
        p.add_argument("--to", required=True)
        p.add_argument("--cc")
        p.add_argument("--bcc")
        p.add_argument("--subject")
        p.add_argument("--body", required=True)
        p.add_argument("--in-reply-to", dest="in_reply_to")

    p = sub.add_parser("attachment")
    p.add_argument("message_id")
    p.add_argument("attachment_id")
    p.add_argument("output_path", nargs="?")

    args = parser.parse_args()

    dispatch = {
        "profile": lambda: profile(),
        "search": lambda: search(args.query, args.max),
        "read": lambda: read(args.message_id),
        "read-raw": lambda: read_raw(args.message_id),
        "threads": lambda: threads(args.query, args.max),
        "thread": lambda: thread(args.thread_id),
        "list-labels": lambda: list_labels(),
        "create-label": lambda: create_label(args.name),
        "delete-label": lambda: delete_label(args.label_id),
        "label": lambda: modify_labels(args.message_id, args.add, args.remove),
        "trash": lambda: trash(args.message_id),
        "untrash": lambda: untrash(args.message_id),
        "draft": lambda: draft(args.to, args.cc, args.bcc, args.subject, args.body, args.in_reply_to),
        "send": lambda: send(args.to, args.cc, args.bcc, args.subject, args.body, args.in_reply_to),
        "attachment": lambda: attachment(args.message_id, args.attachment_id, args.output_path),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()
