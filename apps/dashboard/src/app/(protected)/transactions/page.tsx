"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchTransactions } from "@/lib/api";
import { TransactionTable } from "@/components/transactions/transaction-table";
import { TransactionFilters } from "@/components/transactions/transaction-filters";

export default function TransactionsPage() {
  const [filters, setFilters] = useState({
    search: "",
    status: [] as string[],
    riskLevel: [] as string[],
    type: [] as string[],
  });

  const { data } = useQuery({
    queryKey: ["transactions", filters],
    queryFn: () => fetchTransactions({ page: 1, page_size: 20 }),
  });

  const transactions = data?.items ?? [];

  const filtered = transactions.filter((tx) => {
    if (filters.search) {
      const q = filters.search.toLowerCase();
      const match =
        tx.transaction_id.toLowerCase().includes(q) ||
        tx.sender_id.toLowerCase().includes(q) ||
        (tx.merchant_id?.toLowerCase().includes(q) ?? false);
      if (!match) return false;
    }
    if (filters.status.length > 0 && !filters.status.includes(tx.status)) return false;
    if (filters.riskLevel.length > 0 && tx.risk_level && !filters.riskLevel.includes(tx.risk_level)) return false;
    if (filters.type.length > 0 && !filters.type.includes(tx.type)) return false;
    return true;
  });

  const handleFilterChange = (key: string, value: unknown) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const handleReset = () => {
    setFilters({ search: "", status: [], riskLevel: [], type: [] });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Transactions</h1>
        <p className="text-muted-foreground">
          Monitor and investigate transaction activity
        </p>
      </div>

      <TransactionFilters
        filters={filters}
        onFilterChange={handleFilterChange}
        onReset={handleReset}
      />

      <TransactionTable transactions={filtered} />

      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>
          Showing {filtered.length} of {data?.total ?? 0} transactions
        </span>
      </div>
    </div>
  );
}
