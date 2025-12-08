# OpenAI Whisper Integration Example

This example shows how to integrate the MPG to MP3 chunker with OpenAI's Whisper API for speech-to-text.

**Note**: This example uses the OpenAI API syntax that may need updates based on your OpenAI library version. For the latest API, see the [OpenAI Python library documentation](https://github.com/openai/openai-python).

## Prerequisites

```bash
pip install openai
export OPENAI_API_KEY="your-api-key-here"
```

## NiFi Flow Configuration

```
GetFile
  ↓
UpdateAttribute (set idol.reference)
  ↓
ExecuteScript (mpg_to_mp3_chunks.py)
  ↓
ExecuteScript (whisper_transcribe.py) ← This example
  ↓
MergeContent (by original.link)
  ↓
PutElasticsearch / PutIDOL
```

## Whisper Transcription Processor

Create a new ExecuteScript processor with this code:

```python
"""
OpenAI Whisper Speech-to-Text Processor
Transcribes MP3 chunks using OpenAI Whisper API
"""

import json
import os
import tempfile
import sys

# NiFi imports
try:
    from idolnifi import *
except ImportError:
    def logInfo(*args, **kwargs):
        print("INFO:", *args, **kwargs, file=sys.stderr)
    def logError(*args, **kwargs):
        print("ERROR:", *args, **kwargs, file=sys.stderr)
    def getTempFile(prefix='', extn='.tmp'):
        return tempfile.NamedTemporaryFile(prefix=prefix, suffix=extn, delete=False).name

# OpenAI API
try:
    import openai
    openai.api_key = os.environ.get('OPENAI_API_KEY')
except ImportError:
    logError("openai package not installed. Run: pip install openai")

def handler(context, session, flowfile):
    """Transcribe MP3 chunk using Whisper API"""
    
    if flowfile is None:
        logError("Input FlowFile is None")
        return
    
    # Get chunk metadata
    chunk_start = float(flowfile.getAttribute('audio.chunk.start') or '0.0')
    chunk_duration = float(flowfile.getAttribute('audio.chunk.duration') or '30.0')
    original_link = flowfile.getAttribute('original.link') or 'unknown'
    filename = flowfile.getAttribute('filename') or 'audio.mp3'
    
    logInfo(f"Transcribing chunk: {filename} (start: {chunk_start}s)")
    
    # Write FlowFile content to temp file
    temp_audio = getTempFile(prefix='whisper-', extn='.mp3')
    
    try:
        # Extract audio data from FlowFile
        def read_callback(inputstream):
            with open(temp_audio, 'wb') as f:
                f.write(inputstream.read())
        
        session.read(flowfile, read_callback)
        
        # Call Whisper API
        with open(temp_audio, 'rb') as audio_file:
            transcript_response = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",  # Include timing info
                language=None  # Auto-detect (or set to 'en', 'es', etc.)
            )
        
        # Extract transcript text
        transcript_text = transcript_response.get('text', '').strip()
        language = transcript_response.get('language', 'unknown')
        
        if not transcript_text:
            logInfo(f"No speech detected in chunk {filename}")
            session.transfer(flowfile, 'success')
            return
        
        logInfo(f"Transcript ({language}): {transcript_text[:100]}...")
        
        # Add transcript attributes to FlowFile
        flowfile = session.putAttribute(flowfile, 'transcript.text', transcript_text)
        flowfile = session.putAttribute(flowfile, 'transcript.language', language)
        flowfile = session.putAttribute(flowfile, 'transcript.start', str(chunk_start))
        flowfile = session.putAttribute(flowfile, 'transcript.end', str(chunk_start + chunk_duration))
        flowfile = session.putAttribute(flowfile, 'transcript.source', 'whisper-1')
        
        # Create JSON output
        transcript_json = {
            'text': transcript_text,
            'language': language,
            'start_time': chunk_start,
            'end_time': chunk_start + chunk_duration,
            'duration': chunk_duration,
            'original_video': original_link,
            'chunk_file': filename,
            'model': 'whisper-1'
        }
        
        # Write JSON to FlowFile content
        def write_callback(outputstream):
            json_str = json.dumps(transcript_json, indent=2)
            outputstream.write(json_str.encode('utf-8'))
        
        flowfile = session.write(flowfile, write_callback)
        flowfile = session.putAttribute(flowfile, 'mime.type', 'application/json')
        
        # Transfer to success
        session.transfer(flowfile, 'success')
        logInfo(f"Successfully transcribed chunk {filename}")
        
    except Exception as e:
        logError(f"Error transcribing chunk: {e}")
        session.transfer(flowfile, 'failure')
    
    finally:
        # Cleanup temp file
        if os.path.exists(temp_audio):
            os.remove(temp_audio)
```

## Output Format

Each transcribed chunk produces JSON:

```json
{
  "text": "The quick brown fox jumps over the lazy dog",
  "language": "en",
  "start_time": 30.0,
  "end_time": 60.0,
  "duration": 30.0,
  "original_video": "/data/videos/meeting.mpg",
  "chunk_file": "meeting_chunk_001.mp3",
  "model": "whisper-1"
}
```

## Merging Transcripts

Use MergeContent processor to combine chunks:

**Configuration:**
- Merge Strategy: `Bin-Packing Algorithm`
- Correlation Attribute: `original.link`
- Delimiter Strategy: `Text`
- Demarcator: `,\n` (for JSON array)
- Header: `[\n`
- Footer: `\n]`

**Output (merged transcript):**
```json
[
  {
    "text": "Welcome to the meeting",
    "language": "en",
    "start_time": 0.0,
    "end_time": 30.0,
    "duration": 30.0,
    "original_video": "/data/videos/meeting.mpg",
    "chunk_file": "meeting_chunk_000.mp3",
    "model": "whisper-1"
  },
  {
    "text": "Today we will discuss quarterly results",
    "language": "en",
    "start_time": 30.0,
    "end_time": 60.0,
    "duration": 30.0,
    "original_video": "/data/videos/meeting.mpg",
    "chunk_file": "meeting_chunk_001.mp3",
    "model": "whisper-1"
  }
]
```

## Indexing with IDOL

Use PutIDOL processor to index transcripts:

```xml
<DREADDDATA>
  <DOCUMENT>
    <CONTENT>
      <![CDATA[
        Welcome to the meeting. Today we will discuss quarterly results.
      ]]>
    </CONTENT>
    <FIELDS>
      <FIELD NAME="VIDEO_PATH">/data/videos/meeting.mpg</FIELD>
      <FIELD NAME="LANGUAGE">en</FIELD>
      <FIELD NAME="DURATION">60.0</FIELD>
      <FIELD NAME="TRANSCRIPT_SEGMENTS">
        [{"start":0.0,"end":30.0,"text":"Welcome to the meeting"},
         {"start":30.0,"end":60.0,"text":"Today we will discuss quarterly results"}]
      </FIELD>
    </FIELDS>
  </DOCUMENT>
</DREADDDATA>
```

## Click-to-Playback Integration

Create search results with video links:

```html
<div class="search-result">
  <h3>Meeting Recording - Q4 2024</h3>
  <p>Path: /data/videos/meeting.mpg</p>
  
  <div class="transcript">
    <p>
      <a href="player.html?video=/data/videos/meeting.mpg&t=0">
        [00:00] Welcome to the meeting
      </a>
    </p>
    <p>
      <a href="player.html?video=/data/videos/meeting.mpg&t=30">
        [00:30] Today we will discuss quarterly results
      </a>
    </p>
  </div>
</div>
```

## Advanced: Word-Level Timestamps

For word-level timestamps, parse Whisper's detailed response:

```python
# In transcription processor
transcript_response = openai.Audio.transcribe(
    model="whisper-1",
    file=audio_file,
    response_format="verbose_json",
    timestamp_granularities=["word"]
)

# Extract word-level timing
words = []
for segment in transcript_response.get('segments', []):
    for word_info in segment.get('words', []):
        words.append({
            'word': word_info['word'],
            'start': chunk_start + word_info['start'],
            'end': chunk_start + word_info['end'],
            'confidence': word_info.get('confidence', 1.0)
        })

# Store in FlowFile
flowfile = session.putAttribute(flowfile, 'words_json', json.dumps(words))
```

## Error Handling

Handle API errors gracefully:

```python
try:
    transcript_response = openai.Audio.transcribe(...)
except openai.error.InvalidRequestError as e:
    logError(f"Invalid audio file: {e}")
    session.transfer(flowfile, 'failure')
except openai.error.RateLimitError as e:
    logWarn(f"Rate limit hit: {e}")
    session.transfer(flowfile, 'retry')  # Retry later
except Exception as e:
    logError(f"Unexpected error: {e}")
    session.transfer(flowfile, 'failure')
```

## Cost Estimation

OpenAI Whisper pricing (as of 2024):
- $0.006 per minute of audio
- 30-second chunk = $0.003 per chunk
- 1-hour video = 120 chunks = $0.36

For high-volume processing, consider:
- Local Whisper.cpp (free, GPU-accelerated)
- Azure Batch Speech API (lower cost)
- Google Cloud STT (free tier available)

## Testing

Test with sample MPG file:

```bash
# 1. Extract chunks
curl -F "file=@test.mpg" http://nifi:8080/nifi-api/...

# 2. Verify chunks created
ls -lh *_chunk_*.mp3

# 3. Manually test Whisper
python test_whisper.py chunk_000.mp3

# 4. Check NiFi logs
tail -f /opt/nifi/logs/nifi-app.log | grep -i whisper
```

## See Also

- [Google Cloud STT Example](google_stt_integration.md)
- [Azure Cognitive Services Example](azure_stt_integration.md)
- [Local Whisper.cpp Example](whisper_cpp_integration.md)
- [Main Documentation](../docs/README.md)
