# Smart Librarian

Smart Librarian is a full-stack AI book recommendation app built with FastAPI and React. It searches a local catalog of books with embeddings and ChromaDB, selects one strong match with OpenAI, and returns a polished answer in the same language as the user's request.

The app also supports browser voice input, optional text-to-speech playback, and optional AI-generated cover-style artwork for the recommended book.

## Overview

- Semantic search over a local dataset of 100 books
- One focused recommendation per request
- Responses generated in the same language as the user
- Input moderation and request validation
- Optional generated audio reply
- Optional generated book-cover-style image
- React chat interface with quick prompts and live status states

## How It Works

1. The backend starts from `src/main.py` and runs `ensure_indexed()` during startup.
2. If the ChromaDB collection is empty, the app loads `src/books/books.json`, creates embeddings with `text-embedding-3-small`, and stores them in `src/chrom_db/`.
3. When the user sends a request, the backend validates the text, checks moderation, and retrieves the closest book matches from ChromaDB.
4. `gpt-4o-mini` selects a single recommendation from the retrieved results only, then the backend fetches the full local summary for that title.
5. A final answer is generated in the user's language.
6. If enabled, the backend also generates audio with `edge-tts` and a cover-style image with `gpt-image-1`.
7. The frontend renders the response, auto-plays the latest audio when possible, and displays the generated image inline.

## Main Features

### Backend

- FastAPI API with `/health`, `/chat`, `/docs`, and `/redoc`
- Automatic ChromaDB indexing at startup
- OpenAI embeddings for semantic retrieval
- OpenAI moderation for unsafe input filtering
- Optional server-side speech transcription from a local audio file path
- Graceful fallback to text-only responses if image generation fails

### Frontend

- Chat-style interface for book discovery
- Quick prompt suggestions
- Browser speech recognition button
- Audio replay plus pause/resume controls
- Toggle for generated audio replies
- Toggle for generated cover previews
- Status indicator with `Ready`, `Listening`, and `Thinking`
- Speech recognition language selector:
  - Romanian
  - English
  - French
  - German
  - Spanish
  - Italian

## Tech Stack

### Backend

- Python
- FastAPI
- Pydantic
- ChromaDB
- OpenAI API
- `edge-tts`
- `langdetect`

### AI Models Used

- `text-embedding-3-small` for vector embeddings
- `gpt-4o-mini` for recommendation selection and final response
- `omni-moderation-latest` for input moderation
- `gpt-4o-mini-transcribe` for optional server-side transcription
- `gpt-image-1` for optional cover generation

### Frontend

- React 19
- JavaScript
- Web Speech API
- Fetch API
- Custom CSS UI

## Project Structure

```text
Smart Librarian/
|-- artifacts/
|   `-- book.png
|-- frontend/
|   |-- public/
|   `-- src/
|       |-- components/
|       |-- constants/
|       |-- hooks/
|       |-- pages/
|       |-- services/
|       `-- utils/
|-- src/
|   |-- api/
|   |-- books/
|   |   `-- books.json
|   |-- chatbot/
|   |-- chrom_db/
|   |-- vector_store/
|   `-- main.py
|-- requirements.txt
`-- README.md
```

## Dataset

The project uses a local JSON dataset at `src/books/books.json`.

- Size: 100 books
- Fields per item:
  - `id`
  - `title`
  - `author`
  - `short_summary`
  - `full_summary`
  - `themes`
  - `genre`
  - `year`

## Prerequisites

- Python
- Node.js and npm
- An `OPENAI_API_KEY`

## Backend Setup

From the project root:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:OPENAI_API_KEY="your_openai_api_key"
$env:ALLOWED_ORIGINS="http://localhost:3000"
uvicorn src.main:app --reload
```

Backend URLs:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

Notes:

- `OPENAI_API_KEY` is required for embeddings, moderation, chat completions, transcription, and image generation.
- `ALLOWED_ORIGINS` defaults to `http://localhost:3000` if not set.
- The ChromaDB collection is persisted in `src/chrom_db/`.
- If the collection is already populated, startup reuses it instead of re-indexing the dataset.

## Frontend Setup

From the `frontend` folder:

```powershell
npm install
npm start
```

Frontend URL:

- App: `http://localhost:3000`

Important:

- The frontend currently calls `http://127.0.0.1:8000/chat`.
- If you change the backend host or port, update `frontend/src/services/api.js`.

## API

### `GET /health`

Health check endpoint.

Example response:

```json
{
  "status": "ok",
  "service": "smart-librarian-api",
  "version": "1.0.0"
}
```

### `POST /chat`

Main assistant endpoint.

Request body:

```json
{
  "message": "I want a philosophical science fiction book.",
  "query": null,
  "use_voice_input": false,
  "input_audio_path": null,
  "generate_audio": true,
  "generate_image": true
}
```

Notes:

- Use either `message` or `query`.
- `generate_audio` and `generate_image` are optional flags.
- If `use_voice_input` is `true`, `input_audio_path` must point to a local audio file on the backend machine.
- The current React UI uses browser speech recognition and sends text, not uploaded audio files.

Example response:

```json
{
  "user_message": "I want a philosophical science fiction book.",
  "transcribed_text": null,
  "response": "You might enjoy ...",
  "title": "Example Book Title",
  "audio_generated": true,
  "audio_base64": "...",
  "image_path": "artifacts/book.png",
  "image_base64": "..."
}
```

## Validation and Error Handling

The backend currently handles:

- Empty requests
- Prompts longer than 1200 characters
- Unsafe or disrespectful input flagged by moderation
- Missing `input_audio_path` when server-side voice mode is enabled
- Chat, transcription, audio, and image generation failures

The frontend currently handles:

- Empty text submission
- Unsupported browser speech recognition
- Voice recognition failures
- API request errors
- Audio playback failures caused by browser autoplay policies

## Example Prompts

- `I need a thrilling mystery story with twists and suspense.`
- `I want a romantic classic with emotional depth.`
- `Give me a philosophical science fiction book.`
- `I need an exciting sci-fi tale with dark tone.`

## Current Notes

- The assistant recommends exactly one book per request.
- Audio and image content are returned as Base64 so the frontend can render them immediately.
- Generated artwork is saved to `artifacts/book.png`.
- The frontend includes a welcome message and an embedded sample audio clip.
- Browser autoplay policies may block audio until the user interacts with the page.

## Future Improvements

- Save chat history
- Support multiple recommendations in one response
- Add authentication
- Expose a browser-based audio upload flow to use backend transcription directly
- Add deployment and production configuration
- Improve automated testing coverage

## License

This project is licensed under the MIT License.

```
MIT License

Copyright (c) 2026 Ias Alexandru-Ioan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Author

Ias Alexandru-Ioan
