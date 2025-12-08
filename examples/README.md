# Examples

This directory contains code examples, NiFi processor configurations, and implementation samples for the workarounds.

## Contents

Code examples are organized by workaround type or problem being solved. Each example should include:

- Source code (Java, Groovy, Python, or other languages as needed)
- NiFi flow templates (XML)
- Configuration files
- Sample input/output data (where appropriate)

## Structure

Examples should be organized in subdirectories by topic:

```
examples/
├── legacy-media/           # Legacy media format handling
├── text-encoding/          # Exotic text encoding solutions
├── error-handling/         # Error handling patterns
└── custom-processors/      # Custom NiFi processor implementations
```

## Using Examples

1. Navigate to the relevant example directory
2. Read the accompanying documentation in `/docs`
3. Review the code and configuration files
4. Adapt the example to your specific use case
5. Test thoroughly before deploying to production

## Contributing Examples

When adding new examples:

- Create a subdirectory for related examples
- Include a README.md explaining the example
- Add comments in code for clarity
- Reference the example from relevant documentation
- Include any necessary dependencies or requirements
