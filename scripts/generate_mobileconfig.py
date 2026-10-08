import sys
import uuid
import plistlib
from pathlib import Path

def parse_line_to_domain(line):
    line = line.split('#')[0].split('//')[0].strip()
    if not line:
        return None
    
    if ',' in line:
        parts = line.split(',')
        line = parts[1].strip() if len(parts) > 1 else parts[0].strip()

    if line.startswith('+.'):
        return '.' + line[2:]
    elif line.startswith('.'):
        return line
    else:
        return line

def generate_mobileconfig(input_path_str, output_file):
    domains_set = set()
    target_path = Path(input_path_str)

    if target_path.is_dir():
        list_files = list(target_path.rglob('*.list'))
    elif target_path.is_file():
        list_files = [target_path]
    else:
        print(f"Error: Path {input_path_str} does not exist.")
        sys.exit(1)

    print(f"Found {len(list_files)} rule file(s) to process.")

    for file_path in list_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                domain = parse_line_to_domain(line)
                if domain:
                    domains_set.add(domain)

    domains_list = sorted(list(domains_set))

    payload_uuid = str(uuid.uuid4()).upper()
    profile_uuid = str(uuid.uuid4()).upper()

    mobileconfig = {
        'PayloadContent': [
            {
                'PayloadType': 'com.apple.dnsSettings.managed',
                'PayloadVersion': 1,
                'PayloadIdentifier': 'com.rules.reject.dns',
                'PayloadUUID': payload_uuid,
                'PayloadDisplayName': 'Reject Domain Rules',
                'PayloadDescription': 'Block unwanted domains via local DNS profile.',
                'DNSSettings': {
                    'DNSProtocol': 'HTTPS',
                    'ServerURL': 'https://dns.adguard.com/dns-query',
                    'SupplementalMatchDomains': domains_list
                }
            }
        ],
        'PayloadDisplayName': 'Auto-Generated Reject Rules',
        'PayloadIdentifier': 'com.rules.reject.profile',
        'PayloadOrganization': 'Auto Rule Generator',
        'PayloadRemovalDisallowed': False,
        'PayloadType': 'Configuration',
        'PayloadUUID': profile_uuid,
        'PayloadVersion': 1
    }

    with open(output_file, 'wb') as f:
        plistlib.dump(mobileconfig, f, fmt=plistlib.FMT_XML)

    print(f"Successfully processed {len(domains_list)} total unique domains into {output_file}.")

if __name__ == '__main__':
    in_path = sys.argv[1] if len(sys.argv) > 1 else 'rules/REJECT/domain'
    out_path = sys.argv[2] if len(sys.argv) > 2 else 'reject.mobileconfig'
    generate_mobileconfig(in_path, out_path)