#!/usr/bin/env python3
"""
convert_to_gguf.py - Convert a Hugging Face model to GGUF format using llama.cpp conversion tool.

Usage:
    python3 convert_to_gguf.py <input_model_dir> [output_gguf_file] [--outtype TYPE]

Environment variables:
    LLAMA_CPP_PATH: Path to the llama.cpp directory (default: ../llama.cpp relative to this script)
    GGUF_OUTPUT_DIR: Directory where to place the GGUF file (default: ./gguf relative to script)
    LOG_FILE: Path to log file (default: ./logs/convert_to_gguf.log)

The script expects the llama.cpp conversion tool convert_hf_to_gguf.py to be present in LLAMA_CPP_PATH.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

def setup_logging(log_file: Path):
    """Configure logging to file and stdout."""
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 convert_to_gguf.py <input_model_dir> [output_gguf_file] [--outtype TYPE]")
        sys.exit(1)

    input_model_dir = Path(sys.argv[1]).resolve()
    output_gguf_file = None
    outtype = "f16"  # default

    # Parse optional arguments
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--outtype":
            if i + 1 < len(sys.argv):
                outtype = sys.argv[i + 1]
                i += 2
            else:
                logging.error("--outtype requires an argument")
                sys.exit(1)
        elif not output_gguf_file:
            output_gguf_file = Path(arg)
            i += 1
        else:
            logging.error(f"Unknown argument: {arg}")
            sys.exit(1)

    # Validate input directory
    if not input_model_dir.is_dir():
        logging.error(f"Input model directory does not exist: {input_model_dir}")
        sys.exit(1)

    # Determine llama.cpp path
    llama_cpp_path = Path(os.environ.get("LLAMA_CPP_PATH", Path(__file__).parent.parent / "llama.cpp")).resolve()
    convert_script = llama_cpp_path / "convert_hf_to_gguf.py"
    if not convert_script.is_file():
        logging.error(f"Conversion script not found: {convert_script}")
        sys.exit(1)

    # Determine output directory and file
    ggf_output_dir = Path(os.environ.get("GGUF_OUTPUT_DIR", Path(__file__).parent.parent / "gguf")).resolve()
    ggf_output_dir.mkdir(parents=True, exist_ok=True)

    if output_gguf_file is None:
        # Default output filename based on input directory name
        output_gguf_file = ggf_output_dir / f"{input_model_dir.name}.gguf"
    else:
        # If user provided a relative path, make it relative to ggf_output_dir unless it's absolute
        if not output_gguf_file.is_absolute():
            output_gguf_file = ggf_output_dir / output_gguf_file.name
        else:
            # If absolute, still ensure parent directory exists
            output_gguf_file.parent.mkdir(parents=True, exist_ok=True)

    # Setup logging
    log_file = Path(os.environ.get("LOG_FILE", Path(__file__).parent.parent / "logs" / "convert_to_gguf.log"))
    setup_logging(log_file)

    logging.info(f"Starting GGUF conversion")
    logging.info(f"Input model directory: {input_model_dir}")
    logging.info(f"LLAMA_CPP_PATH: {llama_cpp_path}")
    logging.info(f"Output GGUF file: {output_gguf_file}")
    logging.info(f"Output type: {outtype}")

    # Build command
    cmd = [
        sys.executable,
        str(convert_script),
        str(input_model_dir),
        f"--outtype={outtype}",
        f"--outfile={output_gguf_file}"
    ]

    logging.info(f"Running command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logging.info("Conversion completed successfully")
        if result.stdout:
            logging.info(f"Stdout: {result.stdout}")
        if result.stderr:
            logging.warning(f"Stderr: {result.stderr}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Conversion failed with return code {e.returncode}")
        if e.stdout:
            logging.error(f"Stdout: {e.stdout}")
        if e.stderr:
            logging.error(f"Stderr: {e.stderr}")
        sys.exit(e.returncode)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)

    logging.info(f"GGUF model saved to: {output_gguf_file}")

if __name__ == "__main__":
    main()