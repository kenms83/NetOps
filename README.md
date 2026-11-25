# NetOps

An early-stage, dependency-free Python toolkit for network administrators. The initial utility checks TCP reachability and distinguishes DNS failures, connection refusal, timeouts and other socket errors for an explicitly configured inventory.

## Quick start

Requires Python 3.10 or later. No elevated privileges or external libraries are needed.

```sh
git clone https://github.com/kenms83/NetOps.git
cd NetOps
cp examples/inventory.json inventory.local.json
# Edit the local inventory to list only endpoints you are authorized to check.
python3 netops.py inventory.local.json
python3 netops.py inventory.local.json --json
```

Each entry contains a hostname or IP address and an array of TCP port numbers. Checks run sequentially. Exit codes: 0 = all checks succeeded; 1 = one or more failed; 2 = invalid input.

TCP reachability does not establish application health, verify TLS or authenticate. DNS resolution and retries across multiple addresses may cause elapsed time to exceed the per-address socket timeout. No device configuration is changed. Only check authorized systems. Keep actual inventories and diagnostic reports private.

## Tests

```sh
python3 -m unittest discover -s tests -v
```

Tests use loopback or simulated errors, not remote systems.

## Roadmap

Potential additions: read-only SNMP inventory, switch diagnostic output parsers, and monitoring integrations. These are not yet implemented.

Contributions and issue reports are welcome. Use sanitized examples and never include credentials or confidential infrastructure data.

## License

MIT. See LICENSE in the repository.
