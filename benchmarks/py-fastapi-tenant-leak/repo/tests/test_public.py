from app import Invoice, InvoiceRepository, User, list_open_invoices

user = User(id="u-1", tenant_id="tenant-a")
repo = InvoiceRepository(
    [
        Invoice(1, "tenant-a", "open"),
        Invoice(2, "tenant-b", "open"),
        Invoice(3, "tenant-a", "closed"),
    ]
)
assert [item.id for item in list_open_invoices(user, repo)] == [1]
