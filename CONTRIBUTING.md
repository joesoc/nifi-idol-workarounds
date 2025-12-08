# Contributing to NiFi IDOL Workarounds

Thank you for contributing to this documentation repository! This guide will help you add your workarounds, code examples, and documentation.

## Repository Purpose

This repository documents production-tested workarounds for Apache NiFi when working with IDOL Media Server and KeyView. The focus is on files and formats that are rejected by standard IDOL processing.

## How to Contribute

### Adding a New Workaround

1. **Create Documentation**
   - Copy `docs/TEMPLATE.md` to a new file with a descriptive name (e.g., `docs/legacy-avi-indexing.md`)
   - Fill in all sections of the template
   - Use clear, concise language
   - Include specific examples and error messages

2. **Add Code Examples**
   - Create a directory in `examples/` for your code (e.g., `examples/legacy-avi/`)
   - Include source code with comments
   - Add a README.md in the example directory
   - Reference the example from your documentation

3. **Add Images/Diagrams**
   - Place images in the `images/` directory
   - Use descriptive filenames
   - Organize by category (workflows, architecture, etc.)
   - Reference images in your documentation

4. **Update Main Documentation**
   - Add a link to your workaround in `docs/README.md`
   - Update `README.md` if your contribution changes the repository structure

### Documentation Standards

#### Markdown Style
- Use ATX-style headers (`#`, `##`, `###`)
- Include code blocks with language specification
- Use bullet points for lists
- Add links to related documentation

#### Code Examples
- Include comments explaining key sections
- Follow the language's style guide (Java, Python, etc.)
- Keep examples focused and minimal
- Remove sensitive information (credentials, hostnames)

#### File Organization
```
docs/
├── README.md           # Documentation index
├── getting-started.md  # Getting started guide
├── TEMPLATE.md         # Template for new workarounds
└── [workaround].md     # Individual workaround docs

examples/
├── README.md           # Examples index
└── [workaround]/       # Workaround-specific examples
    ├── README.md       # Example documentation
    └── [code files]    # Implementation code

images/
├── README.md           # Images index
└── [category]/         # Organized by category
    └── [images]        # Image files
```

### Writing Good Documentation

#### Problem Description
- Describe specific symptoms
- Include error messages
- List affected file types
- Explain root causes

#### Solution Overview
- Explain the approach clearly
- Use diagrams where helpful
- Break complex solutions into steps

#### Implementation Details
- Provide step-by-step instructions
- Include configuration examples
- Reference code examples
- Add troubleshooting tips

#### Testing
- Describe how to test the workaround
- Provide test data or generation methods
- List expected results

### Code Contribution Guidelines

#### NiFi Processors
- Export processor configurations as XML templates
- Document all custom properties
- Include controller service configurations
- Test with sample data

#### Custom Code
- Add inline comments for complex logic
- Include error handling
- Follow existing code style
- Keep dependencies minimal

#### Scripts
- Add usage instructions at the top
- Include example invocations
- Handle errors gracefully
- Document prerequisites

### Review Process

1. **Self-Review**
   - Check for typos and grammar
   - Verify all links work
   - Test code examples
   - Ensure images display correctly

2. **Documentation Checklist**
   - [ ] Problem clearly described
   - [ ] Solution approach explained
   - [ ] Implementation steps complete
   - [ ] Code examples included
   - [ ] Testing instructions provided
   - [ ] Known limitations documented

3. **Code Checklist**
   - [ ] Code compiles/runs without errors
   - [ ] Comments explain key sections
   - [ ] Dependencies documented
   - [ ] No sensitive information included

## Questions?

- Review existing workarounds for examples
- Check the template at `docs/TEMPLATE.md`
- Examine code in the `examples/` directory

## License

All contributions will be licensed under the Apache License 2.0, the same as this project.
