import json
import base64
import zlib
import re
import csv
import sys
from pathlib import Path

BASE64_REGEX = re.compile(r"^[A-Za-z0-9+/=]{20,}$")

def extract_base64_payloads(event):
    matches = []
    params = event.get("params", {})
    for k, v in params.items():
        if isinstance(v, str) and BASE64_REGEX.fullmatch(v):
            matches.append((k, v))
    return matches

def try_decode(payload_b64):
    try:
        decoded_bytes = base64.b64decode(payload_b64)
        try:
            decompressed = zlib.decompress(decoded_bytes)
        except:
            try:
                decompressed = zlib.decompress(decoded_bytes, zlib.MAX_WBITS | 16)
            except:
                decompressed = decoded_bytes

        # Assuming UTF-8 encoding; non-UTF-8 data may appear garbled
        decoded_text = decompressed.decode("utf-8", errors="replace")

        # Try parsing embedded JSON
        try:
            json_obj = json.loads(decoded_text)
            formatted_json = json.dumps(json_obj, indent=2)
            return decoded_text, formatted_json
        except:
            return decoded_text, None

    except Exception as e:
        return f"[Decode error: {e}]", None

def scan_file(log_file_path):
    with open(log_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "events" not in data or not isinstance(data["events"], list):
        print("Error: Invalid log format - missing or invalid 'events' key.")
        sys.exit(1)

    decoded_outputs = []
    for event in data["events"]:
        time = event.get("time")
        source = event.get("source")
        source_id = source.get("id") if isinstance(source, dict) else None
        for key, b64string in extract_base64_payloads(event):
            decoded, pretty_json = try_decode(b64string)
            decoded_outputs.append({
                "time": time,
                "source_id": source_id,
                "field": key,
                "decoded_text": decoded,
                "pretty_json": pretty_json
            })
    return decoded_outputs

def save_outputs(results, base_name):
    txt_output = f"{base_name}_decoded.txt"
    csv_output = f"{base_name}_decoded.csv"

    # Check if files exist and prompt for overwrite
    if Path(txt_output).exists() or Path(csv_output).exists():
        overwrite = input("Output files already exist. Overwrite? (y/n): ").lower()
        if overwrite != 'y':
            print("Aborting output save.")
            return

    # Save to TXT
    with open(txt_output, "w", encoding="utf-8") as txt:
        for entry in results:
            txt.write("[+] Base64 Payload Found\n")
            txt.write(f"Time: {entry['time']}\n")
            txt.write(f"Source ID: {entry['source_id']}\n")
            txt.write(f"Field: {entry['field']}\n")
            txt.write("Decoded:\n")
            txt.write(entry['decoded_text'] + "\n")
            if entry['pretty_json']:
                txt.write("\n[JSON Detected]\n")
                txt.write(entry['pretty_json'] + "\n")
            txt.write("="*80 + "\n\n")

    # Save to CSV
    with open(csv_output, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["time", "source_id", "field", "decoded_text"])
        writer.writeheader()
        for entry in results:
            writer.writerow({
                "time": entry['time'],
                "source_id": entry['source_id'],
                "field": entry['field'],
                "decoded_text": entry['decoded_text']
            })

    print(f"\n[*] Saved TXT: {txt_output}")
    print(f"[*] Saved CSV: {csv_output}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 chrome_log_decode_all_payloads.py <path_to_the_file.json>")
        sys.exit(1)

    log_file = sys.argv[1]
    base_name = Path(log_file).stem

    print(f"Processing: {log_file}")
    decoded_data = scan_file(log_file)

    if decoded_data:
        save_outputs(decoded_data, base_name)
    else:
        print("No decodable base64 payloads found.")