# Thai Recipes AI

## Overview

This project is a multi-agent AI application designed to assist users in retrieving information about Thai cuisine or conducting general web searches. The system employs state-of-the-art natural language processing techniques, leveraging tools like LangChain, Astra DB, Google Generative AI, and DuckDuckGo to route and process queries effectively. The primary focus is on delivering relevant answers related to Thai recipes, ingredients, and cultural food traditions.

---

## Features

- **PDF Document Ingestion**: Load and split PDF documents into chunks for processing and retrieval.
- **Vector Store Retrieval**: Store and retrieve embeddings from Astra DB using Cassandra.
- **Search Integration**: Perform web searches using DuckDuckGo for non-Thai cuisine-related questions.
- **Routing Logic**: Route user queries to the appropriate datasource (vectorstore or DuckDuckGo).
- **Structured Outputs**: Provide concise and structured answers for user queries.
- **Graph Workflow**: A state graph defines the routing and processing workflow for seamless query handling.

---

## Prerequisites

### Environment Variables

Create a `.env` file in the project root and define the following variables:

```env
ASTRA_DB_APPLICATION_TOKEN=<your_astra_db_application_token>
ASTRA_DB_ID=<your_astra_db_id>
GOOGLE_API_KEY=<your_google_api_key>
```

### Dependencies

Install the required Python packages:

```bash
pip install langchain cassio langchain_google_genai langgraph python-dotenv tqdm
```

---

## How It Works

### Query Routing

1. User submits a question.
2. The system determines if the question is related to Thai cuisine.
   - If yes, it uses the vectorstore to retrieve relevant documents.
   - If no, it performs a DuckDuckGo web search.

### Workflow

1. **Retrieve Documents**: Load and process a PDF containing Thai recipes using `PyPDFLoader` and `RecursiveCharacterTextSplitter`.
2. **Store Embeddings**: Generate embeddings with Google Generative AI and store them in Astra DB using Cassandra.
3. **Route Queries**: Use the `question_router` to decide the appropriate datasource.
4. **Process Results**: Return a structured response based on the retrieved documents or search results.

---

## Project Structure

```plaintext
├── data/                      # Directory containing PDF documents (e.g., ThaiRecipes.pdf)
├── .env                       # Environment variables file
├── main.py                    # Main application logic
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
```

---

## Usage

1. **Load the Application**:
   
   Make sure the environment variables are set up and run the application script:

   ```bash
   python main.py
   ```

2. **Ask a Question**:
   
   Use the `run_app` function to pass a question:

   ```python
   result = run_app("How do I make Pad Thai?")
   print(result)
   ```

---

## Example Query

**Input**:

```plaintext
What are the key ingredients for Tom Yum soup?
```

**Output**:

```plaintext
{
    "documents": ["Lemongrass, kaffir lime leaves, galangal, chili, shrimp, mushrooms, fish sauce, and lime juice."],
    "question": "What are the key ingredients for Tom Yum soup?"
}
```

---

## Future Enhancements

- **Improved Search Results**: Enhance the integration with web search APIs for better accuracy.
- **User Feedback**: Incorporate feedback loops to refine query processing.
- **Expanded Cuisine Support**: Add support for other cuisines or specialized topics.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## Contributors

- [SURESH BEEKHANI ](mailto:sureshbeekhni26@gmail.com)
