# Stage 3: A2A Compliant AI Content Idea Agent

This project is a fully-featured, A2A (Agent-to-Agent) protocol compliant AI agent built for the HNG internship Stage 3 task. The agent, named "Content Catalyst," is designed to assist content creators by generating timely and relevant ideas based on current events.

## Features

-   **A2A Protocol Compliant:** Built to the official A2A specification using JSON-RPC 2.0, ensuring interoperability with platforms like Telex.
-   **Multi-Step AI Logic:** Implements an intelligent, two-stage AI process:
    1.  **Topic Extraction:** First, it uses Google's Gemini AI to analyze raw, conversational user input and extract a clean, precise search topic.
    2.  **Content Generation:** It then uses the clean topic to fetch a relevant news headline from the GNews API and sends both to Gemini again to generate a high-quality, actionable content idea.
-   **Robust Error Handling:** The agent gracefully handles failures from external APIs and returns compliant error messages.
-   **Modern Tech Stack:** Built with Python and FastAPI for high performance and validated with Pydantic for data integrity.

## Technology Stack

-   **Language:** Python
-   **Framework:** FastAPI
-   **Server:** Uvicorn
-   **Core AI:** Google Gemini (`gemini-2.5-flash`)
-   **Data Source:** GNews API
-   **Libraries:**
    -   `pydantic`: For strict data validation and A2A modeling.
    -   `requests`: For making HTTP requests to the GNews API.
    -   `python-dotenv`: For managing environment variables.
    -   `google-generativeai`: The official Python SDK for the Gemini API.
-   **Hosting:** Railway

## API Endpoint

The agent exposes a single, A2A-compliant endpoint.

### `POST /agent`

Accepts a JSON-RPC request and returns a `TaskResult` object.

-   **Request Body Format:**
    ```json
    {
        "jsonrpc": "2.0",
        "id": "user-request-123",
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [
                    {
                        "kind": "text",
                        "text": "Any topic or question here"
                    }
                ]
            }
        }
    }
    ```

## Local Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-folder>
    ```

2.  **Create and Activate a Virtual Environment:**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables:**
    Create a file named `.env` in the root of the project and add your API keys:
    ```env
    # .env file
    GNEWS_API_KEY=your_key_from_gnews.io
    GEMINI_API_KEY=your_key_from_google_ai_studio
    ```

## Running the Application Locally

Use the Uvicorn server to run the FastAPI application:

```bash
uvicorn main:app --reload

You can test the deployed agent using curl or any API client like Postman.

curl -X POST https://<your-deployed-url>/agent \
-H "Content-Type: application/json" \
-d '{
    "jsonrpc": "2.0",
    "id": "curl-test-001",
    "method": "message/send",
    "params": {
        "message": {
            "role": "user",
            "parts": [
                {
                    "kind": "text",
                    "text": "Nvidia"
                }
            ]
        }
    }
}'