import os
import json
import requests

# Konfiguracja API Linear
LINEAR_API_URL = "https://api.linear.app/graphql"
LINEAR_API_TOKEN = "lin_api_4sZUdjW7NCKIoMCaBE3LLIl0MEqFnalvQ9rUXoZR"

# Folder z notatkami
FOLDER_PATH = "docs/tech_notes"

def get_issue_id_by_slug(slug):
    """ Pobiera ID issue na podstawie rzeczywistego identifier (sluga) """
    query = """
    query {
      issues {
        nodes {
          id
          identifier
          title
          number
        }
      }
    }
    """

    headers = {
        "Authorization": LINEAR_API_TOKEN,
        "Content-Type": "application/json"
    }

    print(f"🔍 Pobieranie wszystkich issue w Linear...")

    response = requests.post(LINEAR_API_URL, json={"query": query}, headers=headers)
    data = response.json()

    print("🔍 Pełna odpowiedź API:", data)  # Debugowanie

    issues = data.get("data", {}).get("issues", {}).get("nodes", [])

    if not issues:
        print("⚠️ Linear nie zwrócił żadnych issue. Sprawdź API Token!")
        return None

    print(f"🔍 Znaleziono {len(issues)} issue w Linear.")

    for issue in issues:
        print(f"🔹 Sprawdzam: {issue['identifier']} vs {slug}")
        if issue["identifier"] == slug:
            print(f"✅ Dopasowanie! ID issue: {issue['id']}")
            return issue["id"]

    print(f"⚠️ Brak dopasowania dla sluga: {slug}. Sprawdź poprawność nazwy.")
    return None

def add_comment_to_issue(issue_id, comment):
    """ Dodaje komentarz do issue w Linear, używając `commentCreate` i poprawnego formatowania """
    safe_comment = json.dumps(comment)  # Zapewnia poprawne kodowanie JSON

    mutation = f"""
    mutation {{
      commentCreate(input: {{issueId: "{issue_id}", body: {safe_comment}}}) {{
        comment {{
          id
        }}
      }}
    }}
    """

    headers = {
        "Authorization": LINEAR_API_TOKEN,
        "Content-Type": "application/json"
    }

    print(f"📝 Dodawanie komentarza do issue ID: {issue_id}")

    response = requests.post(LINEAR_API_URL, json={"query": mutation}, headers=headers)

    print("📝 Odpowiedź API (komentarz):", response.json())  # Debugowanie odpowiedzi API

    return response.status_code == 200

def process_notes():
    """ Pobiera pliki .md, wyciąga slug z nazwy i wysyła do Linear z debugowaniem """
    for filename in os.listdir(FOLDER_PATH):
        if filename.endswith(".md"):
            slug = filename.replace(".md", "").strip().upper()

            print(f"📂 Przetwarzanie pliku: {filename}, slug: {slug}")

            with open(os.path.join(FOLDER_PATH, filename), "r", encoding="utf-8") as file:
                content = file.read().strip()  # Usunięcie ewentualnych pustych linii

            issue_id = get_issue_id_by_slug(slug)

            if issue_id:
                success = add_comment_to_issue(issue_id, content)
                if success:
                    print(f"✅ Dodano notatkę do issue {slug}.")
                else:
                    print(f"❌ Błąd dodawania notatki do issue {slug}.")
            else:
                print(f"⚠️ Nie znaleziono issue dla sluga {slug}. Sprawdź poprawność nazwy.")

if __name__ == "__main__":
    process_notes()
