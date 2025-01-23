#!/usr/bin/env python3
import re
import argparse
import sys

__version__ = "1.0.0"  # Version of the script

# Banner
banner = """
██████╗  █████╗ ████████╗████████╗███████╗██████╗ ███╗   ██╗    ███╗   ███╗ █████╗ ████████╗ ██████╗██╗  ██╗███████╗██████╗ 
██╔══██╗██╔══██╗╚══██╔══╝╚══██╔══╝██╔════╝██╔══██╗████╗  ██║    ████╗ ████║██╔══██╗╚══██╔══╝██╔════╝██║  ██║██╔════╝██╔══██╗
██████╔╝███████║   ██║      ██║   █████╗  ██████╔╝██╔██╗ ██║    ██╔████╔██║███████║   ██║   ██║     ███████║█████╗  ██████╔╝
██╔═══╝ ██╔══██║   ██║      ██║   ██╔══╝  ██╔══██╗██║╚██╗██║    ██║╚██╔╝██║██╔══██║   ██║   ██║     ██╔══██║██╔══╝  ██╔══██╗
██║     ██║  ██║   ██║      ██║   ███████╗██║  ██║██║ ╚████║    ██║ ╚═╝ ██║██║  ██║   ██║   ╚██████╗██║  ██║███████╗██║  ██║
╚═╝     ╚═╝  ╚═╝   ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝    ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
It's an alternative of tomnomnom GF tool
"""

print(banner)

def load_patterns(pattern_file):
    try:
        with open(pattern_file, 'r') as file:
            patterns = file.read().splitlines()
        return patterns
    except FileNotFoundError:
        print(f"Error: File {pattern_file} not found.")
        return []

def process_urls(urls, patterns, output_file=None, append_text="FUZZ", ignore_case=False, clear_values=False):
    results = []
    # Characters to ignore before and after match in case-insensitive mode
    ignore_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-'

    for url in urls:
        url = url.strip()
        matches = []
        for pattern in patterns:
            # Modify regex pattern based on case sensitivity
            if ignore_case:
                regex = re.compile(
                    fr"(?<![{ignore_chars}])({re.escape(pattern)}[^&]*)(?!=[{ignore_chars}])", 
                    flags=re.IGNORECASE
                )
            else:
                regex = re.compile(fr"(?<![{ignore_chars}])({re.escape(pattern)}[^&]*)(?!=[{ignore_chars}])")
            
            matches.extend(regex.finditer(url))
        
        if matches:
            # Sort matches by their start index to ensure we process in the correct order
            matches.sort(key=lambda x: x.start(), reverse=True)  # Reverse to handle overlapping matches
            result = url
            for match in matches:
                matched_part = match.group(0)
                if clear_values:
                    # Remove value but keep parameter, append text specified by -r
                    param = matched_part.split('=')[0] + '='
                    result = result[:match.start()] + param + append_text + result[match.end():]
                else:
                    # Append text after match
                    insert_pos = match.end()
                    result = result[:insert_pos] + append_text + result[insert_pos:]
            
            print(result)  # Print the modified URL
            results.append(result)  # Add to the results list

    # Write results to the output file if specified
    if output_file:
        try:
            with open(output_file, 'w') as file:
                file.write("\n".join(results))
            print(f"Results saved to {output_file}")
        except IOError:
            print(f"Error: Could not write to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Match patterns from a file in URLs, append text at each match, or clear parameter values and append text, and print/save modified results.",
        epilog="Examples:\n"
               '  pm -u "http://example.com" -p /opt/Pattern-Matching/patterns/xss.txt -r "XSS" -o append_text_after_value.txt\n'
               '  pm -f urls.txt -p /opt/Pattern-Matching/patterns/sqli.txt -r "SQLI" -o append_text_after_value_case_insensitive.txt\n'
               '  pm -f urls.txt -p /opt/Pattern-Matching/patterns/lfi.txt -c -r "LFI" -o case_insensitive_with_value_replace.txt\n'
               '  pm -f urls.txt -p /opt/Pattern-Matching/patterns/or.txt -c -i -r "OpenR" -o ignore_case_insensitive_with_value_replace.txt\n',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-f", "--file", help="File containing URLs (optional, stdin is used if not provided)")
    parser.add_argument("-u", "--url", help="Single URL to process (optional, overrides -f)")
    parser.add_argument("-p", "--pattern", required=True, help="Pattern file to use (e.g., xss.txt)")
    parser.add_argument("-o", "--output", help="File to save output results (optional)")
    parser.add_argument("-r", "--replace", help="Text to append after each matched pattern (default: FUZZ)", default="FUZZ")
    parser.add_argument("-i", "--ignore-case", action="store_true", help="Perform case-insensitive matching with additional logic (default is case-sensitive)")
    parser.add_argument("-c", "--clear-values", action="store_true", help="Remove values of matched parameters but keep parameters and append the -r value")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")

    args = parser.parse_args()

    # Load patterns from the file provided in -p
    patterns = load_patterns(args.pattern)
    if not patterns:
        print(f"Error: No patterns loaded from the file {args.pattern}.")
        exit(1)

    # Load URLs from file, single URL, or stdin
    if args.url:
        urls = [args.url]  # Process the single URL provided with -u
    elif args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as file:
                urls = file.readlines()
        except UnicodeDecodeError:
            with open(args.file, 'r', encoding='iso-8859-1') as file:
                urls = file.readlines()
        except FileNotFoundError:
            print(f"Error: File {args.file} not found.")
            exit(1)
    else:
        if sys.stdin.isatty():
            print("Error: No input URLs provided via stdin, -f, or -u.")
            exit(1)
        try:
            # Read stdin as bytes first
            raw_input = sys.stdin.buffer.read()
            try:
                urls = raw_input.decode('utf-8').splitlines()
            except UnicodeDecodeError:
                # Fallback to iso-8859-1 if UTF-8 fails
                urls = raw_input.decode('iso-8859-1').splitlines()
        except Exception as e:
            print(f"Error reading stdin: {e}")
            exit(1)

    process_urls(urls, patterns, args.output, args.replace, args.ignore_case, args.clear_values)