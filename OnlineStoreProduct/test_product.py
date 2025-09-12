import inspect
from product import ProductCatalogDB

def test_add_category_query():
    db = ProductCatalogDB()
    expected = "INSERT INTO categories (category_name) VALUES (%s)"
    actual = inspect.getsource(db.add_category)
    assert expected in actual

def test_add_product_query():
    db = ProductCatalogDB()
    expected = "INSERT INTO products (name, category_id, price, stock_quantity) VALUES (%s, %s, %s, %s)"
    actual = inspect.getsource(db.add_product)
    assert expected in actual

def test_update_product_query():
    db = ProductCatalogDB()
    expected = "UPDATE products SET"
    actual = inspect.getsource(db.update_product)
    assert expected in actual

def test_delete_product_query():
    db = ProductCatalogDB()
    expected = "DELETE FROM products WHERE product_id = %s"
    actual = inspect.getsource(db.delete_product)
    assert expected in actual

def test_search_products_query():
    db = ProductCatalogDB()
    expected = "SELECT * FROM products WHERE 1=1"
    actual = inspect.getsource(db.search_products)
    assert expected in actual

def test_low_stock_report_query():
    db = ProductCatalogDB()
    expected = "SELECT * FROM products WHERE stock_quantity < %s"
    actual = inspect.getsource(db.low_stock_report)
    assert expected in actual

def test_show_all_products_query():
    db = ProductCatalogDB()
    expected = "LEFT JOIN categories c ON p.category_id = c.category_id"
    actual = inspect.getsource(db.show_products)
    assert expected in actual

def test_add_category_signature():
    sig = inspect.signature(ProductCatalogDB.add_category)
    assert list(sig.parameters.keys()) == ["self", "category_name"]

def test_add_product_signature():
    sig = inspect.signature(ProductCatalogDB.add_product)
    assert list(sig.parameters.keys()) == ["self", "name", "category_id", "price", "stock_quantity"]

def test_update_product_signature():
    sig = inspect.signature(ProductCatalogDB.update_product)
    assert list(sig.parameters.keys()) == ["self", "product_id", "price", "stock"]

def test_delete_product_signature():
    sig = inspect.signature(ProductCatalogDB.delete_product)
    assert list(sig.parameters.keys()) == ["self", "product_id"]

def test_search_products_signature():
    sig = inspect.signature(ProductCatalogDB.search_products)
    assert list(sig.parameters.keys()) == ["self", "max_price"]

def test_low_stock_signature():
    sig = inspect.signature(ProductCatalogDB.low_stock_report)
    assert list(sig.parameters.keys()) == ["self", "threshold"]

def test_show_products_signature():
    sig = inspect.signature(ProductCatalogDB.show_products)
    assert list(sig.parameters.keys()) == ["self"]