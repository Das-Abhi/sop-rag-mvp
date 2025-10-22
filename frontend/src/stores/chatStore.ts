import { create } from 'zustand';
import { Message, Citation } from '../types';

interface ChatState {
  messages: Message[];
  loading: boolean;
  error: string | null;
  selectedDocuments: string[];

  addMessage: (message: Message) => void;
  clearMessages: () => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  selectDocument: (docId: string) => void;
  deselectDocument: (docId: string) => void;
  clearSelection: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  loading: false,
  error: null,
  selectedDocuments: [],

  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),

  clearMessages: () => set({ messages: [] }),

  setLoading: (loading) => set({ loading }),

  setError: (error) => set({ error }),

  selectDocument: (docId) =>
    set((state) => ({
      selectedDocuments: [...state.selectedDocuments, docId],
    })),

  deselectDocument: (docId) =>
    set((state) => ({
      selectedDocuments: state.selectedDocuments.filter((id) => id !== docId),
    })),

  clearSelection: () => set({ selectedDocuments: [] }),
}));
