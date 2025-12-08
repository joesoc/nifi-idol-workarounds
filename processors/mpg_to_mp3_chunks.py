"""
MPG to MP3 Chunker - NiFi ExecuteScript Processor
==================================================

Extracts audio from MPG files and splits into 30-second MP3 chunks for speech-to-text processing.

This processor bypasses IDOL Media Server limitations for unsupported formats and languages
by directly extracting and chunking audio using FFmpeg.

Requirements:
    - FFmpeg installed and available in PATH
    - Python 3.6+

Attributes:
    Input:
        - idol.reference: Path to the source MPG file (required)
        - filename: Original filename (optional)
    
    Output:
        - filename: Generated chunk filename (e.g., video_chunk_000.mp3)
        - mime.type: Set to 'audio/mp3'
        - original.link: Path to original source file
        - audio.chunk.start: Start time in seconds (e.g., "0.0", "30.0", "60.0")
        - audio.chunk.duration: Duration in seconds (always "30.0")

Routes:
    - success: Successfully created MP3 chunk(s)
    - failure: Processing failed (if first segment fails)
"""

import os
import subprocess
import sys
import tempfile

# --- NiFi Context Compatibility Layer ---
try:
    from idolnifi import *  # Real NiFi environment injects logging & utils
except ImportError:
    # Fallback for local testing / standalone execution
    def logInfo(*args, **kwargs):
        print("INFO:", *args, **kwargs, file=sys.stderr)
    def logError(*args, **kwargs):
        print("ERROR:", *args, **kwargs, file=sys.stderr)
    def logWarn(*args, **kwargs):
        print("WARN:", *args, **kwargs, file=sys.stderr)
    def getTempFile(prefix: str = '', extn: str = '.tmp'):
        return tempfile.NamedTemporaryFile(prefix=prefix, suffix=extn, delete=False).name

def handler(context, session, flowfile):
    """
    Main processor handler function called by NiFi ExecuteScript processor.
    
    Args:
        context: NiFi processor context
        session: NiFi session for creating/transferring flowfiles
        flowfile: Input flowfile to process
    """
    logInfo("Starting optimized MPG → 30-second MP3 chunk extraction (Diagnostic Bypass Active)...")

    # --- 1. Basic validation ---
    if flowfile is None:
        logError("Input FlowFile is None.")
        return

    # --- 2. Get source path (critical for bypass) ---
    source_link = flowfile.getAttribute('idol.reference')
    if not source_link:
        logError("Required attribute 'idol.reference' missing.")
        source_link = flowfile.getAttribute('filename') or flowfile.getUuid()

    # --- DIAGNOSTIC BYPASS: Use original file directly ---
    temp_mpg_path = source_link
    original_filename = flowfile.getAttribute('filename')
    base_filename = original_filename.rsplit('.', 1)[0] if original_filename and '.' in original_filename else flowfile.getUuid()

    logInfo(f"DIAGNOSTIC BYPASS: Using source file directly: {temp_mpg_path}")
    session.remove(flowfile)  # Original FlowFile discarded — we work from disk

    # --- 3. Chunking configuration ---
    CHUNK_DURATION = 30.0  # seconds (optimal for most STT services)
    segment_index = 0

    while True:
        start_time = segment_index * CHUNK_DURATION
        temp_mp3_path = getTempFile(prefix=f"segment-{segment_index:03d}", extn='.mp3')

        try:
            logInfo(f"Extracting segment {segment_index} @ {start_time:.1f}s")

            # Fast-seek FFmpeg command (-ss BEFORE -i)
            ffmpeg_command = [
                'ffmpeg',
                '-ss', str(start_time),           # Fast keyframe seek
                '-i', temp_mpg_path,              # Input file
                '-t', str(CHUNK_DURATION),        # Duration
                '-vn',                            # No video
                '-acodec', 'libmp3lame',          # MP3 encoder
                '-q:a', '2',                      # High quality VBR (~190-250 kbps)
                '-y',                             # Overwrite output
                temp_mp3_path
            ]

            result = subprocess.run(
                ffmpeg_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False
            )

            # --- Handle FFmpeg exit codes gracefully ---
            if result.returncode != 0:
                if os.path.exists(temp_mp3_path) and os.path.getsize(temp_mp3_path) > 1024:
                    logInfo("FFmpeg exited non-zero but produced final segment → accepting.")
                elif segment_index == 0:
                    logError(f"FFmpeg failed on first segment: {result.stderr.decode()}")
                    raise Exception("FFmpeg failed on first segment")
                else:
                    break  # End of file reached

            # --- Validate output file ---
            if not os.path.exists(temp_mp3_path) or os.path.getsize(temp_mp3_path) < 1024:
                logWarn(f"Segment {segment_index} too small or missing → end of content.")
                if os.path.exists(temp_mp3_path):
                    os.remove(temp_mp3_path)
                break

            logInfo(f"Segment {segment_index} extracted → {os.path.getsize(temp_mp3_path)} bytes")

            # --- 4. Create new FlowFile per chunk ---
            mp3_flowfile = session.create()
            chunk_filename = f"{base_filename}_chunk_{segment_index:03d}.mp3"

            mp3_flowfile = session.putAttribute(mp3_flowfile, 'filename', chunk_filename)
            mp3_flowfile = session.putAttribute(mp3_flowfile, 'mime.type', 'audio/mp3')
            mp3_flowfile = session.putAttribute(mp3_flowfile, 'original.link', source_link)
            mp3_flowfile = session.putAttribute(mp3_flowfile, 'audio.chunk.start', str(start_time))
            mp3_flowfile = session.putAttribute(mp3_flowfile, 'audio.chunk.duration', str(CHUNK_DURATION))

            # --- 5. Write MP3 content ---
            def write_callback(outputstream):
                with open(temp_mp3_path, 'rb') as f:
                    outputstream.writeFromReadable(f)
            session.write(mp3_flowfile, write_callback)

            # --- 6. Cleanup & immediate transfer ---
            if os.path.exists(temp_mp3_path):
                os.remove(temp_mp3_path)

            session.transfer(mp3_flowfile, 'success')
            logInfo(f"Segment {segment_index} transferred to success")

            segment_index += 1

        except Exception as e:
            logError(f"Critical error in segment loop: {e}")
            if os.path.exists(temp_mp3_path):
                os.remove(temp_mp3_path)
            return  # Fail fast — already-transferred chunks remain valid

    # --- Final reporting ---
    if segment_index == 0:
        logError("No MP3 segments created.")
    else:
        logInfo(f"Chunking complete → {segment_index} segments transferred to success.")

    logInfo("MPG → MP3 chunking process finished.")
