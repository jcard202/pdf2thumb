# pdf2pngthumb

**pdf2pngthumb** is a microservice for generating PNG thumbnails of the *first page* of a PDF.

It’s designed for websites or CMS systems that need to display PDF covers or previews in multiple sizes.

- Upload a PDF
- Specify desired thumbnail sizes
- Get all thumbnails back as a single ZIP archive
- Stateless, auto-cleaning, Docker-ready

---

## Features

- Extracts only the first page of uploaded PDF
- Converts to high-quality PNG (300 dpi)
- Generates thumbnails in user-specified sizes
- Returns all thumbnails in one ZIP file
- Automatically cleans up temporary files
- Easy to deploy in Docker

---

## Project Structure

```
pdf2pngthumb/
├── app.py
├── requirements.txt
├── Dockerfile
└── uploads/           # temporary working directories (auto-cleaned)
```

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/pdf2pngthumb.git
cd pdf2pngthumb
```

### 2. Build the Docker Image

```bash
docker build -t pdf2pngthumb .
```

### 3. Run the Container

```bash
docker run -d -p 5000:5000 pdf2pngthumb
```

Your service will be running at:

```
http://localhost:5000
```

---

## API Documentation

### POST /thumbnail

Generate thumbnails from the *first page* of an uploaded PDF.

#### Request

- **Content-Type:** `multipart/form-data`
- **Fields:**
  - `file` (required): PDF file to process
  - `sizes` (required): Comma-separated list of integer sizes (in pixels)

#### Example cURL

```bash
curl -F "file=@document.pdf" -F "sizes=800,400,200" http://localhost:5000/thumbnail --output thumbnails.zip
```

#### Response

- **HTTP 200 OK**
- **Content-Type:** `application/zip`
- Contains all generated thumbnails:

```
thumb-800.png
thumb-400.png
thumb-200.png
```

#### Example Client Flow

1. User uploads a PDF cover.  
2. Service extracts first page → converts to PNG → resizes to all requested sizes.  
3. User receives ZIP archive with all thumbnails.  
4. User unzips and displays thumbnails on the site.

#### Error Responses

- `400 Bad Request` if:
  - `file` is missing
  - `sizes` is missing or invalid

Example:

```json
{"error": "Invalid sizes parameter"}
```

---

## Temporary Files & Cleanup

- Each request uses a **unique working directory** under `uploads/`.
- All intermediate files are deleted after the request completes.
- No leftover data between requests.

---

## Docker Deployment Example

### Build

```bash
docker build -t pdf2pngthumb .
```

### Run

```bash
docker run -d -p 5000:5000 pdf2pngthumb
```

Your service is now ready at:

```
http://localhost:5000/thumbnail
```

---

## Requirements

**System:**
- Linux / macOS / Windows (with Docker)
- ImageMagick
- Ghostscript (for PDF rasterization)

**Python Dependencies:** (included in `requirements.txt`)
```
Flask
PyPDF2
Pillow
Wand
```

These are installed automatically in the Dockerfile.

---

## Example requirements.txt

```
Flask
PyPDF2
Pillow
Wand
```

---

## Example Dockerfile

```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y imagemagick ghostscript && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
WORKDIR /app
COPY . .

# Create uploads directory
RUN mkdir -p /app/uploads

# Expose port
EXPOSE 5000

# Start the app
CMD ["python", "app.py"]
```

---

## Contributing

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/awesome`)
3. Commit your changes (`git commit -am 'Add awesome feature'`)
4. Push to the branch (`git push origin feature/awesome`)
5. Create a new Pull Request

---

## License

This project is licensed under the MIT License.

---

## Author

*Your Name or Organization*

---

## Contact

For issues or questions, please open an issue in the repository.

---

## TL;DR

> pdf2pngthumb = Upload PDF → Specify sizes → Get ZIP with PNG thumbnails.

Fast. Stateless. Clean. Dockerized.

---


