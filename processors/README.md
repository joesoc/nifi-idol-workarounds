# Processors Directory

This directory contains NiFi ExecuteScript processors for working around IDOL Media Server limitations.

## Available Processors

### mpg_to_mp3_chunks.py

**Purpose**: Extract audio from unsupported video formats and split into 30-second MP3 chunks for speech-to-text processing.

**Use Case**: When IDOL Media Server rejects legacy formats (MPEG-1/2) or doesn't support the required language for STT.

**Key Features**:
- Direct file access via `idol.reference` attribute (bypasses FlowFile streaming issues)
- FFmpeg-based high-quality audio extraction (VBR ~190-250 kbps)
- Precise 30-second chunking with timing metadata
- Frame-accurate timestamp preservation for video synchronization
- Compatible with any downstream STT engine

**Requirements**:
- FFmpeg 4.0+ with libmp3lame encoder
- Python 3.6+ (typically bundled with NiFi)
- No Python package dependencies (uses stdlib only)

**Input Attributes**:
- `idol.reference` (required): Absolute path to source MPG file
- `filename` (optional): Original filename for chunk naming

**Output Attributes** (per chunk):
- `filename`: Generated chunk filename (e.g., `video_chunk_000.mp3`)
- `mime.type`: `audio/mp3`
- `original.link`: Path to original source file
- `audio.chunk.start`: Start time in seconds (e.g., `"0.0"`, `"30.0"`)
- `audio.chunk.duration`: Duration in seconds (always `"30.0"`)

**Relationships**:
- `success`: Successfully created MP3 chunk(s)
- `failure`: Processing failed (only if first segment fails)

**Configuration Example**:

```
ExecuteScript Processor:
  Script Engine: python
  Script File: /path/to/processors/mpg_to_mp3_chunks.py
  
Upstream (UpdateAttribute):
  idol.reference: ${absolute.path}
  filename: ${filename}
```

**Documentation**:
- [Main Documentation](../docs/README.md)
- [Configuration Guide](../examples/nifi_configuration.md)
- [Integration Examples](../examples/whisper_integration.md)

---

## Adding New Processors

When contributing new processors to this directory:

### Structure

```python
"""
Processor Name - NiFi ExecuteScript Processor
==============================================

Brief description of what this processor does.

Requirements:
    - List dependencies
    - System requirements

Attributes:
    Input:
        - attribute_name: Description
    
    Output:
        - attribute_name: Description

Routes:
    - success: Description
    - failure: Description
"""

import os
import sys

# NiFi compatibility layer
try:
    from idolnifi import *
except ImportError:
    # Fallback for testing
    def logInfo(*args, **kwargs):
        print("INFO:", *args, **kwargs, file=sys.stderr)
    # ... other mock functions

def handler(context, session, flowfile):
    """
    Main processor handler function.
    
    Args:
        context: NiFi processor context
        session: NiFi session
        flowfile: Input flowfile
    """
    # Your processor logic here
    pass
```

### Best Practices

1. **No External Dependencies**: Prefer Python stdlib to avoid deployment complexity
2. **Graceful Degradation**: Handle missing attributes/files gracefully
3. **Detailed Logging**: Use logInfo/logWarn/logError for observability
4. **Resource Cleanup**: Always clean up temp files in try/finally blocks
5. **Testing Fallback**: Provide mock functions for standalone testing
6. **Documentation**: Include comprehensive docstrings and attribute descriptions

### Testing

Create a test script in `examples/`:

```python
# examples/test_your_processor.py
import sys
from processors.your_processor import handler

# Mock NiFi objects
class MockSession: ...
class MockFlowFile: ...
class MockContext: ...

# Test logic
def test_processor():
    session = MockSession()
    flowfile = MockFlowFile()
    context = MockContext()
    
    handler(context, session, flowfile)
    
    # Assertions
    assert len(session.transferred_files) > 0
```

### Documentation

Add to main documentation:

1. Update [README.md](../README.md) - add processor to list
2. Update [docs/README.md](../docs/README.md) - add usage section
3. Create example in [examples/](../examples/) - show integration pattern
4. Add to this README - document inputs/outputs/configuration

---

## Processor Development Tips

### Debugging in NiFi

Enable debug logging in NiFi's `conf/logback.xml`:

```xml
<logger name="org.apache.nifi.processors.script.ExecuteScript" level="DEBUG"/>
```

View logs:
```bash
tail -f /opt/nifi/logs/nifi-app.log | grep ExecuteScript
```

### Testing Outside NiFi

All processors should support standalone execution:

```python
if __name__ == '__main__':
    # Test code
    import sys
    
    class MockSession: ...
    # ... mock implementations
    
    flowfile = MockFlowFile()
    flowfile.attributes['test.attr'] = 'value'
    
    handler(None, MockSession(), flowfile)
```

Run directly:
```bash
python processors/your_processor.py
```

### Performance Considerations

1. **Avoid blocking I/O**: Use concurrent tasks instead of slow serial processing
2. **Stream when possible**: Don't load entire files into memory
3. **Clean up resources**: Remove temp files immediately after use
4. **Fail fast**: Transfer already-processed chunks even if later ones fail
5. **Monitor memory**: Use `session.write()` callbacks to avoid buffering

### Error Handling Pattern

```python
def handler(context, session, flowfile):
    temp_file = None
    
    try:
        # Setup
        temp_file = getTempFile()
        
        # Processing
        # ... your logic ...
        
        # Success
        session.transfer(flowfile, 'success')
        
    except Exception as e:
        logError(f"Processing failed: {e}")
        session.transfer(flowfile, 'failure')
    
    finally:
        # Cleanup (always runs)
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)
```

---

## Future Processors

Ideas for additional processors:

- **text_converter.py**: Handle exotic text encodings rejected by KeyView
- **image_preprocessor.py**: Enhance scanned documents before OCR
- **audio_normalizer.py**: Normalize audio levels for better STT accuracy
- **video_keyframe_extractor.py**: Extract keyframes for visual search
- **subtitle_extractor.py**: Extract SRT/VTT subtitles from video containers
- **multilingual_detector.py**: Auto-detect language for routing to appropriate STT

Contributions welcome!

---

## License

All processors are provided under the same license as the main repository.

## Support

For processor-specific questions:

1. Read the processor's docstring
2. Check [examples/](../examples/) for usage patterns
3. Review [docs/README.md](../docs/README.md) for detailed documentation
4. Test standalone before deploying to NiFi
5. Open a GitHub issue with:
   - Processor name
   - NiFi version
   - Python version
   - Error logs
   - Sample input characteristics
