import { create } from 'zustand';
import { Document } from '../types';

interface DocumentState {
  documents: Document[];
  loading: boolean;
  error: string | null;
  uploadProgress: number;

  setDocuments: (documents: Document[]) => void;
  addDocument: (document: Document) => void;
  removeDocument: (id: string) => void;
  updateDocument: (id: string, document: Partial<Document>) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setUploadProgress: (progress: number) => void;
}

export const useDocumentStore = create<DocumentState>((set) => ({
  documents: [],
  loading: false,
  error: null,
  uploadProgress: 0,

  setDocuments: (documents) => set({ documents }),

  addDocument: (document) =>
    set((state) => ({ documents: [...state.documents, document] })),

  removeDocument: (id) =>
    set((state) => ({
      documents: state.documents.filter((doc) => doc.document_id !== id),
    })),

  updateDocument: (id, updates) =>
    set((state) => ({
      documents: state.documents.map((doc) =>
        doc.document_id === id ? { ...doc, ...updates } : doc
      ),
    })),

  setLoading: (loading) => set({ loading }),

  setError: (error) => set({ error }),

  setUploadProgress: (progress) => set({ uploadProgress: progress }),
}));
