# Examples Directory

This directory contains examples and guides for using the NiFi IDOL workarounds.

## Contents

### Configuration Guides

- **[nifi_configuration.md](nifi_configuration.md)**: Complete NiFi ExecuteScript processor setup guide
  - Processor properties configuration
  - Scheduling recommendations
  - Upstream/downstream flow examples
  - Performance tuning tips
  - Troubleshooting guide

### Integration Examples

- **[sarvam_ai_integration.md](sarvam_ai_integration.md)**: Sarvam AI STT API integration
  - Complete ExecuteScript processor for Sarvam AI STT
  - JSON output format
  - Merging transcript chunks
  - IDOL indexing examples
  - Click-to-playback implementation
  - Multi-language support for Indian languages
  - Cost estimation

### Testing

- **[test_chunker.py](test_chunker.py)**: Standalone test script
  - Test processor outside NiFi environment
  - Verify FFmpeg installation
  - Debug chunking logic
  - Mock NiFi session for local testing

## Quick Start

### 1. Configure NiFi Processor

See [nifi_configuration.md](nifi_configuration.md) for step-by-step setup:

```
ExecuteScript Processor:
  - Script Engine: python
  - Script File: /path/to/processors/mpg_to_mp3_chunks.py
```

### 2. Test Locally (Optional)

Before deploying to NiFi, test the processor logic:

```bash
python examples/test_chunker.py /path/to/test.mpg
```

### 3. Integrate with STT Service

Choose your speech-to-text provider:

- **Sarvam AI**: Complete STT integration with multi-language support

## Common Patterns

### Pattern 1: Simple MPG → Transcript

```
GetFile (*.mpg)
  ↓
UpdateAttribute (set idol.reference)
  ↓
ExecuteScript (mpg_to_mp3_chunks.py)
  ↓
InvokeHTTP (Sarvam AI STT API)
  ↓
EvaluateJsonPath (extract text)
  ↓
MergeContent (by original.link)
  ↓
PutSarvamAI
```

### Pattern 2: Multi-Language Processing

```
GetFile (*.mpg)
  ↓
UpdateAttribute (set idol.reference, language_code)
  ↓
ExecuteScript (mpg_to_mp3_chunks.py)
  ↓
RouteOnAttribute (by language_code)
  ↓
  └─────→ InvokeHTTP (Sarvam AI STT)
  ↓
MergeContent
  ↓
PutIDOL
```

### Pattern 3: Parallel Chunk Processing

```
GetFile (*.mpg)
  ↓
UpdateAttribute (set idol.reference)
  ↓
ExecuteScript (mpg_to_mp3_chunks.py)
  ↓
[Chunks distributed across NiFi cluster]
  ↓
InvokeHTTP (STT service) [8 concurrent]
  ↓
MergeContent (wait for all chunks)
  ↓
ExecuteScript (reassemble_transcript.py)
  ↓
PutIDOL
```

## Testing Your Flow

### Minimal Test Flow

1. **GenerateFlowFile** - Create test flowfile:
   ```json
   {
     "idol.reference": "/tmp/test.mpg",
     "filename": "test.mpg"
   }
   ```

2. **ExecuteScript** - Run chunker

3. **LogAttribute** - Verify output attributes:
   - `filename`
   - `audio.chunk.start`
   - `audio.chunk.duration`
   - `original.link`

### Validation Checklist

- [ ] FFmpeg installed and in PATH
- [ ] Test MPG file has audio track
- [ ] NiFi can read source file (permissions)
- [ ] Temp directory has sufficient space
- [ ] Output chunks are valid MP3 files
- [ ] Timing metadata is accurate
- [ ] Success relationship connected

## Performance Tips

### High Throughput

```
Concurrent Tasks: 8
Back Pressure: 10000 objects
Run Schedule: 0 sec
```

### Memory Constrained

```
Concurrent Tasks: 2-4
Back Pressure: 1000 objects
Max Heap: 4GB
```

### Network Storage

- Stage files locally first with `FetchFile`
- Use fast temp directory (SSD, not NFS)
- Monitor I/O with `iostat -x 1`

## Contributing

Have a useful example or integration? Please contribute:

1. Fork the repository
2. Add your example to this directory
3. Update this README
4. Submit a pull request

Examples we'd love to see:
- Additional STT service integrations
- Video player implementations
- IDOL/Sarvam AI indexing pipelines
- Error handling patterns
- Monitoring/alerting setups

## Support

For help with examples:

1. Check the main [documentation](../docs/README.md)
2. Review NiFi logs: `tail -f /opt/nifi/logs/nifi-app.log`
3. Test components individually
4. Open a GitHub issue with:
   - Your NiFi flow (XML export)
   - Processor configurations
   - Sample input file characteristics
   - Error messages/logs

## License

All examples are provided under the same license as the main repository.
