# Security

PTK is a local CLI/desktop utility. Do not expose it as an unauthenticated network service. It executes external media parsers and a pretrained ML backend; process only media you are entitled to use and keep the tested dependencies updated deliberately.

Report a suspected vulnerability using GitHub's private vulnerability-reporting feature if available. Do not put credentials, private media, signed URLs or full environment dumps in public issues. If private reporting is unavailable, contact the repository owner privately before disclosing sensitive details.

Resource checks and private staging reduce accidental damage; they are not a sandbox, filesystem quota or protection against a malicious local user. Use a fresh output folder after an interrupted job. Review manifest paths before sharing them.

The automated secret scan checks Git history with Gitleaks; a passing scan does not prove that every secret format or external system is safe. Credentials exposed outside the repository must be rotated separately.
