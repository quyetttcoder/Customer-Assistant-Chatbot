METADATA = [
    {
        "table_name": "products",
        "description": "Table containing information about products currently being sold.",
        "fields": {
            "productName": {
                "type": "str",
                "public": True,
                "desc": "Product name."
            },
            "supplierID": {
                "type": "int",
                "public": False,
                "desc": "Foreign key to the 'suppliers' table, ONLY used to implicitly retrieve supplier information; this ID must not be displayed to the user."
            },
            "categoryID": {
                "type": "int",
                "public": False,
                "desc": "Foreign key to the 'categories' table, ONLY used to implicitly retrieve product category information; this ID must not be displayed to the user."
            },
            "quantityPerUnit": {
                "type": "str",
                "public": True,
                "desc": "Packaging specification or quantity of products contained in each selling unit."
            },
            "unitPrice": {
                "type": "float",
                "public": True,
                "desc": "Unit price of the product."
            },
            "unitsInStock": {
                "type": "int",
                "public": True,
                "desc": "Current quantity of the product in stock."
            },
            "discontinued": {
                "type": "bool",
                "public": True,
                "desc": "Product status: True if the product has been discontinued, False if the product is still being sold."
            }
        }
    },

    {
        "table_name": "suppliers",
        "description": "Table containing information about product suppliers.",
        "fields": {
            "companyName": {
                "type": "str",
                "public": True,
                "desc": "Company or supplier name."
            },
            "contactName": {
                "type": "str",
                "public": True,
                "desc": "Name of the representative or contact person at the supplier."
            },
            "contactTitle": {
                "type": "str",
                "public": True,
                "desc": "Job title of the contact person at the supplier."
            },
            "address": {
                "type": "str",
                "public": True,
                "desc": "Address of the supplier."
            },
            "city": {
                "type": "str",
                "public": True,
                "desc": "City where the supplier is headquartered."
            },
            "postalCode": {
                "type": "str",
                "public": True,
                "desc": "Postal code of the supplier."
            },
            "country": {
                "type": "str",
                "public": True,
                "desc": "Country of the supplier."
            },
            "phone": {
                "type": "str",
                "public": True,
                "desc": "Supplier contact phone number."
            }
        }
    },

    {
        "table_name": "categories",
        "description": "Table containing information about product categories.",
        "fields": {
            "categoryName": {
                "type": "str",
                "public": True,
                "desc": "Product category name."
            },
            "description": {
                "type": "str",
                "public": True,
                "desc": "Description of the product category."
            }
        }
    },

    {
        "table_name": "orders",
        "description": "Table containing general information about customer orders.",
        "fields": {
            "orderID": {
                "type": "int",
                "public": False,
                "desc": "Unique identifier of the order."
            },
            "customerID": {
                "type": "str",
                "public": False,
                "desc": """
                Foreign key to the 'customers' table. When the user asks about a specific order, first require \
                them to provide the contact name (contactName) and phone number (phone), and may additionally require \
                them to provide the address. These fields are retrieved from the 'customers' table through the foreign key \
                in order to accurately verify that the user asking about the order is the actual user who owns the order.
                """
            },
            "orderDate": {
                "type": "datetime",
                "public": True,
                "desc": "Date when the customer placed the order."
            },
            "requiredDate": {
                "type": "datetime",
                "public": True,
                "desc": "Date when the customer requested to receive the order."
            },
            "shippedDate": {
                "type": "datetime",
                "public": True,
                "desc": "Date when the order was handed over to the shipping company or shipped."
            },
            "shipName": {
                "type": "str",
                "public": True,
                "desc": "Name of the person or organization receiving the order."
            },
            "shipAddress": {
                "type": "str",
                "public": True,
                "desc": "Delivery address of the order."
            },
            "shipCity": {
                "type": "str",
                "public": True,
                "desc": "Delivery city."
            },
            "shipCountry": {
                "type": "str",
                "public": True,
                "desc": "Country where the order is delivered."
            },
            "shipperID": {
                "type": "int",
                "public": False,
                "desc": "Foreign key to the 'shippers' table, ONLY used to implicitly retrieve shipping company information; this ID must not be displayed to the user."
            }
        }
    },

    {
        "table_name": "shippers",
        "description": "Table containing information about shipping companies used to deliver orders.",
        "fields": {
            "companyName": {
                "type": "str",
                "public": True,
                "desc": "Name of the shipping company or carrier."
            },
            "phone": {
                "type": "str",
                "public": True,
                "desc": "Contact phone number of the shipping company."
            }
        }
    },

    {
        "table_name": "customers",
        "description": "Table containing customer information. Only a limited number of fields may be used to verify customer identity when order information needs to be retrieved.",
        "fields": {
            "contactName": {
                "type": "str",
                "public": False,
                "desc": "Customer contact name. ONLY used to match and verify customer information in the background when the user requests order information; MUST NOT be returned to the UI."
            },
            "phone": {
                "type": "str",
                "public": False,
                "desc": "Customer phone number. ONLY used to match and verify customer information in the background when the user requests order information; MUST NOT be returned to the UI."
            },
            "address": {
                "type": "str",
                "public": False,
                "desc": "Customer address, only retrieved when the user provides address information. ONLY used to match and verify customer information in the background when the user requests order information; MUST NOT be returned to the UI."
            },
        }
    }
]