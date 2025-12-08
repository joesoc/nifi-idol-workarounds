# NiFi IDOL Workarounds

Production NiFi workarounds to index everything IDOL Media Server and KeyView reject — legacy media, exotic text, and beyond.

## Overview

This repository contains production-tested workarounds for Apache NiFi when working with IDOL Media Server and KeyView. These solutions address challenges in indexing files that are rejected by standard IDOL processing, including:

- **Legacy Media Formats** - Old video codecs, proprietary formats, and deprecated media types
- **Exotic Text Encodings** - Unusual character encodings and legacy text formats
- **Malformed Files** - Handling corrupted or non-standard file structures
- **Edge Cases** - Special situations not covered by default IDOL processing

## Repository Structure

```
nifi-idol-workarounds/
├── docs/           # Documentation and guides
├── examples/       # Code examples and NiFi configurations
├── images/         # Diagrams, screenshots, and illustrations
├── LICENSE         # Apache License 2.0
└── README.md       # This file
```

## Getting Started

1. **Explore the Documentation**: Start with [Getting Started](docs/getting-started.md) to understand the basics
2. **Review Examples**: Browse the [examples](examples/) directory for code samples and configurations
3. **Find Solutions**: Check the [docs](docs/) directory for specific workaround documentation

## Documentation

The documentation is organized to help you quickly find solutions:

- **[Getting Started](docs/getting-started.md)** - Introduction and quick start guide
- **[Documentation Overview](docs/README.md)** - Guide to the documentation structure
- **Workarounds** - Specific solution documentation (to be added)

## Examples

Code examples, NiFi flow templates, and processor configurations are available in the [examples](examples/) directory. Each example includes:

- Implementation code
- Configuration files
- Usage instructions
- Test cases (where applicable)

## Contributing

This is a documentation repository for sharing production workarounds and solutions. When contributing:

1. **Documentation**: Add markdown files to the `docs/` directory
2. **Code**: Add examples to the `examples/` directory with clear comments
3. **Images**: Place diagrams and screenshots in the `images/` directory
4. **Reference**: Link code examples from documentation

Follow the structure and style of existing documentation for consistency.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## About IDOL and NiFi

- **Apache NiFi** - Data flow automation and management platform
- **IDOL Media Server** - HP/Micro Focus content analysis and media indexing
- **KeyView** - Text extraction and format detection technology

These workarounds help bridge gaps when standard IDOL processing cannot handle specific file types or formats.
