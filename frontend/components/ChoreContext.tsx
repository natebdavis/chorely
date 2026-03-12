import {
  createContext,
  ReactNode,
  useContext,
  useState,
  useEffect,
} from "react";

export type Chore = {
  id: string;
  name: string;
  description: string;
  assignedTo: string;
};

type ChoreContextValue = {
  chores: Chore[];
  addChore: (name: string, description: string, assignedTo: string) => void;
  deleteChore: (id: string) => void;
};

const ChoreContext = createContext<ChoreContextValue | undefined>(undefined);

export function ChoreProvider({ children }: { children: ReactNode }) {
  const [chores, setChores] = useState<Chore[]>([]);

  const API_URL = "https://chorely.onrender.com/chores"; // change to your FastAPI IP

  // fetch chores from FastAPI when app loads
  useEffect(() => {
    const fetchChores = async () => {
      try {
        const response = await fetch(API_URL);
        const data = await response.json();
        setChores(data);
      } catch (error) {
        console.error("Failed to fetch chores:", error);
      }
    };

    fetchChores();
  }, []);

  const addChore = (name: string, description: string, assignedTo: string) => {
    setChores((currentChores) => [
      {
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        name: name.trim(),
        description: description.trim(),
        assignedTo: assignedTo.trim(),
      },
      ...currentChores,
    ]);
  };

  const deleteChore = (id: string) => {
    setChores((currentChores) =>
      currentChores.filter((chore) => chore.id !== id)
    );
  };

  return (
    <ChoreContext.Provider value={{ chores, addChore, deleteChore }}>
      {children}
    </ChoreContext.Provider>
  );
}

export function useChores() {
  const context = useContext(ChoreContext);

  if (!context) {
    throw new Error("useChores must be used inside a ChoreProvider");
  }

  return context;
}
