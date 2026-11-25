"""Check TCP connectivity to an explicit inventory of authorized endpoints."""
import argparse
import json
import socket
import sys
import time
from pathlib import Path


def load_inventory(path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(data, list) or not data:
        raise ValueError('Inventory must be a nonempty JSON array')
    for entry in data:
        if not isinstance(entry, dict):
            raise ValueError('Each entry must be an object')
        host, ports = entry.get('host'), entry.get('ports')
        if not isinstance(host, str) or not host or host != host.strip():
            raise ValueError('Each entry needs a nonempty host')
        if not isinstance(ports, list) or not ports or any(type(p) is not int or not 1 <= p <= 65535 for p in ports):
            raise ValueError(f'Invalid ports for {host}')
        if len(set(ports)) != len(ports):
            raise ValueError(f'Duplicate ports for {host}')
    return data


def probe(host, port, timeout=3.0):
    start = time.monotonic()
    result = {'host': host, 'port': port, 'status': 'ok'}
    try:
        with socket.create_connection((host, port), timeout=timeout) as conn:
            result['peer'] = conn.getpeername()[0]
    except socket.gaierror as exc:
        result.update(status='dns_error', error=str(exc))
    except TimeoutError as exc:
        result.update(status='timeout', error=str(exc))
    except ConnectionRefusedError as exc:
        result.update(status='refused', error=str(exc))
    except OSError as exc:
        result.update(status='connection_error', error=str(exc))
    result['elapsed_ms'] = round((time.monotonic() - start) * 1000, 2)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('inventory', help='JSON file containing hosts and TCP ports')
    parser.add_argument('--timeout', type=float, default=3.0, help='Socket timeout per address in seconds')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    args = parser.parse_args(argv)
    if not 0 < args.timeout <= 60:
        parser.error('timeout must be greater than 0 and at most 60')
    try:
        inventory = load_inventory(args.inventory)
    except (OSError, ValueError) as exc:
        print(f'Inventory error: {exc}', file=sys.stderr)
        return 2
    results = [probe(entry['host'], p, args.timeout) for entry in inventory for p in entry['ports']]
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(f"{r['host']}:{r['port']} {r['status']} ({r['elapsed_ms']} ms)")
    return int(any(r['status'] != 'ok' for r in results))


if __name__ == '__main__':
    sys.exit(main())
