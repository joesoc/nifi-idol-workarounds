# NiFi ExecuteScript Configuration Example
# ==========================================
# 
# This file shows how to configure the ExecuteScript processor
# in Apache NiFi to use the mpg_to_mp3_chunks.py processor.

## Processor Configuration

**Processor Type:** ExecuteScript

### Properties

| Property | Value | Description |
|----------|-------|-------------|
| Script Engine | `python` | Use Python scripting engine |
| Script File | `/path/to/processors/mpg_to_mp3_chunks.py` | Absolute path to the processor script |
| Script Body | _(leave empty)_ | Script file takes precedence |
| Module Directory | _(optional)_ | Directory for Python modules if needed |
| Failure strategy | `rollback` | Rollback on failure |

### Scheduling

| Property | Recommended Value | Notes |
|----------|------------------|-------|
| Scheduling Strategy | `Timer driven` | Standard approach |
| Run Schedule | `0 sec` | Continuous processing |
| Concurrent Tasks | `4-8` | Match to CPU core count |
| Run Duration | `0 ms` | Process all queued flowfiles |

### Relationships

| Relationship | Description | Typical Connection |
|--------------|-------------|-------------------|
| `success` | MP3 chunks successfully created | → STT processor or MergeContent |
| `failure` | Processing failed | → LogAttribute or PutFile (errors) |

## Upstream Requirements

The ExecuteScript processor expects these FlowFile attributes to be set:

### Required Attributes

```
idol.reference: /absolute/path/to/source/video.mpg
filename: video.mpg
```

### Setting Attributes with UpdateAttribute

Place an **UpdateAttribute** processor before ExecuteScript:

```
Property: idol.reference
Value: ${absolute.path}

Property: filename  
Value: ${filename}
```

## Complete Flow Example

```
┌──────────────┐
│   GetFile    │ - Fetch MPG files from directory
└──────┬───────┘
       │
┌──────▼───────────┐
│ UpdateAttribute  │ - Set idol.reference to ${absolute.path}
└──────┬───────────┘
       │
┌──────▼──────────────────┐
│   ExecuteScript         │ - mpg_to_mp3_chunks.py
│   (MPG → MP3 Chunker)   │
└──────┬──────────────────┘
       │
       ├─ success ──┐
       │            │
┌──────▼────────┐   │
│ InvokeHTTP    │   │ - Call Sarvam AI STT API
│ (STT Service) │   │
└──────┬────────┘   │
       │            │
┌──────▼────────┐   │
│ EvaluateJSON  │   │ - Extract transcript text
│ Response      │   │
└──────┬────────┘   │
       │            │
┌──────▼────────────▼──┐
│   MergeContent       │ - Reassemble by original.link
└──────┬───────────────┘
       │
┌──────▼───────────┐
│  PutSarvamAI/    │ - Index with IDOL or Sarvam AI
│  PutIDOL         │
└──────────────────┘
```

## Output FlowFile Attributes

Each chunk FlowFile will have:

```python
{
    'filename': 'source_video_chunk_000.mp3',
    'mime.type': 'audio/mp3',
    'original.link': '/path/to/source_video.mpg',
    'audio.chunk.start': '0.0',      # Start time in seconds
    'audio.chunk.duration': '30.0'    # Duration in seconds
}
```

## Advanced Configuration

### Custom Chunk Duration

To modify chunk duration, edit the processor script:

```python
CHUNK_DURATION = 30.0  # Change to 15.0, 60.0, etc.
```

Or create a processor property (requires script modification):

```python
CHUNK_DURATION = float(context.getProperty('Chunk Duration').evaluateAttributeExpressions().getValue() or '30.0')
```

Then add processor property:
```
Property Name: Chunk Duration
Default Value: 30.0
```

### Quality Settings

Modify FFmpeg quality preset in the script:

```python
# Current (Standard quality ~190 kbps):
'-q:a', '2',

# High quality (~245 kbps):
'-q:a', '0',

# Medium quality (~165 kbps):
'-q:a', '4',

# Low quality (~130 kbps):
'-q:a', '6',
```

### Error Handling

For production deployments, route failure relationship:

```
ExecuteScript (failure) → LogAttribute → PutFile (/var/log/nifi/failed-videos/)
```

## Testing

### Manual Test

1. Place a test MPG file: `/tmp/test.mpg`
2. Create test FlowFile with GenerateFlowFile:
   - Properties: `{"idol.reference": "/tmp/test.mpg", "filename": "test.mpg"}`
3. Run through ExecuteScript processor
4. Verify chunks appear on success relationship
5. Check attributes on output FlowFiles

### Validation Checklist

- [ ] FFmpeg installed and in PATH
- [ ] Python 3.6+ available to NiFi
- [ ] Script file readable by NiFi user
- [ ] idol.reference attribute set correctly
- [ ] Temp directory writable by NiFi
- [ ] Output directory has sufficient space
- [ ] Success relationship connected

## Troubleshooting

### Enable Debug Logging

In NiFi's `logback.xml`:

```xml
<logger name="org.apache.nifi.processors.script.ExecuteScript" level="DEBUG"/>
```

### Check Processor Logs

```bash
tail -f /opt/nifi/logs/nifi-app.log | grep "ExecuteScript"
```

### Verify FFmpeg

```bash
su - nifi  # Switch to NiFi user
ffmpeg -version
ffmpeg -i /path/to/test.mpg -t 10 -vn -acodec libmp3lame /tmp/test.mp3
```

### Common Issues

1. **Permission denied**: Ensure NiFi user can read source files
2. **FFmpeg not found**: Add FFmpeg to NiFi's PATH in bootstrap.conf
3. **No output chunks**: Check if source file has audio track
4. **Slow processing**: Increase concurrent tasks or reduce video resolution

## Performance Tuning

### For High-Volume Processing

```
Concurrent Tasks: 8
Yield Duration: 0 sec
Run Duration: 0 ms
Batch Size: 10 (if using ListFile → FetchFile)
```

### For Memory-Constrained Systems

```
Concurrent Tasks: 2-4
Max Concurrent Tasks per Node: 4
Back Pressure Object Threshold: 10000
```

### For Network-Stored Files

- Use local temp directory (not network share)
- Consider staging files locally with FetchFile
- Monitor network I/O with iostat

## Integration Examples

See `/examples/` directory for:
- Sarvam AI STT integration
