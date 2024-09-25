# def acos(x):
#     return math.acos(x)


# def cos(x):
#     return math.cos(x)


# def sin(x):
#     return math.sin(x)


# def radians(x):
#     return math.radians(x)


# def register_math_functions(dbapi_conn, connection_record):
#     dbapi_conn.create_function('acos', 1, acos)
#     dbapi_conn.create_function('cos', 1, cos)
#     dbapi_conn.create_function('sin', 1, sin)
#     dbapi_conn.create_function('radians', 1, radians)
#     print("Registered 'acos', 'cos', 'sin', and 'radians' functions.")


# # Add an event listener to the synchronous connection phase
# event.listen(async_engine.sync_engine, 'connect', register_math_functions)


# async def init_models():
#     async with async_engine.begin() as conn:
#         # Use run_sync to run blocking operations
#         await conn.run_sync(check_existing_tables_and_create)


# # Synchronous function to check existing tables and create if necessary
# def check_existing_tables_and_create(sync_conn):
#     inspector = inspect(sync_conn)
#     existing_tables = inspector.get_table_names()

#     if not existing_tables:
#         models.Base.metadata.create_all(sync_conn)
