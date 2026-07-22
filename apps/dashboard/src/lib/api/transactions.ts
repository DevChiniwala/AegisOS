import { apiClient } from "./client";
import { mockTransactions } from "@/lib/mock-data";
import type { Transaction } from "@/types/transaction";
import type { PaginatedResponse } from "@/types/api";

export interface TransactionFilters {
  page?: number;
  page_size?: number;
  risk_level?: string;
  status?: string;
  type?: string;
  start_date?: string;
  end_date?: string;
}

export async function fetchTransactions(
  filters: TransactionFilters = {}
): Promise<PaginatedResponse<Transaction>> {
  try {
    const { data } = await apiClient.get<PaginatedResponse<Transaction>>(
      "/transactions",
      { params: filters }
    );
    return data;
  } catch {
    const page = filters.page || 1;
    const pageSize = filters.page_size || 10;
    return {
      items: mockTransactions.slice((page - 1) * pageSize, page * pageSize),
      total: mockTransactions.length,
      page,
      page_size: pageSize,
      total_pages: Math.ceil(mockTransactions.length / pageSize),
    };
  }
}

export async function fetchTransaction(id: string): Promise<Transaction> {
  try {
    const { data } = await apiClient.get<Transaction>(`/transactions/${id}`);
    return data;
  } catch {
    const found = mockTransactions.find((t) => t.transaction_id === id);
    if (!found) throw new Error("Transaction not found");
    return found;
  }
}
