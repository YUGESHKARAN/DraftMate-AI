# DraftMate AI

A robust backend service designed to correct and generate content for a social media application. This project leverages advanced natural language processing to ensure high-quality, relevant, and engaging content for users. It is already integrated with the [Tech-Community-App](https://github.com/YUGESHKARAN/Node-Blog-App.git) e-learning platform, providing automated content correction, generation, and moderation for educational and social features.

---

## Features 

- **Content Correction**: Automatically reviews and corrects grammar, spelling, and style in user-generated content.
- **Content Generation**: Generates engaging posts, comments, and learning materials for social interactions.
- **Integration-Ready**: Easily connects with existing applications—already integrated with the Tech. Community App e-learning platform.
- **Moderation Tools**: Detects and filters inappropriate or harmful content to ensure a safe community environment.
- **API Driven**: Provides RESTful endpoints for seamless integration and automation.

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

- **POST /generate-content**  
  Transforms the given draft into professional post content.



## Contributing 

Contributions are welcome! Open an issue or submit a pull request to help improve this project.

## License

This project is licensed under the MIT License.

## Contact

- **Author:** [YUGESHKARAN](https://github.com/YUGESHKARAN)
- **Related Project:** [Tech-Community-App](https://github.com/YUGESHKARAN/Node-Blog-App.git)

---
