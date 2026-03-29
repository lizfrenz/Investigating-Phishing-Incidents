from __future__ import annotations

import base64
import binascii
import quopri
import re
import argparse
import json
import logging
from email.header import decode_header # Added to handle email headers

# ---------------------------------------------------------------------------
# Configuration & Limits
# ---------------------------------------------------------------------------
MAX_INPUT_LENGTH  = 4096
MAX_DECODED_BYTES = 8192
MIN_TOKEN_LENGTH  = 4      
LATIN1_PRINTABLE_THRESHOLD = 0.95  

# Fixed Allowlist: Now allows all standard printable ASCII and whitespace
# This prevents crashes when common email punctuation (<, >, @) is present.
VALID_CHARACTERS = re.compile(r'^[\x20-\x7E\t\n\r]*$')

logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_printable_text(data: bytes) -> tuple[bool, str | None, str | None]:
    if len(data) > MAX_DECODED_BYTES:
        logger.debug("Decoded bytes (%d) exceed MAX_DECODED_BYTES — skipping.", len(data))
        return False, None, None

    for encoding in ("utf-8", "latin-1"):
        try:
            decoded = data.decode(encoding)
            if not decoded:
                continue

            printable_ratio = (
                sum(1 for c in decoded if c.isprintable() or c.isspace())
                / len(decoded)
            )
            threshold = LATIN1_PRINTABLE_THRESHOLD if encoding == "latin-1" else 0.5
            if printable_ratio >= threshold:
                return True, decoded, encoding

        except UnicodeDecodeError:
            continue

    return False, None, None


def decode_mixed_text(input_text: str) -> list[str]:
    results: list[str] = []

    # ------------------------------------------------------------------
    # 1. MIME Encoded-Word (RFC 2047) decoding (e.g., =?utf-8?B?...?=)
    # ------------------------------------------------------------------
    if "=?" in input_text and "?=" in input_text:
        try:
            decoded_parts = decode_header(input_text)
            reconstructed = []
            is_mime_encoded = False
            
            for part, enc in decoded_parts:
                if isinstance(part, bytes):
                    is_mime_encoded = True
                    enc = enc or "utf-8"
                    try:
                        reconstructed.append(part.decode(enc, errors='replace'))
                    except LookupError:
                        reconstructed.append(part.decode('utf-8', errors='replace'))
                elif isinstance(part, str):
                    reconstructed.append(part)

            if is_mime_encoded:
                results.append(f"MIME Header Decoded:\n{repr(''.join(reconstructed))}")
        except Exception as exc:
            logger.debug("MIME header decode failed: %s", exc)

    # ------------------------------------------------------------------
    # 2. Quoted-Printable block decoding
    # ------------------------------------------------------------------
    qp_matched = False
    if "=" in input_text:
        try:
            decoded_bytes = quopri.decodestring(input_text.encode("utf-8"))
            success, text, enc = is_printable_text(decoded_bytes)

            if success and decoded_bytes != input_text.encode("utf-8"):
                results.append(f"Quoted-Printable Decoded ({enc.upper()}):\n{repr(text)}")
                qp_matched = True

        except (ValueError, binascii.Error) as exc:
            logger.debug("QP decode failed: %s", exc)

    # ------------------------------------------------------------------
    # 3. Full-Block Fallback (Handles multi-line Base64/Hex)
    # ------------------------------------------------------------------
    collapsed_text = "".join(input_text.split())
    block_matched = False
    
    if len(collapsed_text) >= MIN_TOKEN_LENGTH and not qp_matched:
        # Try Full Hex Block
        if len(collapsed_text) % 2 == 0 and all(c in "0123456789abcdefABCDEF" for c in collapsed_text):
            try:
                decoded_bytes = binascii.unhexlify(collapsed_text)
                success, text, enc = is_printable_text(decoded_bytes)
                if success:
                    results.append(f"Hexadecimal Block Decoded ({enc.upper()}): {repr(text)}")
                    block_matched = True
            except (binascii.Error, ValueError):
                pass
                
        # Try Full Base64 Block
        if not block_matched:
            try:
                decoded_bytes = base64.b64decode(collapsed_text, validate=True)
                success, text, enc = is_printable_text(decoded_bytes)
                if success:
                    results.append(f"Base64 Block Decoded ({enc.upper()}):\n{repr(text)}")
                    block_matched = True
            except (binascii.Error, ValueError):
                pass

    # ------------------------------------------------------------------
    # 4. Word-by-word fallback (Only if full-block and QP failed)
    # ------------------------------------------------------------------
    if not qp_matched and not block_matched:
        for word in input_text.split():
            if len(word) < MIN_TOKEN_LENGTH:
                continue

            # Strict Hex
            if len(word) % 2 == 0 and all(c in "0123456789abcdefABCDEF" for c in word):
                try:
                    decoded_bytes = binascii.unhexlify(word)
                    success, text, enc = is_printable_text(decoded_bytes)
                    if success:
                        results.append(f"Hexadecimal Decoded ({enc.upper()}): {repr(text)}")
                        continue  
                except (binascii.Error, ValueError) as exc:
                    logger.debug("Hex decode failed for %r: %s", word, exc)

            # Strict Base64
            try:
                decoded_bytes = base64.b64decode(word, validate=True)
                success, text, enc = is_printable_text(decoded_bytes)
                if success:
                    results.append(f"Base64 Decoded ({enc.upper()}): {repr(text)}")
            except (binascii.Error, ValueError) as exc:
                logger.debug("Base64 decode failed for %r: %s", word, exc)

    return list(dict.fromkeys(results))


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _collect_input() -> str:
    print(
        "Paste your encoded string "
        "(type DONE on a new line and press Enter to finish):"
    )
    lines: list[str] = []
    while True:
        try:
            line = input("> ")
            if line.strip().upper() == "DONE":
                break
            lines.append(line.rstrip()) 
        except EOFError:
            break
    return "\n".join(lines)


def _is_jupyter() -> bool:
    try:
        from IPython import get_ipython  # type: ignore
        return get_ipython() is not None
    except ImportError:
        return False


def main() -> None:
    if _is_jupyter():
        class _Args:
            json = False
            debug = False
        args = _Args()
    else:
        parser = argparse.ArgumentParser(
            description="Decode Base64, Hex, MIME Headers, or Quoted-Printable strings."
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Emit results as a JSON object (useful for pipeline/SIEM integration).",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable verbose debug logging.",
        )
        args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    full_input = _collect_input()

    if not full_input.strip():
        print("Error: Input is empty.")
        return

    if len(full_input) > MAX_INPUT_LENGTH:
        print(f"Error: Input exceeds the {MAX_INPUT_LENGTH}-character limit.")
        return

    if not VALID_CHARACTERS.match(full_input):
        print("Error: Input contains unexpected characters.")
        return

    decoded_results = decode_mixed_text(full_input)

    if args.json:
        print(json.dumps({"results": decoded_results}, indent=2))
        return

    if decoded_results:
        print("\n--- Decoded Results ---")
        for result in decoded_results:
            print(result)
    else:
        print("\nNo valid encoded strings could be decoded.")


if __name__ == "__main__":
    main()