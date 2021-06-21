import pytest
import localstack_client.session


@pytest.hookimpl()
def pytest_sessionstart(session):
    print("RUNNING conftest.py::pytest_sessionstart...")
    print("Connecting to localstack client")
    session = localstack_client.session.Session(region_name="us-west-1")
    s3 = session.resource("s3")
    print("Creating s3 bucket named: mybucket")
    try:
        s3.create_bucket(Bucket="mybucket")
    except Exception as e:
        print(f"Encountered an exception: {str(e)}")
    print("DONE")
