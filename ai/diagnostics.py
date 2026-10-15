import re

from ai.evidence import redact

# Each rule matches a known error pattern in the evidence text.
RULES = [
    {
        "id": "disk_full",
        "component": "Linux filesystem",
        "pattern": re.compile(r"no space left on device", re.I),
        "confirmed": "The system reported that a filesystem has no free space.",
        "possible_causes": [
            "Log files growing without rotation",
            "Unused Docker images or containers",
            "Temporary or backup files left behind",
        ],
        "investigate": [
            "df -h",
            "sudo du -xh / --max-depth=1 2>/dev/null | sort -h | tail -10",
            "docker system df",
        ],
        "fix": [
            "Find the largest directories using the du command above.",
            "Review what is inside before deleting anything.",
            "Remove only files or Docker data you are sure are not needed, for example: docker image prune.",
        ],
        "verify": [
            "Run df -h and confirm the filesystem has free space.",
            "Repeat the action that failed.",
        ],
    },
    {
        "id": "port_in_use",
        "component": "Network port",
        "pattern": re.compile(r"address already in use|port is already allocated", re.I),
        "confirmed": "A program tried to use a port that is already taken.",
        "possible_causes": [
            "An earlier copy of the app or container is still running",
            "Another service uses the same port",
        ],
        "investigate": ["sudo ss -tlnp", "docker ps"],
        "fix": [
            "Find the process or container that owns the port.",
            "Stop it if it is not needed, or change the port of the new one.",
        ],
        "verify": [
            "Start the app again and confirm it stays running.",
            "Call the app's health URL with curl.",
        ],
    },
    {
        "id": "connection_refused",
        "component": "Network connection",
        "pattern": re.compile(r"connection refused", re.I),
        "confirmed": "The target refused the connection.",
        "possible_causes": [
            "The service is not running",
            "The service listens on a different port or address",
            "A firewall rejected the connection",
        ],
        "investigate": [
            "sudo ss -tlnp",
            "systemctl status <service>",
            "curl -v http://<host>:<port>",
        ],
        "fix": [
            "Start the service if it is stopped.",
            "Check the port and address in the app configuration.",
            "For a remote host, check security group and firewall rules.",
        ],
        "verify": ["Retry the connection and confirm it succeeds."],
    },
    {
        "id": "aws_access_denied",
        "component": "AWS permissions",
        "pattern": re.compile(
            r"AccessDenied|UnauthorizedOperation|not authorized to perform", re.I
        ),
        "confirmed": "AWS rejected a request because of missing permission.",
        "possible_causes": [
            "The IAM user or role is missing the needed action",
            "A resource policy or permissions boundary blocks it",
            "Wrong account, region or resource name",
        ],
        "investigate": [
            "aws sts get-caller-identity",
            "Check the IAM policies attached to that identity",
            "Read the full error for the action and resource name",
        ],
        "fix": [
            "Identify the exact action and resource named in the error.",
            "Add only that permission to the policy (least privilege).",
            "Do not grant broad admin access as a shortcut.",
        ],
        "verify": ["Repeat the failed AWS call and confirm it succeeds."],
    },
    {
        "id": "out_of_memory",
        "component": "Memory",
        "pattern": re.compile(
            r"out of memory|oom-kill|exited with code 137|exit code 137", re.I
        ),
        "confirmed": "The evidence shows an out-of-memory event or exit code 137.",
        "possible_causes": [
            "Exit code 137 means the process was killed; running out of memory is a common reason but must be checked",
            "The app or container used more memory than was available",
            "A memory limit is set too low, or the app has a memory leak",
        ],
        "investigate": [
            "free -h",
            "dmesg | grep -i -E 'oom|killed process'",
            "docker stats --no-stream",
        ],
        "fix": [
            "Find the process using the most memory.",
            "If usage is normal, raise the memory limit or use a larger instance type.",
            "If memory keeps growing, fix the application.",
        ],
        "verify": [
            "Watch free -h while the app runs.",
            "Confirm the process stays up.",
        ],
    },
    {
        "id": "permission_denied",
        "component": "File or user permissions",
        "pattern": re.compile(r"permission denied", re.I),
        "confirmed": "An operation was blocked by permissions.",
        "possible_causes": [
            "Wrong file owner or mode",
            "Running as a user without the needed rights",
            "SSH key file permissions are too open",
        ],
        "investigate": ["ls -l <path>", "id", "ls -ld <parent-directory>"],
        "fix": [
            "Check who owns the file and what its mode is.",
            "Fix it with chown or chmod on that file only.",
            "Avoid chmod 777.",
        ],
        "verify": ["Repeat the failed action and confirm it works."],
    },
]


def diagnose(evidence):
    """Match evidence against known rules. Report only what the text confirms."""
    clean = redact(evidence)
    findings = []
    for rule in RULES:
        match = rule["pattern"].search(clean)
        if match:
            findings.append(
                {
                    "rule": rule["id"],
                    "component": rule["component"],
                    "observed_error": match.group(0),
                    "confirmed_finding": rule["confirmed"],
                    "possible_causes": rule["possible_causes"],
                    "investigation_commands": rule["investigate"],
                    "corrective_steps": rule["fix"],
                    "verification_steps": rule["verify"],
                }
            )
    return {
        "evidence": clean,
        "matched": bool(findings),
        "findings": findings,
        "llm_explanation": None,
        "safety_note": "Review every step before running it. CloudPulse AI does not run commands for you.",
    }
