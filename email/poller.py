""""This module implements an email poller that checks for new emails at regular intervals.
Checks for unread emails,checks if they need a reply or escalation, and sends replies if applicable."""
import time
from EMail.gmail_client import GmailClient
from EMail.parser import parse_message_to_event
from router.decision import handle_incoming_email

POLL_INTERVAL = 10  # seconds
client = GmailClient()

def start_polling():
    try:
        while True:
            messages = client.list_unread_messages()

            if messages:
                print(f"Found {len(messages)} unread message(s).")

            for m in messages:
                msg = client.get_message(m["id"])
                event = parse_message_to_event(msg)

                print(f"Processing message {event.id} subject: {event.subject}")

                result = handle_incoming_email(event)

                # Only send reply if not escalating
                if not result.should_escalate:
                    client.send_reply(
                        to_email=event.from_address,
                        subject="Re: " + (event.subject or ""),
                        body_text=result.reply_text
                    )

                client.mark_as_read(m["id"])

            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print("Poller stopped.")
