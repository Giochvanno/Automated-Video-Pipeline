# HellReam Engine

An automated Python pipeline for programmatic video production. This project generates scripts, handles text-to-speech (TTS), creates visual assets, and automatically edits everything together into a final, ready-to-publish video file.

It is specifically configured for vertical short-form content (1080x1920) and includes custom logic for visual effects, dynamic subtitles, and audio synchronization.

## Features

* **End-to-End Automation:** Generates the narrative, audio, and visuals based on a single topic input.
* **Smart Asset Resizing:** Automatically scales and crops images to fit the 9:16 aspect ratio without leaving black pillars.
* **Dynamic Audio Engine:** Synchronizes TTS voiceovers with background ambient tracks and random intro hooks.
* **Video Composition:** Utilizes MoviePy for zoom-in effects, crossfade transitions, and VHS overlay layering.
* **Automated Subtitles:** Generates and centers karaoke-style subtitles dynamically timed to the audio track.
* **Resource Management:** Includes a built-in garbage collection and temporary file cleanup system to prevent memory leaks during rendering.

## Prerequisites

* **Python:** 3.8 or higher.
* **ImageMagick:** Required by MoviePy for text and subtitle rendering. You must install ImageMagick and ensure the executable path is correctly mapped in the configuration section of the code.

## Installation

1. Clone the repository:
    git clone [https://github.com/Giochvanno/Automated-Video-Pipeline.git]
    cd Automated-Video-Pipeline

    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate


**Usage**
Run the main assembly script from the terminal:
    assets/
    ├── intro/      (Place short audio hooks here)
    ├── music/
    │   ├── alarm/  (Siren/high-tension tracks)
    │   └── lore/   (Ambient background tracks)
    └── overlays/   (VHS/grain video overlays in .mp4 format)


**Project Structure**
    main.py - The core factory script that manages the assembly pipeline and rendering.

    brain.py - Handles script pacing and director instructions.

    artist.py - Manages visual asset generation.

    voice.py - Handles the text-to-speech processing.

    subtitles.py - Generates synchronized text clips for the video.

**License**
    This project is licensed under the MIT License.