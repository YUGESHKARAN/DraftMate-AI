# DraftMate AI

- A content co-worker for the [Tech-Community-App](https://github.com/YUGESHKARAN/Node-Blog-App.git), designed to refine post content into a standardized format before upload. 
---

## Features 

- **Content Refining**: Reviews and corrects content to standardized format.
- **Production Guardraile**: Implemented Input/Output system level guardrails to prevent prompt injections, model abuse and data level security threats.
- **CORS support**: Uses CORS to prevent security threats under browser level.
- **API Rate-Limiting**: Serving RESTful endpoints with rate limiting to prevent api abuse.

## Getting Started 

### Prerequisites 

- [Node.js](https://nodejs.org/) (v16+ recommended)
- [npm](https://www.npmjs.com/) or [yarn](https://yarnpkg.com/)
- MongoDB or compatible database (if required by your configuration)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YUGESHKARAN/blogChat-backend.git
   cd blogChat-backend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Configure Environment Variables:**
   - Copy `.env.example` to `.env` (if available) or create a new `.env` file.
   - You **must** set the following required environment variable:
     ```
     GROQ_API_KEY=your-groq-api-key-here
     ```

4. **Start the server:**
   ```bash
   npm start
   # or
   yarn start
   ```

## Usage

- The backend can be used as a standalone service or as a microservice within a larger application.

### Integration Example

The backend is already integrated with the [Tech-Community-App](https://github.com/YUGESHKARAN/Node-Blog-App.git), an e-learning platform. Use this as a reference for integrating with your own apps.

## API Overview

- **GET /**  
  Retrieves _{"message": "Welcome to the DraftMate AI!"}_.

- **POST /enhance-content**  
  Transforms the given draft into professional post content.



## Contributing 

Contributions are welcome! Open an issue or submit a pull request to help improve this project.

## License

This project is licensed under the MIT License.

---
