import {
  createContext,
  ReactNode,
  useContext,
  useState,
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

  const addChore = (name: string, description: string, assignedTo: string) => {
    // this adds a new chore to the top of the chore board
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
    // this removes a chore after it has been checked off
    setChores((currentChores) =>
      currentChores.filter((chore) => chore.id !== id)
    );
  };

  return (
    <ChoreContext.Provider
      value={{ chores, addChore, deleteChore }}
    >
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
