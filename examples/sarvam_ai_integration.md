# Sarvam AI Integration Example

This example shows how to integrate the MPG to MP3 chunker with Sarvam AI's Speech-to-Text API.

**Note**: For the latest API documentation, see the [Sarvam AI API documentation](https://docs.sarvam.ai/).

## Prerequisites

```bash
pip install sarvam-ai
export SARVAM_API_KEY="your-api-key-here"
```

## NiFi Flow Configuration

```
GetFile
  ↓
UpdateAttribute (set idol.reference)
  ↓
ExecuteScript (mpg_to_mp3_chunks.py)
  ↓
ExecuteScript (sarvam_ai_transcribe.py) ← This example
  ↓
MergeContent (by original.link)
  ↓
PutSarvamAI / PutIDOL
```

## Sarvam AI Transcription Processor

Create a new ExecuteScript processor with this code:

```python
"""
Sarvam AI Speech-to-Text Processor
Transcribes MP3 chunks using Sarvam AI STT API
"""

import json
import os
import tempfile
import sys
import requests

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

# Sarvam AI API configuration
SARVAM_API_KEY = os.environ.get('SARVAM_API_KEY')
SARVAM_API_URL = "https://api.sarvam.ai/speech-to-text"

def handler(context, session, flowfile):
    """Transcribe MP3 chunk using Sarvam AI API"""
    
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
    temp_audio = getTempFile(prefix='sarvam-', extn='.mp3')
    
    try:
        # Extract audio data from FlowFile
        def read_callback(inputstream):
            with open(temp_audio, 'wb') as f:
                f.write(inputstream.read())
        
        session.read(flowfile, read_callback)
        
        # Call Sarvam AI API
        headers = {
            'Authorization': f'Bearer {SARVAM_API_KEY}'
        }
        
        with open(temp_audio, 'rb') as audio_file:
            files = {'file': audio_file}
            data = {
                'model': 'saarika:v1',
                'language_code': 'auto'  # Auto-detect language
            }
            
            response = requests.post(
                SARVAM_API_URL,
                headers=headers,
                files=files,
                data=data
            )
        
        if response.status_code != 200:
            logError(f"Sarvam AI API error: {response.status_code} - {response.text}")
            session.transfer(flowfile, 'failure')
            return
        
        # Extract transcript from response
        result = response.json()
        transcript_text = result.get('transcript', '').strip()
        language = result.get('language_code', 'unknown')
        
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
        flowfile = session.putAttribute(flowfile, 'transcript.source', 'sarvam-ai')
        
        # Create JSON output
        transcript_json = {
            'text': transcript_text,
            'language': language,
            'start_time': chunk_start,
            'end_time': chunk_start + chunk_duration,
            'duration': chunk_duration,
            'original_video': original_link,
            'chunk_file': filename,
            'model': 'saarika:v1'
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
  "model": "saarika:v1"
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
    "model": "saarika:v1"
  },
  {
    "text": "Today we will discuss quarterly results",
    "language": "en",
    "start_time": 30.0,
    "end_time": 60.0,
    "duration": 30.0,
    "original_video": "/data/videos/meeting.mpg",
    "chunk_file": "meeting_chunk_001.mp3",
    "model": "saarika:v1"
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

## Multi-Language Support

Sarvam AI supports multiple Indian languages and auto-detection:

```python
# Specify language explicitly
data = {
    'model': 'saarika:v1',
    'language_code': 'hi-IN'  # Hindi
}

# Supported languages:
# - en-IN (English - Indian)
# - hi-IN (Hindi)
# - ta-IN (Tamil)
# - te-IN (Telugu)
# - kn-IN (Kannada)
# - ml-IN (Malayalam)
# - mr-IN (Marathi)
# - gu-IN (Gujarati)
# - bn-IN (Bengali)
# - pa-IN (Punjabi)
# - auto (Auto-detect)
```

## Error Handling

Handle API errors gracefully:

```python
try:
    response = requests.post(SARVAM_API_URL, ...)
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 400:
        logError(f"Invalid audio file: {e}")
        session.transfer(flowfile, 'failure')
    elif e.response.status_code == 429:
        logWarn(f"Rate limit hit: {e}")
        session.transfer(flowfile, 'retry')  # Retry later
    else:
        logError(f"API error: {e}")
        session.transfer(flowfile, 'failure')
except Exception as e:
    logError(f"Unexpected error: {e}")
    session.transfer(flowfile, 'failure')
```

## Cost Estimation

Sarvam AI pricing (check current rates):
- Competitive pricing for Indian language STT
- 30-second chunk processing
- 1-hour video = 120 chunks

For high-volume processing, consider:
- Batch processing optimizations
- Caching strategies for repeated content
- Load balancing across multiple API keys

## Testing

Test with sample MPG file:

```bash
# 1. Extract chunks
curl -F "file=@test.mpg" http://nifi:8080/nifi-api/...

# 2. Verify chunks created
ls -lh *_chunk_*.mp3

# 3. Manually test Sarvam AI
python test_sarvam_ai.py chunk_000.mp3

# 4. Check NiFi logs
tail -f /opt/nifi/logs/nifi-app.log | grep -i sarvam
```

## See Also

- [Main Documentation](../docs/README.md)
- [NiFi Configuration Guide](nifi_configuration.md)
- [Sarvam AI API Documentation](https://docs.sarvam.ai/)
