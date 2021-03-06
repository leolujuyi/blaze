from __future__ import absolute_import, division, print_function

import pytest
import sqlalchemy
import subprocess

psycopg2 = pytest.importorskip('psycopg2')
ps = subprocess.Popen("ps aux | grep postgres",shell=True, stdout=subprocess.PIPE)
output = ps.stdout.read()
num_processes = len(output.splitlines())
pytestmark = pytest.mark.skipif(num_processes < 6, reason="No Postgres Installation")

data = [('Alice', 1), ('Bob', 2), ('Charlie', 3)]

url = 'postgresql://localhost/postgres'
# url = 'postgresql://postgres:postgres@localhost/postgres'
engine = sqlalchemy.create_engine(url)

try:
    name = 'tmpschema'
    create = sqlalchemy.schema.CreateSchema(name)
    engine.execute(create)
    metadata = sqlalchemy.MetaData()
    metadata.reflect(engine, schema=name)
    drop = sqlalchemy.schema.DropSchema(name)
    engine.execute(drop)
except sqlalchemy.exc.OperationalError:
    pytestmark = pytest.mark.skipif(True, reason="Can not connect to postgres")


from blaze import into, resource
from contextlib import contextmanager


@contextmanager
def existing_schema(name):
    create = sqlalchemy.schema.CreateSchema(name)
    try:
        engine.execute(create)
    except:
        pass

    try:
        yield
    finally:
        metadata = sqlalchemy.MetaData()
        metadata.reflect(engine, schema=name)
        for t in metadata.tables.values():
            t.drop(bind=engine)

        drop = sqlalchemy.schema.DropSchema(name)
        engine.execute(drop)

@contextmanager
def non_existing_schema(name):
    try:
        yield
    finally:
        metadata = sqlalchemy.MetaData()
        metadata.reflect(engine, schema=name)
        for t in metadata.tables.values():
            t.drop(bind=engine)

        try:
            drop = sqlalchemy.schema.DropSchema(name)
            engine.execute(drop)
        except:
            pass


"""
def test_resource_specifying_database_name():
    with existing_schema('myschema'):
        sql = resource(url + '::myschema.accounts', dshape='var * {name: string, value: int}')
        assert isinstance(sql, sqlalchemy.Table)
        assert sql.table.schema == 'myschema'
"""
