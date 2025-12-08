# Images and Diagrams

This directory contains images, diagrams, and screenshots used in the documentation.

## Organization

Images should be organized by category or documentation file:

```
images/
├── architecture/       # System architecture diagrams
├── workflows/         # NiFi workflow screenshots
├── examples/          # Example outputs and results
└── diagrams/          # General diagrams and illustrations
```

## File Naming

Use descriptive filenames that indicate what the image shows:
- `nifi-flow-legacy-media.png` - NiFi flow for legacy media processing
- `architecture-overview.svg` - System architecture overview
- `error-handling-flowchart.png` - Error handling flowchart

## Image Formats

- **PNG** - Screenshots and diagrams with solid colors
- **JPEG** - Photos and complex images
- **SVG** - Vector diagrams that may need scaling

## Referencing Images

In markdown documentation, reference images using relative paths:

```markdown
![Architecture Overview](../images/architecture/overview.png)
```

## Contributing Images

- Use clear, high-resolution images
- Crop images to show only relevant content
- Add alt text descriptions for accessibility
- Optimize file sizes for web viewing
