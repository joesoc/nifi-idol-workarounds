# Getting Started

This guide helps you understand and implement the NiFi IDOL workarounds for indexing legacy media and exotic text formats.

## Overview

IDOL Media Server and KeyView are powerful indexing tools, but they may reject certain file types:
- Legacy media formats (old video codecs, proprietary formats)
- Exotic text encodings
- Corrupted or malformed files
- Files with unusual metadata

These workarounds provide production-tested solutions for handling such files in Apache NiFi.

## Prerequisites

- Apache NiFi (version information will be added based on specific implementations)
- Basic understanding of NiFi processors and flow design
- Access to IDOL Media Server and KeyView (if available)

## Quick Start

1. Review the specific workaround documentation in the `/docs` directory
2. Examine the corresponding code examples in the `/examples` directory
3. Import or adapt the NiFi processor configurations for your environment
4. Test with sample problematic files before deploying to production

## Repository Structure

```
nifi-idol-workarounds/
├── docs/           # Documentation files
├── examples/       # Code examples and NiFi configurations
├── images/         # Diagrams and screenshots
└── README.md       # Repository overview
```

## Finding Workarounds

Browse the `/docs` directory for specific workarounds. Each workaround includes:
- Problem description
- Solution approach
- Implementation details
- Code examples
- Testing guidance

## Need Help?

- Check the documentation in `/docs` for detailed explanations
- Review code examples in `/examples` for implementation references
- Examine test cases to understand expected behavior
