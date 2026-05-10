# Presentation Generator
By: Balla Krisztián (RZWVC0)

AI-powered presentation generation from long PDF documents.

The system:
- extracts text from PDFs,
- extracts figures/images,
- generates semantic presentation slides using GPT-4.1,
- renders the presentation as HTML/CSS,
- exports the final presentation as a PDF.



## Requirements

- OpenAI API key
- Docker



## OpenAI API Key

Create a `.env` file in the `src/` folder and put your OpenAI API key there:

```env
OPENAI_API_KEY=your_api_key_here
```



## Docker Usage

### Build the Docker Image

```bash
./build_docker.sh
```

This builds the container with:
- Ubuntu 22.04
- Python
- Playwright + Chromium
- all required dependencies

---

### Run the Docker Container

```bash
./run_docker.sh
```

After starting the container the script executes the following command, so you're immediately placed in a shell inside the container:
```bash
docker exec -it ${container_name} bash
```


## Running the Presentation Generator

The project includes a convenience wrapper script:

```bash
./ppt_generator.sh
```

The script:
- automatically loads the `.env` file,
- validates required arguments,
- checks the OpenAI API key,
- launches the presentation generation pipeline.


### Basic Usage

```bash
./ppt_generator.sh --input input/sample.pdf
```

This generates:
- `output/presentation.html`
- `output/generated_presentation.pdf`



### Custom Output Paths

```bash
./ppt_generator.sh \
    --input input/paper.pdf \
    --html-output output/custom.html \
    --pdf-output output/final.pdf
```



### Full Example

```bash
./run.sh \
    --input input/paper.pdf \
    --html-output output/presentation.html \
    --pdf-output output/final.pdf \
    --temp-image-folder temp_images \
    --temp-table-folder temp_tables
```



### Command Line Arguments

| Argument | Description |
|---|---|
| `--input` | Input PDF document (required) |
| `--html-output` | Output HTML presentation |
| `--pdf-output` | Output PDF presentation |
| `--temp-image-folder` | Temporary extracted figure directory |
| `--temp-table-folder` | Temporary extracted table directory |

---

### Notes

- `--input` is required.
- The script automatically reads `OPENAI_API_KEY` from `.env`.
- Temporary folders are created automatically if they do not exist.
- The generated PDF uses Playwright + Chromium for rendering.

---

# Output

The pipeline generates:
- an HTML presentation,
- a PDF presentation,
- temporary extracted figures/tables.

Example:

```text
output/
├── presentation.html
└── presentation.pdf
```