# Smart Librarian

Smart Librarian is a full-stack AI-powered book recommendation app that helps users discover books based on mood, genre, theme, tone, or reading preferences. The project includes a **FastAPI backend** and a **React frontend**, with support for **voice input**, **text-to-speech audio replies**, and **AI-generated book cover previews**.

## Features

### Core functionality

* Get book recommendations from an AI assistant
* Ask using mood, theme, genre, atmosphere, or style
* Receive a focused recommendation response

### Voice and media

* Browser-based voice input using Speech Recognition API
* Optional audio reply generation with automatic playback
* Optional AI-generated image preview for the recommended book

### User experience

* Clean chat-style interface
* Quick prompt suggestions
* Real-time status indicators: Ready, Listening, Thinking
* Multi-language speech recognition support

## Project structure

```text
smart-librarian/
├── backend/
│   ├── main application with FastAPI routes
│   ├── chatbot logic
│   ├── speech-to-text integration
│   ├── text-to-speech integration
│   ├── image generation utilities
│   └── request/response schemas
└── frontend/
    ├── React application
    ├── chat interface
    ├── voice input controls
    ├── audio replay support
    └── generated image rendering
```

## Backend overview

The backend exposes an API for processing user requests and returning enriched assistant responses.

### Main endpoints

#### `GET /health`

Checks whether the API is running.

Example response:

```json
{
  "status": "ok",
  "service": "smart-librarian-api",
  "version": "1.0.0"
}
```

#### `POST /chat`

Main endpoint for assistant interaction.

#### `POST /assistant`

Alias endpoint with the same behavior as `/chat`.

### Backend capabilities

* Validates user input length and quality
* Blocks unsafe or disrespectful input through moderation
* Supports text or voice-driven requests
* Calls chatbot logic to generate a recommendation
* Optionally generates audio from the response
* Optionally generates a book-related image from the title
* Returns everything in a structured response object

### Validation behavior

The backend handles:

* empty messages
* overly long prompts
* meaningless prompts such as `...`, `ok`, or repeated characters
* moderation failures
* missing voice input path when voice mode is enabled
* runtime errors from chatbot, TTS, STT, or image generation

## Frontend overview

The frontend is a React-based chat application that communicates with the backend and presents the assistant experience in a modern UI.

### Frontend capabilities

* Send text prompts to the backend
* Use quick suggestion prompts
* Capture voice input directly in the browser
* Toggle audio generation on or off
* Toggle image generation on or off
* Automatically play the latest generated audio reply
* Replay the latest assistant audio response
* Display generated book artwork inline in the conversation

### Supported speech recognition languages

* Romanian (`ro-RO`)
* English (`en-US`)
* French (`fr-FR`)
* German (`de-DE`)
* Spanish (`es-ES`)
* Italian (`it-IT`)

## Request and response flow

1. The user writes a message or uses voice input in the frontend.
2. The frontend sends the message to the backend.
3. The backend validates and moderates the input.
4. The chatbot generates a recommendation and optional title.
5. If enabled:

   * the backend generates audio with text-to-speech
   * the backend generates an image preview based on the title
6. The frontend renders the assistant reply, plays audio automatically, and shows the generated image.

## Example request

```json
{
  "message": "I want a philosophical science fiction book.",
  "generate_audio": true,
  "generate_image": true
}
```

## Example response

```json
{
  "user_message": "I want a philosophical science fiction book.",
  "transcribed_text": null,
  "response": "You might enjoy ...",
  "title": "Example Book Title",
  "audio_generated": true,
  "audio_base64": "...",
  "image_path": "generated/example.png",
  "image_base64": "..."
}
```

## Tech stack

### Backend

* Python
* FastAPI
* Pydantic schemas
* CORS middleware
* Custom chatbot module
* Speech-to-text integration
* Text-to-speech integration
* Image generation utilities

### Frontend

* React
* JavaScript
* Browser Speech Recognition API
* CSS-based custom UI

## Configuration

### Backend environment

The backend uses the following environment variable:

* `ALLOWED_ORIGINS` — comma-separated list of frontend origins allowed by CORS

Default value:

```env
ALLOWED_ORIGINS=http://localhost:3000
```

## Running the project

### 1. Start the backend

Install dependencies and run the FastAPI server.

Example:

```bash
uvicorn main:app --reload
```

> Adjust the import path depending on where your FastAPI entry file is located.

### 2. Start the frontend

Install frontend dependencies and start the React development server.

Example:

```bash
npm install
npm start
```

## Usage

1. Open the frontend in your browser.
2. Type a request such as a genre, tone, mood, or theme.
3. Optionally enable:

   * auto voice reply
   * cover preview
4. Submit the message.
5. Read, listen to, and view the assistant response.

## Example prompts

* `I need a thrilling mystery story with twists and suspense.`
* `I want a romantic classic with emotional depth.`
* `Give me a philosophical science fiction book.`
* `I need an exciting sci-fi tale with dark tone.`

## Error handling

The application includes error handling for:

* unsupported browser voice input
* failed voice recognition
* failed API requests
* invalid or empty user input
* moderation issues
* audio or image generation failures

## Future improvements

* Add authentication and user history
* Save chat sessions
* Support multiple recommendations per prompt
* Add filters for author, publication year, or language
* Improve accessibility and mobile responsiveness
* Add deployment instructions for production

## Notes

* Audio is stored and transferred as Base64.
* Generated images are also returned as Base64 for direct rendering in the frontend.
* The frontend currently hides the audio element and plays generated responses automatically when possible.
* Browser autoplay policies may block automatic playback until the user interacts with the page.

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

* **Ias Alexandru-Ioan**
