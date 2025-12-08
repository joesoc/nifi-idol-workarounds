# Quick Reference

Quick links and tips for working with this documentation repository.

## Quick Links

- [Getting Started](docs/getting-started.md) - Introduction for new users
- [Documentation Template](docs/TEMPLATE.md) - Template for new workarounds
- [Contributing Guide](CONTRIBUTING.md) - Detailed contribution guidelines
- [Documentation Index](docs/README.md) - Overview of all documentation
- [Examples Index](examples/README.md) - Code examples directory

## Adding a New Workaround

**Quick Steps:**
1. Copy `docs/TEMPLATE.md` to `docs/your-workaround-name.md`
2. Fill in all sections with your workaround details
3. Add code examples to `examples/your-workaround-name/`
4. Add images to `images/` (organized by category)
5. Update `docs/README.md` to link your new documentation

## Directory Structure

```
nifi-idol-workarounds/
├── docs/              # Markdown documentation
│   ├── README.md      # Documentation index
│   ├── TEMPLATE.md    # Template for new docs
│   └── *.md           # Workaround documentation
├── examples/          # Code samples and configurations
│   ├── README.md      # Examples index
│   └── */             # Workaround-specific examples
├── images/            # Images and diagrams
│   ├── README.md      # Images index
│   └── */             # Organized by category
├── .gitignore         # Excluded files
├── CONTRIBUTING.md    # Contribution guidelines
├── LICENSE            # Apache 2.0 License
├── README.md          # Main repository overview
└── QUICKREF.md        # This file
```

## Common Tasks

### Viewing Documentation
- Start with `README.md` for overview
- Read `docs/getting-started.md` for introduction
- Browse `docs/` for specific workarounds

### Adding Code Examples
- Create a subdirectory in `examples/`
- Add a README.md explaining the example
- Include well-commented code
- Reference from documentation

### Adding Images
- Place in `images/` organized by category
- Use descriptive filenames
- Reference with relative paths: `![Alt](../images/category/image.png)`

### Documentation Style
- Use ATX headers (`#`, `##`, `###`)
- Code blocks with language: ` ```java ` or ` ```xml `
- Bullet lists for items
- Link to related docs

## What Goes Where

| Content Type | Location | Example |
|--------------|----------|---------|
| Workaround docs | `docs/` | `docs/legacy-media-workaround.md` |
| Code examples | `examples/` | `examples/legacy-media/Processor.java` |
| NiFi templates | `examples/` | `examples/legacy-media/flow.xml` |
| Screenshots | `images/workflows/` | `images/workflows/nifi-flow.png` |
| Diagrams | `images/diagrams/` | `images/diagrams/architecture.svg` |
| Architecture | `images/architecture/` | `images/architecture/system.png` |

## Tips

- **Keep It Simple**: Focus on clarity over complexity
- **Show Examples**: Include code snippets and screenshots
- **Test First**: Verify workarounds before documenting
- **Link Everything**: Cross-reference related documentation
- **Stay Organized**: Use the established directory structure

## Getting Help

- Review existing documentation for examples
- Check the template for guidance
- Look at other workaround docs for patterns
- Read the CONTRIBUTING.md for detailed guidelines
