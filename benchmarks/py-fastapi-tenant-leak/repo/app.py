from dataclasses import dataclass

from fastapi import FastAPI

app = FastAPI()


@dataclass(frozen=True)
class User:
    id: str
    tenant_id: str


@dataclass(frozen=True)
class Invoice:
    id: int
    tenant_id: str
    status: str


class InvoiceRepository:
    def __init__(self, invoices: list[Invoice]) -> None:
        self.invoices = invoices


def list_open_invoices(user: User, repo: InvoiceRepository) -> list[Invoice]:
    return [invoice for invoice in repo.invoices if invoice.status == "open"]
