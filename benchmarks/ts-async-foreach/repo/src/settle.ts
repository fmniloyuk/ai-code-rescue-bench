export type Invoice = { id: string; amountCents: number };
export type Charge = (invoice: Invoice) => Promise<void>;

export async function settleAll(invoices: Invoice[], charge: Charge): Promise<string[]> {
  const settled: string[] = [];
  invoices.forEach(async (invoice) => {
    await charge(invoice);
    settled.push(invoice.id);
  });
  return settled;
}
