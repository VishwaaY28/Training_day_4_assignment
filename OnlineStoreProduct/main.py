from product import ProductCatalogDB

db=ProductCatalogDB()

db.add_category("fashion")
db.add_product("Shirt",1,600,10)
db.add_product("Jeans",1,1200,2)
#
db.update_product(1,500,11)
db.delete_product(2)
db.search_products(1000)
db.low_stock_report(5)
db.show_products()