# Security Policy

## Reporting a vulnerability

Please do not open a public issue for a suspected vulnerability. Use GitHub's
private vulnerability reporting feature for this repository, or contact the
maintainer privately through their GitHub profile.

Include a concise description, reproduction steps, affected versions, and the
potential impact. Do not include live credentials or sensitive datasets.

## Deployment guidance

- Use dedicated read-only database accounts.
- Restrict database hosts and network access.
- Rotate all development credentials before deployment.
- Configure authentication in front of public deployments.
- Review model-provider data handling before connecting organizational data.
- Monitor metadata-only audit events and dependency updates.
