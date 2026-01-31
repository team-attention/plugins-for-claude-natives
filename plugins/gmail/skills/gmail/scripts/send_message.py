#!/usr/bin/env python3
"""Gmail 메시지 발송 CLI.

Usage:
    # 새 메일 발송
    uv run python send_message.py --account work \
        --to "user@example.com" \
        --subject "안녕하세요" \
        --body "메일 내용입니다."

    # HTML 메일
    uv run python send_message.py --account work \
        --to "user@example.com" \
        --subject "공지" \
        --body "<h1>제목</h1><p>내용</p>" \
        --html

    # 첨부파일 포함
    uv run python send_message.py --account work \
        --to "user@example.com" \
        --subject "파일 전송" \
        --body "첨부파일을 확인해주세요." \
        --attach file1.pdf,file2.xlsx

    # 답장
    uv run python send_message.py --account work \
        --to "user@example.com" \
        --subject "Re: 원본 제목" \
        --body "답장 내용" \
        --reply-to <message_id> \
        --thread <thread_id>

    # 초안 생성
    uv run python send_message.py --account work \
        --to "user@example.com" \
        --subject "나중에 보낼 메일" \
        --body "초안 내용" \
        --draft
"""

import argparse
import json
from pathlib import Path

from gmail_client import ADCGmailClient, GmailClient, get_all_accounts


def main():
    parser = argparse.ArgumentParser(description="Gmail 메시지 발송")
    parser.add_argument("--account", "-a", help="계정 식별자")
    parser.add_argument("--adc", action="store_true", help="Application Default Credentials 사용")
    parser.add_argument("--to", "-t", required=True, help="수신자 (쉼표 구분)")
    parser.add_argument("--subject", "-s", required=True, help="제목")
    parser.add_argument("--body", "-b", required=True, help="본문")
    parser.add_argument("--cc", help="참조")
    parser.add_argument("--bcc", help="숨은 참조")
    parser.add_argument("--html", action="store_true", help="HTML 형식")
    parser.add_argument("--attach", help="첨부파일 경로 (쉼표 구분)")
    parser.add_argument("--reply-to", help="답장할 메시지 ID")
    parser.add_argument("--thread", help="스레드 ID")
    parser.add_argument("--draft", action="store_true", help="초안으로 저장")
    parser.add_argument("--json", action="store_true", help="JSON 형식 출력")

    args = parser.parse_args()
    base_path = Path(__file__).parent.parent

    if args.adc:
        client = ADCGmailClient()
    else:
        accounts = get_all_accounts(base_path)
        if not accounts:
            print("❌ 등록된 계정이 없습니다.")
            return

        account = args.account or accounts[0]
        client = GmailClient(account, base_path)

    attachments = args.attach.split(",") if args.attach else None

    if args.draft:
        result = client.create_draft(
            to=args.to,
            subject=args.subject,
            body=args.body,
            cc=args.cc,
            bcc=args.bcc,
            html=args.html,
        )
        status_msg = "초안 저장됨"
    else:
        result = client.send_message(
            to=args.to,
            subject=args.subject,
            body=args.body,
            cc=args.cc,
            bcc=args.bcc,
            html=args.html,
            attachments=attachments,
            reply_to_message_id=args.reply_to,
            thread_id=args.thread,
        )
        status_msg = "발송 완료"

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"✅ {status_msg}")
        print(f"   ID: {result['id']}")
        if 'thread_id' in result:
            print(f"   Thread ID: {result['thread_id']}")


if __name__ == "__main__":
    main()
