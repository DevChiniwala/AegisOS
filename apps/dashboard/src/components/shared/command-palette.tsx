"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  ArrowLeftRight,
  Network,
  Activity,
  Radio,
  Settings,
  LayoutDashboard,
  Play,
  Zap,
} from "lucide-react";

interface CommandItem {
  id: string;
  label: string;
  description?: string;
  icon: React.ReactNode;
  action: () => void;
  category: string;
}

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const router = useRouter();

  const commands: CommandItem[] = [
    {
      id: "nav-dashboard",
      label: "Go to Dashboard",
      icon: <LayoutDashboard size={16} />,
      action: () => router.push("/dashboard"),
      category: "Navigation",
    },
    {
      id: "nav-transactions",
      label: "Go to Transactions",
      icon: <ArrowLeftRight size={16} />,
      action: () => router.push("/transactions"),
      category: "Navigation",
    },
    {
      id: "nav-investigations",
      label: "Go to Investigations",
      icon: <Search size={16} />,
      action: () => router.push("/investigations"),
      category: "Navigation",
    },
    {
      id: "nav-graph",
      label: "Go to Graph Explorer",
      icon: <Network size={16} />,
      action: () => router.push("/graph"),
      category: "Navigation",
    },
    {
      id: "nav-live",
      label: "Go to Live Feed",
      icon: <Radio size={16} />,
      action: () => router.push("/live"),
      category: "Navigation",
    },
    {
      id: "nav-models",
      label: "Go to Models",
      icon: <Activity size={16} />,
      action: () => router.push("/models"),
      category: "Navigation",
    },
    {
      id: "nav-settings",
      label: "Go to Settings",
      icon: <Settings size={16} />,
      action: () => router.push("/settings"),
      category: "Navigation",
    },
    {
      id: "action-score",
      label: "Score Transaction",
      description: "Score a transaction for fraud risk",
      icon: <Zap size={16} />,
      action: () => router.push("/transactions?action=score"),
      category: "Actions",
    },
    {
      id: "action-investigate",
      label: "Start Investigation",
      description: "Launch multi-agent investigation",
      icon: <Play size={16} />,
      action: () => router.push("/investigations?action=new"),
      category: "Actions",
    },
  ];

  const filtered = commands.filter(
    (cmd) =>
      cmd.label.toLowerCase().includes(query.toLowerCase()) ||
      cmd.description?.toLowerCase().includes(query.toLowerCase()) ||
      cmd.category.toLowerCase().includes(query.toLowerCase())
  );

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setOpen((prev) => !prev);
        setQuery("");
        setSelectedIndex(0);
      }

      if (!open) return;

      if (e.key === "Escape") {
        setOpen(false);
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prev) => Math.min(prev + 1, filtered.length - 1));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((prev) => Math.max(prev - 1, 0));
      } else if (e.key === "Enter" && filtered[selectedIndex]) {
        filtered[selectedIndex].action();
        setOpen(false);
      }
    },
    [open, filtered, selectedIndex]
  );

  useEffect(() => {
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  if (!open) return null;

  const grouped = filtered.reduce<Record<string, CommandItem[]>>((acc, cmd) => {
    if (!acc[cmd.category]) acc[cmd.category] = [];
    acc[cmd.category].push(cmd);
    return acc;
  }, {});

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh]">
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm"
        onClick={() => setOpen(false)}
      />
      <div className="relative w-full max-w-lg rounded-xl border border-zinc-700 bg-zinc-900 shadow-2xl">
        <div className="flex items-center gap-2 border-b border-zinc-700 px-4 py-3">
          <Search size={16} className="text-zinc-400" />
          <input
            type="text"
            placeholder="Search commands..."
            className="flex-1 bg-transparent text-sm text-white outline-none placeholder:text-zinc-500"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
          />
          <kbd className="rounded border border-zinc-600 px-1.5 py-0.5 text-[10px] text-zinc-400">
            ESC
          </kbd>
        </div>

        <div className="max-h-[300px] overflow-y-auto p-2">
          {Object.entries(grouped).map(([category, items]) => (
            <div key={category}>
              <div className="px-2 py-1.5 text-[11px] font-medium uppercase tracking-wider text-zinc-500">
                {category}
              </div>
              {items.map((cmd) => {
                const globalIndex = filtered.indexOf(cmd);
                const isSelected = globalIndex === selectedIndex;
                return (
                  <button
                    key={cmd.id}
                    className={`flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm transition-colors ${
                      isSelected
                        ? "bg-zinc-700/50 text-white"
                        : "text-zinc-300 hover:bg-zinc-800"
                    }`}
                    onClick={() => {
                      cmd.action();
                      setOpen(false);
                    }}
                    onMouseEnter={() => setSelectedIndex(globalIndex)}
                  >
                    <span className="text-zinc-400">{cmd.icon}</span>
                    <div className="flex-1">
                      <div>{cmd.label}</div>
                      {cmd.description && (
                        <div className="text-xs text-zinc-500">
                          {cmd.description}
                        </div>
                      )}
                    </div>
                  </button>
                );
              })}
            </div>
          ))}

          {filtered.length === 0 && (
            <div className="px-3 py-8 text-center text-sm text-zinc-500">
              No commands found
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
