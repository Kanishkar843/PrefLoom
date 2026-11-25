# Environment report

Updated 2026-11-22, Asia/Kolkata. Windows 11 Home 10.0.26300, Intel Core 7 150U, 15.72GiB usable RAM. Available RAM varied from below 1GiB to about 3GiB during builds; model execution and application stacks are serialized. K: had 159GiB free. C: reached 60MB free; two identical task-created WSL MSI downloads were removed after SHA-256 verification against the retained K: installer, recovering roughly 700MB. Unrelated temporary files were untouched.

Git 2.51.0, Node 22.15.0/npm 10.9.2, default Python 3.13.2; application virtual environments use Python 3.12.12. WSL 3.0.5/kernel 6.18.58 and Docker Desktop 4.99.0/Engine 29.9.3/Compose 5.7.0 were installed with prior authorization. No automatic reboot and no Windows security-policy bypass. Tool installations and large caches are under K:/Projects/.build-tools. GitHub CLI 2.105.0 is portable; Git Credential Manager lists the requested GitHub account. Do not print tokens.

Portable PostgreSQL 17.12 listens only on 127.0.0.1:55439 with a generated local password. DeltaIndex additionally uses locally compiled pgvector 0.8.7 and community redis-windows Redis 8.10.3 on 127.0.0.1:56379 with a generated password; this Windows build is not an official Redis distribution. Docker uses the project-specific Linux images and limits. Only one project's Compose stack runs at a time.

Local network TLS requires the Windows trust store. Docker build uses an optional external BuildKit public-root secret; certificate verification remains enabled. Slow Linux package downloads and native managed-Python OpenSSL file-I/O crashes were observed and recorded in test reports. Live LLM credentials are not configured. No mocked provider test is counted as live inference.
