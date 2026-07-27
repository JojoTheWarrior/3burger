import argparse
import copy
import json
import sys
import urllib.error
import urllib.request


SUBMIT_ORDER_URL = "https://aws-api.harveys.ca/CaraAPI/Service/VECOMV3/OrderService/submitOrder/EN?c=submitOrder"
SENSITIVE_KEYS = {
    "cardAccountNbr",
    "cardCVVCode",
    "authToken",
}


def load_payload(path):
    if path == "-":
        return json.load(sys.stdin)

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def redact_value(key, value):
    if key == "cardAccountNbr" and isinstance(value, str):
        return f"************{value[-4:]}" if len(value) >= 4 else "********"
    if key in SENSITIVE_KEYS:
        return "[REDACTED]"
    return value


def redact_payload(value):
    if isinstance(value, dict):
        return {
            key: redact_value(key, redact_payload(item))
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_payload(item) for item in value]
    return value


def send_submit_order(payload, url):
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://order.harveys.ca",
            "Referer": "https://order.harveys.ca/",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/150.0.0.0 Safari/537.36"
            ),
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return response.status, dict(response.headers), response.read()
    except urllib.error.HTTPError as error:
        return error.code, dict(error.headers), error.read()


def print_response(status, headers, body):
    content_type = headers.get("Content-Type", "")
    text = body.decode("utf-8", errors="replace")

    print(f"HTTP {status}")
    print(f"Content-Type: {content_type or '(missing)'}")
    print()

    if "application/json" in content_type.lower():
        try:
            print(json.dumps(json.loads(text), indent=2))
            return
        except json.JSONDecodeError:
            pass

    print(text[:4000])
    if len(text) > 4000:
        print("\n... response truncated ...")


def main():
    parser = argparse.ArgumentParser(
        description="Send a Harvey's submitOrder JSON POST and print the response."
    )
    parser.add_argument(
        "payload",
        help="Path to a JSON payload file, or '-' to read JSON from stdin.",
    )
    parser.add_argument("--url", default=SUBMIT_ORDER_URL)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the redacted payload without sending the POST.",
    )
    args = parser.parse_args()

    payload = load_payload(args.payload)

    if args.dry_run:
        print(json.dumps(redact_payload(copy.deepcopy(payload)), indent=2))
        return

    status, headers, body = send_submit_order(payload, args.url)
    print_response(status, headers, body)


if __name__ == "__main__":
    main()
