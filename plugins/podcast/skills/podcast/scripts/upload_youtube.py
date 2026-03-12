#!/usr/bin/env python3
"""YouTube Data API v3 resumable upload — standard library only"""

import argparse
import glob
import http.server
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

SCOPES = "https://www.googleapis.com/auth/youtube.upload"
REDIRECT_PORT = 8085
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}"


def find_client_secret():
    """Auto-discover Google OAuth client secret"""
    patterns = [
        os.path.expanduser("~/Downloads/client_secret_*.json"),
        os.path.expanduser("~/.config/google/client_secret_*.json"),
    ]
    for p in patterns:
        matches = glob.glob(p)
        if matches:
            return sorted(matches)[-1]
    return None


def load_client_config(path):
    with open(path) as f:
        data = json.load(f)
    cfg = data.get("installed") or data.get("web")
    return cfg["client_id"], cfg["client_secret"]


def get_auth_code(client_id):
    """Browser OAuth flow → authorization code"""
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        + urllib.parse.urlencode({
            "client_id": client_id,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": SCOPES,
            "access_type": "offline",
            "prompt": "consent",
        })
    )

    code_holder = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            code_holder["code"] = qs.get("code", [None])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("Auth complete! You can close this tab.".encode("utf-8"))

        def log_message(self, *args):
            pass

    server = http.server.HTTPServer(("localhost", REDIRECT_PORT), Handler)
    print("  Opening browser for Google auth...")
    webbrowser.open(auth_url)
    server.handle_request()
    server.server_close()
    return code_holder.get("code")


def exchange_code(client_id, client_secret, code, token_path):
    data = urllib.parse.urlencode({
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }).encode()

    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    with urllib.request.urlopen(req) as resp:
        tokens = json.loads(resp.read())

    with open(token_path, "w") as f:
        json.dump(tokens, f, indent=2)
    print(f"  Token saved: {token_path}")
    return tokens["access_token"]


def refresh_token(client_id, client_secret, token_path):
    with open(token_path) as f:
        tokens = json.load(f)

    data = urllib.parse.urlencode({
        "refresh_token": tokens["refresh_token"],
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
    }).encode()

    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data)
    with urllib.request.urlopen(req) as resp:
        new_tokens = json.loads(resp.read())

    tokens["access_token"] = new_tokens["access_token"]
    with open(token_path, "w") as f:
        json.dump(tokens, f, indent=2)
    return tokens["access_token"]


def get_access_token(client_secret_path, token_path):
    client_id, client_secret = load_client_config(client_secret_path)

    if os.path.exists(token_path):
        try:
            return refresh_token(client_id, client_secret, token_path)
        except Exception:
            print("  Token expired. Re-authenticating...")

    code = get_auth_code(client_id)
    if not code:
        print("ERROR: Failed to get authorization code.", file=sys.stderr)
        sys.exit(1)
    return exchange_code(client_id, client_secret, code, token_path)


def upload_video(access_token, video_path, title, description, tags, privacy):
    """Resumable upload"""
    metadata = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "22",
            "defaultLanguage": "ko",
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }

    meta_bytes = json.dumps(metadata).encode("utf-8")
    file_size = os.path.getsize(video_path)

    init_req = urllib.request.Request(
        "https://www.googleapis.com/upload/youtube/v3/videos?"
        + urllib.parse.urlencode({"uploadType": "resumable", "part": "snippet,status"}),
        data=meta_bytes,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=utf-8",
            "X-Upload-Content-Length": str(file_size),
            "X-Upload-Content-Type": "video/mp4",
        },
        method="POST",
    )

    with urllib.request.urlopen(init_req) as resp:
        upload_url = resp.headers["Location"]

    print(f"  Uploading... ({file_size / 1024 / 1024:.1f} MB)")
    with open(video_path, "rb") as f:
        video_data = f.read()

    upload_req = urllib.request.Request(
        upload_url,
        data=video_data,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "video/mp4",
            "Content-Length": str(file_size),
        },
        method="PUT",
    )

    with urllib.request.urlopen(upload_req, timeout=300) as resp:
        return json.loads(resp.read())


def main():
    parser = argparse.ArgumentParser(description="YouTube Upload")
    parser.add_argument("--video", required=True, help="MP4 file path")
    parser.add_argument("--title", required=True, help="Video title")
    parser.add_argument("--description", default="", help="Video description")
    parser.add_argument("--tags", default="", help="Tags (comma-separated)")
    parser.add_argument("--privacy", default="unlisted", choices=["public", "unlisted", "private"])
    parser.add_argument("--client-secret", default=None, help="OAuth client secret path")
    parser.add_argument("--token-path", default=None, help="Token storage path")
    args = parser.parse_args()

    client_secret = args.client_secret or find_client_secret()
    if not client_secret:
        print("ERROR: Google OAuth client secret not found.", file=sys.stderr)
        print("  Place client_secret_*.json in ~/Downloads/ or use --client-secret", file=sys.stderr)
        sys.exit(1)

    token_path = args.token_path or os.path.join(os.path.dirname(args.video), "youtube_token.json")
    tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []

    print("1/2 OAuth authentication...")
    access_token = get_access_token(client_secret, token_path)

    print("2/2 YouTube upload...")
    result = upload_video(access_token, args.video, args.title, args.description, tags, args.privacy)

    video_id = result["id"]
    url = f"https://youtu.be/{video_id}"
    print(f"\nUpload complete!")
    print(f"  URL: {url}")
    print(f"  Status: {result['status']['privacyStatus']}")

    meta_path = os.path.join(os.path.dirname(args.video), "metadata.json")
    with open(meta_path, "w") as f:
        json.dump({
            "youtube_url": url,
            "youtube_id": video_id,
            "title": args.title,
            "description": args.description,
            "privacy": result["status"]["privacyStatus"],
        }, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
