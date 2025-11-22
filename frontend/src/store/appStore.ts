import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

type View = 'dashboard' | 'backtest' | 'sensitivity' | 'historical';

interface AppState {
  currentDate: Date;
  setCurrentDate: (date: Date) => void;
  activeView: View;
  setActiveView: (view: View) => void;
  selectedCountry: string | null;
  setSelectedCountry: (country: string | null) => void;
  useOptimizedModel: boolean;
  setUseOptimizedModel: (use: boolean) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      currentDate: new Date(),
      setCurrentDate: (date) => set({ currentDate: date }),
      activeView: 'dashboard',
      setActiveView: (view) => set({ activeView: view }),
      selectedCountry: null,
      setSelectedCountry: (country) => set({ selectedCountry: country }),
      useOptimizedModel: true,  // Default to optimized model
      setUseOptimizedModel: (use) => set({ useOptimizedModel: use }),
    }),
    {
      name: 'geopolitical-market-game-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        currentDate: state.currentDate.toISOString(),
        activeView: state.activeView,
        useOptimizedModel: state.useOptimizedModel,
      }),
      // Custom deserializer to convert ISO string back to Date
      onRehydrateStorage: () => (state) => {
        if (state?.currentDate) {
          state.currentDate = new Date(state.currentDate as any);
        }
      },
    }
  )
);

