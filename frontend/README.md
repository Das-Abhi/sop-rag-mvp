# SOP RAG MVP - Frontend

React + TypeScript frontend for the Retrieval-Augmented Generation system.

## Features

- 💬 **Chat Interface** - Ask questions about your documents in real-time
- 📄 **Document Management** - Upload, organize, and manage PDF documents
- 🔗 **Citation Tracking** - See sources for every answer
- 🔄 **Real-time Updates** - WebSocket integration for live progress
- 📊 **Document Stats** - Track text chunks, images, and tables
- 🎨 **Responsive Design** - Works on desktop and mobile

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **Axios** - HTTP client
- **Lucide** - Icons

## Quick Start

### Prerequisites
- Node.js 16+
- Backend running on `http://localhost:8000`

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

### Build

```bash
npm run build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── ChatInterface.tsx
│   │   ├── DocumentManager.tsx
│   │   ├── DocumentCard.tsx
│   │   ├── MessageBubble.tsx
│   │   └── ...
│   ├── services/            # API client
│   │   └── api.ts
│   ├── stores/              # Zustand state management
│   │   ├── chatStore.ts
│   │   └── documentStore.ts
│   ├── types/               # TypeScript types
│   │   └── index.ts
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
├── vite.config.ts           # Vite configuration
├── tsconfig.json            # TypeScript config
├── tailwind.config.js       # Tailwind config
└── package.json
```

## API Integration

The frontend connects to the backend API:

### Documents
- `GET /api/v1/documents` - List all documents
- `POST /api/v1/documents/upload` - Upload PDF
- `DELETE /api/v1/documents/{id}` - Delete document

### Queries
- `POST /api/v1/query` - Submit RAG query with citations
- `GET /api/v1/query/health` - Check RAG service health

### WebSocket
- `WS /ws` - Real-time updates on document processing

## Usage

### Upload Document
1. Click "Upload Document" in Documents tab
2. Select a PDF file
3. Wait for processing to complete (status will change to "completed")

### Ask Questions
1. Go to Chat tab
2. Select one or more documents
3. Type your question
4. View the response with source citations

## Environment Variables

Create a `.env` file:

```
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## Development Notes

- All API calls include error handling and loading states
- WebSocket auto-connects and handles reconnection
- Document selection is persistent in chat
- Citations show document source and page number
- Responsive design uses Tailwind breakpoints (md, lg)

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Contributing

1. Create a feature branch
2. Keep components simple and focused
3. Use TypeScript for type safety
4. Test with the backend API running

## License

MIT
