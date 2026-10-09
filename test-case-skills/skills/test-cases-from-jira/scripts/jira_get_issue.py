"""Read-only Jira issue fetcher for the test-cases-from-jira skill.

Usage: python jira_get_issue.py <ISSUE-KEY or browse URL>

Reads JIRA_BASE_URL, JIRA_EMAIL and JIRA_API_TOKEN from the environment.
Sends GET requests only. There is deliberately no code path that writes.
Prints the issue as plain text: summary, status, last updated, description,
acceptance criteria, subtasks and linked issues. If the issue is an Epic,
it also finds every child issue and prints each one in the same format.
"""
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

MAX_CHILDREN = 100


def fail(message):
    print("ERROR: " + message, file=sys.stderr)
    sys.exit(1)


def get_json(url, auth_header, soft=False):
    # GET only. Never pass a method or a body here.
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", auth_header)
    req.add_header("Accept", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        if soft:
            return None
        hints = {
            401: "Jira rejected the credentials. Check JIRA_EMAIL and JIRA_API_TOKEN.",
            403: "The account is not allowed to see this issue.",
            404: "Issue not found, or the account cannot see it.",
        }
        fail("Jira returned HTTP %d. %s" % (e.code, hints.get(e.code, "")))
    except urllib.error.URLError as e:
        fail("Could not reach Jira: %s" % e.reason)


def adf_to_text(node):
    """Flatten Atlassian Document Format (or a plain string) to text."""
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    kind = node.get("type")
    if kind == "text":
        return node.get("text", "")
    if kind == "hardBreak":
        return "\n"
    children = node.get("content", [])
    if kind == "listItem":
        inner = " ".join(adf_to_text(c).strip() for c in children)
        return "- " + inner + "\n"
    inner = "".join(adf_to_text(c) for c in children)
    if kind in ("paragraph", "heading", "codeBlock", "blockquote"):
        return inner + "\n"
    if kind == "mention":
        return node.get("attrs", {}).get("text", "")
    return inner


def find_children(base, key, auth):
    """Return the keys of issues whose parent is `key` (epic children, subtasks)."""
    jql = urllib.parse.quote("parent = %s ORDER BY key ASC" % key)
    keys, token = [], None
    while len(keys) < MAX_CHILDREN:
        url = "%s/rest/api/3/search/jql?jql=%s&fields=summary&maxResults=50" % (base, jql)
        if token:
            url += "&nextPageToken=" + urllib.parse.quote(token)
        page = get_json(url, auth, soft=True)
        if page is None:
            # Older sites: fall back to the classic search endpoint.
            url = "%s/rest/api/3/search?jql=%s&fields=summary&maxResults=%d" % (base, jql, MAX_CHILDREN)
            page = get_json(url, auth)
            keys = [i["key"] for i in page.get("issues", [])]
            break
        keys += [i["key"] for i in page.get("issues", [])]
        token = page.get("nextPageToken")
        if not token or page.get("isLast"):
            break
    return keys[:MAX_CHILDREN]


def print_issue(base, key, auth, heading):
    issue = get_json("%s/rest/api/3/issue/%s?expand=names" % (base, key), auth)
    fields = issue.get("fields", {})
    names = issue.get("names", {})
    issue_type = (fields.get("issuetype") or {}).get("name") or ""

    print(heading)
    print("KEY: " + issue.get("key", key))
    print("SUMMARY: " + (fields.get("summary") or ""))
    print("TYPE: " + issue_type)
    print("STATUS: " + ((fields.get("status") or {}).get("name") or ""))
    print("UPDATED: " + (fields.get("updated") or ""))
    print()
    print("DESCRIPTION:")
    print(adf_to_text(fields.get("description")).strip() or "(empty)")
    print()

    # Acceptance criteria usually lives in a custom field, so find it by name.
    ac_found = False
    for field_id, label in names.items():
        if re.search(r"acceptance\s+criteria", label or "", re.I):
            text = adf_to_text(fields.get(field_id)).strip()
            print("ACCEPTANCE CRITERIA (field '%s'):" % label)
            print(text or "(empty)")
            print()
            ac_found = True
    if not ac_found:
        print("ACCEPTANCE CRITERIA: no field with that name exists on this issue")
        print()

    subtasks = fields.get("subtasks") or []
    if subtasks:
        print("SUBTASKS:")
        for s in subtasks:
            print("- %s: %s" % (s.get("key"), (s.get("fields") or {}).get("summary", "")))
        print()

    links = fields.get("issuelinks") or []
    if links:
        print("LINKED ISSUES:")
        for link in links:
            kind = link.get("type", {})
            if "outwardIssue" in link:
                other, rel = link["outwardIssue"], kind.get("outward", "relates to")
            else:
                other, rel = link.get("inwardIssue", {}), kind.get("inward", "relates to")
            print("- %s %s: %s" % (rel, other.get("key"), (other.get("fields") or {}).get("summary", "")))
        print()
    return issue_type


def main():
    if len(sys.argv) != 2:
        fail("usage: python jira_get_issue.py <ISSUE-KEY or browse URL>")
    match = re.search(r"[A-Z][A-Z0-9]+-\d+", sys.argv[1])
    if not match:
        fail("could not find an issue key like PROJ-123 in: " + sys.argv[1])
    key = match.group(0)

    base = os.environ.get("JIRA_BASE_URL", "").rstrip("/")
    email = os.environ.get("JIRA_EMAIL", "")
    token = os.environ.get("JIRA_API_TOKEN", "")
    missing = [n for n, v in (("JIRA_BASE_URL", base), ("JIRA_EMAIL", email), ("JIRA_API_TOKEN", token)) if not v]
    if missing:
        fail("missing environment variables: " + ", ".join(missing))
    if not base.startswith("https://"):
        fail("JIRA_BASE_URL must start with https://")

    raw = base64.b64encode((email + ":" + token).encode("utf-8")).decode("ascii")
    auth = "Basic " + raw

    issue_type = print_issue(base, key, auth, "=== ISSUE ===")

    if issue_type.lower() == "epic":
        children = find_children(base, key, auth)
        print("=== CHILD ISSUES OF %s: %d found ===" % (key, len(children)))
        if len(children) >= MAX_CHILDREN:
            print("WARNING: stopped at %d children; there may be more." % MAX_CHILDREN)
        print()
        for child in children:
            print_issue(base, child, auth, "--- CHILD ---")


if __name__ == "__main__":
    main()
