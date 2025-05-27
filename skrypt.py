import os
import re
import requests

from dotenv import load_dotenv
load_dotenv()

# Config
LINEAR_API_KEY = os.getenv("key")
REPO_URL = "https://github.com/dawid997997/Disproportion/tree/master/docs/tech_notes"  # Zmień na swój
TECH_NOTES_FOLDER = "tech_notes"

headers = {
    "Authorization": LINEAR_API_KEY,
    "Content-Type": "application/json"
}

def extract_slug(filename):
    match = re.match(r"(APP-\d+)", filename)
    return match.group(1) if match else None

def post_comment_to_issue(issue_slug, note_url):
    query = """
    mutation CreateComment($input: CommentCreateInput!) {
      commentCreate(input: $input) {
        success
      }
    }
    """
    variables = {
        "input": {
            "issueId": issue_slug,
            "body": f" Powiązana notatka techniczna: [Zobacz plik]({note_url})"
        }
    }

    response = requests.post(
        "https://api.linear.app/graphql",
        headers=headers,
        json={"query": query, "variables": variables}
    )

    if response.status_code == 200:
        print(f" Dodano komentarz do {issue_slug}")
    else:
        print(f" Błąd dodawania do {issue_slug}: {response.text}")

def get_issue_id_by_slug(slug):
    query = """
    query IssueBySlug($slug: String!) {
      issue(slug: $slug) {
        id
      }
    }
    """
    variables = {"slug": slug}

    response = requests.post(
        "https://api.linear.app/graphql",
        headers=headers,
        json={"query": query, "variables": variables}
    )

    data = response.json()
    try:
        return data["data"]["issue"]["id"]
    except:
        print(f" Nie znaleziono taska o slugu {slug}")
        return None

def main():
    for filename in os.listdir(TECH_NOTES_FOLDER):
        if not filename.endswith(".md"):
            continue

        slug = extract_slug(filename)
        if not slug:
            print(f" Pominięto plik (brak slugu): {filename}")
            continue

        issue_id = get_issue_id_by_slug(slug)
        if not issue_id:
            continue

        note_url = f"{REPO_URL}/{filename}"
        post_comment_to_issue(issue_id, note_url)

if __name__ == "__main__":
    main()
