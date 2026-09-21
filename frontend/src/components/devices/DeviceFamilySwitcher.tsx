interface Props {
  selected: string;
  onSelect: (family: string) => void;
}

export default function DeviceFamilySwitcher({ selected, onSelect }: Props) {
  return (
    <div className="flex bg-gray-950 border border-gray-800 rounded-lg p-1 mb-4">
      <button
        onClick={() => onSelect("simulation")}
        className={`flex-1 text-xs px-3 py-1.5 rounded-md transition font-medium ${
          selected === "simulation" 
            ? "bg-gray-800 text-emerald-400 shadow" 
            : "text-gray-500 hover:text-gray-300"
        }`}
      >
        Simulation
      </button>
      <button
        onClick={() => onSelect("edge")}
        className={`flex-1 text-xs px-3 py-1.5 rounded-md transition font-medium ${
          selected === "edge" 
            ? "bg-gray-800 text-emerald-400 shadow" 
            : "text-gray-500 hover:text-gray-300"
        }`}
      >
        Edge Hardware
      </button>
    </div>
  );
}