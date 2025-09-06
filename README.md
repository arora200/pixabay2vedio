# Programmatically Generated Video

This project is a command-line application that automatically creates videos from text scripts. It analyzes the script, generates audio using text-to-speech, retrieves relevant video clips from Pixabay, and combines them into a final video.

## Getting Started

### Prerequisites

*   Python 3.x
*   Git

### Installation

1.  Clone the repository:

    ```bash
    git clone https://github.com/your-username/your-repository-name.git
    ```

2.  Navigate to the project directory:

    ```bash
    cd your-repository-name
    ```

3.  Install the required dependencies:

    ```bash
    pip install -r video_creation_cli/requirements.txt
    ```

### Configuration

To use the application, you need a Pixabay API key. You can get one for free from the [Pixabay website](https://pixabay.com/api/docs/).

Once you have your API key, you can either set it as an environment variable named `PIXABAY_API_KEY` or pass it as a command-line argument.

## Usage

To run the application, you can use the `run_video_cli.bat` script:

```bash
run_video_cli.bat your_script.txt
```

Replace `your_script.txt` with the path to your script file.

## Running the Demo

To see a quick demonstration of the project, you can run the `run_demo.bat` script. This script will generate a short video based on the `demo_script.txt` file.

To run the demo, you need to provide your Pixabay API key as a command-line argument:

```bash
run_demo.bat YOUR_API_KEY
```

Replace `YOUR_API_KEY` with your actual Pixabay API key.