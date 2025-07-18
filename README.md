# Chrome Log Payload Decoder

## Description

This Python script processes Chrome JSON log files to extract and decode Base64-encoded payloads. It identifies Base64 strings within event parameters, decodes them, attempts decompression (if applicable), and parses embedded JSON data. The results are saved in both a detailed text file and a structured CSV file for further analysis.

## Features

- Extracts Base64-encoded strings from JSON log event parameters.
- Supports decoding of Base64 payloads, including zlib-compressed data.
- Attempts to parse decoded text as JSON for structured output.
- Saves results to a text file (detailed format) and a CSV file (tabular format).
- Includes input validation and overwrite protection for output files.

## Usage

Run the script with a JSON log file as a command-line argument:

```bash
python3 chrome_log_decode_all_payloads.py <path_to_file.json>
```

### Example

```bash
python3 chrome_log_decode_all_payloads.py example.json
```

### Output Files

- **`<filename>_decoded.txt`**: Contains detailed output with timestamps, source IDs, field names, decoded text, and formatted JSON (if detected).
- **`<filename>_decoded.csv`**: Contains structured data with columns for time, source ID, field name, and decoded text.

If output files already exist, the script will prompt for confirmation to overwrite them.

## Requirements

- Python 3.x
- Standard library modules: `json`, `base64`, `zlib`, `re`, `csv`, `sys`, `pathlib`

## Installation

No installation is required. Download the script and run it with Python 3.

```bash
git clone <repository_url>
cd <repository_directory>
python3 chrome_log_decode_all_payloads.py <log_file.json>
```

## Input Format

The script expects a JSON log file with the following structure:

```json
{
  "events": [
    {
      "time": "<timestamp>",
      "source": { "id": "<source_id>" },
      "params": { "<key>": "<base64_string>", ... }
    },
    ...
  ]
}
```

If the `"events"` key is missing or not a list, the script will exit with an error message.

## Limitations

- Assumes Base64 payloads can be decoded to UTF-8 text; non-UTF-8 data may result in garbled output (handled with error replacement).
- Only processes payloads matching the regex `^[A-Za-z0-9+/=]{20,}$`.
- CSV output excludes JSON data; only decoded text is included.

## Error Handling

- Validates the input JSON structure and exits with an error if invalid.
- Safely handles missing or malformed `"source"` fields in events.
- Catches and reports decoding errors in the output (e.g., invalid Base64 or decompression failures).
- Prompts for confirmation before overwriting existing output files.

## Example Output

For an input file `example.json`, the script generates:

- `example_decoded.txt`:
  ```
  [+] Base64 Payload Found
  Time: 2025-07-18T12:00:00Z
  Source ID: 12345
  Field: payload
  Decoded:
  Sample decoded text
  [JSON Detected]
  {
    "key": "value"
  }
  ================================================
  ```

- `example_decoded.csv`:
  ```csv
  time,source_id,field,decoded_text
  2025-07-18T12:00:00Z,12345,payload,Sample decoded text
  ```

## Contributing

Submit issues or pull requests via the repository for bug reports or feature suggestions.

## License

MIT License (see [LICENSE](LICENSE) file).
