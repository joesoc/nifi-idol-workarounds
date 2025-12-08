#!/usr/bin/env python3
"""
Test Script for MPG to MP3 Chunker
===================================

Simple standalone test to verify the processor logic works correctly
outside of NiFi environment.

Usage:
    python test_chunker.py /path/to/test.mpg

Requirements:
    - FFmpeg installed
    - Python 3.6+
    - Test MPG file
"""

import os
import sys
import subprocess
import tempfile

class MockSession:
    """Mock NiFi session for testing"""
    
    def __init__(self):
        self.created_files = []
        self.removed_files = []
        self.transferred_files = []
    
    def create(self):
        """Create a new mock FlowFile"""
        return MockFlowFile()
    
    def remove(self, flowfile):
        """Remove a FlowFile"""
        self.removed_files.append(flowfile)
        print(f"  → Removed original FlowFile")
    
    def putAttribute(self, flowfile, key, value):
        """Set attribute on FlowFile"""
        flowfile.attributes[key] = value
        return flowfile
    
    def write(self, flowfile, callback):
        """Write to FlowFile using callback"""
        import io
        outputstream = io.BytesIO()
        
        class OutputStream:
            def __init__(self, stream):
                self.stream = stream
            
            def writeFromReadable(self, readable):
                self.stream.write(readable.read())
        
        callback(OutputStream(outputstream))
        flowfile.content = outputstream.getvalue()
        return flowfile
    
    def transfer(self, flowfile, relationship):
        """Transfer FlowFile to relationship"""
        self.transferred_files.append((flowfile, relationship))
        print(f"  ✓ Transferred to '{relationship}': {flowfile.attributes.get('filename', 'unknown')}")
        print(f"    - Start: {flowfile.attributes.get('audio.chunk.start', 'N/A')}s")
        print(f"    - Duration: {flowfile.attributes.get('audio.chunk.duration', 'N/A')}s")
        print(f"    - Size: {len(flowfile.content)} bytes")

class MockFlowFile:
    """Mock FlowFile for testing"""
    
    def __init__(self):
        self.attributes = {}
        self.content = b''
        self.uuid = 'test-flowfile-001'
    
    def getAttribute(self, key):
        """Get attribute value"""
        return self.attributes.get(key)
    
    def getUuid(self):
        """Get FlowFile UUID"""
        return self.uuid

class MockContext:
    """Mock NiFi context for testing"""
    pass

def logInfo(*args, **kwargs):
    """Mock logging function"""
    print("INFO:", *args, **kwargs)

def logError(*args, **kwargs):
    """Mock logging function"""
    print("ERROR:", *args, **kwargs, file=sys.stderr)

def logWarn(*args, **kwargs):
    """Mock logging function"""
    print("WARN:", *args, **kwargs)

def getTempFile(prefix='', extn='.tmp'):
    """Mock temp file function"""
    return tempfile.NamedTemporaryFile(prefix=prefix, suffix=extn, delete=False).name

def test_processor(mpg_path):
    """
    Test the processor with a real MPG file
    
    Args:
        mpg_path: Path to test MPG file
    """
    print("\n" + "="*70)
    print(f"Testing MPG to MP3 Chunker")
    print("="*70)
    
    # Verify FFmpeg is available
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE,
                              check=True)
        print("\n✓ FFmpeg found")
    except FileNotFoundError:
        print("\n✗ FFmpeg not found in PATH")
        print("  Install: sudo apt-get install ffmpeg")
        return False
    except subprocess.CalledProcessError:
        print("\n✗ FFmpeg execution failed")
        return False
    
    # Verify input file exists
    if not os.path.exists(mpg_path):
        print(f"\n✗ Input file not found: {mpg_path}")
        return False
    
    print(f"✓ Input file exists: {mpg_path}")
    print(f"  Size: {os.path.getsize(mpg_path) / (1024*1024):.2f} MB")
    
    # Check if file has audio
    probe_cmd = [
        'ffmpeg', '-i', mpg_path,
        '-af', 'volumedetect',
        '-f', 'null', '-'
    ]
    result = subprocess.run(probe_cmd, 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE)
    output = result.stderr.decode()
    
    if 'Audio:' not in output:
        print("\n✗ No audio stream found in file")
        return False
    
    print("✓ Audio stream detected")
    
    # Create mock NiFi objects
    context = MockContext()
    session = MockSession()
    
    # Create input FlowFile
    flowfile = MockFlowFile()
    flowfile.attributes['idol.reference'] = mpg_path
    flowfile.attributes['filename'] = os.path.basename(mpg_path)
    
    print(f"\n" + "-"*70)
    print("Processing...")
    print("-"*70 + "\n")
    
    # Import and run processor
    # Note: In real test, we'd import from the actual module
    # For this demo, we'll inline the processor logic
    
    from processors.mpg_to_mp3_chunks import handler
    
    # Run processor
    handler(context, session, flowfile)
    
    # Report results
    print("\n" + "-"*70)
    print("Results")
    print("-"*70)
    print(f"\n✓ Original FlowFile removed: {len(session.removed_files)}")
    print(f"✓ Chunks created: {len(session.transferred_files)}")
    
    success_count = sum(1 for _, rel in session.transferred_files if rel == 'success')
    print(f"✓ Successful transfers: {success_count}")
    
    total_size = sum(len(ff.content) for ff, _ in session.transferred_files)
    print(f"✓ Total output size: {total_size / 1024:.2f} KB")
    
    if success_count > 0:
        avg_size = total_size / success_count
        print(f"✓ Average chunk size: {avg_size / 1024:.2f} KB")
    
    print("\n" + "="*70)
    print("Test completed successfully!")
    print("="*70 + "\n")
    
    return True

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python test_chunker.py /path/to/test.mpg")
        print("\nThis script tests the MPG to MP3 chunker processor")
        print("outside of the NiFi environment.")
        sys.exit(1)
    
    mpg_path = sys.argv[1]
    
    try:
        success = test_processor(mpg_path)
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
